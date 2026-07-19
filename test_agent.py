import os
import json
import sys
from dotenv import load_dotenv

# Load env variables from .env file
load_dotenv()

from vector_store import init_vector_store
from agent import generate_sports_quiz

def run_test():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        print("Please create a backend/.env file and set GEMINI_API_KEY=your_key_here.")
        sys.exit(1)
        
    print("=== Step 1: Initializing ChromaDB and seeding facts ===")
    init_vector_store()
    
    print("\n=== Step 2: Testing Quiz Generation for 'Badminton', Medium ===")
    try:
        result = generate_sports_quiz(
            sport="Badminton", 
            difficulty="Medium", 
            gemini_api_key=api_key
        )
        
        # Pretty print results
        quiz = result["quiz"]
        trace = result["trace"]
        
        print("\n--- AGENT TRACE DETAILS ---")
        print(f"Model used: {trace['model_used']}")
        print(f"Search Query run: '{trace['search_query']}'")
        print(f"Number of ChromaDB docs retrieved: {len(trace['chromadb_retrieved'])}")
        print(f"Number of Web Search results retrieved: {len(trace['web_search_results'])}")
        
        print("\n--- GENERATED QUIZ QUESTIONS ---")
        print(f"Sport: {quiz.get('sport')}")
        print(f"Difficulty: {quiz.get('difficulty')}")
        print("="*40)
        
        for idx, q in enumerate(quiz.get("questions", []), 1):
            print(f"\nQuestion {idx}: {q.get('question')}")
            for opt in q.get("options", []):
                print(f"  {opt}")
            print(f"Correct Answer: {q.get('correct_answer')}")
            print(f"Explanation: {q.get('explanation')}")
            print("-" * 30)
            
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
