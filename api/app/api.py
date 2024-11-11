from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from postgres.database import get_db
from services import get_recommendations_postgres, get_recommendations_elastic, recommend_kafka_spark
from models import UserRating, ItemEmbedding
from typing import List


router = APIRouter()

#@router.get("/recommend/postgres", response_model=list[ItemEmbedding])
@router.get("/recommend/postgres")
def recommend_books_postgres(item_id: int, db: Session = Depends(get_db)):
    recommendations = get_recommendations_postgres(db, item_id)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book not found or no recommendations available")
    return recommendations

@router.get("/recommend/elasticsearch", response_model=list[str])
def recommend_books_elasticsearch(title: str):
    recommendations = get_recommendations_elastic(title)
    if not recommendations:
        raise HTTPException(status_code=404, detail="Book not found or no recommendations available")
    return recommendations

@router.post("/recommend/spark")
#async def recommend(ratings: List[UserRating], background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
async def recommend(ratings, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    recommend_kafka_spark(ratings)    
    # Add a background task to fetch the recommendation response
    
    #background_tasks.add_task(get_recommendations, request_data["user_id"])
    return {"status": "Recommendation request sent successfully"}