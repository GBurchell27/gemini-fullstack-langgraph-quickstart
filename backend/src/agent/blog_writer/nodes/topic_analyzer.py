"""
Topic Analyzer Node

Analyzes blog ideas to extract topics, generate research questions, and identify keywords.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig

from ..state import BlogWriterState, update_progress, add_error
from ..schemas import TopicAnalysis
from ..prompts import TOPIC_ANALYZER_PROMPT, get_current_date

# Set up logging
logger = logging.getLogger(__name__)


def topic_analyzer_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Analyze the blog topic and generate research questions.
    
    This node:
    1. Analyzes the main topic and subtopics
    2. Assesses complexity level
    3. Generates research questions
    4. Identifies target keywords
    5. Provides audience insights
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with topic analysis
    """
    
    logger.info("=" * 50)
    logger.info("STARTING TOPIC ANALYZER NODE")
    logger.info(f"Blog idea: {state.get('blog_idea', '')[:100]}...")
    logger.info("=" * 50)
    
    try:
        # Get configuration
        blog_idea = state.get('blog_idea', '')
        target_audience = state.get('target_audience', 'general')
        tone = state.get('tone', 'professional')
        
        # Check if we have a valid blog idea
        if not blog_idea or len(blog_idea.strip()) < 10:
            error_msg = "Invalid blog idea for topic analysis"
            logger.error(error_msg)
            add_error(state, error_msg)
            state['current_step'] = 'failed'
            return state
            
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.7,
            max_retries=2,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        # Use structured output for consistent results
        structured_llm = llm.with_structured_output(TopicAnalysis)
        
        # Format the prompt
        current_date = get_current_date()
        formatted_prompt = TOPIC_ANALYZER_PROMPT.format(
            current_date=current_date,
            blog_idea=blog_idea,
            target_audience=target_audience,
            tone=tone
        )
        
        logger.debug("Sending request to Gemini for topic analysis...")
        
        # Get the analysis
        try:
            analysis_result = structured_llm.invoke(formatted_prompt)
            logger.debug(f"Received analysis: {analysis_result}")
            
        except Exception as e:
            error_msg = f"Failed to get topic analysis from LLM: {str(e)}"
            logger.error(error_msg)
            add_error(state, error_msg, {'llm_error': str(e)})
            state['current_step'] = 'failed'
            return state
            
        # Update state with analysis results
        state['topic_analysis'] = {
            'main_topic': analysis_result.main_topic,
            'subtopics': analysis_result.subtopics,
            'complexity': analysis_result.complexity,
            'audience_insights': analysis_result.audience_insights,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add research questions to state (will accumulate)
        state['research_questions'] = analysis_result.research_questions
        
        # Add target keywords to state (will accumulate)
        state['target_keywords'] = analysis_result.target_keywords
        
        # Log the results
        logger.info(f"Main topic identified: {analysis_result.main_topic}")
        logger.info(f"Complexity level: {analysis_result.complexity}")
        logger.info(f"Number of subtopics: {len(analysis_result.subtopics)}")
        logger.info(f"Research questions generated: {len(analysis_result.research_questions)}")
        logger.info(f"Target keywords identified: {len(analysis_result.target_keywords)}")
        
        # Add debug info
        state['debug_info'].append({
            'node': 'topic_analyzer',
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'main_topic': analysis_result.main_topic,
                'complexity': analysis_result.complexity,
                'subtopics_count': len(analysis_result.subtopics),
                'questions_count': len(analysis_result.research_questions),
                'keywords_count': len(analysis_result.target_keywords)
            }
        })
        
        # Update progress
        update_progress(state, 'research_coordination', 0.15)
        
        logger.info("TOPIC ANALYZER COMPLETED SUCCESSFULLY")
        logger.info(f"Next step: {state['current_step']}")
        
        # Log sample outputs for debugging
        logger.debug("Sample research questions:")
        for i, question in enumerate(analysis_result.research_questions[:3]):
            logger.debug(f"  {i+1}. {question}")
            
        logger.debug("Target keywords:")
        for i, keyword in enumerate(analysis_result.target_keywords[:5]):
            logger.debug(f"  - {keyword}")
        
        return state
        
    except Exception as e:
        error_msg = f"Unexpected error in topic analyzer: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg, {'exception': str(e), 'type': type(e).__name__})
        state['current_step'] = 'failed'
        return state 