
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from pipeline import run_research_pipeline

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Multi-Agent AI Research System",
    description="AI-powered research using Search, Reader, Writer and Critic agents.",
    version="1.0.0",
)

# Serve CSS and JavaScript
app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static",
)


class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)


@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Research API is running"}


@app.post("/api/research")
async def research(request: ResearchRequest):
    topic = request.topic.strip()

    if len(topic) < 3:
        raise HTTPException(
            status_code=422,
            detail="Please enter a topic with at least 3 characters.",
        )

    try:
        # Run synchronous LangChain calls without blocking the event loop.
        result = await run_in_threadpool(
            run_research_pipeline,
            topic,
        )

        return {
            "success": True,
            "topic": topic,
            "search_results": result.get("search_results", ""),
            "scraped_content": result.get("scraped_content", ""),
            "report": result.get("report", ""),
            "feedback": result.get("feedback", ""),
        }

    
    except Exception as exc:
        import traceback

        print("\n========== RESEARCH PIPELINE ERROR ==========")
        traceback.print_exc()
        print("=============================================\n")

        raise HTTPException(
            status_code=500,
            detail=f"{type(exc).__name__}: {str(exc)}",
        ) from exc

