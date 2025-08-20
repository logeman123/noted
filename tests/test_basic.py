"""
Basic tests for the Apple Notes to shopping list pipeline.
Phase 1: Test core functionality without external dependencies.
"""

import json
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from claude_interface import ClaudeProcessor


class TestClaudeInterface(unittest.TestCase):
    
    def setUp(self):
        # Mock the Anthropic client to avoid API calls in tests
        with patch('claude_interface.Anthropic'):
            self.processor = ClaudeProcessor(
                api_key="test-key",
                model="claude-3-sonnet-20240229"
            )

    def test_format_note_content_text_only(self):
        """Test formatting note content with text only."""
        note_content = {
            "text": "milk\nbread\neggs"
        }
        
        result = self.processor._format_note_content(note_content)
        self.assertIn("Text content:", result)
        self.assertIn("milk", result)

    def test_format_note_content_with_images(self):
        """Test formatting note content with images."""
        note_content = {
            "text": "shopping list",
            "images": ["image1.jpg", "image2.jpg"]
        }
        
        result = self.processor._format_note_content(note_content)
        self.assertIn("Contains 2 images", result)

    def test_format_note_content_with_links(self):
        """Test formatting note content with links."""
        note_content = {
            "text": "check this product",
            "links": ["https://example.com/product1", "https://example.com/product2"]
        }
        
        result = self.processor._format_note_content(note_content)
        self.assertIn("Links found:", result)
        self.assertIn("https://example.com/product1", result)

    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        response_text = '''Here's your shopping list:
        {
            "shopping_list": [
                {
                    "item": "milk",
                    "category": "dairy",
                    "priority": "high"
                }
            ],
            "total_estimated_cost": "$3.99"
        }
        Some additional text after.'''
        
        result = self.processor._parse_response(response_text)
        self.assertIn("shopping_list", result)
        self.assertEqual(result["shopping_list"][0]["item"], "milk")

    def test_parse_response_invalid_json(self):
        """Test handling invalid JSON response."""
        response_text = "This is not JSON content at all."
        
        result = self.processor._parse_response(response_text)
        self.assertIn("error", result)
        self.assertIn("raw_response", result)

    def test_analyze_item_timing_basic(self):
        """Test basic timing analysis."""
        items = [
            {"item": "milk", "priority": "high"},
            {"item": "snacks", "priority": "low"},
            {"item": "bread", "priority": "medium"}
        ]
        
        result = self.processor.analyze_item_timing(items)
        
        self.assertIn("timing_analysis", result)
        self.assertEqual(len(result["timing_analysis"]), 3)
        
        # Check that high priority items get "today" timing
        high_priority_item = next(
            item for item in result["timing_analysis"] 
            if item["item"] == "milk"
        )
        self.assertEqual(high_priority_item["suggested_timing"], "today")


class TestNotesProcessor(unittest.TestCase):
    
    @patch('notes_processor.yaml.safe_load')
    @patch('builtins.open')
    def test_load_config(self, mock_open, mock_yaml):
        """Test configuration loading."""
        mock_yaml.return_value = {
            "claude": {"api_key": "test", "model": "test-model"},
            "output": {"format": "json"}
        }
        
        from notes_processor import NotesProcessor
        
        # This will use the mocked config
        processor = NotesProcessor("test_config.yaml")
        self.assertEqual(processor.config["claude"]["api_key"], "test")

    def test_format_markdown_output(self):
        """Test markdown formatting."""
        from notes_processor import NotesProcessor
        
        with patch('notes_processor.yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {
                "claude": {"api_key": "test", "model": "test", "max_tokens": 1000, "temperature": 0.1},
                "output": {"format": "markdown"},
                "debug": {"log_level": "INFO"}
            }
            
            with patch('builtins.open'):
                processor = NotesProcessor("test_config.yaml")
            
            shopping_list = {
                "shopping_list": [
                    {"item": "milk", "category": "dairy", "priority": "high", "estimated_cost": "$3.99"},
                    {"item": "bread", "category": "bakery", "priority": "medium", "estimated_cost": "$2.50"}
                ],
                "total_estimated_cost": "$6.49"
            }
            
            result = processor._format_markdown(shopping_list)
            self.assertIn("# Shopping List", result)
            self.assertIn("## Dairy", result)
            self.assertIn("**milk**", result)

    def test_format_text_output(self):
        """Test plain text formatting."""
        from notes_processor import NotesProcessor
        
        with patch('notes_processor.yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {
                "claude": {"api_key": "test", "model": "test", "max_tokens": 1000, "temperature": 0.1},
                "output": {"format": "text"},
                "debug": {"log_level": "INFO"}
            }
            
            with patch('builtins.open'):
                processor = NotesProcessor("test_config.yaml")
            
            shopping_list = {
                "shopping_list": [
                    {"item": "milk", "priority": "high", "estimated_cost": "$3.99"}
                ],
                "total_estimated_cost": "$3.99"
            }
            
            result = processor._format_text(shopping_list)
            self.assertIn("SHOPPING LIST", result)
            self.assertIn("[ ] milk", result)
            self.assertIn("Total: $3.99", result)


if __name__ == "__main__":
    unittest.main()