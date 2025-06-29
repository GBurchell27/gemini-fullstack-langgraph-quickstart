"""
Blog Writer State Management

This module defines the state structure for the blog writing workflow,
following the existing LangGraph patterns in the codebase.
"""

from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator
from dataclasses import dataclass, field


class BlogWriterState(TypedDict):
    """Main state for the blog writing workflow"""
    
    # Input and configuration
    blog_idea: str
    target_audience: Optional[str]
    tone: Optional[str]
    length: Optional[str]
    
    # Topic analysis
    topic_analysis: Optional[Dict[str, Any]]
    research_questions: Annotated[List[str], operator.add]
    target_keywords: Annotated[List[str], operator.add]
    
    # Research phase
    research_plan: Optional[Dict[str, Any]]
    research_tasks: Annotated[List[Dict[str, Any]], operator.add]
    search_queries_executed: Annotated[List[str], operator.add]
    web_research_results: Annotated[List[Dict[str, Any]], operator.add]
    research_summary: Optional[Dict[str, Any]]
    competitor_analysis: Annotated[List[Dict[str, Any]], operator.add]
    internal_content_matches: Annotated[List[Dict[str, Any]], operator.add]
    synthesized_research: Optional[Dict[str, Any]]
    
    # Content strategy
    content_strategy: Optional[Dict[str, Any]]
    title_options: Annotated[List[str], operator.add]
    outline: Optional[Dict[str, Any]]
    key_messages: Annotated[List[str], operator.add]
    cta_suggestions: Annotated[List[str], operator.add]
    
    # Content creation
    introduction: Optional[str]
    body_sections: Annotated[List[Dict[str, str]], operator.add]
    conclusion: Optional[str]
    assembled_content: Optional[str]
    
    # Enhancement
    internal_links: Annotated[List[Dict[str, str]], operator.add]
    external_links: Annotated[List[Dict[str, str]], operator.add]
    content_with_links: Optional[str]
    
    # SEO optimization
    seo_metadata: Optional[Dict[str, Any]]
    meta_title: Optional[str]
    meta_description: Optional[str]
    tags: Annotated[List[str], operator.add]
    categories: Annotated[List[str], operator.add]
    
    # Output
    markdown_content: Optional[str]
    quality_score: Optional[float]
    quality_report: Optional[Dict[str, Any]]
    final_output: Optional[Dict[str, Any]]
    final_blog_result: Optional[Dict[str, Any]]
    
    # System tracking
    current_step: str
    progress: float
    errors: Annotated[List[str], operator.add]
    warnings: Annotated[List[str], operator.add]
    debug_info: Annotated[List[Dict[str, Any]], operator.add]
    
    # Configuration
    max_research_iterations: Optional[int]
    max_web_searches: Optional[int]


class ResearchState(TypedDict):
    """State for individual research operations"""
    search_query: str
    research_type: str  # 'web', 'competitor', 'internal'
    results: List[Dict[str, Any]]
    id: int


class ContentWritingState(TypedDict):
    """State for individual content writing operations"""
    section_type: str  # 'introduction', 'body', 'conclusion'
    section_index: Optional[int]
    section_outline: Dict[str, Any]
    research_context: Dict[str, Any]
    content: str
    id: int


class WebSearchState(TypedDict):
    """State for individual web search operations"""
    search_query: str
    search_id: int
    blog_idea: Optional[str]
    main_topic: Optional[str]
    research_questions: Optional[List[str]]


@dataclass
class BlogWriterConfig:
    """Configuration for blog writer workflow"""
    
    # Research settings
    max_web_searches: int = field(default=5)
    max_research_iterations: int = field(default=3)
    research_depth: str = field(default="medium")  # low, medium, high
    
    # Content settings
    target_word_count: int = field(default=1500)
    max_sections: int = field(default=8)
    include_examples: bool = field(default=True)
    
    # SEO settings
    keyword_density_target: float = field(default=0.02)  # 2%
    max_internal_links: int = field(default=5)
    max_external_links: int = field(default=3)
    
    # Quality settings
    min_quality_score: float = field(default=0.7)
    enable_fact_checking: bool = field(default=True)
    
    # System settings
    llm_model: str = field(default="gemini-2.0-flash-exp")
    enable_parallel_processing: bool = field(default=True)
    timeout_seconds: int = field(default=300)
    
    # Debug settings
    debug_mode: bool = field(default=False)
    save_intermediate_outputs: bool = field(default=True)


# Helper functions for state management
def initialize_blog_writer_state(blog_idea: str, **kwargs) -> BlogWriterState:
    """Initialize a new blog writer state with default values"""
    
    return BlogWriterState(
        # Input
        blog_idea=blog_idea,
        target_audience=kwargs.get('target_audience', 'general'),
        tone=kwargs.get('tone', 'professional'),
        length=kwargs.get('length', 'medium'),
        
        # Initialize empty lists and None values
        topic_analysis=None,
        research_questions=[],
        target_keywords=[],
        research_plan=None,
        research_tasks=[],
        search_queries_executed=[],
        web_research_results=[],
        research_summary=None,
        competitor_analysis=[],
        internal_content_matches=[],
        synthesized_research=None,
        content_strategy=None,
        title_options=[],
        outline=None,
        key_messages=[],
        cta_suggestions=[],
        introduction=None,
        body_sections=[],
        conclusion=None,
        assembled_content=None,
        internal_links=[],
        external_links=[],
        content_with_links=None,
        seo_metadata=None,
        meta_title=None,
        meta_description=None,
        tags=[],
        categories=[],
        markdown_content=None,
        quality_score=None,
        quality_report=None,
        final_output=None,
        final_blog_result=None,
        
        # System
        current_step='input_processing',
        progress=0.0,
        errors=[],
        warnings=[],
        debug_info=[]
    )


def update_progress(state: BlogWriterState, step: str, progress: float) -> None:
    """Update the current step and progress in the state"""
    state['current_step'] = step
    state['progress'] = progress
    
    if state.get('debug_info') is None:
        state['debug_info'] = []
        
    state['debug_info'].append({
        'step': step,
        'progress': progress,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })


def add_error(state: BlogWriterState, error: str, context: Optional[Dict] = None) -> None:
    """Add an error to the state with optional context"""
    if state.get('errors') is None:
        state['errors'] = []
        
    error_entry = {
        'message': error,
        'step': state.get('current_step', 'unknown'),
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    if context:
        error_entry['context'] = context
        
    state['errors'].append(str(error_entry))


def add_warning(state: BlogWriterState, warning: str, context: Optional[Dict] = None) -> None:
    """Add a warning to the state with optional context"""
    if state.get('warnings') is None:
        state['warnings'] = []
        
    warning_entry = {
        'message': warning,
        'step': state.get('current_step', 'unknown'),
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    if context:
        warning_entry['context'] = context
        
    state['warnings'].append(str(warning_entry)) 