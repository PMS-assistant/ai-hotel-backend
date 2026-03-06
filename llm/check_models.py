"""
Utility script to check which Claude models are available.
Run: python -m llm.check_models
"""
from anthropic import Anthropic
from llm.config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

models = client.models.list()

print("Available models:")
for model in models.data:
    print("-", model.id)