from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.models.schemas import UserInput, LifeDestinyResult
from app.services.analysis_service import generate_life_analysis, get_cached_analysis, get_db_analysis, save_analysis_async
from app.utils.hash import hash_user_input
from app.db.database import engine, Base, get_db
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="LifeKLine API", version="1.0.0")

# Create tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze", response_model=LifeDestinyResult)
async def analyze_destiny(input_data: UserInput, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    print(f"Analyzing for: {input_data.name}")
    
    # 1. Generate Hash
    input_hash = hash_user_input(input_data)
    
    # 2. Check Redis
    cached_result = await get_cached_analysis(input_hash)
    if cached_result:
        print("Returning cached result from Redis")
        return cached_result
    
    # 3. Check DB
    db_result = await get_db_analysis(db, input_hash)
    if db_result:
        print("Returning result from DB")
        # Add to Redis in background
        background_tasks.add_task(save_analysis_async, input_hash, db_result)
        return db_result
    
    # 4. Generate new analysis
    print("Generating new analysis")
    try:
        result = await generate_life_analysis(input_data)
        # 5. Save to DB and Redis in background
        background_tasks.add_task(save_analysis_async, input_hash, result)
        return result
    except HTTPException as he:
        raise he
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
