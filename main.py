from fastapi import FastAPI
from pydantic import BaseModel
from llm.anthropic_service import ask_claude

# Create FastAPI app
app = FastAPI()

# Request model
class ChatRequest(BaseModel):
    message: str

# Root endpoint
@app.get("/")
def root():
    return {"status": "AI Hotel Backend Running"}

# Chat endpoint
@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = ask_claude(request.message)

        return {
            "success": True,
            "response": response
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }