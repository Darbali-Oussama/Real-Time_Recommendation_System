from sqlalchemy.orm import Session
from repositories import get_item_embedding_by_title, get_similar_titles


def get_recommendations(db: Session, title: str, limit: int = 5):
    # Get the embedding for the input title
    embedding = get_item_embedding_by_title(db, title)
    #embedding = np.array(embedding).flatten().tolist()
    if not embedding:
        return []
    
    # Find similar titles based on the embedding
    similar_titles = get_similar_titles(db, embedding, limit)
    return [title for title in similar_titles[1:]]