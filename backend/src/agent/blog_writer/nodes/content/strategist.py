"""
Content Strategist Node

Creates comprehensive content strategy based on research findings, including:
- Optimized blog titles
- Detailed content outlines
- Keyword distribution planning
- Content structure and flow
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...schemas import ContentOutline
from ...prompts import CONTENT_STRATEGIST_PROMPT, get_current_date

# Set up logging
logger = logging.getLogger(__name__)


def content_strategist_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Create comprehensive content strategy based on research findings.
    
    This node:
    1. Analyzes research results from web and internal sources
    2. Generates optimized blog titles
    3. Creates detailed content outline
    4. Plans keyword distribution
    5. Suggests CTAs and content flow
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with content strategy
    """
    
    logger.info("=" * 50)
    logger.info("STARTING CONTENT STRATEGIST NODE")
    logger.info("=" * 50)
    
    try:
        # Get data from previous nodes
        topic_analysis = state.get('topic_analysis', {})
        research_summary = state.get('research_summary', {})
        internal_matches = state.get('internal_content_matches', [])
        target_keywords = state.get('target_keywords', [])
        target_audience = state.get('target_audience', 'general')
        tone = state.get('tone', 'professional')
        length = state.get('length', 'medium')
        
        # Validate inputs
        if not topic_analysis or not research_summary:
            error_msg = "Missing topic analysis or research summary for content strategy"
            logger.error(error_msg)
            add_error(state, error_msg)
            state['current_step'] = 'failed'
            return state
            
        main_topic = topic_analysis.get('main_topic', '')
        logger.info(f"Creating content strategy for: {main_topic}")
        logger.info(f"Target audience: {target_audience}")
        logger.info(f"Tone: {tone}")
        logger.info(f"Length: {length}")
        
        # Calculate target word count based on length
        word_count_map = {
            'short': 800,
            'medium': 1500,
            'long': 2500
        }
        target_word_count = word_count_map.get(length, 1500)
        
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.4,  # Slightly higher for creativity in content strategy
            max_retries=2,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        # Prepare research summary for the prompt
        research_summary_text = _prepare_research_summary(research_summary, internal_matches)
        
        # Format the content strategy prompt
        formatted_prompt = CONTENT_STRATEGIST_PROMPT.format(
            research_summary=research_summary_text,
            target_audience=target_audience,
            tone=tone,
            length=length,
            word_count=target_word_count
        )
        
        logger.debug("Sending request to Gemini for content strategy...")
        
        try:
            # Get content strategy using regular invoke (not structured for more flexibility)
            response = llm.invoke(formatted_prompt)
            strategy_content = response.content if hasattr(response, 'content') else str(response)
            
            logger.debug(f"Received content strategy: {strategy_content[:200]}...")
            
        except Exception as e:
            error_msg = f"Failed to get content strategy from LLM: {str(e)}"
            logger.error(error_msg)
            add_error(state, error_msg, {'llm_error': str(e)})
            state['current_step'] = 'failed'
            return state
        
        # Parse the content strategy response
        parsed_strategy = _parse_content_strategy(strategy_content, target_word_count)
        
        # Generate additional strategic elements
        keyword_strategy = _create_keyword_strategy(target_keywords, parsed_strategy['outline'])
        content_flow = _analyze_content_flow(parsed_strategy['outline'])
        
        # Create comprehensive content strategy
        content_strategy = {
            'title_options': parsed_strategy['title_options'],
            'selected_title': parsed_strategy['title_options'][0] if parsed_strategy['title_options'] else main_topic,
            'outline': parsed_strategy['outline'],
            'key_messages': parsed_strategy['key_messages'],
            'cta_suggestions': parsed_strategy['cta_suggestions'],
            'target_word_count': target_word_count,
            'keyword_strategy': keyword_strategy,
            'content_flow': content_flow,
            'audience_considerations': _extract_audience_considerations(topic_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
        # Update state with content strategy
        state['content_strategy'] = content_strategy
        state['title_options'] = parsed_strategy['title_options']
        state['outline'] = parsed_strategy['outline']
        state['key_messages'] = parsed_strategy['key_messages']
        state['cta_suggestions'] = parsed_strategy['cta_suggestions']
        
        # Add debug info
        state['debug_info'].append({
            'node': 'content_strategist',
            'timestamp': datetime.now().isoformat(),
            'strategy': {
                'title_count': len(parsed_strategy['title_options']),
                'section_count': len(parsed_strategy['outline'].get('sections', [])),
                'target_words': target_word_count,
                'keyword_count': len(keyword_strategy.get('primary_placements', []))
            }
        })
        
        # Log strategy details
        logger.info(f"Content strategy created:")
        logger.info(f"  - Generated {len(parsed_strategy['title_options'])} title options")
        logger.info(f"  - Created outline with {len(parsed_strategy['outline'].get('sections', []))} sections")
        logger.info(f"  - Target word count: {target_word_count}")
        logger.info(f"  - Key messages: {len(parsed_strategy['key_messages'])}")
        logger.info(f"  - CTA options: {len(parsed_strategy['cta_suggestions'])}")
        
        # Log selected title and top sections
        logger.info(f"Selected title: {content_strategy['selected_title']}")
        outline_sections = parsed_strategy['outline'].get('sections', [])
        if outline_sections:
            logger.debug("Top content sections:")
            for i, section in enumerate(outline_sections[:3]):
                section_title = section.get('title', f'Section {i+1}')
                logger.debug(f"  {i+1}. {section_title}")
        
        # Update progress and next step
        update_progress(state, 'content_creation', 0.7)
        
        logger.info("CONTENT STRATEGIST COMPLETED SUCCESSFULLY")
        logger.info(f"Next step: {state['current_step']}")
        
        return state
        
    except Exception as e:
        error_msg = f"Unexpected error in content strategist: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg, {'exception': str(e), 'type': type(e).__name__})
        state['current_step'] = 'failed'
        return state


def _prepare_research_summary(research_summary: Dict[str, Any], internal_matches: List[Dict[str, Any]]) -> str:
    """Prepare a comprehensive research summary for the content strategy prompt"""
    
    summary_parts = []
    
    # Web research summary
    if 'key_insights' in research_summary:
        insights = research_summary['key_insights'][:10]  # Top 10 insights
        summary_parts.append("**Key Research Insights:**")
        for i, insight in enumerate(insights, 1):
            summary_parts.append(f"{i}. {insight}")
    
    # Sources summary
    if 'sources' in research_summary:
        sources = research_summary['sources'][:5]  # Top 5 sources
        summary_parts.append("\n**Authoritative Sources:**")
        for source in sources:
            title = source.get('title', 'Unknown')
            snippet = source.get('snippet', '')[:100]
            summary_parts.append(f"- {title}: {snippet}...")
    
    # Internal content summary
    if internal_matches:
        summary_parts.append("\n**Related Internal Content:**")
        for match in internal_matches[:3]:  # Top 3 matches
            title = match.get('title', 'Unknown')
            category = match.get('category', '')
            summary_parts.append(f"- {title} ({category})")
    
    # Research statistics
    if research_summary:
        summary_parts.append(f"\n**Research Statistics:**")
        summary_parts.append(f"- Web sources found: {research_summary.get('unique_sources', 0)}")
        summary_parts.append(f"- Internal matches: {len(internal_matches)}")
        
        if 'internal_research' in research_summary:
            internal_stats = research_summary['internal_research']
            coverage_score = internal_stats.get('content_coverage', {}).get('coverage_score', 0)
            summary_parts.append(f"- Content coverage score: {coverage_score:.1%}")
    
    return "\n".join(summary_parts)


def _parse_content_strategy(strategy_content: str, target_word_count: int) -> Dict[str, Any]:
    """Parse the LLM response to extract structured content strategy"""
    
    # Initialize default structure
    parsed = {
        'title_options': [],
        'outline': {'sections': []},
        'key_messages': [],
        'cta_suggestions': []
    }
    
    # Split content into sections
    sections = strategy_content.split('\n\n')
    
    current_section = None
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Identify section type
        section_lower = section.lower()
        
        if 'title' in section_lower and ('option' in section_lower or 'suggestion' in section_lower):
            current_section = 'titles'
            # Extract titles from this section
            titles = _extract_list_items(section)
            parsed['title_options'].extend(titles)
            
        elif 'outline' in section_lower or 'structure' in section_lower:
            current_section = 'outline'
            # Parse outline structure
            outline_sections = _parse_outline_section(section, target_word_count)
            parsed['outline']['sections'] = outline_sections
            
        elif 'key message' in section_lower or 'takeaway' in section_lower:
            current_section = 'messages'
            messages = _extract_list_items(section)
            parsed['key_messages'].extend(messages)
            
        elif 'cta' in section_lower or 'call-to-action' in section_lower or 'call to action' in section_lower:
            current_section = 'ctas'
            ctas = _extract_list_items(section)
            parsed['cta_suggestions'].extend(ctas)
            
        else:
            # Continue parsing based on current section
            if current_section == 'titles':
                titles = _extract_list_items(section)
                parsed['title_options'].extend(titles)
            elif current_section == 'messages':
                messages = _extract_list_items(section)
                parsed['key_messages'].extend(messages)
            elif current_section == 'ctas':
                ctas = _extract_list_items(section)
                parsed['cta_suggestions'].extend(ctas)
    
    # Ensure we have fallbacks if parsing failed
    if not parsed['title_options']:
        parsed['title_options'] = ['Complete Guide to the Topic', 'Best Practices and Tips', 'Everything You Need to Know']
    
    if not parsed['outline']['sections']:
        parsed['outline']['sections'] = _create_default_outline(target_word_count)
    
    if not parsed['key_messages']:
        parsed['key_messages'] = ['Provide comprehensive information', 'Share practical insights', 'Guide readers to action']
    
    if not parsed['cta_suggestions']:
        parsed['cta_suggestions'] = ['Learn more about this topic', 'Get started with implementation', 'Share your experience']
    
    return parsed


def _extract_list_items(text: str) -> List[str]:
    """Extract list items from text (numbered or bulleted)"""
    
    items = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Remove list markers
        cleaned = line
        
        # Remove numbered markers (1., 2., etc.)
        if line and line[0].isdigit() and '.' in line[:5]:
            parts = line.split('.', 1)
            if len(parts) > 1:
                cleaned = parts[1].strip()
        
        # Remove bullet markers (-, *, •)
        elif line.startswith(('-', '*', '•')):
            cleaned = line[1:].strip()
        
        # Remove markdown emphasis
        cleaned = cleaned.replace('**', '').replace('*', '').replace('_', '')
        
        if cleaned and len(cleaned) > 5:  # Only keep meaningful items
            items.append(cleaned)
    
    return items


def _parse_outline_section(text: str, target_word_count: int) -> List[Dict[str, Any]]:
    """Parse outline section into structured format"""
    
    sections = []
    lines = text.split('\n')
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a main section (numbered or marked)
        is_main_section = (
            (line[0].isdigit() and '.' in line[:5]) or
            line.startswith(('**', '##', '#')) or
            line.startswith(('-', '*')) and len(line) > 20
        )
        
        if is_main_section:
            # Save previous section
            if current_section:
                sections.append(current_section)
            
            # Start new section
            title = line
            # Clean up title
            for marker in ['**', '##', '#', '-', '*']:
                title = title.replace(marker, '')
            
            # Remove numbering
            if title and title[0].isdigit() and '.' in title[:5]:
                parts = title.split('.', 1)
                if len(parts) > 1:
                    title = parts[1].strip()
            
            title = title.strip()
            
            current_section = {
                'title': title,
                'content_points': [],
                'target_words': target_word_count // 5,  # Rough estimate
                'type': 'body'
            }
        
        else:
            # This is a sub-point
            if current_section and line:
                # Clean up sub-point
                cleaned = line.replace('-', '').replace('*', '').replace('•', '').strip()
                if cleaned:
                    current_section['content_points'].append(cleaned)
    
    # Add the last section
    if current_section:
        sections.append(current_section)
    
    return sections if sections else _create_default_outline(target_word_count)


def _create_default_outline(target_word_count: int) -> List[Dict[str, Any]]:
    """Create a default outline structure"""
    
    section_count = max(3, min(8, target_word_count // 200))  # 3-8 sections based on length
    words_per_section = target_word_count // section_count
    
    return [
        {
            'title': 'Introduction',
            'content_points': ['Hook the reader', 'Present the problem', 'Preview the solution'],
            'target_words': words_per_section,
            'type': 'introduction'
        },
        {
            'title': 'Main Concept Overview',
            'content_points': ['Define key terms', 'Explain the fundamentals', 'Provide context'],
            'target_words': words_per_section,
            'type': 'body'
        },
        {
            'title': 'Practical Applications',
            'content_points': ['Real-world examples', 'Step-by-step guidance', 'Best practices'],
            'target_words': words_per_section,
            'type': 'body'
        },
        {
            'title': 'Conclusion',
            'content_points': ['Summarize key points', 'Reinforce value', 'Call to action'],
            'target_words': words_per_section,
            'type': 'conclusion'
        }
    ]


def _create_keyword_strategy(target_keywords: List[str], outline: Dict[str, Any]) -> Dict[str, Any]:
    """Create keyword distribution strategy across content sections"""
    
    if not target_keywords:
        return {'primary_placements': [], 'secondary_placements': [], 'density_target': 0.02}
    
    primary_keyword = target_keywords[0] if target_keywords else ''
    secondary_keywords = target_keywords[1:5] if len(target_keywords) > 1 else []
    
    sections = outline.get('sections', [])
    
    # Plan keyword placement
    placements = []
    
    for i, section in enumerate(sections):
        section_title = section.get('title', f'Section {i+1}')
        
        # Primary keyword in first and last sections
        if i == 0 or i == len(sections) - 1:
            placements.append({
                'section': section_title,
                'keywords': [primary_keyword],
                'placement': 'title_and_content',
                'density': 0.03
            })
        else:
            # Secondary keywords in middle sections
            keyword_for_section = secondary_keywords[i % len(secondary_keywords)] if secondary_keywords else primary_keyword
            placements.append({
                'section': section_title,
                'keywords': [keyword_for_section],
                'placement': 'content',
                'density': 0.02
            })
    
    return {
        'primary_keyword': primary_keyword,
        'secondary_keywords': secondary_keywords,
        'primary_placements': placements,
        'density_target': 0.02,
        'meta_keywords': target_keywords[:5]
    }


def _analyze_content_flow(outline: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze and optimize content flow"""
    
    sections = outline.get('sections', [])
    
    flow_analysis = {
        'section_count': len(sections),
        'estimated_reading_time': sum(section.get('target_words', 200) for section in sections) // 200,  # ~200 words per minute
        'content_progression': [],
        'transition_suggestions': []
    }
    
    # Analyze progression
    for i, section in enumerate(sections):
        section_type = section.get('type', 'body')
        progression_item = {
            'section': section.get('title', f'Section {i+1}'),
            'type': section_type,
            'purpose': _get_section_purpose(section_type, i, len(sections))
        }
        flow_analysis['content_progression'].append(progression_item)
        
        # Suggest transitions
        if i < len(sections) - 1:
            next_section = sections[i + 1]
            transition = f"Transition from {section.get('title', 'current section')} to {next_section.get('title', 'next section')}"
            flow_analysis['transition_suggestions'].append(transition)
    
    return flow_analysis


def _get_section_purpose(section_type: str, index: int, total_sections: int) -> str:
    """Get the purpose of a section based on its type and position"""
    
    if section_type == 'introduction' or index == 0:
        return 'Hook readers and introduce the topic'
    elif section_type == 'conclusion' or index == total_sections - 1:
        return 'Summarize and drive action'
    else:
        return 'Provide detailed information and value'


def _extract_audience_considerations(topic_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Extract audience considerations from topic analysis"""
    
    audience_insights = topic_analysis.get('audience_insights', {})
    
    if isinstance(audience_insights, str):
        # If it's a string, create a basic structure
        return {
            'pain_points': audience_insights,
            'content_approach': 'Address reader needs directly',
            'tone_considerations': 'Match expertise level'
        }
    
    return {
        'pain_points': audience_insights.get('pain_points', 'Unknown pain points'),
        'solutions_seeking': audience_insights.get('solutions_seeking', 'Practical guidance'),
        'detail_level': audience_insights.get('detail_level', 'Appropriate depth'),
        'desired_action': audience_insights.get('desired_action', 'Apply learnings'),
        'content_approach': 'Focus on practical value and clear guidance',
        'tone_considerations': 'Professional yet accessible'
    } 