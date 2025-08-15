# backend/categorize_articles.py
import os
import json
import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client
from embedding_utils import generate_embedding, get_or_create_collection, ARTICLES_COLLECTION

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
if not supabase_url or not supabase_key:
    raise ValueError("Supabase credentials must be set.")
supabase: Client = create_client(supabase_url, supabase_key)

def categorize_articles(similarity_threshold=0.4):
    print('Starting article categorization...')
    try:
        response = supabase.table('categories').select('id, name, embedding').execute()
        category_objects = response.data
    except Exception as e:
        raise Exception(f"Could not fetch categories: {e}")

    if not category_objects:
        raise Exception("No categories found. Please run setup_categories.py first.")

    category_embeddings_np = np.array([json.loads(cat['embedding']) for cat in category_objects if cat['embedding']])
    articles_collection = get_or_create_collection(ARTICLES_COLLECTION)

    try:
        response = supabase.table('articles').select('*').eq('is_categorized', 'false').execute()
        uncategorized_articles = response.data
    except Exception as e:
        raise Exception(f"Could not fetch uncategorized articles: {e}")

    if not uncategorized_articles:
        print('No new uncategorized articles found.')
        return

    for article in uncategorized_articles:
        print(f'  Processing article: "{article["title"]}" ({article["url"]})')
        article_embedding = generate_embedding(article['raw_content'])
        if not article_embedding:
            print(f'    Failed to generate embedding for article. Skipping.')
            continue
        try:
            articles_collection.add(
                documents=[article['raw_content']],
                metadatas=[{"url": article['url'], "title": article['title']}],
                ids=[str(article['id'])],
                embeddings=[article_embedding]
            )
        except Exception as e:
            print(f'    Warning: Failed to add article to ChromaDB: {e}')

        similarities = np.dot(category_embeddings_np, np.array(article_embedding))
        matched_category_ids = []
        for i, sim in enumerate(similarities):
            if sim >= similarity_threshold:
                matched_category_ids.append(category_objects[i]['id'])
                print(f'    Matched with category: {category_objects[i]["name"]} (Similarity: {sim:.4f})')
        try:
            if matched_category_ids:
                rows_to_insert = [{'article_id': article['id'], 'category_id': cat_id} for cat_id in matched_category_ids]
                supabase.table('article_categories').insert(rows_to_insert).execute()
                print(f'    Successfully linked article to {len(matched_category_ids)} categories.')
            supabase.table('articles').update({'is_categorized': True}).eq('id', article['id']).execute()
        except Exception as e:
            print(f"    Error updating article status or links: {e}")
    print('Finished article categorization.')

if __name__ == "__main__":
    categorize_articles()