# backend/setup_categories.py

import os
import json
from dotenv import load_dotenv
from supabase import create_client, Client
# Assuming your embedding utility is in the same folder or accessible
from embedding_utils import generate_embedding 

# --- New: Initialize Supabase Client ---
# Load environment variables from the .env file
load_dotenv() 

# Get the Supabase URL and Key from the environment
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

# Check if the credentials are set
if not supabase_url or not supabase_key:
    raise ValueError("Supabase URL and Key must be set in the .env file.")

# Create the Supabase client
supabase: Client = create_client(supabase_url, supabase_key)
# --- End of New Section ---


PREDEFINED_CATEGORIES = [
    "Ransomware",
    "Phishing & Social Engineering",
    "Malware (General)",
    "Denial-of-Service (DoS/DDoS)",
    "Data Breaches & Leaks",
    "Supply Chain Attacks",
    "Insider Threats",
    "Cloud Security Incidents",
    "Web Application Attacks",
    "Software & Hardware Vulnerabilities (CVEs)",
    "Zero-Day Exploits",
    "Nation-State Threats (APTs)",
    "Cybercrime Groups",
    "Hacktivism",
    "Threat Intelligence (General)",
    "AI in Cybersecurity",
    "Authentication & Access Control",
    "Network Security",
    "Endpoint Security",
    "Data Security & Privacy",
    "Incident Response & Forensics",
    "Security Best Practices & Awareness",
    "Cyber Policy & Regulations",
    "Cyber Warfare & Geopolitics",
]

def setup_categories():
    """Sets up predefined cybersecurity categories and generates their embeddings."""
    print('Setting up predefined categories and generating embeddings...')

    for category_name in PREDEFINED_CATEGORIES:
        print(f'  Processing category: {category_name}')
        
        embedding = generate_embedding(category_name)
        
        if embedding:
            # This is the new way to insert/update data
            data_to_insert = {
                "name": category_name, 
                "embedding": json.dumps(embedding) # Store as a JSON string
            }
            
            try:
                # 'upsert' will INSERT a new row, or UPDATE it if a row with the 
                # same 'name' already exists. This is our new "get_or_create".
                response = supabase.table('categories').upsert(
                    data_to_insert, 
                    on_conflict='name' # Check for conflicts based on the name column
                ).execute()
                print(f'  Successfully upserted: {category_name}')
            except Exception as e:
                print(f'  Error upserting {category_name}: {e}')
        else:
            print(f'  Skipped {category_name} (embedding failed)')

    print('Finished setting up categories.')


if __name__ == "__main__":
    # Make sure your embedding utility file (e.g., embedding_utils.py)
    # is in this same 'backend' folder.
    setup_categories()