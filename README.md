~~Hey, this is my personal project I'm working on that translates thoughts I have in my head while walking --> actionable todos and shopping lists~~

# Apple Notes → Claude → Shopping Lists

A minimal pipeline that converts Apple Notes into optimized shopping lists using Claude AI. The system analyzes notes (text, images, links) and provides intelligent timing recommendations.

## Phase 1: Basic Pipeline (Current)

### Quick Start

1. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up Apple Notes MCP server:**
   ```bash
   pip install mcp-apple-notes
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Configure Claude API:**
   - Copy `config.yaml` and add your Claude API key
   - Get API key from [Claude Console](https://console.anthropic.com/)

4. **Configure MCP server in Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "apple-notes": {
         "command": "uvx",
         "args": ["mcp-apple-notes@latest"]
       }
     }
   }
   ```

### Usage

```bash
# Basic usage with mock data (for testing)
python src/notes_processor.py --note-id "test-note-123"

# With different output formats
python src/notes_processor.py --note-id "test-note-123" --output-format markdown

# Debug mode
python src/notes_processor.py --note-id "test-note-123" --debug
```

### What it does

- **Extracts items** from Apple Notes (text, images, links)
- **Categorizes and prioritizes** items using Claude AI
- **Estimates costs** based on typical market prices  
- **Suggests timing** for optimal purchasing
- **Outputs structured lists** in JSON, Markdown, or plain text

### Example Output

```json
{
  "shopping_list": [
    {
      "item": "organic milk (2%, half gallon)",
      "category": "dairy", 
      "priority": "high",
      "estimated_cost": "$4.99",
      "quantity": "1"
    }
  ],
  "total_estimated_cost": "$24.95",
  "timing": {
    "optimal_shopping_day": "Saturday"
  }
}
```

## Future Phases

- **Phase 2:** Price tracking and smart timing
- **Phase 3:** Reddit review integration  
- **Phase 4:** RAG optimization for personal preferences

See `WORKFLOW.md` for detailed implementation plan.

## Testing

```bash
# Run tests
python -m pytest tests/

# Test basic functionality
python tests/test_basic.py
```
