import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from llm.anthropic_service import ask_claude

# Create FastAPI app
app = FastAPI(
    title="StayIntel - AI Hotel Intelligence Platform",
    description="Operational Intelligence System for Independent Hotels",
    version="0.1.0"
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

        if result["success"]:
            return ChatResponse(
                success=True,
                decision=DecisionOutput(**result["decision"])
            )
        else:
            return ChatResponse(
                success=False,
                error=result.get("error"),
                raw_response=result.get("raw_response")
            )

    except Exception as e:
        return ChatResponse(
            success=False,
            error=str(e)
        )