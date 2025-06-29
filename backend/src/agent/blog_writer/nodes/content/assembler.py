"""
Content Assembler

Combines written sections into a cohesive blog post with smooth transitions.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from google.genai import Client

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...prompts import get_current_date

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")

genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))


TRANSITION_GENERATOR_PROMPT = """
Generate a smooth transition between these two blog sections.

Previous section ends with:
{previous_ending}

Next section begins with:
{next_beginning}

Create a 1-2 sentence transition that:
1. Connects the ideas naturally
2. Maintains the flow of the article
3. Uses the specified tone: {tone}
4. Is concise and clear

Do not repeat content from either section. Just provide the transition text.
"""

CONTENT_FLOW_OPTIMIZER_PROMPT = """
Review this assembled blog content and suggest improvements for better flow and coherence.

Title: {title}
Target Audience: {target_audience}
Tone: {tone}

Content:
{content}

Analyze the content for:
1. Logical flow between sections
2. Clarity and readability
3. Consistency in tone and style
4. Effective use of transitions
5. Overall coherence

Provide specific suggestions for improvement, focusing on:
- Where transitions could be smoother
- Sections that might need reordering
- Areas that feel disconnected
- Opportunities to strengthen the narrative flow

Be concise and actionable in your suggestions.
"""


def content_assembler_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Assemble all written sections into a cohesive blog post.
    
    This node:
    1. Combines introduction, body sections, and conclusion
    2. Generates smooth transitions between sections
    3. Optimizes content flow
    4. Creates the final assembled content
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with assembled content
    """
    
    logger.info("=" * 50)
    logger.info("STARTING CONTENT ASSEMBLY")
    logger.info("=" * 50)
    
    try:
        # Get all sections
        introduction = state.get('introduction', '')
        body_sections = state.get('body_sections', [])
        conclusion = state.get('conclusion', '')
        
        # Get metadata
        content_strategy = state.get('content_strategy', {})
        title_options = content_strategy.get('title_options', [])
        selected_title = title_options[0] if title_options else state.get('blog_idea', 'Blog Post')
        
        target_audience = state.get('target_audience', 'general')
        tone = state.get('tone', 'professional')
        
        logger.info(f"Assembling content with title: {selected_title}")
        logger.info(f"Sections to assemble: Introduction + {len(body_sections)} body sections + Conclusion")
        
        # Validate required sections
        if not introduction:
            logger.warning("No introduction found")
            add_warning(state, "Missing introduction section")
        
        if not body_sections:
            logger.error("No body sections found")
            add_error(state, "No body sections available for assembly")
            return state
            
        if not conclusion:
            logger.warning("No conclusion found")
            add_warning(state, "Missing conclusion section")
        
        # Sort body sections by index
        sorted_body_sections = sorted(
            [s for s in body_sections if isinstance(s, dict) and s.get('type') == 'body'],
            key=lambda x: x.get('section_index', 0)
        )
        
        logger.info(f"Sorted {len(sorted_body_sections)} body sections")
        
        # Assemble content with transitions
        assembled_content = assemble_content_with_transitions(
            selected_title,
            introduction,
            sorted_body_sections,
            conclusion,
            tone
        )
        
        # Calculate statistics
        total_word_count = len(assembled_content.split())
        
        # Analyze content flow
        flow_analysis = analyze_content_flow(
            assembled_content,
            selected_title,
            target_audience,
            tone
        )
        
        # Update state
        state['assembled_content'] = assembled_content
        
        # Add assembly statistics to debug info
        assembly_stats = {
            'sections_assembled': 1 + len(sorted_body_sections) + (1 if conclusion else 0),  # intro + body + conclusion
            'total_word_count': total_word_count,
            'introduction_included': bool(introduction),
            'body_sections_count': len(sorted_body_sections),
            'conclusion_included': bool(conclusion),
            'transitions_generated': len(sorted_body_sections) + (1 if conclusion else 0),  # Between sections
            'flow_analysis': flow_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        state['debug_info'].append({
            'node': 'content_assembler',
            'timestamp': datetime.now().isoformat(),
            'statistics': assembly_stats
        })
        
        logger.info(f"Content assembly complete:")
        logger.info(f"  - Total word count: {total_word_count}")
        logger.info(f"  - Sections assembled: {assembly_stats['sections_assembled']}")
        logger.info(f"  - Transitions generated: {assembly_stats['transitions_generated']}")
        
        # Update progress and set next step
        update_progress(state, 'content_enhancement', 0.65)
        state['current_step'] = 'internal_linking'
        
        return state
        
    except Exception as e:
        error_msg = f"Error in content assembly: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        return state


def assemble_content_with_transitions(
    title: str,
    introduction: str,
    body_sections: List[Dict[str, Any]],
    conclusion: str,
    tone: str
) -> str:
    """
    Assemble content with smooth transitions between sections.
    
    Args:
        title: Blog post title
        introduction: Introduction text
        body_sections: List of body section objects
        conclusion: Conclusion text
        tone: Writing tone for transitions
        
    Returns:
        Assembled content with transitions
    """
    
    logger.debug("Assembling content with transitions")
    
    content_parts = []
    
    # Add title
    content_parts.append(f"# {title}\n")
    
    # Add introduction
    if introduction:
        content_parts.append(introduction)
    
    # Add body sections with transitions
    for i, section in enumerate(body_sections):
        section_content = section.get('content', '')
        section_title = section.get('title', '')
        
        if not section_content:
            logger.warning(f"Empty content for body section {i}")
            continue
        
        # Generate transition from previous section
        if i == 0 and introduction:
            # Transition from introduction to first body section
            transition = generate_transition(
                get_text_ending(introduction),
                get_text_beginning(section_content),
                tone
            )
            if transition:
                content_parts.append(transition)
        elif i > 0:
            # Transition from previous body section
            previous_section = body_sections[i-1]
            previous_content = previous_section.get('content', '')
            transition = generate_transition(
                get_text_ending(previous_content),
                get_text_beginning(section_content),
                tone
            )
            if transition:
                content_parts.append(transition)
        
        # Add section header if it has a title
        if section_title:
            content_parts.append(f"\n## {section_title}\n")
        
        # Add section content
        content_parts.append(section_content)
    
    # Add transition to conclusion
    if conclusion and body_sections:
        last_section = body_sections[-1]
        last_content = last_section.get('content', '')
        transition = generate_transition(
            get_text_ending(last_content),
            get_text_beginning(conclusion),
            tone
        )
        if transition:
            content_parts.append(transition)
    
    # Add conclusion
    if conclusion:
        content_parts.append("\n## Conclusion\n")
        content_parts.append(conclusion)
    
    # Join all parts
    assembled = '\n\n'.join(content_parts)
    
    # Clean up extra whitespace
    assembled = clean_assembled_content(assembled)
    
    return assembled


def generate_transition(
    previous_ending: str,
    next_beginning: str,
    tone: str
) -> str:
    """
    Generate a smooth transition between two content sections.
    
    Args:
        previous_ending: Ending text of previous section
        next_beginning: Beginning text of next section
        tone: Writing tone
        
    Returns:
        Transition text or empty string if generation fails
    """
    
    if not previous_ending or not next_beginning:
        return ""
    
    try:
        prompt = TRANSITION_GENERATOR_PROMPT.format(
            previous_ending=previous_ending,
            next_beginning=next_beginning,
            tone=tone
        )
        
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.5,
                "max_output_tokens": 200
            }
        )
        
        transition = response.text.strip()
        
        # Validate transition (should be short)
        if len(transition.split()) > 50:  # Too long
            logger.warning("Generated transition too long, skipping")
            return ""
            
        return transition
        
    except Exception as e:
        logger.warning(f"Failed to generate transition: {str(e)}")
        return ""


def analyze_content_flow(
    content: str,
    title: str,
    target_audience: str,
    tone: str
) -> Dict[str, Any]:
    """
    Analyze the flow and coherence of assembled content.
    
    Args:
        content: Assembled content
        title: Blog title
        target_audience: Target audience
        tone: Writing tone
        
    Returns:
        Flow analysis results
    """
    
    try:
        prompt = CONTENT_FLOW_OPTIMIZER_PROMPT.format(
            title=title,
            target_audience=target_audience,
            tone=tone,
            content=content[:3000]  # Limit content to avoid token limits
        )
        
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.3,
                "max_output_tokens": 800
            }
        )
        
        suggestions = response.text.strip()
        
        return {
            'analysis_generated': True,
            'suggestions': suggestions,
            'content_length': len(content),
            'word_count': len(content.split()),
            'estimated_reading_time': estimate_reading_time(content)
        }
        
    except Exception as e:
        logger.warning(f"Failed to analyze content flow: {str(e)}")
        return {
            'analysis_generated': False,
            'error': str(e),
            'content_length': len(content),
            'word_count': len(content.split()),
            'estimated_reading_time': estimate_reading_time(content)
        }


def get_text_ending(text: str, words: int = 15) -> str:
    """Get the last N words of a text."""
    if not text:
        return ""
    
    words_list = text.split()
    if len(words_list) <= words:
        return text
    
    return ' '.join(words_list[-words:])


def get_text_beginning(text: str, words: int = 15) -> str:
    """Get the first N words of a text."""
    if not text:
        return ""
    
    words_list = text.split()
    if len(words_list) <= words:
        return text
    
    return ' '.join(words_list[:words])


def clean_assembled_content(content: str) -> str:
    """Clean up the assembled content."""
    
    # Remove excessive whitespace
    lines = content.split('\n')
    cleaned_lines = []
    
    previous_was_empty = False
    for line in lines:
        line = line.strip()
        
        # Skip multiple empty lines
        if not line:
            if not previous_was_empty:
                cleaned_lines.append('')
            previous_was_empty = True
        else:
            cleaned_lines.append(line)
            previous_was_empty = False
    
    return '\n'.join(cleaned_lines)


def estimate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes."""
    word_count = len(content.split())
    minutes = max(1, round(word_count / words_per_minute))
    return minutes 