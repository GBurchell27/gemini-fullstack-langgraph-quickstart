"""
Research Coordinator Node

Plans and coordinates research activities based on topic analysis.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig

from ..state import BlogWriterState, update_progress, add_error
from ..schemas import ResearchPlan
from ..prompts import RESEARCH_COORDINATOR_PROMPT, get_current_date

# Set up logging
logger = logging.getLogger(__name__)


def research_coordinator_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Plan and coordinate research activities.
    
    This node:
    1. Analyzes research questions from topic analysis
    2. Prioritizes research tasks
    3. Allocates resources (number of searches per question)
    4. Creates research strategy
    5. Identifies internal content opportunities
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with research plan
    """
    
    logger.info("=" * 50)
    logger.info("STARTING RESEARCH COORDINATOR NODE")
    logger.info("=" * 50)
    
    try:
        # Get data from previous nodes
        topic_analysis = state.get('topic_analysis', {})
        research_questions = state.get('research_questions', [])
        target_keywords = state.get('target_keywords', [])
        
        # Validate inputs
        if not topic_analysis or not research_questions:
            error_msg = "Missing topic analysis or research questions"
            logger.error(error_msg)
            add_error(state, error_msg)
            state['current_step'] = 'failed'
            return state
            
        logger.info(f"Planning research for: {topic_analysis.get('main_topic', 'Unknown')}")
        logger.info(f"Number of research questions: {len(research_questions)}")
        logger.info(f"Complexity level: {topic_analysis.get('complexity', 'medium')}")
        
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.3,  # Lower temperature for more consistent planning
            max_retries=2,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        # Use structured output for research plan
        structured_llm = llm.with_structured_output(ResearchPlan)
        
        # Format the prompt
        current_date = get_current_date()
        
        # Format topic analysis for the prompt
        topic_analysis_str = f"""
Main Topic: {topic_analysis.get('main_topic', '')}
Subtopics: {', '.join(topic_analysis.get('subtopics', []))}
Complexity: {topic_analysis.get('complexity', 'medium')}
Research Questions:
{chr(10).join([f"- {q}" for q in research_questions])}
Target Keywords: {', '.join(target_keywords[:10])}
        """
        
        formatted_prompt = RESEARCH_COORDINATOR_PROMPT.format(
            topic_analysis=topic_analysis_str.strip(),
            length=state.get('length', 'medium'),
            max_searches=state.get('max_web_searches', 5)
        )
        
        logger.debug("Sending request to Gemini for research planning...")
        
        # Get the research plan
        try:
            research_plan = structured_llm.invoke(formatted_prompt)
            logger.debug(f"Received research plan: {research_plan}")
            
        except Exception as e:
            error_msg = f"Failed to get research plan from LLM: {str(e)}"
            logger.error(error_msg)
            add_error(state, error_msg, {'llm_error': str(e)})
            state['current_step'] = 'failed'
            return state
            
        # Update state with research plan
        state['research_plan'] = {
            'strategy': research_plan.research_strategy,
            'focus_areas': research_plan.focus_areas,
            'resource_allocation': research_plan.resource_allocation,
            'internal_content_opportunities': research_plan.internal_content_opportunities,
            'search_queries': research_plan.search_queries,
            'timestamp': datetime.now().isoformat()
        }
        
        # Add prioritized research tasks to state
        state['research_tasks'] = [
            {
                'task': task.task,
                'priority': task.priority,
                'search_count': task.search_count
            }
            for task in research_plan.prioritized_tasks
        ]
        
        # Log the plan details
        logger.info(f"Research strategy: {research_plan.research_strategy}")
        logger.info(f"Number of focus areas: {len(research_plan.focus_areas)}")
        logger.info(f"Prioritized tasks: {len(research_plan.prioritized_tasks)}")
        logger.info(f"Search queries prepared: {len(research_plan.search_queries)}")
        
        # Log resource allocation
        logger.info("Resource allocation:")
        for area, allocation in research_plan.resource_allocation.items():
            logger.info(f"  - {area}: {allocation}")
            
        # Add debug info
        state['debug_info'].append({
            'node': 'research_coordinator',
            'timestamp': datetime.now().isoformat(),
            'plan': {
                'strategy': research_plan.research_strategy,
                'tasks_count': len(research_plan.prioritized_tasks),
                'queries_count': len(research_plan.search_queries),
                'focus_areas': research_plan.focus_areas[:3]  # First 3 focus areas
            }
        })
        
        # Update progress and next step
        update_progress(state, 'web_research', 0.25)
        
        logger.info("RESEARCH COORDINATOR COMPLETED SUCCESSFULLY")
        logger.info(f"Next step: {state['current_step']}")
        
        # Log sample outputs for debugging
        logger.debug("Top priority research tasks:")
        for i, task in enumerate(research_plan.prioritized_tasks[:3]):
            logger.debug(f"  {i+1}. {task.task} (Priority: {task.priority})")
            
        logger.debug("Sample search queries:")
        for i, query in enumerate(research_plan.search_queries[:3]):
            logger.debug(f"  - {query}")
        
        return state
        
    except Exception as e:
        error_msg = f"Unexpected error in research coordinator: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg, {'exception': str(e), 'type': type(e).__name__})
        state['current_step'] = 'failed'
        return state 