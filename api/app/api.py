from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services import get_recommendations

router = APIRouter()

@router.get("/recommend", response_model=list[str])
def recommend_books(title: str, db: Session = Depends(get_db)):
    recommendations = get_recommendations(db, title)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book not found or no recommendations available")
    return recommendations
