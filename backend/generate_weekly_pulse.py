# backend/generate_weekly_pulses.py

import os
import re
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# --- Initialize Clients ---
load_dotenv()

# Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials must be set.")
supabase: Client = create_client(supabase_url, supabase_key)

# Gemini AI
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    raise ValueError("GOOGLE_API_KEY must be set.")
genai.configure(api_key=gemini_api_key)
# --- End of Initialization ---

MIN_PULSES_FOR_WEEKLY_SUMMARY = 15

def generate_weekly_pulse():
    """Generates a single weekly pulse by summarizing all daily pulses from the past week."""
    print("Starting weekly pulse generation...")

    # 1. Data Collection
    today = datetime.now(timezone.utc)
    one_week_ago = today - timedelta(days=7)

    response = supabase.table('pulses') \
        .select('title, blurb, content, published_date') \
        .gte('published_date', one_week_ago.isoformat()) \
        .execute()

    if response.error:
        raise Exception(f"Error fetching daily pulses: {response.error.message}")

    daily_pulses = response.data
    print(f"Found {len(daily_pulses)} daily pulses from the past week.")

    if len(daily_pulses) < MIN_PULSES_FOR_WEEKLY_SUMMARY:
        print(f"Not enough pulses for a weekly summary (found {len(daily_pulses)}, need {MIN_PULSES_FOR_WEEKLY_SUMMARY}). Exiting.")
        return

    # 2. Content Structuring
    structured_content = "=== START OF WEEKLY PULSE DATA ===\n\n"
    for pulse in sorted(daily_pulses, key=lambda p: p['published_date']):
        pulse_date = datetime.fromisoformat(pulse['published_date']).strftime('%A, %B %d, %Y')
        structured_content += f"--- PULSE FROM: {pulse_date} ---\n"
        structured_content += f"TITLE: {pulse['title']}\n"
        structured_content += f"BLURB: {pulse['blurb']}\n"
        structured_content += f"CONTENT: {pulse['content']}\n\n"
    structured_content += "=== END OF WEEKLY PULSE DATA ==="

    # 3. AI-Powered Synthesis (The Prompt)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    You are an executive-level cybersecurity analyst writing a weekly roundup for industry leaders. Your task is to analyze the following collection of daily cybersecurity pulse reports from the past week and synthesize them into a single, cohesive summary.

    **Instructions:**
    1.  **Identify Major Themes:** Read all the provided daily reports and identify the 3-5 most significant, overarching themes or trends. Do not simply list daily events.
    2.  **Synthesize and Connect:** Explain how events connect. Did an early-week vulnerability lead to a late-week data breach? Did multiple reports point to the same threat actor?
    3.  **Provide Actionable Insight:** Conclude with a forward-looking "What to Watch For" section, providing actionable advice based on the week's trends.
    4.  **Adhere to the Output Format STRICTLY.** Do not include any text or pleasantries outside of this format.

    **Daily Pulse Data:**
    {structured_content}

    **Required Output Format:**
    TITLE: [A concise, impactful title for the weekly cybersecurity roundup]
    BLURB: [A 2-3 sentence executive summary of the week's most critical developments and what they mean.]
    CONTENT: [A multi-paragraph analysis covering the major themes, how they evolved throughout the week, and a final "What to Watch For" section. Use double newlines to separate paragraphs.]
    """

    print("Sending content to Gemini for synthesis...")
    response = model.generate_content(prompt)
    generated_text = response.text.strip()

    # 4. Storing the Weekly Pulse
    match = re.search(r"TITLE:\s*(.*?)\s*BLURB:\s*(.*?)\s*CONTENT:\s*(.*)", generated_text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise Exception(f"Failed to parse generated content from LLM. Raw output: {generated_text}")

    title, blurb, content = (g.strip() for g in match.groups())

    insert_response = supabase.table('weekly_pulses').insert({
        'title': title,
        'blurb': blurb,
        'content': content
    }).execute()

    if insert_response.error:
        raise Exception(f"Error inserting weekly pulse: {insert_response.error.message}")

    print(f"Successfully generated and saved new weekly pulse: '{title}'")

if __name__ == "__main__":
    generate_weekly_pulse()