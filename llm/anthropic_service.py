import os
import json
from dotenv import load_dotenv
from anthropic import Anthropic
from llm.system_prompts import DECISION_SYSTEM_PROMPT

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)


def ask_claude(user_message: str) -> dict:
    """
    Send a message to Claude and get a structured JSON decision back.
    Returns parsed dict on success, or error dict on failure.
    """
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=DECISION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    raw_text = response.content[0].text
    return parse_claude_response(raw_text)


def parse_claude_response(raw_text: str) -> dict:
    """
    Parse Claude's response into structured JSON.
    Handles markdown code blocks and plain JSON.
    """
    cleaned = raw_text.strip()

    # Remove markdown code fences if present
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        lines = [line for line in lines if not line.strip().startswith("```")]
        cleaned = "\n".join(lines).strip()

    try:
        parsed = json.loads(cleaned)
        return {
            "success": True,
            "decision": parsed
        }
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Claude did not return valid JSON",
            "raw_response": raw_text
        }
