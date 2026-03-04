from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from llm.anthropic_service import ask_claude

# Create FastAPI app
app = FastAPI(
    title="StayIntel - AI Hotel Intelligence Platform",
    description="Operational Intelligence System for Independent Hotels",
    version="0.1.0"
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