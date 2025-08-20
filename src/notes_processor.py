#!/usr/bin/env python3
"""
Main processor for converting Apple Notes to shopping lists.
Phase 1: Basic pipeline implementation.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
from dotenv import load_dotenv

from claude_interface import ClaudeProcessor


class NotesProcessor:
    def __init__(self, config_path: str = "config.yaml"):
        # Load environment variables from .env file
        load_dotenv()
        
        self.config = self._load_config(config_path)
        self._setup_logging()
        
        # Get API key from environment or config
        api_key = os.getenv("CLAUDE_API_KEY") or self.config["claude"]["api_key"]
        if not api_key or api_key == "your-claude-api-key-here":
            raise ValueError("Claude API key not found. Set CLAUDE_API_KEY in .env file or config.yaml")
        
        self.claude = ClaudeProcessor(
            api_key=api_key,
            model=self.config["claude"]["model"],
            max_tokens=self.config["claude"]["max_tokens"],
            temperature=self.config["claude"]["temperature"]
        )
        self.logger = logging.getLogger(__name__)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing config: {e}")
            sys.exit(1)

    def _setup_logging(self):
        """Configure logging based on config settings."""
        log_level = getattr(logging, self.config.get("debug", {}).get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def fetch_note_from_mcp(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch note content via Apple Notes MCP server.
        This is a placeholder - actual MCP integration needed.
        """
        # TODO: Implement actual MCP server communication
        # For now, return a mock note for testing
        
        self.logger.warning("Using mock note data - MCP integration needed")
        return {
            "id": note_id,
            "title": "Shopping List",
            "text": """Need to get:
- Organic milk (2%)
- Whole grain bread
- Free-range eggs (dozen)
- Bananas
- Greek yogurt
- Olive oil (extra virgin)
- Paper towels
- Dish soap
- Light bulbs (LED, 60W equivalent)""",
            "images": [],
            "links": [],
            "created_date": datetime.now().isoformat(),
            "modified_date": datetime.now().isoformat()
        }

    def process_note(self, note_id: str) -> Dict[str, Any]:
        """
        Main processing pipeline: Note → Claude → Shopping List
        """
        self.logger.info(f"Processing note: {note_id}")
        
        # Step 1: Fetch note content
        note_content = self.fetch_note_from_mcp(note_id)
        if not note_content:
            return {"error": f"Could not fetch note: {note_id}"}
        
        # Step 2: Process with Claude
        shopping_list = self.claude.process_note_to_shopping_list(note_content)
        
        if "error" in shopping_list:
            return shopping_list
        
        # Step 3: Add timing analysis (basic for Phase 1)
        if shopping_list.get("shopping_list"):
            timing_analysis = self.claude.analyze_item_timing(
                shopping_list["shopping_list"]
            )
            shopping_list["timing"] = timing_analysis
        
        # Step 4: Add metadata
        shopping_list["metadata"] = {
            "source_note_id": note_id,
            "processed_at": datetime.now().isoformat(),
            "version": "1.0",
            "phase": "1 - Basic Pipeline"
        }
        
        return shopping_list

    def save_output(self, shopping_list: Dict[str, Any], note_id: str):
        """Save the shopping list to output directory."""
        if not self.config["output"]["save_to_file"]:
            return
        
        # Create output directory
        output_dir = Path(self.config["output"]["output_directory"])
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shopping_list_{note_id}_{timestamp}.json"
        output_path = output_dir / filename
        
        # Save file
        with open(output_path, 'w') as file:
            json.dump(shopping_list, file, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Shopping list saved to: {output_path}")

    def format_output(self, shopping_list: Dict[str, Any]) -> str:
        """Format shopping list for display."""
        if "error" in shopping_list:
            return f"Error: {shopping_list['error']}"
        
        output_format = self.config["output"]["format"]
        
        if output_format == "json":
            return json.dumps(shopping_list, indent=2, ensure_ascii=False)
        
        elif output_format == "markdown":
            return self._format_markdown(shopping_list)
        
        elif output_format == "text":
            return self._format_text(shopping_list)
        
        else:
            return json.dumps(shopping_list, indent=2, ensure_ascii=False)

    def _format_markdown(self, shopping_list: Dict[str, Any]) -> str:
        """Format as markdown."""
        lines = ["# Shopping List\n"]
        
        # Group by category
        categories = {}
        for item in shopping_list.get("shopping_list", []):
            category = item.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        for category, items in categories.items():
            lines.append(f"## {category.title()}\n")
            for item in items:
                priority = item.get("priority", "medium")
                cost = item.get("estimated_cost", "")
                lines.append(f"- **{item['item']}** ({priority} priority) - {cost}")
            lines.append("")
        
        lines.append(f"**Total Estimated Cost:** {shopping_list.get('total_estimated_cost', 'N/A')}")
        
        return "\n".join(lines)

    def _format_text(self, shopping_list: Dict[str, Any]) -> str:
        """Format as plain text."""
        lines = ["SHOPPING LIST", "=" * 40, ""]
        
        for item in shopping_list.get("shopping_list", []):
            priority = item.get("priority", "medium")
            cost = item.get("estimated_cost", "")
            lines.append(f"[ ] {item['item']} ({priority}) - {cost}")
        
        lines.extend(["", f"Total: {shopping_list.get('total_estimated_cost', 'N/A')}"])
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Convert Apple Notes to shopping lists")
    parser.add_argument("--note-id", help="Apple Note ID to process")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--output-format", choices=["json", "markdown", "text"], 
                       help="Override output format")
    parser.add_argument("--cost-summary", action="store_true", help="Show cost tracking summary")
    
    args = parser.parse_args()
    
    # Override config for debug mode
    if args.debug:
        os.environ["LOG_LEVEL"] = "DEBUG"
    
    try:
        processor = NotesProcessor(args.config)
        
        # Handle cost summary command
        if args.cost_summary:
            processor.claude.cost_tracker.print_stats()
            return
        
        # Require note-id for processing
        if not args.note_id:
            print("Error: --note-id is required for processing notes")
            print("Use --cost-summary to view cost statistics")
            return
        
        # Override output format if specified
        if args.output_format:
            processor.config["output"]["format"] = args.output_format
        
        # Process the note
        shopping_list = processor.process_note(args.note_id)
        
        # Save output
        processor.save_output(shopping_list, args.note_id)
        
        # Display result
        formatted_output = processor.format_output(shopping_list)
        print(formatted_output)
        
        # Show cost info if debug mode
        if args.debug:
            print("\n" + "="*50)
            processor.claude.cost_tracker.print_stats()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()