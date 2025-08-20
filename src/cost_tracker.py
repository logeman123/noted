"""
Cost tracking and optimization utilities for the Claude API usage.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Sonnet 4 pricing (per 1M tokens)
SONNET_4_PRICING = {
    "input": 3.0,   # $3 per 1M input tokens
    "output": 15.0  # $15 per 1M output tokens
}

class CostTracker:
    def __init__(self, log_file: str = "cost_log.json"):
        self.log_file = Path(log_file)
        self.ensure_log_file()
    
    def ensure_log_file(self):
        """Create cost log file if it doesn't exist."""
        if not self.log_file.exists():
            self.save_log({
                "total_calls": 0,
                "total_cost": 0.0,
                "calls": []
            })
    
    def load_log(self) -> Dict[str, Any]:
        """Load cost tracking log."""
        try:
            with open(self.log_file) as f:
                return json.load(f)
        except:
            return {"total_calls": 0, "total_cost": 0.0, "calls": []}
    
    def save_log(self, data: Dict[str, Any]):
        """Save cost tracking log."""
        with open(self.log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens from text (rough: ~4 chars per token)."""
        return max(1, len(text) // 4)
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given token usage."""
        input_cost = (input_tokens / 1_000_000) * SONNET_4_PRICING["input"]
        output_cost = (output_tokens / 1_000_000) * SONNET_4_PRICING["output"]
        return input_cost + output_cost
    
    def log_api_call(self, 
                     input_text: str, 
                     output_text: str, 
                     note_id: str = "unknown",
                     metadata: Optional[Dict] = None):
        """Log an API call with cost calculation."""
        
        input_tokens = self.estimate_tokens(input_text)
        output_tokens = self.estimate_tokens(output_text)
        cost = self.calculate_cost(input_tokens, output_tokens)
        
        call_data = {
            "timestamp": datetime.now().isoformat(),
            "note_id": note_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost": round(cost, 6),
            "metadata": metadata or {}
        }
        
        # Load existing log
        log_data = self.load_log()
        
        # Update totals
        log_data["total_calls"] += 1
        log_data["total_cost"] += cost
        log_data["calls"].append(call_data)
        
        # Keep only last 100 calls to prevent file bloat
        if len(log_data["calls"]) > 100:
            log_data["calls"] = log_data["calls"][-100:]
        
        # Save updated log
        self.save_log(log_data)
        
        return call_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cost statistics."""
        log_data = self.load_log()
        
        if not log_data["calls"]:
            return {
                "total_calls": 0,
                "total_cost": 0.0,
                "average_cost": 0.0,
                "recent_calls": []
            }
        
        recent_calls = log_data["calls"][-10:]  # Last 10 calls
        avg_cost = log_data["total_cost"] / log_data["total_calls"]
        
        return {
            "total_calls": log_data["total_calls"],
            "total_cost": round(log_data["total_cost"], 4),
            "average_cost": round(avg_cost, 4),
            "recent_calls": recent_calls,
            "daily_estimate": round(avg_cost * 30, 2),  # If 30 calls per day
            "monthly_estimate": round(avg_cost * 900, 2)  # If 30 calls per day * 30 days
        }
    
    def print_stats(self):
        """Print formatted cost statistics."""
        stats = self.get_stats()
        
        print("💰 Cost Tracking Summary")
        print("=" * 30)
        print(f"Total API calls: {stats['total_calls']}")
        print(f"Total cost: ${stats['total_cost']:.4f}")
        print(f"Average cost per call: ${stats['average_cost']:.4f}")
        print(f"Est. daily cost (30 calls): ${stats['daily_estimate']:.2f}")
        print(f"Est. monthly cost: ${stats['monthly_estimate']:.2f}")
        
        if stats['recent_calls']:
            print(f"\nRecent calls:")
            for call in stats['recent_calls'][-5:]:
                print(f"  {call['timestamp'][:19]} | ${call['cost']:.4f} | {call['input_tokens']}→{call['output_tokens']} tokens")


def create_cost_optimized_configs():
    """Create different configuration profiles for cost optimization."""
    configs = {
        "minimal": {
            "max_tokens": 1000,
            "temperature": 0.0,
            "description": "Fastest, cheapest responses"
        },
        "balanced": {
            "max_tokens": 2000, 
            "temperature": 0.0,
            "description": "Good balance of cost and quality"
        },
        "detailed": {
            "max_tokens": 4000,
            "temperature": 0.1,
            "description": "More detailed responses, higher cost"
        }
    }
    
    return configs


class ItemCache:
    """Cache common shopping items to reduce API calls."""
    
    def __init__(self, cache_file: str = "item_cache.json"):
        self.cache_file = Path(cache_file)
        self.ensure_cache_file()
    
    def ensure_cache_file(self):
        """Create cache file if it doesn't exist."""
        if not self.cache_file.exists():
            # Pre-populate with common items
            common_items = {
                "milk": {
                    "category": "dairy",
                    "priority": "high", 
                    "estimated_cost": "$4.99",
                    "quantity": "1 gallon"
                },
                "bread": {
                    "category": "bakery",
                    "priority": "high",
                    "estimated_cost": "$3.49", 
                    "quantity": "1 loaf"
                },
                "eggs": {
                    "category": "dairy",
                    "priority": "high",
                    "estimated_cost": "$3.99",
                    "quantity": "1 dozen"
                }
            }
            self.save_cache(common_items)
    
    def load_cache(self) -> Dict[str, Any]:
        """Load item cache."""
        try:
            with open(self.cache_file) as f:
                return json.load(f)
        except:
            return {}
    
    def save_cache(self, cache_data: Dict[str, Any]):
        """Save item cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def get_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get cached item data."""
        cache = self.load_cache()
        # Simple fuzzy matching
        item_lower = item_name.lower()
        for cached_item, data in cache.items():
            if cached_item.lower() in item_lower or item_lower in cached_item.lower():
                return data
        return None
    
    def add_item(self, item_name: str, item_data: Dict[str, Any]):
        """Add item to cache."""
        cache = self.load_cache()
        cache[item_name.lower()] = item_data
        self.save_cache(cache)
    
    def extract_and_cache_items(self, shopping_list: Dict[str, Any]):
        """Extract items from shopping list and add to cache."""
        if "shopping_list" not in shopping_list:
            return
        
        cache = self.load_cache()
        updated = False
        
        for item in shopping_list["shopping_list"]:
            item_name = item.get("item", "").lower()
            if item_name and item_name not in cache:
                cache[item_name] = {
                    "category": item.get("category"),
                    "priority": item.get("priority"),
                    "estimated_cost": item.get("estimated_cost"),
                    "quantity": item.get("quantity")
                }
                updated = True
        
        if updated:
            self.save_cache(cache)


if __name__ == "__main__":
    # Demo the cost tracker
    tracker = CostTracker()
    tracker.print_stats()
    
    print("\n" + "="*50)
    
    # Demo the item cache
    cache = ItemCache()
    cached_milk = cache.get_item("organic milk")
    if cached_milk:
        print("Found cached item:")
        print(json.dumps(cached_milk, indent=2))
    else:
        print("No cached item found")