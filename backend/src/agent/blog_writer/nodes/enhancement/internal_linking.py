"""
Internal Linking Node

Identifies and adds internal links to the assembled blog content based on:
- Existing content database matches
- Contextual relevance analysis
- Strategic anchor text placement
"""

import os
import logging
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from google.genai import Client

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...schemas import InternalLink
from ...tools.content_db import content_db
from ...prompts import get_current_date

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")

genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))


INTERNAL_LINKING_ANALYSIS_PROMPT = """
Analyze this blog content and identify optimal placement for internal links.

Blog Content:
{content}

Available Internal Content:
{available_content}

Current Date: {current_date}

Your task:
1. Identify 3-7 strategic locations in the blog where internal links would add value
2. For each location, specify:
   - The exact text to link (anchor text)
   - Which internal content to link to
   - Why this link adds value to the reader
   - The paragraph/section where it should be placed

Criteria for good internal linking:
- Links should be contextually relevant and helpful
- Anchor text should be natural and descriptive
- Avoid over-linking (max 1-2 links per 150 words)
- Links should enhance user experience, not distract
- Target authoritative internal content that provides additional value

Respond with a JSON object containing:
{{
    "internal_links": [
        {{
            "anchor_text": "exact text to link",
            "target_content_id": "content_id",
            "target_title": "title of target content",
            "target_url": "relative URL path",
            "placement_context": "surrounding paragraph text for context",
            "value_proposition": "why this link helps the reader",
            "section_type": "introduction|body|conclusion",
            "priority": 1
        }}
    ],
    "linking_strategy": "overall approach explanation",
    "total_links_recommended": 0
}}
"""

ANCHOR_TEXT_OPTIMIZER_PROMPT = """
Optimize the anchor text for internal links to be more natural and SEO-friendly.

Current anchor text: {current_anchor}
Target content title: {target_title}
Context paragraph: {context}
Main topic: {main_topic}

Create 2-3 alternative anchor text options that:
- Sound natural in the context
- Are descriptive and clickable  
- Include relevant keywords when appropriate
- Are 2-6 words long ideally
- Match the tone: {tone}

Respond with a JSON object:
{{
    "optimized_options": [
        "option 1",
        "option 2", 
        "option 3"
    ],
    "recommended": "best option",
    "reasoning": "why this option is best"
}}
"""


def internal_linking_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Add strategic internal links to the assembled blog content.
    
    This node:
    1. Analyzes the assembled content for linking opportunities
    2. Identifies relevant internal content from the database
    3. Determines optimal anchor text and placement
    4. Inserts links into the content
    5. Tracks linking statistics
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with internal links added
    """
    
    logger.info("=" * 50)
    logger.info("STARTING INTERNAL LINKING")
    logger.info("=" * 50)
    
    try:
        # Ensure internal_links field exists and is properly initialized
        if 'internal_links' not in state:
            state['internal_links'] = []
            logger.info("Initialized internal_links field in state")
            
        # Ensure debug_info field exists
        if 'debug_info' not in state:
            state['debug_info'] = []
            logger.info("Initialized debug_info field in state")
        
        # Get assembled content
        assembled_content = state.get('assembled_content', '')
        if not assembled_content:
            logger.warning("No assembled content found for internal linking")
            add_warning(state, "No assembled content available for internal linking")
            # Set content_with_links to assembled_content even if empty, and continue workflow
            state['content_with_links'] = assembled_content
            state['current_step'] = 'external_linking'
            return state
        
        # Get existing internal content matches
        internal_content_matches = state.get('internal_content_matches', [])
        
        # Get additional context
        topic_analysis = state.get('topic_analysis', {})
        main_topic = topic_analysis.get('main_topic', '')
        tone = state.get('tone', 'professional')
        
        logger.info(f"Analyzing content for internal links")
        logger.info(f"Content length: {len(assembled_content)} characters")
        logger.info(f"Available internal content: {len(internal_content_matches)} pieces")
        
        # If no internal content is available, skip linking but continue workflow
        if not internal_content_matches:
            logger.info("No internal content matches available for linking")
            state['content_with_links'] = assembled_content
            state['internal_links'] = []
            state['current_step'] = 'external_linking'
            return state
        
        # Analyze content for linking opportunities
        linking_analysis = analyze_internal_linking_opportunities(
            assembled_content,
            internal_content_matches,
            main_topic,
            tone
        )
        
        if not linking_analysis or not linking_analysis.get('internal_links'):
            logger.info("No internal linking opportunities identified")
            state['content_with_links'] = assembled_content
            state['internal_links'] = []
            state['current_step'] = 'external_linking'
            return state
        
        # Process and optimize links
        optimized_links = []
        for link_data in linking_analysis['internal_links']:
            try:
                optimized_link = optimize_internal_link(
                    link_data,
                    assembled_content,
                    main_topic,
                    tone
                )
                if optimized_link:
                    optimized_links.append(optimized_link)
            except Exception as e:
                logger.warning(f"Failed to optimize link: {str(e)}")
                continue
        
        # Sort links by priority and remove duplicates
        optimized_links = deduplicate_and_prioritize_links(optimized_links)
        
        # Insert links into content
        content_with_links = insert_internal_links(assembled_content, optimized_links)
        
        # Create InternalLink objects for state
        internal_link_objects = []
        for link in optimized_links:
            internal_link_objects.append({
                'anchor_text': link['anchor_text'],
                'target_url': link['target_url'],
                'target_title': link['target_title'],
                'section_type': link.get('section_type', 'body'),
                'value_proposition': link.get('value_proposition', ''),
                'inserted': link.get('inserted', False)
            })
        
        # Update state with defensive checks
        state['content_with_links'] = content_with_links
        state['internal_links'] = internal_link_objects
        
        # Add linking statistics to debug info
        linking_stats = {
            'links_identified': len(linking_analysis['internal_links']),
            'links_optimized': len(optimized_links),
            'links_inserted': sum(1 for link in optimized_links if link.get('inserted', False)),
            'content_length_before': len(assembled_content),
            'content_length_after': len(content_with_links),
            'linking_strategy': linking_analysis.get('linking_strategy', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        # Ensure debug_info exists before appending
        if 'debug_info' not in state:
            state['debug_info'] = []
            
        state['debug_info'].append({
            'node': 'internal_linking',
            'timestamp': datetime.now().isoformat(),
            'statistics': linking_stats
        })
        
        logger.info(f"Internal linking complete:")
        logger.info(f"  - Links identified: {linking_stats['links_identified']}")
        logger.info(f"  - Links optimized: {linking_stats['links_optimized']}")
        logger.info(f"  - Links inserted: {linking_stats['links_inserted']}")
        
        # Update progress and set next step
        update_progress(state, 'enhancement', 0.7)
        state['current_step'] = 'external_linking'
        
        logger.info("Internal linking node completed successfully")
        
        return state
        
    except Exception as e:
        error_msg = f"Error in internal linking: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        
        # Ensure internal_links field exists even on error
        if 'internal_links' not in state:
            state['internal_links'] = []
            
        # Ensure content_with_links is set to continue workflow
        assembled_content = state.get('assembled_content', '')
        state['content_with_links'] = assembled_content
        
        # Set next step to continue workflow even on error
        state['current_step'] = 'external_linking'
        
        logger.info("Internal linking failed but workflow will continue")
        
        return state


def analyze_internal_linking_opportunities(
    content: str,
    internal_content: List[Dict[str, Any]],
    main_topic: str,
    tone: str
) -> Dict[str, Any]:
    """
    Analyze content for internal linking opportunities using AI.
    
    Args:
        content: Blog content to analyze
        internal_content: Available internal content for linking
        main_topic: Main topic of the blog
        tone: Writing tone
        
    Returns:
        Dictionary with linking analysis and recommendations
    """
    
    try:
        # Prepare available content summary
        available_content_summary = []
        for item in internal_content[:10]:  # Limit to top 10 for prompt size
            available_content_summary.append({
                'id': item.get('id', ''),
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'category': item.get('category', ''),
                'relevance_score': item.get('relevance_score', 0),
                'summary': item.get('content', '')[:200] + '...' if item.get('content') else ''
            })
        
        # Generate linking analysis
        prompt = INTERNAL_LINKING_ANALYSIS_PROMPT.format(
            content=content[:4000],  # Limit content length for prompt
            available_content=str(available_content_summary),
            current_date=get_current_date()
        )
        
        # Use structured output for reliable parsing
        model = genai_client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={'temperature': 0.3, 'max_output_tokens': 2000}
        )
        
        response_text = model.text.strip()
        logger.debug(f"Linking analysis response: {response_text[:500]}...")
        
        # Parse the response
        linking_analysis = parse_linking_analysis_response(response_text)
        
        return linking_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing internal linking opportunities: {str(e)}")
        return {}


def optimize_internal_link(
    link_data: Dict[str, Any],
    content: str,
    main_topic: str,
    tone: str
) -> Dict[str, Any]:
    """
    Optimize anchor text and placement for an internal link.
    
    Args:
        link_data: Original link data from analysis
        content: Full blog content
        main_topic: Main topic for context
        tone: Writing tone
        
    Returns:
        Optimized link data
    """
    
    try:
        current_anchor = link_data.get('anchor_text', '')
        target_title = link_data.get('target_title', '')
        context = link_data.get('placement_context', '')
        
        # Generate optimized anchor text options
        prompt = ANCHOR_TEXT_OPTIMIZER_PROMPT.format(
            current_anchor=current_anchor,
            target_title=target_title,
            context=context,
            main_topic=main_topic,
            tone=tone
        )
        
        model = genai_client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={'temperature': 0.3, 'max_output_tokens': 500}
        )
        
        response_text = model.text.strip()
        
        # Parse optimization response
        optimization_result = parse_anchor_optimization_response(response_text)
        
        # Update link data with optimized anchor text
        optimized_link = link_data.copy()
        if optimization_result.get('recommended'):
            optimized_link['anchor_text'] = optimization_result['recommended']
            optimized_link['optimization_reasoning'] = optimization_result.get('reasoning', '')
            optimized_link['alternative_anchors'] = optimization_result.get('optimized_options', [])
        
        return optimized_link
        
    except Exception as e:
        logger.warning(f"Error optimizing anchor text: {str(e)}")
        return link_data


def insert_internal_links(content: str, links: List[Dict[str, Any]]) -> str:
    """
    Insert internal links into the content.
    
    Args:
        content: Original blog content
        links: List of optimized link data
        
    Returns:
        Content with internal links inserted
    """
    
    try:
        modified_content = content
        links_inserted = 0
        
        # Sort links by position (if available) or priority
        sorted_links = sorted(links, key=lambda x: x.get('priority', 5))
        
        for link in sorted_links:
            anchor_text = link.get('anchor_text', '')
            target_url = link.get('target_url', '')
            target_title = link.get('target_title', '')
            
            if not anchor_text or not target_url:
                continue
            
            # Create markdown link
            markdown_link = f"[{anchor_text}]({target_url} \"{target_title}\")"
            
            # Find the anchor text in content (case-insensitive, whole word)
            pattern = r'\b' + re.escape(anchor_text) + r'\b'
            
            if re.search(pattern, modified_content, re.IGNORECASE):
                # Replace first occurrence only
                modified_content = re.sub(
                    pattern, 
                    markdown_link, 
                    modified_content, 
                    count=1, 
                    flags=re.IGNORECASE
                )
                link['inserted'] = True
                links_inserted += 1
                
                logger.debug(f"Inserted link: {anchor_text} -> {target_url}")
            else:
                logger.warning(f"Could not find anchor text in content: {anchor_text}")
                link['inserted'] = False
        
        logger.info(f"Inserted {links_inserted} internal links into content")
        
        return modified_content
        
    except Exception as e:
        logger.error(f"Error inserting internal links: {str(e)}")
        return content


def deduplicate_and_prioritize_links(links: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate links and prioritize the best ones.
    
    Args:
        links: List of link data
        
    Returns:
        Deduplicated and prioritized links
    """
    
    # Remove duplicates based on anchor text
    seen_anchors = set()
    unique_links = []
    
    for link in links:
        anchor_text = link.get('anchor_text', '').lower()
        if anchor_text not in seen_anchors:
            seen_anchors.add(anchor_text)
            unique_links.append(link)
    
    # Sort by priority (lower number = higher priority)
    prioritized_links = sorted(unique_links, key=lambda x: x.get('priority', 5))
    
    # Limit to top 7 links to avoid over-linking
    return prioritized_links[:7]


def parse_linking_analysis_response(response_text: str) -> Dict[str, Any]:
    """Parse the AI response for linking analysis."""
    
    try:
        import json
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            logger.warning("No JSON found in linking analysis response")
            return {}
            
    except Exception as e:
        logger.error(f"Error parsing linking analysis response: {str(e)}")
        return {}


def parse_anchor_optimization_response(response_text: str) -> Dict[str, Any]:
    """Parse the AI response for anchor text optimization."""
    
    try:
        import json
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            logger.warning("No JSON found in anchor optimization response")
            return {'recommended': '', 'reasoning': '', 'optimized_options': []}
            
    except Exception as e:
        logger.error(f"Error parsing anchor optimization response: {str(e)}")
        return {'recommended': '', 'reasoning': '', 'optimized_options': []} 