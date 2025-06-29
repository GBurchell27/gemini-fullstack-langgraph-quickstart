"""
Content Section Writers

Handles parallel generation of blog sections (introduction, body, conclusion).
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send
from google.genai import Client

from ...state import BlogWriterState, ContentWritingState, update_progress, add_error, add_warning
from ...schemas import BlogSection
from ...prompts import (
    INTRODUCTION_WRITER_PROMPT,
    BODY_SECTION_WRITER_PROMPT,
    CONCLUSION_WRITER_PROMPT,
    get_current_date
)

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")

genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))


def section_writing_dispatcher(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Prepare section writing tasks and execute them sequentially.
    
    This node:
    1. Creates writing tasks for introduction, body sections, and conclusion
    2. Executes section writing sequentially 
    3. Prepares context for each section
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with written sections
    """
    
    logger.info("=" * 50)
    logger.info("STARTING SECTION WRITING DISPATCHER")
    logger.info("=" * 50)
    
    # Get content strategy
    content_strategy = state.get('content_strategy', {})
    outline = content_strategy.get('outline', {})
    
    if not outline:
        logger.error("No content outline found in strategy")
        add_error(state, "Content outline missing from strategy")
        state['current_step'] = 'content_assembly'
        return state
    
    # Get selected title (first option or fallback)
    title_options = content_strategy.get('title_options', [])
    selected_title = title_options[0] if title_options else state.get('blog_idea', 'Blog Post')
    
    # Prepare shared context
    research_context = prepare_research_context(state)
    
    logger.info(f"Selected title: {selected_title}")
    logger.info(f"Outline sections: {len(outline.get('sections', []))}")
    
    # Initialize section storage
    introduction = ""
    body_sections = []
    conclusion = ""
    section_id = 0
    
    try:
        # 1. Write Introduction section
        introduction_outline = outline.get('introduction', {})
        if introduction_outline:
            logger.debug("Writing introduction section")
            section_state = {
                "section_type": "introduction",
                "section_index": None,
                "section_outline": {
                    "title": selected_title,
                    "content": introduction_outline,
                    "target_words": introduction_outline.get('word_count', 200)
                },
                "research_context": research_context,
                "content": "",
                "id": section_id
            }
            intro_result = write_individual_section(section_state, config)
            introduction = intro_result.get('introduction', '')
            section_id += 1
        
        # 2. Write Body sections
        body_section_outlines = outline.get('sections', [])
        for idx, section_outline in enumerate(body_section_outlines):
            logger.debug(f"Writing body section {idx+1}: {section_outline.get('title', 'Untitled')}")
            section_state = {
                "section_type": "body",
                "section_index": idx,
                "section_outline": section_outline,
                "research_context": research_context,
                "content": "",
                "id": section_id
            }
            body_result = write_individual_section(section_state, config)
            body_sections.extend(body_result.get('body_sections', []))
            section_id += 1
        
        # 3. Write Conclusion section
        conclusion_outline = outline.get('conclusion', {})
        if conclusion_outline:
            logger.debug("Writing conclusion section")
            section_state = {
                "section_type": "conclusion",
                "section_index": None,
                "section_outline": {
                    "title": "Conclusion",
                    "content": conclusion_outline,
                    "target_words": conclusion_outline.get('word_count', 200),
                    "key_messages": content_strategy.get('key_messages', []),
                    "cta_options": content_strategy.get('cta_suggestions', [])
                },
                "research_context": research_context,
                "content": "",
                "id": section_id
            }
            conclusion_result = write_individual_section(section_state, config)
            conclusion = conclusion_result.get('conclusion', '')
            section_id += 1
        
        # Update state with all sections
        state['introduction'] = introduction
        state['body_sections'] = body_sections
        state['conclusion'] = conclusion
        
        logger.info(f"Section writing complete: {len(body_sections)} body sections")
        
        # Update progress and set next step
        update_progress(state, 'content_assembly', 0.6)
        state['current_step'] = 'content_assembly'
        
        return state
        
    except Exception as e:
        error_msg = f"Error in section writing dispatcher: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        state['current_step'] = 'content_assembly'
        return state


def write_individual_section(
    state: ContentWritingState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Write an individual blog section.
    
    This node:
    1. Determines section type and appropriate prompt
    2. Uses LLM to generate content
    3. Validates and formats the result
    
    Args:
        state: Content writing state with section details
        config: LangGraph configuration
        
    Returns:
        Updated state with written section
    """
    
    section_type = state.get('section_type', '')
    section_id = state.get('id', 0)
    section_outline = state.get('section_outline', {})
    research_context = state.get('research_context', {})
    
    logger.info(f"Writing {section_type} section (ID: {section_id})")
    
    try:
        # Select appropriate prompt and generate content
        if section_type == "introduction":
            content = write_introduction_section(section_outline, research_context)
        elif section_type == "body":
            content = write_body_section(section_outline, research_context)
        elif section_type == "conclusion":
            content = write_conclusion_section(section_outline, research_context)
        else:
            raise ValueError(f"Unknown section type: {section_type}")
        
        # Count words
        word_count = len(content.split())
        
        # Extract keywords used (simple approach)
        keywords_used = extract_keywords_from_content(content, research_context.get('target_keywords', []))
        
        # Create section result
        section_result = {
            'type': section_type,
            'title': section_outline.get('title', ''),
            'content': content,
            'word_count': word_count,
            'keywords_used': keywords_used,
            'section_index': state.get('section_index'),
            'id': section_id,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Section {section_id} ({section_type}) completed: {word_count} words")
        
        # Return appropriate field based on section type
        if section_type == "introduction":
            return {
                'introduction': content,
                'body_sections': []
            }
        elif section_type == "conclusion":
            return {
                'conclusion': content,
                'body_sections': []
            }
        else:  # body section
            return {
                'body_sections': [section_result],
                'introduction': None,
                'conclusion': None
            }
            
    except Exception as e:
        error_msg = f"Error writing {section_type} section {section_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Return error state
        return {
            'body_sections': [],
            'errors': [error_msg]
        }


def write_introduction_section(
    section_outline: Dict[str, Any],
    research_context: Dict[str, Any]
) -> str:
    """Write the introduction section using LLM."""
    
    prompt = INTRODUCTION_WRITER_PROMPT.format(
        title=section_outline.get('title', ''),
        target_audience=research_context.get('target_audience', 'general'),
        tone=research_context.get('tone', 'professional'),
        key_points=format_key_points(section_outline.get('content', {}))
    )
    
    response = genai_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config={
            "temperature": 0.7,
            "max_output_tokens": 1000
        }
    )
    
    return clean_llm_response(response.text)


def write_body_section(
    section_outline: Dict[str, Any],
    research_context: Dict[str, Any]
) -> str:
    """Write a body section using LLM."""
    
    # Get relevant research data for this section
    relevant_research = extract_relevant_research(
        section_outline.get('title', ''),
        research_context.get('research_summary', {})
    )
    
    prompt = BODY_SECTION_WRITER_PROMPT.format(
        section_title=section_outline.get('title', ''),
        section_outline=format_section_outline(section_outline),
        research_data=relevant_research,
        keywords=', '.join(research_context.get('target_keywords', [])),
        tone=research_context.get('tone', 'professional'),
        target_words=section_outline.get('word_count', 300)
    )
    
    response = genai_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config={
            "temperature": 0.7,
            "max_output_tokens": 2000
        }
    )
    
    return clean_llm_response(response.text)


def write_conclusion_section(
    section_outline: Dict[str, Any],
    research_context: Dict[str, Any]
) -> str:
    """Write the conclusion section using LLM."""
    
    prompt = CONCLUSION_WRITER_PROMPT.format(
        title=research_context.get('blog_title', ''),
        key_messages=format_list(section_outline.get('key_messages', [])),
        main_points=format_list(research_context.get('main_points', [])),
        cta_options=format_list(section_outline.get('cta_options', []))
    )
    
    response = genai_client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config={
            "temperature": 0.7,
            "max_output_tokens": 1000
        }
    )
    
    return clean_llm_response(response.text)


def aggregate_sections(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Aggregate results from parallel section writing.
    
    This node:
    1. Collects all written sections
    2. Organizes them in proper order
    3. Calculates statistics
    4. Updates progress
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with organized sections
    """
    
    logger.info("=" * 50)
    logger.info("AGGREGATING WRITTEN SECTIONS")
    logger.info("=" * 50)
    
    # Get all sections
    introduction = state.get('introduction', '')
    body_sections = state.get('body_sections', [])
    conclusion = state.get('conclusion', '')
    
    # Sort body sections by index if they have one
    sorted_body_sections = sorted(
        [s for s in body_sections if isinstance(s, dict) and s.get('type') == 'body'],
        key=lambda x: x.get('section_index', 0)
    )
    
    # Calculate statistics
    intro_word_count = len(introduction.split()) if introduction else 0
    body_word_count = sum(s.get('word_count', 0) for s in sorted_body_sections)
    conclusion_word_count = len(conclusion.split()) if conclusion else 0
    total_word_count = intro_word_count + body_word_count + conclusion_word_count
    
    # Collect all keywords used
    all_keywords = []
    for section in sorted_body_sections:
        all_keywords.extend(section.get('keywords_used', []))
    
    # Update state with section statistics
    section_stats = {
        'introduction_words': intro_word_count,
        'body_sections_count': len(sorted_body_sections),
        'body_words': body_word_count,
        'conclusion_words': conclusion_word_count,
        'total_words': total_word_count,
        'keywords_used': list(set(all_keywords)),  # Remove duplicates
        'sections_completed': bool(introduction) + len(sorted_body_sections) + bool(conclusion),
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to debug info
    state['debug_info'].append({
        'node': 'aggregate_sections',
        'timestamp': datetime.now().isoformat(),
        'statistics': section_stats
    })
    
    logger.info(f"Section aggregation complete:")
    logger.info(f"  - Introduction: {intro_word_count} words")
    logger.info(f"  - Body sections: {len(sorted_body_sections)} sections, {body_word_count} words")
    logger.info(f"  - Conclusion: {conclusion_word_count} words")
    logger.info(f"  - Total: {total_word_count} words")
    logger.info(f"  - Keywords used: {len(all_keywords)} unique keywords")
    
    # Update body_sections with sorted list
    state['body_sections'] = sorted_body_sections
    
    # Update progress
    update_progress(state, 'content_assembly', 0.6)
    
    return state


# Helper functions

def prepare_research_context(state: BlogWriterState) -> Dict[str, Any]:
    """Prepare research context for section writers."""
    
    topic_analysis = state.get('topic_analysis', {})
    research_summary = state.get('research_summary', {})
    content_strategy = state.get('content_strategy', {})
    
    return {
        'blog_idea': state.get('blog_idea', ''),
        'target_audience': state.get('target_audience', 'general'),
        'tone': state.get('tone', 'professional'),
        'main_topic': topic_analysis.get('main_topic', ''),
        'target_keywords': topic_analysis.get('target_keywords', []),
        'research_questions': state.get('research_questions', []),
        'research_summary': research_summary,
        'key_insights': research_summary.get('key_insights', []),
        'internal_content': state.get('internal_content_matches', []),
        'main_points': content_strategy.get('key_messages', []),
        'blog_title': content_strategy.get('title_options', [''])[0] if content_strategy.get('title_options') else ''
    }


def format_key_points(content_dict: Dict[str, Any]) -> str:
    """Format key points for prompt inclusion."""
    
    if isinstance(content_dict, dict):
        points = []
        for key, value in content_dict.items():
            if isinstance(value, list):
                points.extend(value)
            elif isinstance(value, str):
                points.append(value)
        return '\n'.join(f"- {point}" for point in points)
    elif isinstance(content_dict, list):
        return '\n'.join(f"- {point}" for point in content_dict)
    else:
        return str(content_dict)


def format_section_outline(section: Dict[str, Any]) -> str:
    """Format section outline for prompt inclusion."""
    
    outline_parts = []
    
    if 'title' in section:
        outline_parts.append(f"Title: {section['title']}")
    
    if 'subsections' in section:
        outline_parts.append("Subsections:")
        for subsection in section['subsections']:
            outline_parts.append(f"  - {subsection}")
    
    if 'key_points' in section:
        outline_parts.append("Key Points:")
        for point in section['key_points']:
            outline_parts.append(f"  - {point}")
    
    if 'word_count' in section:
        outline_parts.append(f"Target Word Count: {section['word_count']}")
    
    return '\n'.join(outline_parts)


def format_list(items: List[str]) -> str:
    """Format a list for prompt inclusion."""
    return '\n'.join(f"- {item}" for item in items) if items else "None specified"


def extract_relevant_research(section_title: str, research_summary: Dict[str, Any]) -> str:
    """Extract research relevant to a specific section."""
    
    # Get all research insights
    insights = research_summary.get('key_insights', [])
    sources = research_summary.get('sources', [])
    
    # Simple keyword matching to find relevant insights
    section_keywords = section_title.lower().split()
    relevant_insights = []
    
    for insight in insights[:10]:  # Limit to top 10
        insight_lower = insight.lower()
        if any(keyword in insight_lower for keyword in section_keywords):
            relevant_insights.append(insight)
    
    # If no specific matches, include general insights
    if not relevant_insights:
        relevant_insights = insights[:5]
    
    # Format for prompt
    research_text = "Key Research Insights:\n"
    for insight in relevant_insights:
        research_text += f"- {insight}\n"
    
    # Add source count
    research_text += f"\nBased on {len(sources)} authoritative sources."
    
    return research_text


def extract_keywords_from_content(content: str, target_keywords: List[str]) -> List[str]:
    """Extract which target keywords are used in the content."""
    
    content_lower = content.lower()
    used_keywords = []
    
    for keyword in target_keywords:
        if keyword.lower() in content_lower:
            used_keywords.append(keyword)
    
    return used_keywords


def clean_llm_response(text: str) -> str:
    """Clean up LLM response text."""
    
    if not text:
        return ""
    
    # Remove common artifacts
    text = text.strip()
    
    # Remove markdown artifacts if they wrap the entire content
    if text.startswith('```') and text.endswith('```'):
        lines = text.split('\n')
        if len(lines) > 2:
            text = '\n'.join(lines[1:-1])
    
    return text 