import os
from contextlib import asynccontextmanager
from typing import Optional, Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.init_db import init_db, seed_demo_data
from llm.anthropic_service import ask_claude
from llm.tool_runner import run_tool
from routers import auth, dashboard, integrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """On startup: create tables and seed demo data."""
    init_db()
    seed_demo_data()
    yield
    # shutdown if needed


# Create FastAPI app
app = FastAPI(
    title="StayIntel - AI Hotel Intelligence Platform",
    description="Operational Intelligence System for Independent Hotels",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS so frontend (e.g. Vite/React on localhost:5173 or :3000) can call this API
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router)
app.include_router(integrations.router)
app.include_router(auth.router)


# ── Request / Response Models ──

class ChatRequest(BaseModel):
    message: str

class DecisionOutput(BaseModel):
    intent: str
    confidence: float
    requires_tool: bool
    tool_name: Optional[str] = None
    tool_arguments: Optional[dict] = None
    reply_to_user: str
    tool_result: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    success: bool
    decision: Optional[DecisionOutput] = None
    error: Optional[str] = None
    raw_response: Optional[str] = None


# ── Endpoints ──

@app.get("/")
def root():
    return {"status": "StayIntel Backend Running", "version": "0.1.0"}


@app.get("/health")
def health():
    """Health check for load balancers and frontend."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = ask_claude(request.message)

        if not result["success"]:
            return ChatResponse(
                success=False,
                error=result.get("error"),
                raw_response=result.get("raw_response"),
            )

        decision: Dict[str, Any] = dict(result["decision"])

        tool_result: Optional[Dict[str, Any]] = None
        if decision.get("requires_tool") and decision.get("tool_name"):
            tool_result = run_tool(
                decision["tool_name"],
                decision.get("tool_arguments") or {},
            )
            decision["tool_result"] = tool_result

        return ChatResponse(
            success=True,
            decision=DecisionOutput(**decision),
        )

    except Exception as e:
        return ChatResponse(
            success=False,
            error=str(e)
        )