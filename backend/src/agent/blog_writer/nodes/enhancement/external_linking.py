"""
External Linking Node

Identifies and adds strategic external links to the blog content for:
- Supporting claims with authoritative sources
- Providing additional value to readers
- Enhancing credibility and trustworthiness
- Following SEO best practices
"""

import os
import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from google.genai import Client

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...schemas import ExternalLink
from ...prompts import get_current_date

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")

genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))


EXTERNAL_LINKING_ANALYSIS_PROMPT = """
Analyze this blog content and identify where external links would add credibility and value.

Blog Content:
{content}

Research Sources Found:
{research_sources}

Topic: {main_topic}
Target Audience: {target_audience}
Current Date: {current_date}

Your task:
1. Identify 2-5 strategic locations where external links would:
   - Support factual claims or statistics
   - Provide authoritative sources
   - Offer additional valuable resources
   - Enhance credibility without directing traffic away unnecessarily

2. For each external link opportunity, specify:
   - The claim or statement that needs support
   - The type of external source needed (research, authority site, tool, etc.)
   - Suggested anchor text
   - Why this link adds value

Guidelines for external linking:
- Link to high-authority, reputable sources
- Support claims with data or research
- Use descriptive, natural anchor text
- Open external links in new tabs
- Limit to 2-5 high-value external links
- Avoid competitor links unless necessary for comparison

Respond with a JSON object:
{{
    "external_links": [
        {{
            "anchor_text": "text to link",
            "claim_being_supported": "the statement or claim",
            "source_type": "research|authority|tool|government|academic",
            "suggested_domain": "example.com (if you have a specific suggestion)",
            "value_proposition": "why this external link helps",
            "section_type": "introduction|body|conclusion",
            "priority": 1,
            "opens_new_tab": true
        }}
    ],
    "linking_strategy": "overall external linking approach",
    "total_external_links": 0
}}
"""

EXTERNAL_SOURCE_VALIDATION_PROMPT = """
Evaluate if these suggested external links are appropriate and valuable for this blog post.

Blog Topic: {main_topic}
Target Audience: {target_audience}

Suggested External Links:
{external_links}

For each link, evaluate:
1. Relevance to the content
2. Authority and credibility of the suggested domain
3. Value to the target audience
4. SEO impact (positive/neutral/negative)

Respond with a JSON object:
{{
    "validated_links": [
        {{
            "anchor_text": "validated anchor text",
            "claim_being_supported": "the claim",
            "source_type": "research|authority|tool|government|academic",
            "value_score": 1,
            "keep_link": true,
            "validation_notes": "why this link is good/bad"
        }}
    ],
    "overall_assessment": "quality assessment of the external linking strategy"
}}
"""


def external_linking_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Add strategic external links to enhance content credibility and value.
    
    This node:
    1. Analyzes content for claims that need external support
    2. Identifies appropriate external link opportunities
    3. Validates suggested external sources
    4. Inserts high-quality external links
    5. Tracks external linking statistics
    
    Args:
        state: Current blog writer state with linked content
        config: LangGraph configuration
        
    Returns:
        Updated state with external links added
    """
    
    logger.info("=" * 50)
    logger.info("STARTING EXTERNAL LINKING")
    logger.info("=" * 50)
    
    try:
        # Get content with internal links
        content_with_links = state.get('content_with_links')
        if not content_with_links:
            # Fall back to assembled content if no internal links were added
            content_with_links = state.get('assembled_content', '')
        
        if not content_with_links:
            logger.warning("No content found for external linking")
            add_warning(state, "No content available for external linking")
            return state
        
        # Get research context and metadata
        research_summary = state.get('research_summary', {})
        web_research_results = state.get('web_research_results', [])
        topic_analysis = state.get('topic_analysis', {})
        main_topic = topic_analysis.get('main_topic', '')
        target_audience = state.get('target_audience', 'general')
        
        logger.info(f"Analyzing content for external links")
        logger.info(f"Content length: {len(content_with_links)} characters")
        logger.info(f"Research sources available: {len(web_research_results)}")
        
        # Analyze content for external linking opportunities
        external_linking_analysis = analyze_external_linking_opportunities(
            content_with_links,
            web_research_results,
            main_topic,
            target_audience
        )
        
        if not external_linking_analysis or not external_linking_analysis.get('external_links'):
            logger.info("No external linking opportunities identified")
            state['external_links'] = []
            return state
        
        # Validate suggested external links
        validated_links = validate_external_links(
            external_linking_analysis['external_links'],
            main_topic,
            target_audience
        )
        
        # Insert external links into content
        content_with_external_links = insert_external_links(content_with_links, validated_links)
        
        # Create ExternalLink objects for state
        external_link_objects = []
        for link in validated_links:
            if link.get('keep_link', True):
                external_link_objects.append({
                    'anchor_text': link['anchor_text'],
                    'target_url': link.get('target_url', '#'),  # Placeholder URL
                    'source_type': link.get('source_type', 'authority'),
                    'claim_supported': link.get('claim_being_supported', ''),
                    'opens_new_tab': link.get('opens_new_tab', True),
                    'value_score': link.get('value_score', 3),
                    'inserted': link.get('inserted', False)
                })
        
        # Update state
        state['content_with_links'] = content_with_external_links
        state['external_links'] = external_link_objects
        
        # Add external linking statistics to debug info
        external_linking_stats = {
            'links_identified': len(external_linking_analysis['external_links']),
            'links_validated': len(validated_links),
            'links_inserted': sum(1 for link in validated_links if link.get('inserted', False)),
            'high_value_links': sum(1 for link in validated_links if link.get('value_score', 0) >= 4),
            'content_length_before': len(content_with_links),
            'content_length_after': len(content_with_external_links),
            'linking_strategy': external_linking_analysis.get('linking_strategy', ''),
            'timestamp': datetime.now().isoformat()
        }
        
        state['debug_info'].append({
            'node': 'external_linking',
            'timestamp': datetime.now().isoformat(),
            'statistics': external_linking_stats
        })
        
        logger.info(f"External linking complete:")
        logger.info(f"  - Links identified: {external_linking_stats['links_identified']}")
        logger.info(f"  - Links validated: {external_linking_stats['links_validated']}")
        logger.info(f"  - Links inserted: {external_linking_stats['links_inserted']}")
        logger.info(f"  - High-value links: {external_linking_stats['high_value_links']}")
        
        # Update progress and set next step  
        update_progress(state, 'enhancement', 0.8)
        state['current_step'] = 'final_output'
        
        return state
        
    except Exception as e:
        error_msg = f"Error in external linking: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        return state


def analyze_external_linking_opportunities(
    content: str,
    research_sources: List[Dict[str, Any]],
    main_topic: str,
    target_audience: str
) -> Dict[str, Any]:
    """
    Analyze content for external linking opportunities using AI.
    
    Args:
        content: Blog content to analyze
        research_sources: Available research sources from web research
        main_topic: Main topic of the blog
        target_audience: Target audience
        
    Returns:
        Dictionary with external linking analysis and recommendations
    """
    
    try:
        # Prepare research sources summary
        research_sources_summary = []
        for source in research_sources[:10]:  # Limit for prompt size
            research_sources_summary.append({
                'title': source.get('title', ''),
                'url': source.get('url', ''),
                'domain': extract_domain_from_url(source.get('url', '')),
                'snippet': source.get('snippet', '')[:150] + '...' if source.get('snippet') else '',
                'relevance_score': source.get('relevance_score', 0)
            })
        
        # Generate external linking analysis
        prompt = EXTERNAL_LINKING_ANALYSIS_PROMPT.format(
            content=content[:4000],  # Limit content length for prompt
            research_sources=str(research_sources_summary),
            main_topic=main_topic,
            target_audience=target_audience,
            current_date=get_current_date()
        )
        
        # Use AI to identify external linking opportunities
        model = genai_client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={'temperature': 0.3, 'max_output_tokens': 2000}
        )
        
        response_text = model.text.strip()
        logger.debug(f"External linking analysis response: {response_text[:500]}...")
        
        # Parse the response
        external_linking_analysis = parse_external_linking_response(response_text)
        
        return external_linking_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing external linking opportunities: {str(e)}")
        return {}


def validate_external_links(
    external_links: List[Dict[str, Any]],
    main_topic: str,
    target_audience: str
) -> List[Dict[str, Any]]:
    """
    Validate suggested external links for quality and appropriateness.
    
    Args:
        external_links: List of suggested external links
        main_topic: Main topic for context
        target_audience: Target audience
        
    Returns:
        List of validated external links
    """
    
    try:
        # For now, implement basic validation
        # This could be enhanced with actual URL checking and domain authority verification
        
        validated_links = []
        for link in external_links:
            # Basic validation criteria
            anchor_text = link.get('anchor_text', '')
            claim_supported = link.get('claim_being_supported', '')
            source_type = link.get('source_type', '')
            
            # Simple validation logic
            keep_link = (
                len(anchor_text) > 0 and
                len(claim_supported) > 0 and
                source_type in ['research', 'authority', 'tool', 'government', 'academic']
            )
            
            validated_link = link.copy()
            validated_link['keep_link'] = keep_link
            validated_link['value_score'] = 3 if keep_link else 1
            validated_link['validation_notes'] = 'Basic validation passed' if keep_link else 'Validation failed'
            
            validated_links.append(validated_link)
        
        return validated_links
        
    except Exception as e:
        logger.error(f"Error validating external links: {str(e)}")
        return external_links


def insert_external_links(content: str, links: List[Dict[str, Any]]) -> str:
    """
    Insert external links into the content.
    
    Args:
        content: Content with internal links
        links: List of validated external link data
        
    Returns:
        Content with external links inserted
    """
    
    try:
        modified_content = content
        links_inserted = 0
        
        # Filter to only links that should be kept
        valid_links = [link for link in links if link.get('keep_link', True)]
        
        # Sort links by priority and value score
        sorted_links = sorted(
            valid_links, 
            key=lambda x: (x.get('priority', 5), -x.get('value_score', 0))
        )
        
        for link in sorted_links:
            anchor_text = link.get('anchor_text', '')
            suggested_domain = link.get('suggested_domain', 'example.com')
            opens_new_tab = link.get('opens_new_tab', True)
            
            if not anchor_text:
                continue
            
            # Create placeholder external link
            # In a real implementation, you would use actual URLs
            target_url = f"https://{suggested_domain}"
            if opens_new_tab:
                markdown_link = f"[{anchor_text}]({target_url}){{:target=\"_blank\" rel=\"noopener noreferrer\"}}"
            else:
                markdown_link = f"[{anchor_text}]({target_url})"
            
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
                link['target_url'] = target_url
                links_inserted += 1
                
                logger.debug(f"Inserted external link: {anchor_text} -> {target_url}")
            else:
                logger.warning(f"Could not find anchor text in content: {anchor_text}")
                link['inserted'] = False
        
        logger.info(f"Inserted {links_inserted} external links into content")
        
        return modified_content
        
    except Exception as e:
        logger.error(f"Error inserting external links: {str(e)}")
        return content


def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except Exception:
        return "unknown-domain.com"


def parse_external_linking_response(response_text: str) -> Dict[str, Any]:
    """Parse the AI response for external linking analysis."""
    
    try:
        import json
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            logger.warning("No JSON found in external linking analysis response")
            return {}
            
    except Exception as e:
        logger.error(f"Error parsing external linking analysis response: {str(e)}")
        return {} 