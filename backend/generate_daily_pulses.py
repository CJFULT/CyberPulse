# backend/generate_daily_pulses.py

import os
import re
import json
import time
from datetime import timedelta, datetime, timezone
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai
from embedding_utils import generate_embedding, get_or_create_collection, PULSES_COLLECTION

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
    raise ValueError("GOOGLE_API_KEY must be set in the .env file.")
genai.configure(api_key=gemini_api_key)
# --- End of Initialization ---

def slugify(text):
    """Converts a string into a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[\s\W-]+', '-', text) # Replace spaces and non-word chars with a hyphen
    return text.strip('-')


def generate_pulses(min_articles_for_pulse=3):
    """Generates daily pulses for categories based on newly categorized articles."""
    print('Starting daily pulse generation...')
    
    model = genai.GenerativeModel('gemini-2.5-pro')
    pulses_collection = get_or_create_collection(PULSES_COLLECTION)

    # --- NEW: Fetch recent articles and their categories ---
    # 1. Fetch recent, categorized articles that haven't been used for a pulse yet
    one_week_ago_dt = datetime.now(timezone.utc) - timedelta(days=7)
    one_week_ago_iso = one_week_ago_dt.isoformat()

    response = supabase.table('articles').select('*, article_categories(category_id)') \
        .eq('is_categorized', 'true') \
        .eq('processed_for_pulse', 'false') \
        .gte('scraped_date', f'"{one_week_ago_iso}"') \
        .execute()
        
    articles = response.data
    if not articles:
        print("No new articles available to generate pulses.")
        return

    # 2. Group articles by their category
    articles_by_category = defaultdict(list)
    for article in articles:
        for cat_link in article.get('article_categories', []):
            articles_by_category[cat_link['category_id']].append(article)

    # 3. Fetch all category details (name, etc.)
    cat_response = supabase.table('categories').select('id, name').execute()
    category_details = {cat['id']: cat for cat in cat_response.data}
    # --- End of New Section ---

    total_pulses_generated = 0
    articles_to_mark_processed = set()

    for category_id, articles_in_cat in articles_by_category.items():
        category_name = category_details.get(category_id, {}).get('name', 'Unknown Category')
        
        if len(articles_in_cat) < min_articles_for_pulse:
            print(f'Skipping category "{category_name}" (only {len(articles_in_cat)} articles, needs {min_articles_for_pulse}).')
            continue

        print(f'\n--- Processing Category: {category_name} ({len(articles_in_cat)} articles) ---')

        # Combine content and gather article IDs to be marked as processed
        combined_content = []
        for article in articles_in_cat:
            combined_content.append(f"### Article Title: {article['title']}\n{article['raw_content']}\n---")
            articles_to_mark_processed.add(article['id'])
        
        full_combined_text = "\n\n".join(combined_content)

        # RAG implementation (retrieving past pulses from ChromaDB) remains the same...
        past_pulses_context = "" # Your RAG logic here if you add it back

        # --- The prompt for the AI remains the same ---
        prompt = f"""

        ## The Synthesis Architect: Pulse Generation Protocol

        ### 1. Core Mandate
        Your sole purpose is to act as "The Synthesis Architect." You are to receive three distinct excerpts from a single article concerning technology, AI, or cybersecurity. Your mission is to transcend simple summarization and perform a rigorous, transformative synthesis of these excerpts. You will also be provided with past pulses to aid in identifying trends and second-order consequences. The final output must be a cohesive, non-plagiarized "pulse" designed to provide actionable and informative insight for a broad audience, including industry experts, students, and those with foundational knowledge. Your analysis must reveal novel trends, strategic implications, and non-obvious consequences.

        ### 2. Operational Directives
        * **Analytical Frameworks:** You must apply a combination of the following analytical frameworks to the excerpts:
            * **Systems Thinking:** Identify the broader system, its actors, feedback loops, and points of leverage or constraint. Analyze the excerpts not as isolated events but as components of a larger, interconnected system.
            * **Economic Principles:** Analyze the incentives, costs, and benefits for all actors. Determine who captures the value and how the economic calculus for attackers or defenders might change.
            * **Game Theory & Strategy:** View the situation as a strategic game. Identify the players, their goals, and potential competitive advantages or moats.
            * **Second-Order Thinking:** Go beyond the immediate effects. For every action or event described, ask "And then what?" to uncover non-obvious, downstream consequences. Use the provided "Past Pulses" for pattern recognition to enhance this analysis.
        * **Stratechery-style Analysis:** Emulate the principles of Ben Thompson's Stratechery model.
            * Connect the current events in the excerpts to durable theoretical frameworks.
            * Focus on the "why" and "so what?"—the strategic implications for the future, not just "what" happened.
            * Use clear, precise language to make complex strategic concepts accessible to an intelligent audience.
        * **Plagiarism & Paraphrasing Prevention:** You are strictly forbidden from summarizing, rephrasing, or restating the original text. Your output must be a novel synthesis of the underlying concepts. Do not use direct quotes or closely rephrased sentences from the source material. Your analysis should be a new creation, not a derivative work.

        ### 3. Output Structure
        Your final output must be formatted exactly as follows, with no additional commentary, prose, or introductions.

        **Title:**
        * A concise, impactful, and SEO-friendly title (5-10 words) that captures the core insight of the synthesis.

        **Blurb:**
        * A short, 2-3 sentence summary of the "pulse." (min 20 words, max 120 words) It must explain the core insight and its significance, serving as a teaser for the full analysis.

        **Context:**
        * A detailed, well-structured synthesis (2-3 paragraphs, min 250 words, max 350 words) that combines the insights from all three excerpts. This section must reveal the second-order consequences and strategic implications uncovered through your analytical process. The analysis should progress logically, building from a foundational concept to a powerful conclusion.

        ### 4. Input Protocol
        You will receive input in the following format, where `[category_name]` and the article excerpts are dynamically provided by the system. You will also be provided with a section for "Past Pulses".

        **Category:**
        {category_name.upper()}

        **New Articles:**
        {full_combined_text}

        **Past Pulses:**
        {past_pulses_context}
        """
        
        
        
        try:
            print(f'  Sending combined content for "{category_name}" to LLM...')
            response = model.generate_content(prompt)
            generated_text = response.text.strip()
            
            match = re.search(
                r"^\s*\**\s*TITLE\s*\**\s*:\s*(.*?)\s*\**\s*BLURB\s*\**\s*:\s*(.*?)\s*\**\s*CONTEXT\s*\**\s*:\s*(.*)",
                generated_text,
                re.DOTALL | re.IGNORECASE | re.MULTILINE
            )
            if not match:
                print(f"  ERROR: Failed to parse LLM output for {category_name}.")
                print(f"  --- RAW LLM OUTPUT --- \n{generated_text}\n  --- END RAW LLM OUTPUT ---")
                continue

            title = match.group(1).lstrip(' *')
            blurb = match.group(2).lstrip(' *')
            content = match.group(3).lstrip(' *')

            pulse_slug = slugify(title)

            # --- NEW: Insert the new pulse into Supabase ---
            pulse_response = supabase.table('pulses').insert({
                'title': f"{title.strip()}",
                'blurb': blurb.strip(),
                'content': content.strip(),
                'category_id': category_id,
                'slug': pulse_slug
            }).execute()
            
            new_pulse_id = pulse_response.data[0]['id']
            print(f'  Successfully generated and saved new pulse for {category_name}.')
            total_pulses_generated += 1
            # --- End of New Section ---

            # Add new pulse to ChromaDB (logic remains the same)
            pulse_embedding = generate_embedding(content.strip())
            if pulse_embedding:
                pulses_collection.add(
                    documents=[content.strip()],
                    metadatas=[{"pulse_id": new_pulse_id, "category": category_name}],
                    ids=[str(new_pulse_id)],
                    embeddings=[pulse_embedding]
                )

            print('  Pausing for 60 seconds to respect API rate limits...')
            time.sleep(60)

        except Exception as e:
            print(f'  Error generating or saving pulse for {category_name}: {e}')

    # --- NEW: Mark all used articles as processed ---
    if articles_to_mark_processed:
        print(f'\nMarking {len(articles_to_mark_processed)} articles as processed_for_pulse...')
        supabase.table('articles').update({'processed_for_pulse': True}) \
            .in_('id', list(articles_to_mark_processed)) \
            .execute()
    # --- End of New Section ---

    print(f'\nFinished daily pulse generation. Total pulses generated: {total_pulses_generated}.')


if __name__ == "__main__":
    generate_pulses()