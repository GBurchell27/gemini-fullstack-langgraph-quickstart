"""
Blog Writer Graph

Main graph construction for the blog writing workflow.
"""

import logging
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig

from .state import BlogWriterState, BlogWriterConfig
from .nodes import input_processor_node
from .nodes.topic_analyzer import topic_analyzer_node
from .nodes.research_coordinator import research_coordinator_node
from .nodes.research.web_research import (
    web_research_dispatcher,
    perform_web_search,
    aggregate_web_research
)
from .nodes.research.internal_research import internal_research_node

# Set up logging
logger = logging.getLogger(__name__)


def should_continue_or_fail(state: BlogWriterState) -> str:
    """
    Conditional routing function to check if workflow should continue or stop on error.
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name based on state
    """
    if state.get('current_step') == 'failed':
        return "error_handler"
    elif state.get('current_step') == 'topic_analysis':
        return "topic_analyzer"
    elif state.get('current_step') == 'research_coordination':
        return "research_coordinator"
    elif state.get('current_step') == 'web_research':
        return "web_research_dispatcher"
    elif state.get('current_step') == 'internal_research':
        return "internal_research"
    return "placeholder_final"


def create_blog_writer_graph(config: BlogWriterConfig = None):
    """
    Create the blog writer workflow graph.
    
    This creates a LangGraph workflow that processes blog creation requests
    through multiple specialized nodes.
    
    Args:
        config: Optional configuration for the workflow
        
    Returns:
        Compiled LangGraph workflow
    """
    
    if config is None:
        config = BlogWriterConfig()
        
    logger.info("Creating blog writer graph with config:")
    logger.info(f"  - Max web searches: {config.max_web_searches}")
    logger.info(f"  - Max research iterations: {config.max_research_iterations}")
    logger.info(f"  - Target word count: {config.target_word_count}")
    logger.info(f"  - Debug mode: {config.debug_mode}")
    
    # Create the graph
    builder = StateGraph(BlogWriterState)
    
    # Add nodes
    builder.add_node("input_processor", input_processor_node)
    builder.add_node("topic_analyzer", topic_analyzer_node)
    builder.add_node("research_coordinator", research_coordinator_node)
    
    # Add web research nodes
    builder.add_node("web_research_dispatcher", web_research_dispatcher)
    builder.add_node("perform_web_search", perform_web_search)
    builder.add_node("aggregate_web_research", aggregate_web_research)
    
    # Add internal research node
    builder.add_node("internal_research", internal_research_node)
    
    # TODO: Add more nodes as we implement them
    # builder.add_node("web_research", web_research_agent)
    # etc...
    
    # Add error handler node
    def error_handler_node(state: BlogWriterState, config: RunnableConfig) -> BlogWriterState:
        """Handle errors and prepare final error output"""
        logger.error("WORKFLOW FAILED - Error Handler Activated")
        logger.error(f"Errors: {state.get('errors', [])}")
        
        state['final_output'] = {
            'status': 'error',
            'message': 'Blog creation failed due to errors',
            'errors': state.get('errors', []),
            'step_failed': state.get('current_step', 'unknown')
        }
        return state
    
    builder.add_node("error_handler", error_handler_node)
    
    # Add placeholder web research node
    def placeholder_web_research_node(state: BlogWriterState, config: RunnableConfig) -> BlogWriterState:
        """Placeholder for web research"""
        logger.info("PLACEHOLDER: Web research would happen here")
        
        research_plan = state.get('research_plan', {})
        logger.info(f"Research strategy: {research_plan.get('strategy', 'N/A')}")
        logger.info(f"Focus areas: {research_plan.get('focus_areas', [])[:3]}")
        logger.info(f"Search queries prepared: {len(research_plan.get('search_queries', []))}")
        
        state['current_step'] = 'completed'
        state['progress'] = 0.35
        state['final_output'] = {
            'status': 'milestone_2_complete',
            'message': 'Topic analysis and research coordination completed successfully',
            'topic_analysis': state.get('topic_analysis'),
            'research_plan': research_plan,
            'research_tasks': state.get('research_tasks', [])[:5],
            'next_steps': 'Implement web research and content generation nodes'
        }
        return state
    
    builder.add_node("placeholder_web_research", placeholder_web_research_node)
    
    # Add placeholder internal research node
    def placeholder_internal_research_node(state: BlogWriterState, config: RunnableConfig) -> BlogWriterState:
        """Placeholder for internal content research"""
        logger.info("PLACEHOLDER: Internal content research would happen here")
        
        research_summary = state.get('research_summary', {})
        logger.info(f"Web research found {research_summary.get('unique_sources', 0)} unique sources")
        logger.info(f"Key insights: {len(research_summary.get('key_insights', []))}")
        
        state['current_step'] = 'completed'
        state['progress'] = 0.5
        state['final_output'] = {
            'status': 'research_complete',
            'message': 'Web research completed successfully',
            'topic_analysis': state.get('topic_analysis'),
            'research_summary': research_summary,
            'search_queries_executed': state.get('search_queries_executed', []),
            'next_steps': 'Implement internal content research and synthesis'
        }
        return state
    
    builder.add_node("placeholder_internal_research", placeholder_internal_research_node)
    
    # Add placeholder final node for now
    def placeholder_final_node(state: BlogWriterState, config: RunnableConfig) -> BlogWriterState:
        """Temporary placeholder for testing"""
        logger.info("PLACEHOLDER: Workflow would continue here...")
        
        # Double-check we shouldn't be here if there was an error
        if state.get('current_step') == 'failed':
            logger.warning("WARNING: Reached placeholder_final despite failed state")
            return error_handler_node(state, config)
            
        state['current_step'] = 'completed'
        state['progress'] = 1.0
        state['final_output'] = {
            'status': 'placeholder',
            'message': 'Blog writer workflow initialized successfully',
            'next_steps': 'Implement remaining nodes'
        }
        return state
    
    builder.add_node("placeholder_final", placeholder_final_node)
    
    # Set entry point
    builder.add_edge(START, "input_processor")
    
    # Add conditional routing after input processor
    builder.add_conditional_edges(
        "input_processor",
        should_continue_or_fail,
        {
            "topic_analyzer": "topic_analyzer",
            "placeholder_final": "placeholder_final",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after topic analyzer
    builder.add_conditional_edges(
        "topic_analyzer",
        should_continue_or_fail,
        {
            "research_coordinator": "research_coordinator",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after research coordinator
    builder.add_conditional_edges(
        "research_coordinator",
        should_continue_or_fail,
        {
            "web_research_dispatcher": "web_research_dispatcher",
            "error_handler": "error_handler"
        }
    )
    
    # Add edges for web research flow
    # Web research dispatcher uses Send for parallel searches
    builder.add_conditional_edges(
        "web_research_dispatcher",
        lambda x: ["perform_web_search"],  # Always goes to perform_web_search
        ["perform_web_search"]
    )
    
    # All web searches go to aggregation
    builder.add_edge("perform_web_search", "aggregate_web_research")
    
    # After aggregation, check where to go next
    builder.add_conditional_edges(
        "aggregate_web_research",
        should_continue_or_fail,
        {
            "internal_research": "internal_research",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after internal research
    builder.add_conditional_edges(
        "internal_research",
        should_continue_or_fail,
        {
            "placeholder_final": "placeholder_final",
            "error_handler": "error_handler"
        }
    )
    
    # Add edges to END
    builder.add_edge("placeholder_final", END)
    builder.add_edge("placeholder_web_research", END)
    builder.add_edge("placeholder_internal_research", END)
    builder.add_edge("error_handler", END)
    
    # TODO: Add more conditional edges and routing logic as we add nodes
    
    # Compile the graph
    graph = builder.compile()
    
    logger.info("Blog writer graph created successfully")
    
    return graph


# Create a default instance
blog_writer_graph = create_blog_writer_graph() 