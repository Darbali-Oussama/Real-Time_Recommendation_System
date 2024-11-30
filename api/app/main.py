from fastapi import FastAPI
from api import router as api_router
from postgres.database import engine
from models import Base
from topic_creator import create_topics


# Create kafka topics
create_topics()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Register the API router
app.include_router(api_router, prefix="/api/v1")

# Run the application 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
