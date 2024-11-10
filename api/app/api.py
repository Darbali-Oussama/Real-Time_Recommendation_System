from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import get_recommendations_postgres, get_recommendations_elastic

router = APIRouter()

@router.get("/recommend/postgres", response_model=list[str])
def recommend_books_postgres(title: str, db: Session = Depends(get_db)):
    recommendations = get_recommendations_postgres(db, title)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book not found or no recommendations available")
    return recommendations

@router.get("/recommend/elasticsearch", response_model=list[str])
def recommend_books_elasticsearch(title: str):
    recommendations = get_recommendations_elastic(title)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book not found or no recommendations available")
    return recommendations