#!/usr/bin/env python3
"""
Script to test the pipeline with real Apple Notes using MCP integration.
This demonstrates fetching actual notes and processing them.
"""

import json
import subprocess
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from notes_processor import NotesProcessor

def get_notes_via_applescript():
    """
    Alternative method to get Apple Notes using AppleScript.
    This bypasses MCP and directly queries Apple Notes.
    """
    applescript = '''
    tell application "Notes"
        set noteList to {}
        repeat with aNote in notes
            try
                set noteInfo to {name of aNote, id of aNote, plaintext of aNote}
                set end of noteList to noteInfo
            end try
        end repeat
        return noteList
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"AppleScript error: {e}")
        return None

def parse_applescript_notes(raw_output):
    """Parse the AppleScript output into note objects."""
    # This is a simplified parser - AppleScript output format can be complex
    # For a production system, you'd want more robust parsing
    
    print("Raw AppleScript output:")
    print(raw_output)
    print("\n" + "="*50 + "\n")
    
    # For now, let's create a mock note from the actual data
    # In a real implementation, you'd properly parse the AppleScript output
    
    if "shopping" in raw_output.lower() or "buy" in raw_output.lower() or "get" in raw_output.lower():
        # Found what looks like a shopping-related note
        return {
            "id": "real-note-from-applescript",
            "title": "Real Apple Note (Shopping Related)",
            "text": raw_output[:500] + "..." if len(raw_output) > 500 else raw_output,
            "images": [],
            "links": [],
            "source": "applescript"
        }
    
    return None

def test_with_applescript():
    """Test using AppleScript to fetch real notes."""
    print("🍎 Testing with Real Apple Notes via AppleScript")
    print("=" * 55)
    
    # Get notes using AppleScript
    print("Fetching notes from Apple Notes app...")
    raw_notes = get_notes_via_applescript()
    
    if not raw_notes:
        print("❌ Could not fetch notes from Apple Notes")
        return False
    
    # Parse the notes
    note = parse_applescript_notes(raw_notes)
    
    if not note:
        print("❌ No shopping-related notes found")
        print("💡 Try creating a note in Apple Notes with shopping items like:")
        print("   - milk")
        print("   - bread") 
        print("   - eggs")
        return False
    
    print("✅ Found a shopping-related note!")
    print(f"Note title: {note['title']}")
    print(f"Note preview: {note['text'][:100]}...")
    
    # Process with our pipeline
    print("\n🤖 Processing with Claude...")
    try:
        processor = NotesProcessor()
        
        # Override the fetch method temporarily
        original_fetch = processor.fetch_note_from_mcp
        
        def mock_fetch(note_id):
            return note
        
        processor.fetch_note_from_mcp = mock_fetch
        
        # Process the note
        result = processor.process_note("real-note")
        
        # Restore original method
        processor.fetch_note_from_mcp = original_fetch
        
        # Display results
        print("\n✅ Processing complete!")
        print(processor.format_output(result))
        
        # Save the result
        processor.save_output(result, "real-apple-note")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing note: {e}")
        return False

def test_manual_input():
    """Allow manual input of note content for testing."""
    print("\n📝 Manual Note Input Test")
    print("=" * 30)
    
    print("Paste your shopping note content below (press Enter twice when done):")
    lines = []
    empty_count = 0
    
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
        else:
            empty_count = 0
            lines.append(line)
    
    if not lines:
        print("❌ No content provided")
        return False
    
    note_content = "\n".join(lines)
    
    # Create a note object
    note = {
        "id": "manual-input",
        "title": "Manual Input Note",
        "text": note_content,
        "images": [],
        "links": [],
        "source": "manual"
    }
    
    print(f"\n📄 Processing note with {len(note_content)} characters...")
    
    try:
        processor = NotesProcessor()
        
        # Override the fetch method
        def mock_fetch(note_id):
            return note
        
        processor.fetch_note_from_mcp = mock_fetch
        
        # Process the note
        result = processor.process_note("manual-input")
        
        # Display results
        print("\n✅ Processing complete!")
        print(processor.format_output(result))
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing note: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Real Apple Notes Testing")
    print("=" * 40)
    
    print("\nChoose testing method:")
    print("1. Try to fetch from Apple Notes app (AppleScript)")
    print("2. Manual input (paste note content)")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        success = test_with_applescript()
        if not success:
            print("\n💡 AppleScript method failed. Try method 2 for manual input.")
    elif choice == "2":
        test_manual_input()
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice")
        return

if __name__ == "__main__":
    main()