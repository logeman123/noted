#!/usr/bin/env python3
"""
Test which Claude models are available in your account.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Common model names to test
models_to_test = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620", 
    "claude-3-5-sonnet",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-3-haiku",
    "claude-sonnet-4-20250514"  # Current working model
]

print("🧪 Testing Claude Model Availability")
print("=" * 45)

for model in models_to_test:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "hi"}]
        )
        print(f"✅ {model} - WORKS")
    except Exception as e:
        if "not_found_error" in str(e):
            print(f"❌ {model} - NOT AVAILABLE")
        else:
            print(f"⚠️  {model} - ERROR: {str(e)[:50]}...")

print("\n💡 Recommendation: Use the cheapest working model from above")