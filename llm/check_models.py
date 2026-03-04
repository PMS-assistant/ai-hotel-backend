"""
Utility script to check which Claude models are available.
Run: python -m llm.check_models
"""
from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

models = client.models.list()

print("Available models:")
for model in models.data:
    print("-", model.id)