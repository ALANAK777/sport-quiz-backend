import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
from duckduckgo_search import DDGS
from datetime import datetime
from vector_store import query_sports_facts

# Load environment variables
load_dotenv()

# Define structured Pydantic models for Gemini response
class QuizQuestion(BaseModel):
    question: str = Field(description="The multiple choice quiz question.")
    options: List[str] = Field(description="Four distinct answer options formatted as list of strings (e.g., ['A. Option A', 'B. Option B', 'C. Option C', 'D. Option D']).")
    correct_answer: str = Field(description="The correct option letter. Must be one of: 'A', 'B', 'C', 'D'.")
    explanation: str = Field(description="A short explanation of why the correct answer is correct, referencing facts.")

class Quiz(BaseModel):
    sport: str = Field(description="The sport name.")
    difficulty: str = Field(description="The difficulty level.")
    questions: List[QuizQuestion] = Field(description="List of 4 to 5 quiz questions.")

def web_search(query: str, max_results: int = 6) -> List[Dict[str, str]]:
    """Runs a DuckDuckGo search for the given query and returns titles, bodies, and links."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            if not results:
                return []
            
            search_items = []
            for r in results:
                search_items.append({
                    "title": r.get("title", "No Title"),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", "")
                })
            return search_items
    except Exception as e:
        print(f"Error during web search: {e}")
        return []

def generate_sports_quiz(sport: str, difficulty: str = "Medium", gemini_api_key: str = None) -> Dict[str, Any]:
    """
    Retrieves local ChromaDB facts and recent web search results,
    then generates a structured quiz using Gemini.
    """
    # Dynamically reload .env to ensure fresh keys are read
    load_dotenv(override=True)

    # Initialize API key: try parameter first, then environment
    api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in your environment or .env file.")

    # 1. Retrieve facts from ChromaDB
    print(f"Retrieving facts from ChromaDB for sport: {sport}...")
    local_facts = query_sports_facts(sport, difficulty, n_results=5)
    
    # 2. Perform Web Search with dynamic date range (current date & last 1 year)
    now = datetime.now()
    current_year = now.year
    prev_year = current_year - 1
    current_month_name = now.strftime("%B")
    current_date_str = now.strftime("%B %d, %Y")

    search_query = f"latest {sport} sports news winners tournament results {prev_year} {current_year} {current_month_name}"
    print(f"Searching the web for: '{search_query}'...")
    web_results = web_search(search_query, max_results=6)
    
    # Format contexts for LLM prompt
    chroma_context_str = ""
    if local_facts:
        chroma_context_str = "\n".join([
            f"- [{fact['difficulty']}] {fact['text']}" for fact in local_facts
        ])
    else:
        chroma_context_str = "No local database records found."
        
    web_context_str = ""
    if web_results:
        web_context_str = "\n".join([
            f"- Source: {res['title']} ({res['url']})\n  Info: {res['snippet']}"
            for res in web_results
        ])
    else:
        web_context_str = "No search results returned."

    # 3. Create Gemini Client
    client = genai.Client(api_key=api_key)
    
    # Formulate System and User Prompt with current date awareness
    system_instruction = (
        "You are an expert sports quiz generator. Your task is to generate engaging, "
        "accurate, and challenging sports-related multiple-choice quizzes for social media.\n"
        f"The current date is {current_date_str}. When generating questions about recent events or records, "
        f"focus on tournaments, champions, and milestones occurring from {prev_year} to {current_year}.\n"
        "You MUST ensure extreme factual accuracy. Ground your questions in the provided "
        "retrieved database context and recent web search results. If the context does not contain "
        "enough info, you may use your knowledge base, but do not hallucinate or conflict with verified facts.\n"
        f"Match the difficulty level: {difficulty}."
    )
    
    user_prompt = f"""
Generate a multiple-choice quiz for the sport "{sport}" at "{difficulty}" difficulty.

Here are local database records for "{sport}" retrieved from ChromaDB:
[CHROMA DB CONTEXT]
{chroma_context_str}

Here are recent web search results related to "{sport}":
[WEB SEARCH CONTEXT]
{web_context_str}

REQUIREMENTS:
1. Generate exactly 4 or 5 questions.
2. Each question must have four options (labelled A, B, C, D) inside the 'options' list. 
   Format them as: "A. Option content", "B. Option content", etc.
3. Mark the correct_answer as "A", "B", "C", or "D".
4. Provide a clear, short explanation for the correct answer, citing details.
5. Ensure questions match the '{difficulty}' difficulty.
   - Easy: Well-known general knowledge facts.
   - Medium: Specific milestones, matches, players, or stats.
   - Hard: Deep history, obscure records, or detailed statistical feats.
"""

    print("Generating quiz using Gemini model...")
    # Generate structured JSON
    # We use gemini-2.5-flash as the default model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Quiz,
            temperature=0.7,
        )
    )
    
    # Parse the response text as JSON (Gemini SDK handles Pydantic schema formatting internally)
    # The return object can be parsed into a dict
    import json
    try:
        quiz_data = json.loads(response.text)
    except Exception as e:
        print(f"Error parsing Gemini JSON response: {e}")
        # Fallback raw parsing/retry or bubble up
        raise RuntimeError("Failed to parse quiz response from model.") from e

    # Build agent logs / trace trace for debugging & UI display
    agent_trace = {
        "chromadb_retrieved": local_facts,
        "search_query": search_query,
        "web_search_results": web_results,
        "model_used": "gemini-2.5-flash"
    }

    return {
        "quiz": quiz_data,
        "trace": agent_trace
    }

if __name__ == "__main__":
    # Test execution
    import sys
    test_key = os.getenv("GEMINI_API_KEY")
    if not test_key:
        print("Please set GEMINI_API_KEY environment variable to test.")
        sys.exit(1)
        
    try:
        from vector_store import init_vector_store
        init_vector_store()
        res = generate_sports_quiz("Badminton", "Medium", test_key)
        print("Generated Quiz JSON:")
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Test failed: {e}")
