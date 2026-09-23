import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Mock Knowledge Base (Textbook excerpts)
KNOWLEDGE_BASE = [
    "Introduction to Programming covers the basics of writing code. Variables, loops (for, while), and conditionals (if/else) are foundational concepts. It emphasizes algorithmic thinking over syntax.",
    "Data Structures explores how data is organized in memory. Key structures include arrays, linked lists, stacks, queues, and hash tables. Understanding Big O notation is critical here.",
    "Algorithms build upon data structures to solve complex problems efficiently. Topics include sorting (merge sort, quick sort), searching (binary search), dynamic programming, and graph traversals (BFS, DFS).",
    "Operating Systems focuses on resource management. Key areas include process scheduling, concurrency and multithreading, memory management (paging, segmentation), and file systems.",
    "Computer Networks teaches how data travels across the globe. The OSI model, TCP/IP stack, routing protocols, and socket programming are core elements.",
    "Databases handle structured data persistence. Relational databases (SQL), normalization, ACID properties, transaction management, and indexing are the primary focus.",
    "Machine Learning introduces predictive modeling. Linear regression, classification, clustering, support vector machines, and the mathematics of gradient descent are covered.",
    "Deep Learning extends machine learning using artificial neural networks. Convolutional Neural Networks (CNNs) for vision, Recurrent Neural Networks (RNNs) for sequences, and modern transformers."
]

def retrieve_context(topics):
    """
    Given a list of scheduled topics (dict objects), extract their names and find the most relevant 
    pieces of information from the knowledge base using TF-IDF and cosine similarity.
    """
    if not topics:
        return ""
        
    # Build query from remaining topic names
    query_text = " ".join([t["name"] for t in topics])
    
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit on knowledge base + query to ensure identical feature space
    tfidf_matrix = vectorizer.fit_transform(KNOWLEDGE_BASE + [query_text])
    
    kb_vectors = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]
    
    similarities = cosine_similarity(query_vector, kb_vectors)[0]
    
    # Get top 3 most relevant knowledge snippets
    top_indices = similarities.argsort()[-3:][::-1]
    
    retrieved_docs = []
    for idx in top_indices:
        if similarities[idx] > 0.05: # Only include if there's some relevance
            retrieved_docs.append(KNOWLEDGE_BASE[idx])
            
    return "\n".join(retrieved_docs)

def retrieve_context_for_topic(topic_name):
    """
    Find the most relevant piece of information for a single topic using TF-IDF.
    """
    if not topic_name:
        return "Review core concepts and practice thoroughly."
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(KNOWLEDGE_BASE + [topic_name])
    
    kb_vectors = tfidf_matrix[:-1]
    query_vector = tfidf_matrix[-1]
    
    similarities = cosine_similarity(query_vector, kb_vectors)[0]
    best_idx = similarities.argmax()
    
    if similarities[best_idx] > 0.01:
        return KNOWLEDGE_BASE[best_idx]
        
    return "Review foundational theory and apply concepts to practical scenarios."
