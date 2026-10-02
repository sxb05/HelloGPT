# HelloGPT

> **Work in progress**
>
> HelloGPT is an actively developed ChatGPT-style assistant built with a React + TypeScript frontend and a Python/FastAPI backend. The project is functional in several areas, but it is **not complete** and its APIs, UI, data model, and configuration may continue to change.

## Overview

HelloGPT is being developed as a practical AI assistant with:

- A dark, responsive chat interface inspired by modern AI products
- Conversation history backed by SQLite
- LangGraph-based agent orchestration
- Google Gemini model integration
- Long-term memory tools
- Web search tooling
- Retrieval-augmented generation for uploaded documents
- PDF, DOCX, TXT, and Markdown document ingestion
- A FastAPI API that serves the frontend in production

## Current status

### Currently available

- Create and select conversations
- Persist user and assistant messages
- Send chat messages through the FastAPI backend
- Choose between the configured Gemini model names from the frontend
- Upload supported documents for indexing
- Responsive sidebar with conversation history
- Production frontend build through Vite

### Still in progress

- Authentication and user accounts
- Production database and deployment configuration
- Streaming assistant responses
- Conversation deletion, renaming, and search behavior
- Complete document-management UI
- Automated backend and frontend test coverage
- Production-grade observability and error reporting
- Final security, privacy, and rate-limit review

## Technology stack

### Frontend

- React 18
- TypeScript
- Vite
- `lucide-react`
- CSS-based responsive styling and animations

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- LangChain
- LangGraph
- SQLAlchemy
- SQLite for local persistence
- Chroma for vector search
- Google Gemini for model and embedding access

## Project structure

```text
.
├── app.py                    # FastAPI application and API routes
├── agent.py                  # LangGraph agent construction and model selection
├── db.py                     # SQLAlchemy models and conversation persistence
├── rag.py                    # Document parsing, chunking, and vector indexing
├── tools.py                  # Agent tools such as memory and web search
├── requirements.txt          # Python dependencies
├── data/                     # Local SQLite and LangGraph checkpoint files
├── chroma_db/                # Local Chroma vector-store data
├── uploads/                  # Uploaded document files
└── frontend/
    ├── src/
    │   ├── App.tsx           # Main chat interface and API integration
    │   ├── main.tsx          # React entry point
    │   └── styles.css        # Application styling
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- npm
- A Google Gemini API key
- Optional: a Tavily API key if web search is enabled

## Local setup

The commands below are written for PowerShell on Windows.

### 1. Clone the project

```powershell
git clone <repository-url>
Set-Location .\RAGRAPH_bot
```

### 2. Create and activate a Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Do not commit `.env` or any API keys to source control.

### 5. Install frontend dependencies

```powershell
Set-Location .\frontend
npm install
Set-Location ..
```

### 6. Start the development servers

Start the backend in one terminal:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Start the Vite frontend in a second terminal:

```powershell
Set-Location .\frontend
npm run dev
```

Open the Vite URL shown in the terminal, normally:

```text
http://localhost:5173
```

The Vite development server proxies `/api` requests to the FastAPI server at `http://127.0.0.1:8000`.

## Production frontend build

Build the frontend:

```powershell
Set-Location .\frontend
npm run build
```

The generated files are placed in `frontend/dist`. When that directory exists, FastAPI serves the built frontend and its assets.

Run the backend:

```powershell
Set-Location ..
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Check backend availability |
| `GET` | `/api/conversations` | List saved conversations |
| `POST` | `/api/conversations` | Create a conversation |
| `GET` | `/api/conversations/{thread_id}/messages` | Load conversation history |
| `POST` | `/api/chat` | Send a message and receive an assistant response |
| `POST` | `/api/conversations/{thread_id}/files` | Upload and index a supported document |

Example chat request:

```json
{
  "thread_id": "conversation-id",
  "message": "Explain retrieval-augmented generation.",
  "model": "gemini-3.1-flash-lite"
}
```

## Development notes

- Local database files and vector-store data are created at runtime.
- The frontend currently uses a non-streaming chat request and displays a loading state while waiting for the response.
- Model names are validated by the agent layer; keep frontend model options aligned with `agent.py`.
- Uploaded documents are associated with a conversation thread for retrieval.
- The project currently favors local development and experimentation over deployment hardening.

## Validation

Run the frontend type check and production build:

```powershell
Set-Location .\frontend
npm run build
```

Before making a production deployment, add and run backend tests, frontend interaction tests, security checks, and a deployment-specific configuration review.

## Contributing

This project is still being shaped. When contributing:

1. Keep changes focused and document behavior changes.
2. Avoid committing secrets, local databases, uploads, or generated build artifacts.
3. Run the frontend build before opening a pull request.
4. Describe known limitations and follow-up work clearly.

## License

No project license has been defined yet. Until a license is added, treat the repository as proprietary and obtain permission before redistributing or reusing the code.
