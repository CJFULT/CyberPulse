# backend/analyzer.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_key_excerpts_by_similarity(full_content, title, num_excerpts=3):
    """
    Analyzes article content to find the paragraphs most similar to the title.

    This function uses a TF-IDF (Term Frequency-Inverse Document Frequency)
    vectorizer to understand word importance and cosine similarity to measure
    relevance between the title and each paragraph.

    Args:
        full_content (str): The complete text of the article.
        title (str): The title of the article.
        num_excerpts (int): The number of top paragraphs to extract.

    Returns:
        str: A string containing the most relevant paragraphs, separated by
             newlines, or the original content if it's too short to analyze.
    """
    # 1. Segment the article into paragraphs. We filter for paragraphs of a
    #    meaningful length to avoid analyzing stray lines or headings.
    paragraphs = [p.strip() for p in full_content.split('\n') if len(p.strip()) > 150]

    # Edge Case: If there aren't enough paragraphs to choose from,
    # it's safer to return the whole article than an incorrect summary.
    if len(paragraphs) < num_excerpts:
        print("  - Not enough content to perform analysis. Using full content.")
        return full_content

    # 2. Vectorize the content using TF-IDF. The title is included in the list
    #    so it can be compared against the paragraphs.
    documents = [title] + paragraphs
    
    try:
        tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    except ValueError:
        # This can happen if the content is just stop words or symbols.
        print("  - TF-IDF Vectorization failed. Using full content.")
        return full_content

    # The first vector (index 0) is the title. The rest are paragraphs.
    title_vector = tfidf_matrix[0:1]
    paragraph_vectors = tfidf_matrix[1:]

    # 3. Calculate the cosine similarity between the title and each paragraph.
    similarities = cosine_similarity(title_vector, paragraph_vectors).flatten()

    # 4. Select the top N paragraphs. We get the indices of the 'num_excerpts'
    #    highest scores.
    top_indices = similarities.argsort()[-num_excerpts:]
    
    # Sort the indices so the paragraphs are returned in their original order.
    top_indices.sort()

    # Join the selected paragraphs into a single string.
    top_excerpts = [paragraphs[i] for i in top_indices]
    
    print(f"  - Successfully extracted {len(top_excerpts)} key excerpts.")
    return "\n\n---\n\n".join(top_excerpts)