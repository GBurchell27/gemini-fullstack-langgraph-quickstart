"""
Blog Writer Graph

Main graph construction for the blog writing workflow.
"""

import logging
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableConfig

from src.agent.blog_writer.state import BlogWriterState, BlogWriterConfig
from src.agent.blog_writer.nodes import input_processor_node
from src.agent.blog_writer.nodes.topic_analyzer import topic_analyzer_node
from src.agent.blog_writer.nodes.research_coordinator import research_coordinator_node
from src.agent.blog_writer.nodes.research.web_research import (
    web_research_dispatcher,
    perform_web_search,
    aggregate_web_research
)
from src.agent.blog_writer.nodes.research.internal_research import internal_research_node
from src.agent.blog_writer.nodes.content.strategist import content_strategist_node
from src.agent.blog_writer.nodes.content.writers import (
    section_writing_dispatcher
)
from src.agent.blog_writer.nodes.content.assembler import content_assembler_node
from src.agent.blog_writer.nodes.enhancement.internal_linking import internal_linking_node
from src.agent.blog_writer.nodes.enhancement.external_linking import external_linking_node

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
    elif state.get('current_step') == 'web_search_execution':
        return "aggregate_web_research"
    elif state.get('current_step') == 'internal_research':
        return "internal_research"
    elif state.get('current_step') == 'content_strategy':
        return "content_strategist"
    elif state.get('current_step') == 'content_creation':
        return "section_writing_dispatcher"
    elif state.get('current_step') == 'section_writing':
        return "section_writing_dispatcher"
    elif state.get('current_step') == 'content_assembly':
        return "content_assembler"
    elif state.get('current_step') == 'internal_linking':
        return "internal_linking"
    elif state.get('current_step') == 'external_linking':
        return "external_linking"
    elif state.get('current_step') == 'final_output':
        return "final_output_generator"
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
    
    # Add content strategist node
    builder.add_node("content_strategist", content_strategist_node)
    
    # Add section writing nodes
    builder.add_node("section_writing_dispatcher", section_writing_dispatcher)
    
    # Add content assembler node
    builder.add_node("content_assembler", content_assembler_node)
    
    # Add enhancement nodes
    builder.add_node("internal_linking", internal_linking_node)
    builder.add_node("external_linking", external_linking_node)
    
    # Add final output generator node
    def final_output_generator(state: BlogWriterState, config: RunnableConfig) -> BlogWriterState:
        """Generate final blog output with all enhancements"""
        logger.info("=" * 50)
        logger.info("GENERATING FINAL OUTPUT")
        logger.info("=" * 50)
        
        try:
            # Get final content
            final_content = state.get('content_with_links', state.get('assembled_content', ''))
            
            # Get metadata
            content_strategy = state.get('content_strategy', {})
            title_options = content_strategy.get('title_options', [])
            selected_title = title_options[0] if title_options else state.get('blog_idea', 'Blog Post')
            
            # Create final blog result
            blog_result = {
                'title': selected_title,
                'content_markdown': final_content,
                'seo_metadata': state.get('seo_metadata', {}),
                'quality_metrics': state.get('quality_metrics', {}),
                'internal_links': state.get('internal_links', []),
                'external_links': state.get('external_links', []),
                'word_count': len(final_content.split()),
                'created_at': datetime.now().isoformat(),
                'processing_summary': {
                    'nodes_executed': len(state.get('debug_info', [])),
                    'workflow_completed': True
                }
            }
            
            state['final_blog_result'] = blog_result
            state['current_step'] = 'completed'
            state['progress'] = 1.0
            
            logger.info(f"Final output generated for: {selected_title}")
            logger.info(f"Word count: {blog_result['word_count']}")
            logger.info(f"Internal links: {len(blog_result['internal_links'])}")
            logger.info(f"External links: {len(blog_result['external_links'])}")
            
            return state
            
        except Exception as e:
            logger.error(f"Error in final output generation: {str(e)}")
            state['errors'] = state.get('errors', []) + [f"Output generation failed: {str(e)}"]
            return state
    
    builder.add_node("final_output_generator", final_output_generator)
    
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
    # Web research dispatcher prepares searches, then goes to execution
    builder.add_conditional_edges(
        "web_research_dispatcher",
        should_continue_or_fail,
        {
            "aggregate_web_research": "aggregate_web_research",
            "internal_research": "internal_research",
            "error_handler": "error_handler"
        }
    )
    
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
            "content_strategist": "content_strategist",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after content strategist
    builder.add_conditional_edges(
        "content_strategist",
        should_continue_or_fail,
        {
            "section_writing_dispatcher": "section_writing_dispatcher",
            "error_handler": "error_handler",
            "placeholder_final": "placeholder_final"
        }
    )
    
    # Add edges for section writing flow
    # Section writing dispatcher now handles all writing internally
    builder.add_conditional_edges(
        "section_writing_dispatcher",
        should_continue_or_fail,
        {
            "content_assembler": "content_assembler",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after content assembler
    builder.add_conditional_edges(
        "content_assembler",
        should_continue_or_fail,
        {
            "internal_linking": "internal_linking",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after internal linking
    builder.add_conditional_edges(
        "internal_linking",
        should_continue_or_fail,
        {
            "external_linking": "external_linking",
            "error_handler": "error_handler"
        }
    )
    
    # Add conditional routing after external linking
    builder.add_conditional_edges(
        "external_linking",
        should_continue_or_fail,
        {
            "final_output_generator": "final_output_generator",
            "error_handler": "error_handler"
        }
    )
    
    # Add edges to END
    builder.add_edge("final_output_generator", END)
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