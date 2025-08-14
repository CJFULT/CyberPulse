# backend/generate_weekly_pulses.py

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
    """Generates weekly pulses for categories based on newly categorized articles."""
    print('Starting weekly pulse generation...')
    
    model = genai.GenerativeModel('gemini-2.5-flash')
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
        You are an **expert cybersecurity analyst** and a **dedicated educator** for a leading cybersecurity news platform. Your primary goal is to synthesize complex cybersecurity information into clear, actionable, and highly digestible weekly "Pulses" for a broad audience. This audience includes both cybersecurity professionals seeking concise updates and general users who need to understand critical threats and protective measures to make informed decisions in their personal and professional lives.

        You must achieve the following:
        1.  **Comprehensive Understanding:** Analyze the provided new articles thoroughly, drawing out the most significant developments, evolving technologies, and strategic insights relevant to the specific category: **{category_name}**.
        2.  **Historical Context (if provided):** If "Relevant Past Pulses" are supplied, use them to:
            * Establish a historical understanding of the topic's trajectory.
            * Identify how current events represent continuations, accelerations, or new deviations from past trends.
            * Highlight the outcomes of previously developing stories or security measures.
            * Avoid repeating information extensively covered in very recent past pulses, focusing on *new* developments.
        3.  **Actionable Intelligence:** Emphasize practical implications. What immediate risks should users be aware of? What preventive steps, good habits, or protective measures can they implement based on this information? How does this information impact their decision-making?
        4.  **Simplicity and Digestibility:** Explain complex cybersecurity concepts, technologies, and strategies using **simple, everyday language that is easy to understand for anyone over the age of 10**, regardless of their technical background or native English proficiency. Avoid jargon wherever possible, or explain it clearly if unavoidable. The goal is deep retention and understanding.
        5.  **Category Focus:** **CRITICALLY, ensure that the entire pulse content (Title, Blurb, and Content) remains laser-focused on the specific category: {category_name}.** Do NOT drift into broad cybersecurity goals or general threats. Every piece of information must directly pertain to this particular topic, its sub-trends, and actionable advice within its scope.
        6.  **News Source Integrity:** Remember you are a news source. The information should be factual, derived directly from the provided articles and past pulses. Maintain an informative, authoritative, and helpful tone.

        **STRICTLY adhere to the following output format. Do NOT include any additional text, pleasantries, or explanations outside this format.**
        **IMPORTANT: Do NOT use any bolding (asterisks), italics, or any other markdown/special formatting in the output, EXCEPT for the colons after TITLE, BLURB, and CONTENT.**
        **Ensure the generated content is derived directly from the provided articles and, if provided, considers the context of past pulses.**
        ...
        --- NEW ARTICLES FOR {category_name.upper()} START ---
        {full_combined_text}
        --- NEW ARTICLES FOR {category_name.upper()} END ---
        {past_pulses_context}

        TITLE: [A concise, impactful title (max 10 words) summarizing the most critical weekly update for {category_name}.]
        BLURB: [A captivating summary (min 20 words, max 120 words) detailing the core points and immediate takeaways from this week's developments in {category_name}. Focus on what users need to know now.]
        CONTENT: [A detailed, accessible explanation (2-3 paragraphs, min 250 words, max 350 words) expanding on the key aspects, trends, and actionable insights for {category_name} this week. Clearly explain any complex concepts. Use double newlines to separate paragraphs.]
        """
        
        try:
            print(f'  Sending combined content for "{category_name}" to LLM...')
            response = model.generate_content(prompt)
            generated_text = response.text.strip()
            
            match = re.search(r"TITLE:\s*(.*?)\s*BLURB:\s*(.*?)\s*CONTENT:\s*(.*)", generated_text, re.DOTALL | re.IGNORECASE)
            if not match:
                print(f"  ERROR: Failed to parse LLM output for {category_name}.")
                continue

            title, blurb, content = match.groups()

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

    print(f'\nFinished weekly pulse generation. Total pulses generated: {total_pulses_generated}.')


if __name__ == "__main__":
    generate_pulses()