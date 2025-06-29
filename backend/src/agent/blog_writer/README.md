# Blog Writer System

## Current Status

### ✅ Milestone 1: Foundation Setup - COMPLETE
- State Management with TypedDict pattern
- Schema Validation with Pydantic
- Basic Graph Structure with error handling
- API Integration configured
- Comprehensive logging and debugging

### 🚧 Milestone 2: Topic Analysis Pipeline - IN PROGRESS
#### ✅ Step 2.1: Topic Analyzer Node - COMPLETE
- Analyzes blog ideas using Gemini
- Extracts main topic and subtopics
- Generates research questions
- Identifies target keywords
- Provides audience insights

#### ⏳ Step 2.2: Research Coordinator - TODO
- Plan research strategy
- Prioritize queries
- Allocate resources

## File Structure
```
backend/src/agent/blog_writer/
├── __init__.py           # Package initialization
├── state.py              # State management and helpers
├── schemas.py            # Pydantic validation schemas
├── graph.py              # LangGraph workflow definition
├── api_utils.py          # API utilities and formatters
├── prompts.py            # All prompts for the system ✨ NEW
├── nodes/
│   ├── __init__.py       # Nodes package init
│   ├── input_processor.py # Input validation node
│   └── topic_analyzer.py  # Topic analysis node ✨ NEW
├── test_basic_setup.py   # Basic functionality tests
├── test_api.py           # API integration tests
├── test_topic_analyzer.py # Topic analyzer tests ✨ NEW
└── README.md             # This file
```

## Testing Instructions

### Test Topic Analyzer (Milestone 2, Step 2.1)
```bash
cd backend
python src/agent/blog_writer/test_topic_analyzer.py
```

This will test:
- Topic analysis for different blog types (technical, beginner, business)
- Research question generation
- Keyword identification
- Error handling scenarios

Expected output:
- Main topic identification
- 3-5 subtopics per blog idea
- 5-10 research questions
- 5-8 target keywords
- Audience insights

### Test Basic Functionality (Milestone 1)
```bash
cd backend
python src/agent/blog_writer/test_basic_setup.py
```

### Test API Integration
First, start the LangGraph API server:
```bash
cd backend
langgraph up
```

Then in another terminal:
```bash
cd backend
python src/agent/blog_writer/test_api.py
```

## Current Capabilities

The system now can:
1. Accept and validate blog creation requests
2. **Analyze topics and generate research questions** ✨ NEW
3. **Identify target keywords for SEO** ✨ NEW
4. **Provide audience insights** ✨ NEW
5. Handle errors gracefully with proper routing
6. Provide detailed logging for debugging

## API Usage

The blog writer is available through LangGraph's API:

```json
POST http://localhost:2024/threads/{thread_id}/runs
{
  "assistant_id": "blog_writer",
  "input": {
    "blog_idea": "Your blog topic here",
    "target_audience": "your target audience",
    "tone": "professional|casual|technical|conversational|academic",
    "length": "short|medium|long"
  }
}
```

## Topic Analysis Output Example

```json
{
  "main_topic": "Building Scalable Microservices with Python",
  "complexity": "high",
  "subtopics": [
    "API Gateway Design Patterns",
    "Service Discovery Mechanisms",
    "Distributed Tracing Implementation"
  ],
  "research_questions": [
    "What are the best Python frameworks for microservices?",
    "How to implement service discovery in Python?",
    "What are the best practices for API gateway design?"
  ],
  "target_keywords": [
    "python microservices",
    "scalable architecture python",
    "microservices api gateway"
  ],
  "audience_insights": {
    "pain_points": "Managing complexity in distributed systems",
    "solutions_sought": "Practical implementation guidance",
    "detail_level": "Advanced technical depth",
    "action_items": "Implement learned patterns in their projects"
  }
}
```

## Next Steps

**Milestone 2 Completion:**
- ✅ Topic Analyzer (Step 2.1)
- ⏳ Research Coordinator (Step 2.2)

**Upcoming Milestones:**
- Milestone 3: Research Implementation
- Milestone 4: Content Generation
- Milestone 5: Enhancement & Output
- Milestone 6: Frontend Integration

## Configuration

The system uses `BlogWriterConfig` dataclass:
- `max_web_searches`: Maximum searches per iteration (default: 5)
- `max_research_iterations`: Maximum research loops (default: 3)
- `target_word_count`: Target blog length (default: 1500)
- `llm_model`: Gemini model to use (default: gemini-2.0-flash-exp)

## Debug Tips

1. **Check Logs**: Topic analyzer outputs detailed logs
2. **State Inspection**: Check `topic_analysis` field in state
3. **Error Details**: Look for LLM errors in the errors array
4. **Progress Tracking**: Topic analysis moves progress to 0.15

## Dependencies

Make sure you have:
- `GEMINI_API_KEY` environment variable set
- `langchain-google-genai` package installed
- All dependencies from `backend/pyproject.toml`

## Known Issues

1. Error messages may appear duplicated in the errors array (minor issue)
2. API test requires LangGraph server to be running
3. Job tracking is currently in-memory only

## Support

For issues or questions, check:
- Log output for detailed error information
- State debug_info for execution flow
- Graph visualization with `blog_writer_graph.get_graph().draw()` 