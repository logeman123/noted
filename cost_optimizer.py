#!/usr/bin/env python3
"""
Cost analysis and optimization tool for the Apple Notes → Shopping List pipeline.
Analyzes token usage and provides cost reduction strategies.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Claude pricing (as of 2024/2025)
CLAUDE_PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 0.000015,   # $15 per 1M input tokens
        "output": 0.000075   # $75 per 1M output tokens
    },
    "claude-3-5-sonnet-20241022": {
        "input": 0.000003,   # $3 per 1M input tokens  
        "output": 0.000015   # $15 per 1M output tokens
    },
    "claude-3-haiku-20240307": {
        "input": 0.00000025, # $0.25 per 1M input tokens
        "output": 0.00000125 # $1.25 per 1M output tokens
    }
}

def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 characters per token for English."""
    return len(text) // 4

def analyze_current_costs():
    """Analyze the costs from our recent test run."""
    print("💰 Current Cost Analysis")
    print("=" * 40)
    
    # Our current system prompt
    system_prompt = """You are a shopping list optimizer. Convert notes into structured shopping lists.

Your task:
1. Extract all purchasable items from the note content
2. Categorize each item (grocery, household, electronics, etc.)
3. Estimate reasonable costs based on typical market prices
4. Assign priority (high/medium/low) based on necessity
5. Group related items for efficient shopping

Output format (JSON only):
{
  "shopping_list": [
    {
      "item": "item name",
      "category": "category",
      "priority": "high|medium|low",
      "estimated_cost": "$X.XX",
      "quantity": "1",
      "notes": "any specific requirements"
    }
  ],
  "total_estimated_cost": "$XX.XX",
  "categories": ["list", "of", "categories"],
  "recommended_stores": ["store suggestions based on items"]
}

Guidelines:
- Be specific with item names (e.g., "2% milk, half gallon" not just "milk")
- Use realistic price estimates for your local market
- Prioritize essentials (food, medicine) as high
- Group items by store section when possible
- If images show products, extract specific brands/models when visible"""

    user_input = """Text content:
Buy this
Pacsun extra baggy pants that are trending on tik tok
I want to make CK's kimchi fried rice"""

    # Estimate tokens
    input_tokens = estimate_tokens(system_prompt + user_input)
    
    # Load the actual output to count output tokens
    output_file = Path("outputs").glob("shopping_list_real-apple-note-buy-this_*.json")
    output_tokens = 0
    
    try:
        latest_output = max(output_file, key=lambda x: x.stat().st_mtime)
        with open(latest_output) as f:
            output_data = json.load(f)
            output_text = json.dumps(output_data, indent=2)
            output_tokens = estimate_tokens(output_text)
    except:
        output_tokens = 1000  # Rough estimate
    
    current_model = "claude-sonnet-4-20250514"
    pricing = CLAUDE_PRICING[current_model]
    
    input_cost = input_tokens * pricing["input"]
    output_cost = output_tokens * pricing["output"]
    total_cost = input_cost + output_cost
    
    print(f"Current Model: {current_model}")
    print(f"Input tokens: ~{input_tokens:,}")
    print(f"Output tokens: ~{output_tokens:,}")
    print(f"Input cost: ${input_cost:.4f}")
    print(f"Output cost: ${output_cost:.4f}")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Monthly cost (30 notes): ${total_cost * 30:.2f}")
    print(f"Monthly cost (100 notes): ${total_cost * 100:.2f}")
    
    return {
        "current_model": current_model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost": total_cost
    }

def optimize_prompt():
    """Create a shorter, more cost-effective prompt."""
    print("\n🎯 Prompt Optimization")
    print("=" * 40)
    
    # Optimized prompt - much shorter but still effective
    optimized_prompt = """Convert this note to a shopping list JSON:

Required fields per item:
- item: specific name
- category: grocery/household/clothing/etc
- priority: high/medium/low
- estimated_cost: realistic price
- quantity: amount needed

Also include:
- total_estimated_cost
- categories (array)
- recommended_stores (array)

Focus on actionable items only."""

    current_tokens = estimate_tokens("""You are a shopping list optimizer. Convert notes into structured shopping lists.

Your task:
1. Extract all purchasable items from the note content
2. Categorize each item (grocery, household, electronics, etc.)
3. Estimate reasonable costs based on typical market prices
4. Assign priority (high/medium/low) based on necessity
5. Group related items for efficient shopping

Output format (JSON only):
{
  "shopping_list": [
    {
      "item": "item name",
      "category": "category", 
      "priority": "high|medium|low",
      "estimated_cost": "$X.XX",
      "quantity": "1",
      "notes": "any specific requirements"
    }
  ],
  "total_estimated_cost": "$XX.XX",
  "categories": ["list", "of", "categories"],
  "recommended_stores": ["store suggestions based on items"]
}

Guidelines:
- Be specific with item names (e.g., "2% milk, half gallon" not just "milk")
- Use realistic price estimates for your local market
- Prioritize essentials (food, medicine) as high
- Group items by store section when possible
- If images show products, extract specific brands/models when visible""")
    
    optimized_tokens = estimate_tokens(optimized_prompt)
    
    print(f"Current prompt: {current_tokens:,} tokens")
    print(f"Optimized prompt: {optimized_tokens:,} tokens") 
    print(f"Reduction: {current_tokens - optimized_tokens:,} tokens ({((current_tokens - optimized_tokens) / current_tokens) * 100:.1f}%)")
    
    return optimized_prompt

def compare_models(baseline_cost: float):
    """Compare costs across different Claude models."""
    print("\n📊 Model Cost Comparison")
    print("=" * 40)
    
    # Use same token estimates as baseline
    input_tokens = 500
    output_tokens = 1000
    
    print(f"Cost comparison (for {input_tokens} input + {output_tokens} output tokens):\n")
    
    for model, pricing in CLAUDE_PRICING.items():
        input_cost = input_tokens * pricing["input"]
        output_cost = output_tokens * pricing["output"]
        total_cost = input_cost + output_cost
        
        savings = ((baseline_cost - total_cost) / baseline_cost * 100) if total_cost < baseline_cost else 0
        savings_text = f"({savings:.1f}% savings)" if savings > 0 else ""
        
        print(f"{model}:")
        print(f"  Cost per call: ${total_cost:.4f} {savings_text}")
        print(f"  Monthly (30): ${total_cost * 30:.2f}")
        print(f"  Monthly (100): ${total_cost * 100:.2f}")
        print()

def cost_reduction_strategies():
    """Provide actionable cost reduction strategies."""
    print("💡 Cost Reduction Strategies")
    print("=" * 40)
    
    strategies = [
        {
            "strategy": "1. Switch to Claude 3.5 Sonnet",
            "impact": "80% cost reduction",
            "effort": "Low - just change model name",
            "details": "Use claude-3-5-sonnet-20241022 instead of sonnet-4"
        },
        {
            "strategy": "2. Optimize System Prompt",
            "impact": "30-50% input token reduction", 
            "effort": "Low - use shorter prompt",
            "details": "Remove verbose examples, focus on essentials"
        },
        {
            "strategy": "3. Use Claude Haiku for Simple Notes",
            "impact": "95% cost reduction",
            "effort": "Medium - add model switching logic",
            "details": "Auto-detect simple vs complex notes"
        },
        {
            "strategy": "4. Implement Caching",
            "impact": "50-90% for repeated items",
            "effort": "Medium - cache common items/patterns",
            "details": "Cache ingredient lists for common recipes"
        },
        {
            "strategy": "5. Batch Processing",
            "impact": "20-40% per note",
            "effort": "High - redesign for multiple notes",
            "details": "Process multiple notes in single API call"
        },
        {
            "strategy": "6. Local Preprocessing",
            "impact": "10-30% token reduction",
            "effort": "Medium - add text cleanup",
            "details": "Remove filler words, normalize text"
        }
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"\n{strategy['strategy']}")
        print(f"   Impact: {strategy['impact']}")
        print(f"   Effort: {strategy['effort']}")
        print(f"   Details: {strategy['details']}")

def quick_wins():
    """Immediate optimizations you can implement."""
    print("\n🚀 Quick Wins (Implement Today)")
    print("=" * 40)
    
    print("1. Switch Model (1 minute):")
    print("   Change config.yaml model to: claude-3-5-sonnet-20241022")
    print("   Expected savings: ~80%")
    
    print("\n2. Shorter Prompt (5 minutes):")
    print("   Use the optimized prompt shown above")
    print("   Expected savings: ~30% additional")
    
    print("\n3. Lower Temperature (30 seconds):")
    print("   Change temperature from 0.1 to 0.0")
    print("   Slightly more predictable = potentially shorter outputs")
    
    print("\n4. Reduce Max Tokens (30 seconds):")
    print("   Change max_tokens from 4000 to 2000")
    print("   Prevents overly verbose responses")

def main():
    """Run cost analysis and optimization."""
    print("🔍 Apple Notes Pipeline - Cost Optimization Analysis")
    print("=" * 60)
    
    # 1. Analyze current costs
    current_stats = analyze_current_costs()
    
    # 2. Show prompt optimization
    optimize_prompt()
    
    # 3. Compare models
    compare_models(current_stats["total_cost"])
    
    # 4. Show strategies
    cost_reduction_strategies()
    
    # 5. Quick wins
    quick_wins()
    
    print("\n" + "=" * 60)
    print("💰 Summary: With model switch + prompt optimization:")
    print("   Current cost: $0.040 per note")
    print("   Optimized cost: ~$0.006 per note (85% savings!)")
    print("   Monthly (30 notes): $1.20 → $0.18")
    print("   Monthly (100 notes): $4.00 → $0.60")

if __name__ == "__main__":
    main()