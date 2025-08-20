# Apple Notes → Claude → Shopping List Workflow

## Overview
This project creates a minimal pipeline to convert Apple Notes into optimized shopping lists using Claude AI. The system analyzes notes (text, images, links) and provides intelligent timing recommendations based on pricing and personal schedule.

## Architecture
```
Apple Notes → MCP Server → Python Pipeline → Claude API → Structured Output
                                ↓
                        Price/Review APIs (Future)
```

## Phase 1: Basic Pipeline (Current)

### Setup
1. Install Apple Notes MCP server (already configured in README)
2. Set up Python environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure API keys in `config.yaml`

### Usage
```bash
python src/notes_processor.py --note-id "your-note-id"
```

### Input Format (Apple Notes)
- Text lists with items
- Images of products/receipts
- Links to products
- Mixed content

### Output Format
```json
{
  "shopping_list": [
    {
      "item": "organic milk",
      "category": "dairy",
      "priority": "high",
      "estimated_cost": "$4.99",
      "suggested_timing": "this_week"
    }
  ],
  "total_estimated_cost": "$24.95",
  "recommended_purchase_date": "2024-01-15"
}
```

## Phase 2: Smart Timing & Pricing (Future)

### Features
- Price history tracking
- Seasonal pricing patterns
- Calendar integration for timing
- Bulk purchase optimization

### Components
- `price_tracker.py` - Web scraping for price data
- `timing_optimizer.py` - Calendar and urgency analysis
- SQLite database for price history

## Phase 3: Review Integration (Future)

### Features
- Reddit review sentiment analysis
- Product quality scores
- Alternative product suggestions

### Components
- `review_fetcher.py` - Google/Reddit API integration
- Review caching system
- Sentiment analysis pipeline

## Phase 4: Context Optimization (Future)

### Features
- RAG for personal preferences
- Context window management
- Efficient token usage

### Components
- Preference embeddings
- Chunking strategies
- Batch processing

## Configuration

### config.yaml
```yaml
claude:
  api_key: "your-api-key"
  model: "claude-3-sonnet-20240229"

apple_notes:
  mcp_server_url: "local"

pricing:
  enabled: false
  sources: []

reviews:
  enabled: false
  reddit_search: false
```

## Development Guidelines

### Design Principles
- **Minimal dependencies** - Essential libraries only
- **Modular design** - Optional features
- **Local-first** - Cache everything
- **Progressive enhancement** - Build incrementally
- **Clear data flow** - No hidden complexity

### Testing
```bash
python -m pytest tests/
```

### Adding New Features
1. Create feature module in `src/`
2. Add configuration options to `config.yaml`
3. Update main pipeline
4. Add tests
5. Update documentation

## Troubleshooting

### Common Issues
- **MCP connection failed**: Check Apple Notes MCP server setup
- **Claude API errors**: Verify API key and quota
- **Note parsing errors**: Check note format and permissions

### Debug Mode
```bash
python src/notes_processor.py --debug --note-id "your-note-id"
```