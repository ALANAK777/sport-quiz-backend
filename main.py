import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from vector_store import init_vector_store, get_chroma_client
from agent import generate_sports_quiz

# Load environment variables from .env
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize the ChromaDB vector store and seed it if needed
    print("Starting FastAPI app...")
    try:
        init_vector_store()
        print("Vector store initialization complete.")
    except Exception as e:
        print(f"Warning: Failed to initialize vector store at startup: {e}")
    yield
    # Shutdown: Clean up resources if needed
    print("Shutting down FastAPI app...")

app = FastAPI(
    title="AI Sports Quiz Generation Agent API",
    description="Backend API for generating sports quizzes using RAG with ChromaDB and web search.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sport-quiz-frontend.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuizGenerationRequest(BaseModel):
    sport: str
    difficulty: str = "Medium"

@app.get("/")
def root():
    """Root endpoint confirming backend server status."""
    return {
        "message": "Sports Quiz AI Backend is running successfully!",
        "status": "online",
        "docs": "/docs"
    }

@app.get("/api/status")
def get_status():
    """Returns database record count and key status."""
    load_dotenv(override=True)
    try:
        client = get_chroma_client()
        collection = client.get_collection(name="sports_facts")
        count = collection.count()
    except Exception as e:
        count = 0
        print(f"Error checking vector store count: {e}")
        
    has_api_key = bool(os.getenv("GEMINI_API_KEY"))
    
    return {
        "status": "online",
        "chromadb_record_count": count,
        "has_backend_api_key": has_api_key
    }

@app.post("/api/generate")
async def generate_quiz(
    request: QuizGenerationRequest, 
    x_gemini_api_key: str = Header(None, alias="X-Gemini-API-Key")
):
    """
    Generates a sports quiz.
    Supports API key from 'X-Gemini-API-Key' request header or backend '.env' environment variable.
    """
    # 1. Retrieve the Gemini API key
    api_key = x_gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Gemini API key is missing. Please set GEMINI_API_KEY in the backend `.env` file or provide it in the API Key input."
        )

    # 2. Validate input parameters
    if not request.sport or not request.sport.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sport name cannot be empty."
        )

    valid_difficulties = ["Easy", "Medium", "Hard"]
    if request.difficulty not in valid_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported difficulty. Supported options are: {', '.join(valid_difficulties)}"
        )

    # 3. Invoke the Agent logic
    try:
        result = generate_sports_quiz(
            sport=request.sport,
            difficulty=request.difficulty,
            gemini_api_key=api_key
        )
        return result
    except Exception as e:
        print(f"Error during quiz generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
