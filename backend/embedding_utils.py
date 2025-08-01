# backend/embedding_utils.py

import chromadb
from sentence_transformers import SentenceTransformer
import os

# --- This is the key change ---
# Get the absolute path of the directory where this script is located (the 'backend' folder)
backend_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path for the ChromaDB data folder *inside* the 'backend' folder
CHROMA_DB_PATH = os.path.join(backend_dir, 'chroma_db_data')
# --- End of change ---

# Initialize ChromaDB client (persistent)
print(f"Initializing ChromaDB at: {CHROMA_DB_PATH}")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Load a pre-trained Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding_model():
    """Returns the SentenceTransformer model."""
    return model

def get_chroma_client():
    """Returns the ChromaDB client."""
    return chroma_client

def generate_embedding(text: str):
    """Generates a vector embedding for the given text."""
    if not text or not isinstance(text, str):
        return None
    # The .encode() method returns a numpy array. We convert it to a list for compatibility.
    return model.encode(text).tolist()

def get_or_create_collection(collection_name: str):
    """Gets or creates a ChromaDB collection."""
    return chroma_client.get_or_create_collection(name=collection_name)

# Define collection names (constants for consistency)
ARTICLES_COLLECTION = "cybersecurity_articles"
PULSES_COLLECTION = "cybersecurity_pulses"