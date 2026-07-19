# Sports Quiz AI - Backend API

A Python FastAPI server providing RAG-augmented sports quiz generation using **ChromaDB**, **DuckDuckGo Web Search**, and **Google Gemini LLM**.

---

## 📁 Backend Directory Structure

```
backend/
├── .env                # Local environment variables (GEMINI_API_KEY)
├── .env.example        # Environment template file
├── requirements.txt    # Python package dependencies
├── main.py             # FastAPI REST server endpoints & CORS configuration
├── agent.py            # AI Agent: ChromaDB retrieval + Web Search + Gemini LLM
├── vector_store.py     # ChromaDB initialization, persistence & query logic
├── test_agent.py       # Standalone CLI testing script
└── vercel.json         # Vercel serverless configuration
```

---

## 🛠️ Tech Stack & Dependencies

- **Framework**: FastAPI + Uvicorn
- **Vector Database**: ChromaDB (persistent local storage, `/tmp/chroma_db` on Vercel)
- **Web Search Engine**: DuckDuckGo Search (`duckduckgo-search`)
- **LLM SDK**: Google Gen AI SDK (`google-genai`) with Pydantic JSON Schema validation (`response_schema=Quiz`)
- **Config**: `python-dotenv`

---

## 🔑 Environment Setup

Create a `.env` file inside the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ⚡ Running Locally

1. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Run the FastAPI server:
   ```powershell
   python main.py
   ```
   - API will be live at: **`http://127.0.0.1:8000`**
   - Interactive Swagger docs available at: **`http://127.0.0.1:8000/docs`**

---

## 🌐 API Endpoints

### `GET /api/status`
Returns database record count and key configuration status.

### `POST /api/generate`
Generates a 4-5 question sports quiz.
- **Header**: `X-Gemini-API-Key` (Optional if set in `.env`)
- **Body**:
  ```json
  {
    "sport": "Cricket",
    "difficulty": "Medium"
  }
  ```
- **Response**:
  ```json
  {
    "quiz": {
      "sport": "Cricket",
      "difficulty": "Medium",
      "questions": [...]
    },
    "trace": {
      "chromadb_retrieved": [...],
      "search_query": "...",
      "web_search_results": [...],
      "model_used": "gemini-2.5-flash"
    }
  }
  ```

---

## 🚀 Vercel Deployment

Deploy the `backend` directory directly to Vercel:
1. Import `backend` folder on Vercel.
2. Add Environment Variable: `GEMINI_API_KEY`.
3. Vercel deploys `main.py` using `vercel.json`.
