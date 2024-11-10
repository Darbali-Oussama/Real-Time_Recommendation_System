from sqlalchemy.orm import Session
from repositories import get_item_embedding_by_title_postgres, get_similar_titles_postgres, get_embedding_from_elasticsearch, get_similar_titles_elasticsearch


def get_recommendations_postgres(db: Session, title: str, limit: int = 5):
    # Get the embedding for the input title
    embedding = get_item_embedding_by_title_postgres(db, title)
    #embedding = np.array(embedding).flatten().tolist()
    if not embedding:
        return []
    
    # Find similar titles based on the embedding
    similar_titles = get_similar_titles_postgres(db, embedding, limit)
    return [title for title in similar_titles[1:]]

def get_recommendations_elastic(title: str, limit: int = 5):
    # Get the embedding for the input title
    embedding = get_embedding_from_elasticsearch(title)
    if not embedding:
        return []
    
    # Find similar titles based on the embedding
    similar_titles = get_similar_titles_elasticsearch(embedding, limit)
    return [title for title in similar_titles[1:]]