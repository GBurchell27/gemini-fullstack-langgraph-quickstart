"""
SEO Optimizer Node

Basic SEO optimization for blog content.
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime

from langchain_core.runnables import RunnableConfig

from ...state import BlogWriterState, update_progress, add_error, add_warning

# Set up logging
logger = logging.getLogger(__name__)


def seo_optimizer_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Optimize blog content for SEO.
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with SEO optimizations
    """
    
    logger.info("=" * 50)
    logger.info("STARTING SEO OPTIMIZATION")
    logger.info("=" * 50)
    
    try:
        # Get content and metadata
        content_with_links = state.get('content_with_links')
        if not content_with_links:
            content_with_links = state.get('assembled_content', '')
        
        if not content_with_links:
            logger.warning("No content found for SEO optimization")
            add_warning(state, "No content available for SEO optimization")
            return state
        
        # Get metadata
        content_strategy = state.get('content_strategy', {})
        title_options = content_strategy.get('title_options', [])
        selected_title = title_options[0] if title_options else state.get('blog_idea', 'Blog Post')
        
        topic_analysis = state.get('topic_analysis', {})
        target_keywords = topic_analysis.get('target_keywords', [])
        
        # Create basic SEO metadata
        seo_metadata = {
            'meta_title': selected_title[:60],  # Truncate to 60 chars
            'meta_description': f"Learn about {selected_title.lower()}. Comprehensive guide covering key aspects."[:160],
            'url_slug': selected_title.lower().replace(' ', '-').replace(',', ''),
            'focus_keyword': target_keywords[0] if target_keywords else '',
            'additional_keywords': target_keywords[:5],
            'tags': target_keywords[:5],
            'estimated_reading_time': max(1, len(content_with_links.split()) // 200),
            'word_count': len(content_with_links.split()),
            'timestamp': datetime.now().isoformat()
        }
        
        # Update state
        state['seo_metadata'] = seo_metadata
        
        # Add SEO statistics to debug info
        seo_stats = {
            'meta_title_length': len(seo_metadata['meta_title']),
            'meta_description_length': len(seo_metadata['meta_description']),
            'focus_keyword': seo_metadata['focus_keyword'],
            'total_keywords': len(seo_metadata['additional_keywords']),
            'timestamp': datetime.now().isoformat()
        }
        
        state['debug_info'].append({
            'node': 'seo_optimizer',
            'timestamp': datetime.now().isoformat(),
            'statistics': seo_stats
        })
        
        logger.info(f"SEO optimization complete:")
        logger.info(f"  - Meta title: {seo_metadata['meta_title']}")
        logger.info(f"  - Focus keyword: {seo_metadata['focus_keyword']}")
        logger.info(f"  - Additional keywords: {len(seo_metadata['additional_keywords'])}")
        
        # Update progress
        update_progress(state, 'enhancement', 0.9)
        
        return state
        
    except Exception as e:
        error_msg = f"Error in SEO optimization: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        return state
