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

def slugify(text):
    """Converts a string into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[\s\W-]+', '-', text)
    return text.strip('-')

def generate_weekly_pulse():
    """Generates a single weekly pulse by summarizing all daily pulses from the past week."""
    print("Starting weekly pulse generation...")

    # 1. Data Collection
    today = datetime.now(timezone.utc)
    one_week_ago = today - timedelta(days=7)

    try:
        response = supabase.table('pulses') \
            .select('title, blurb, content, published_date') \
            .gte('published_date', one_week_ago.isoformat()) \
            .execute()

        # The data is directly in the response object
        daily_pulses = response.data

    except Exception as e:
        raise Exception(f"Error fetching daily pulses: {e}")

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
    model = genai.GenerativeModel('gemini-2.5-pro')
    prompt = f"""
    You are a senior Strategic Cybersecurity Intelligence Analyst preparing a weekly brief for an audience of CISOs, board members, and other senior leaders. Your mission is to distill raw daily intelligence into high-level, forward-looking strategic insights.

    Your goal is NOT to simply summarize the daily reports. It is to **synthesize** them by identifying underlying trends and performing **second-order thinking** to produce a cohesive strategic brief that provides unique, actionable value.

    **Core Directives:**

    1.  **Identify Converging Trends:** Do not list individual events. Analyze the complete dataset to identify 2-4 significant, overarching trends. Consider questions like: Are disparate attacks targeting the same industry? Is a new TTP (Tactic, Technique, and Procedure) being used by multiple threat actors? Is there a subtle, underlying technological vulnerability connecting seemingly unrelated incidents?

    2.  **Employ Second-Order Thinking:** Your primary value is to analyze the "so what?" factor. Move beyond direct cause-and-effect to explore the broader implications.
        * **Poor, First-Order Thought:** "A vulnerability in library X was announced, and a patch was released."
        * **Excellent, Second-Order Thought:** "The critical vulnerability in library X, which is embedded in thousands of enterprise products, highlights a systemic risk in software supply chains. This event suggests that procurement and risk management teams need to re-evaluate their dependency analysis, as patching is merely a reactive measure to a deeper, systemic issue."

    3.  **Generate Novel, Actionable Intelligence:** Your final section must provide strategic, non-obvious guidance. Do not give generic advice.
        * **STRICTLY FORBIDDEN ADVICE:** Anything related to common best practices, including but not limited to: multifactor authentication (MFA), general employee awareness training, principle of least privilege, prompt patching/updates, data encryption, data backups, password policies, or network segmentation. Your audience already knows this.
        * **REQUIRED ACTIONABLE INTELLIGENCE:** Focus on strategic shifts. Advise on things like: re-prioritizing threat models based on new adversary TTPs, suggesting specific intelligence requirements for threat hunting teams, or recommending discussions with legal counsel about the implications of a new attack vector on regulatory compliance.

    **Daily Intelligence Data:**
    {structured_content}

    **Required Output Format (Strict Adherence Required):**

    TITLE: [A concise, forward-looking title that captures the week's strategic narrative.]
    BLURB: [A 2-3 sentence executive summary. Immediately state the most critical strategic takeaway for a time-constrained leader.]
    CONTENT: [The full analysis. Use Markdown for subheadings as specified below. Use double newlines for paragraphs.]
    **Key Intelligence Themes**

    A brief introductory paragraph that sets the strategic tone for the week, framing the subsequent analysis.

    **Theme 1: [Descriptive Title for the First Major Trend]**
    A multi-paragraph analysis of the first major trend identified. Weave together events from different daily pulses to build your case. Focus on the "why" and the connections between events, not just the "what."

    **Theme 2: [Descriptive Title for the Second Major Trend]**
    A multi-paragraph analysis of the second major trend, following the same methodology as above. Connect disparate events and explain their collective significance.

    *(Add additional themes as necessary, up to a maximum of four)*

    **Strategic Outlook & Actionable Intelligence**

    A concluding section that synthesizes the themes into a forward-looking perspective. Provide 2-3 specific, non-generic, and strategic recommendations for senior leadership based on the week's intelligence.
    """


    generation_config = {
        "temperature": 0.4,
        "max_output_tokens": 8192, # Explicitly set a high limit for the response
    }


    print("Sending content to Gemini for synthesis...")
    response = model.generate_content(
        prompt,
        generation_config=generation_config,
        )
    generated_text = response.text.strip()

    # 4. Storing the Weekly Pulse
    match = re.search(r"TITLE:\s*(.*?)\s*BLURB:\s*(.*?)\s*CONTENT:\s*(.*)", generated_text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise Exception(f"Failed to parse generated content from LLM. Raw output: {generated_text}")

    title, blurb, content = (g.strip() for g in match.groups())

    pulse_slug = slugify(title)

    try:
        supabase.table('weekly_pulses').insert({
            'title': title,
            'blurb': blurb,
            'content': content,
            'slug': pulse_slug,
        }).execute()
    except Exception as e:
        raise Exception(f"Error inserting weekly pulse: {e}")

    print(f"Successfully generated and saved new weekly pulse: '{title}'")

if __name__ == "__main__":
    generate_weekly_pulse()