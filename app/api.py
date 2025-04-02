# app/api.py
import sys
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Add the project root to the path so we can import the src module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import quran_rag_query, initialize_data_and_models

# Initialize the FastAPI app
app = FastAPI(
    title="Quran Knowledge Explorer API",
    description="API for querying information about the Quran using RAG technology",
    version="1.0.0"
)

# Initialize the RAG system on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize models and data
        initialize_data_and_models()
    except Exception as e:
        print(f"Error initializing RAG system: {str(e)}")
        # We'll continue anyway and try to initialize later if needed

# Request model
class QuestionRequest(BaseModel):
    question: str
    surah_filter: Optional[int] = None
    verse_filter: Optional[int] = None

# Response model
class AnswerResponse(BaseModel):
    answer: str
    filters_applied: Dict[str, Any]

@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Get an answer to a question about the Quran
    """
    try:
        # Process the query
        answer = quran_rag_query(
            request.question, 
            request.surah_filter, 
            request.verse_filter
        )
        
        # Prepare response
        filters = {}
        if request.surah_filter:
            filters["surah"] = request.surah_filter
        if request.verse_filter:
            filters["verse"] = request.verse_filter
            
        return AnswerResponse(
            answer=answer,
            filters_applied=filters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/api/ask")
async def ask_question_get(
    question: str = Query(..., description="Your question about the Quran"),
    surah: Optional[int] = Query(None, description="Optional surah number filter"),
    verse: Optional[int] = Query(None, description="Optional verse number filter")
):
    """
    Get an answer to a question about the Quran (GET endpoint)
    """
    try:
        # Process the query
        answer = quran_rag_query(question, surah, verse)
        
        # Prepare response
        filters = {}
        if surah:
            filters["surah"] = surah
        if verse:
            filters["verse"] = verse
            
        return AnswerResponse(
            answer=answer,
            filters_applied=filters
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Welcome to the Quran Knowledge Explorer API"}

# Run the API with uvicorn when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
