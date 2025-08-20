#!/usr/bin/env python3
"""
Process a real Apple Note through the pipeline.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from notes_processor import NotesProcessor

def main():
    # Real note content from your Apple Notes
    real_note = {
        "id": "buy-this-note",
        "title": "Buy this",
        "text": """Buy this
Pacsun extra baggy pants that are trending on tik tok
I want to make CK's kimchi fried rice""",
        "images": [],
        "links": [],
        "created_date": datetime.now().isoformat(),
        "modified_date": datetime.now().isoformat(),
        "source": "real_apple_notes"
    }
    
    print("🍎 Processing Real Apple Note")
    print("=" * 40)
    print(f"Title: {real_note['title']}")
    print(f"Content: {real_note['text']}")
    print("\n🤖 Sending to Claude for analysis...")
    
    try:
        processor = NotesProcessor()
        
        # Override fetch method to use our real note
        def fetch_real_note(note_id):
            return real_note
        
        processor.fetch_note_from_mcp = fetch_real_note
        
        # Process the note
        result = processor.process_note("buy-this-note")
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("✅ Processing complete!\n")
        
        # Show markdown format
        print("📋 Shopping List (Markdown):")
        print("-" * 30)
        formatted = processor.format_output(result)
        print(formatted)
        
        # Save the result
        processor.save_output(result, "real-apple-note-buy-this")
        print(f"\n💾 Saved to outputs/")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()