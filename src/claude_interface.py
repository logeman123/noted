"""
Claude API interface for processing notes into shopping lists.
Minimal wrapper focused on the specific use case.
"""

import json
import logging
from typing import Dict, List, Any, Optional
import anthropic
from anthropic import Anthropic
from cost_tracker import CostTracker


class ClaudeProcessor:
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", 
                 max_tokens: int = 4000, temperature: float = 0.1):
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)
        self.cost_tracker = CostTracker()

    def process_note_to_shopping_list(self, note_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert note content into a structured shopping list.
        
        Args:
            note_content: Dictionary containing text, images, links from note
            
        Returns:
            Structured shopping list with items, categories, and metadata
        """
        system_prompt = """Convert this note to a shopping list JSON:

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

        user_prompt = self._format_note_content(note_content)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            # Extract JSON from response
            response_text = response.content[0].text
            
            # Log cost tracking
            full_input = system_prompt + "\n\n" + user_prompt
            self.cost_tracker.log_api_call(
                input_text=full_input,
                output_text=response_text,
                note_id=note_content.get("id", "unknown"),
                metadata={"model": self.model}
            )
            
            return self._parse_response(response_text)
            
        except Exception as e:
            self.logger.error(f"Claude API error: {e}")
            return {"error": f"Failed to process note: {str(e)}"}

    def _format_note_content(self, note_content: Dict[str, Any]) -> str:
        """Format note content for Claude prompt."""
        formatted_parts = []
        
        if note_content.get("text"):
            formatted_parts.append(f"Text content:\n{note_content['text']}")
        
        if note_content.get("images"):
            formatted_parts.append(f"Contains {len(note_content['images'])} images")
            # For now, just note presence of images
            # In Phase 3, we'll add actual image analysis
        
        if note_content.get("links"):
            formatted_parts.append("Links found:")
            for link in note_content["links"]:
                formatted_parts.append(f"- {link}")
        
        return "\n\n".join(formatted_parts)

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's response and extract JSON."""
        try:
            # Look for JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse Claude response: {e}")
            return {
                "error": "Failed to parse response",
                "raw_response": response_text
            }

    def analyze_item_timing(self, items: List[Dict[str, Any]], 
                          schedule_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze optimal timing for purchasing items.
        This is a placeholder for Phase 2 functionality.
        """
        # For now, return basic timing suggestions
        timing_suggestions = []
        
        for item in items:
            suggestion = {
                "item": item.get("item"),
                "suggested_timing": "this_week",  # Default
                "reason": "Standard timing"
            }
            
            # Basic priority-based timing
            if item.get("priority") == "high":
                suggestion["suggested_timing"] = "today"
                suggestion["reason"] = "High priority item"
            elif item.get("priority") == "low":
                suggestion["suggested_timing"] = "next_week"
                suggestion["reason"] = "Low priority, can wait"
                
            timing_suggestions.append(suggestion)
        
        return {
            "timing_analysis": timing_suggestions,
            "optimal_shopping_day": "Saturday",  # Default suggestion
            "note": "Basic timing analysis - Phase 2 will add price and calendar integration"
        }