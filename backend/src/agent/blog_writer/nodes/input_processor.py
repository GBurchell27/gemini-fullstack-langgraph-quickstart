"""
Input Processor Node

First node in the blog writer workflow that validates and processes the initial blog request.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from ..state import BlogWriterState, update_progress, add_error
from ..schemas import BlogRequest
from langchain_core.runnables import RunnableConfig

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add console handler with formatting
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


def input_processor_node(
    state: BlogWriterState, 
    config: RunnableConfig
) -> BlogWriterState:
    """
    Process and validate the initial blog request.
    
    This node:
    1. Validates the input blog idea
    2. Sets default values for optional parameters
    3. Prepares the state for the next steps
    4. Logs all activities for debugging
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with validated input and initial setup
    """
    
    logger.info("=" * 50)
    logger.info("STARTING INPUT PROCESSOR NODE")
    logger.info(f"Blog idea: {state.get('blog_idea', 'Not provided')[:100]}...")
    logger.info(f"Target audience: {state.get('target_audience', 'Not set')}")
    logger.info(f"Tone: {state.get('tone', 'Not set')}")
    logger.info(f"Length: {state.get('length', 'Not set')}")
    logger.info("=" * 50)
    
    try:
        # Extract input from state
        blog_idea = state.get('blog_idea', '')
        
        # Validate using Pydantic schema
        try:
            request = BlogRequest(
                idea=blog_idea,
                target_audience=state.get('target_audience'),
                tone=state.get('tone'),
                length=state.get('length')
            )
            logger.debug(f"Validated request: {request.dict()}")
            
        except Exception as e:
            error_msg = f"Input validation failed: {str(e)}"
            logger.error(error_msg)
            add_error(state, error_msg, {'validation_error': str(e)})
            state['current_step'] = 'failed'
            state['progress'] = 0.0
            return state
        
        # Update state with validated and normalized values
        state['blog_idea'] = request.idea
        state['target_audience'] = request.target_audience
        state['tone'] = request.tone
        state['length'] = request.length
        
        # Initialize tracking fields if not present
        if 'errors' not in state:
            state['errors'] = []
        if 'warnings' not in state:
            state['warnings'] = []
        if 'debug_info' not in state:
            state['debug_info'] = []
            
        # Add initial debug info
        state['debug_info'].append({
            'node': 'input_processor',
            'timestamp': datetime.now().isoformat(),
            'input': {
                'idea': request.idea[:100] + '...' if len(request.idea) > 100 else request.idea,
                'audience': request.target_audience,
                'tone': request.tone,
                'length': request.length
            },
            'validation': 'passed'
        })
        
        # Determine complexity based on idea length and keywords
        complexity_keywords = ['complex', 'technical', 'advanced', 'comprehensive', 'detailed']
        idea_lower = blog_idea.lower()
        
        complexity = 'high' if any(keyword in idea_lower for keyword in complexity_keywords) else 'medium'
        if len(blog_idea) < 50:
            complexity = 'low'
            
        logger.info(f"Determined complexity level: {complexity}")
        
        # Set initial research parameters based on length
        if request.length == 'short':
            state['max_research_iterations'] = 1
            state['max_web_searches'] = 3
        elif request.length == 'long':
            state['max_research_iterations'] = 3
            state['max_web_searches'] = 8
        else:  # medium
            state['max_research_iterations'] = 2
            state['max_web_searches'] = 5
            
        logger.info(f"Research parameters set - iterations: {state.get('max_research_iterations')}, "
                   f"searches: {state.get('max_web_searches')}")
        
        # Update progress
        update_progress(state, 'topic_analysis', 0.05)
        
        logger.info("INPUT PROCESSOR COMPLETED SUCCESSFULLY")
        logger.info(f"Next step: {state['current_step']}")
        logger.debug(f"State keys: {list(state.keys())}")
        
        return state
        
    except Exception as e:
        error_msg = f"Unexpected error in input processor: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg, {'exception': str(e), 'type': type(e).__name__})
        state['current_step'] = 'failed'
        state['progress'] = 0.0
        return state 