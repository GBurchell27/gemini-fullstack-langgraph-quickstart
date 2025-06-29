"""
Output Generator Node

Generates final blog output in multiple formats including:
- Markdown formatting
- HTML conversion
- JSON export
- Final packaging with all metadata
"""

import os
import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.runnables import RunnableConfig

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...schemas import BlogResult

# Set up logging
logger = logging.getLogger(__name__)


def output_generator_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Generate final blog output in multiple formats with complete metadata.
    
    This node:
    1. Packages content into final blog result format
    2. Generates multiple output formats (markdown, HTML, JSON)
    3. Includes all metadata and analytics
    4. Creates comprehensive final output
    5. Calculates processing statistics
    
    Args:
        state: Current blog writer state with all enhancements
        config: LangGraph configuration
        
    Returns:
        Updated state with final blog result
    """
    
    logger.info("=" * 50)
    logger.info("STARTING OUTPUT GENERATION")
    logger.info("=" * 50)
    
    try:
        # Get final content and metadata
        final_content = state.get('content_with_links')
        if not final_content:
            final_content = state.get('assembled_content', '')
        
        if not final_content:
            logger.error("No content found for output generation")
            add_error(state, "No content available for output generation")
            return state
        
        # Get all metadata
        content_strategy = state.get('content_strategy', {})
        title_options = content_strategy.get('title_options', [])
        selected_title = title_options[0] if title_options else state.get('blog_idea', 'Blog Post')
        
        seo_metadata = state.get('seo_metadata', {})
        quality_metrics = state.get('quality_metrics', {})
        internal_links = state.get('internal_links', [])
        external_links = state.get('external_links', [])
        debug_info = state.get('debug_info', [])
        
        # Calculate processing time (if available)
        processing_start = None
        processing_end = datetime.now()
        processing_time_seconds = 0
        
        if debug_info:
            first_entry = debug_info[0] if debug_info else {}
            last_entry = debug_info[-1] if debug_info else {}
            
            try:
                if first_entry.get('timestamp') and last_entry.get('timestamp'):
                    start_time = datetime.fromisoformat(first_entry['timestamp'])
                    end_time = datetime.fromisoformat(last_entry['timestamp'])
                    processing_time_seconds = (end_time - start_time).total_seconds()
            except Exception:
                processing_time_seconds = 0
        
        logger.info(f"Generating final output for: {selected_title}")
        logger.info(f"Content length: {len(final_content)} characters")
        logger.info(f"Processing time: {processing_time_seconds:.1f} seconds")
        
        # Generate different content formats
        markdown_content = format_as_markdown(final_content, seo_metadata)
        html_content = convert_markdown_to_html(markdown_content)
        
        # Calculate final statistics
        word_count = len(final_content.split())
        reading_time = quality_metrics.get('reading_time_minutes', calculate_reading_time_basic(final_content))
        
        # Create comprehensive blog result
        blog_result = {
            'title': selected_title,
            'content_markdown': markdown_content,
            'content_html': html_content,
            'seo_metadata': seo_metadata,
            'quality_metrics': quality_metrics,
            'internal_links': internal_links,
            'external_links': external_links,
            'word_count': word_count,
            'estimated_reading_time': reading_time,
            'created_at': datetime.now().isoformat(),
            'processing_time_seconds': processing_time_seconds,
            'processing_summary': create_processing_summary(debug_info),
            'content_statistics': calculate_content_statistics(final_content, internal_links, external_links),
            'export_formats': {
                'markdown': markdown_content,
                'html': html_content,
                'plain_text': convert_to_plain_text(final_content),
                'json': create_json_export(state)
            },
            'metadata': {
                'blog_idea': state.get('blog_idea', ''),
                'target_audience': state.get('target_audience', 'general'),
                'tone': state.get('tone', 'professional'),
                'length': state.get('length', 'medium'),
                'topic_analysis': state.get('topic_analysis', {}),
                'research_summary': state.get('research_summary', {}),
                'content_strategy': content_strategy
            }
        }
        
        # Update state with final result
        state['final_blog_result'] = blog_result
        state['current_step'] = 'completed'
        state['progress'] = 1.0
        
        # Add final output statistics to debug info
        output_stats = {
            'final_word_count': word_count,
            'final_reading_time': reading_time,
            'total_internal_links': len(internal_links),
            'total_external_links': len(external_links),
            'processing_time_seconds': processing_time_seconds,
            'quality_score': quality_metrics.get('overall_score', 0),
            'seo_score': quality_metrics.get('seo_score', 0),
            'output_formats_generated': len(blog_result['export_formats']),
            'timestamp': datetime.now().isoformat()
        }
        
        state['debug_info'].append({
            'node': 'output_generator',
            'timestamp': datetime.now().isoformat(),
            'statistics': output_stats
        })
        
        logger.info(f"Output generation complete:")
        logger.info(f"  - Final word count: {word_count}")
        logger.info(f"  - Reading time: {reading_time} minutes")
        logger.info(f"  - Internal links: {len(internal_links)}")
        logger.info(f"  - External links: {len(external_links)}")
        logger.info(f"  - Quality score: {quality_metrics.get('overall_score', 0):.1f}/10")
        logger.info(f"  - Processing time: {processing_time_seconds:.1f} seconds")
        
        # Update final progress
        update_progress(state, 'completed', 1.0)
        
        return state
        
    except Exception as e:
        error_msg = f"Error in output generation: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        return state


def format_as_markdown(content: str, seo_metadata: Dict[str, Any]) -> str:
    """
    Format content as proper markdown with SEO metadata.
    
    Args:
        content: Blog content
        seo_metadata: SEO metadata
        
    Returns:
        Formatted markdown content
    """
    
    try:
        # Start with metadata block
        markdown_parts = []
        
        # Add front matter (YAML) if SEO metadata is available
        if seo_metadata:
            front_matter = "---\n"
            front_matter += f"title: \"{seo_metadata.get('meta_title', '')}\"\n"
            front_matter += f"description: \"{seo_metadata.get('meta_description', '')}\"\n"
            front_matter += f"slug: \"{seo_metadata.get('url_slug', '')}\"\n"
            
            if seo_metadata.get('tags'):
                front_matter += f"tags: {seo_metadata['tags']}\n"
            
            if seo_metadata.get('categories'):
                front_matter += f"categories: {seo_metadata['categories']}\n"
            
            front_matter += f"date: \"{datetime.now().isoformat()}\"\n"
            front_matter += "---\n\n"
            
            markdown_parts.append(front_matter)
        
        # Add main content
        markdown_parts.append(content)
        
        # Add schema markup as HTML comment
        if seo_metadata.get('schema_markup'):
            schema_comment = f"\n\n<!-- Schema Markup -->\n<script type=\"application/ld+json\">\n{seo_metadata['schema_markup']}\n</script>"
            markdown_parts.append(schema_comment)
        
        return '\n'.join(markdown_parts)
        
    except Exception as e:
        logger.error(f"Error formatting markdown: {str(e)}")
        return content


def convert_markdown_to_html(markdown_content: str) -> str:
    """
    Convert markdown content to HTML.
    
    Args:
        markdown_content: Markdown content
        
    Returns:
        HTML content
    """
    
    try:
        # Simple markdown to HTML conversion
        # In a full implementation, you'd use a proper markdown library like markdown or mistune
        
        html_content = markdown_content
        
        # Convert headers
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
        
        # Convert links
        html_content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html_content)
        
        # Convert paragraphs (simple approach)
        paragraphs = html_content.split('\n\n')
        html_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                html_paragraphs.append(f'<p>{para}</p>')
            else:
                html_paragraphs.append(para)
        
        return '\n\n'.join(html_paragraphs)
        
    except Exception as e:
        logger.error(f"Error converting to HTML: {str(e)}")
        return f"<div>{markdown_content}</div>"


def convert_to_plain_text(content: str) -> str:
    """
    Convert content to plain text by removing markdown formatting.
    
    Args:
        content: Markdown content
        
    Returns:
        Plain text content
    """
    
    try:
        # Remove markdown formatting
        plain_text = content
        
        # Remove headers
        plain_text = re.sub(r'^#+\s*(.+)$', r'\1', plain_text, flags=re.MULTILINE)
        
        # Remove links but keep text
        plain_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', plain_text)
        
        # Remove bold/italic
        plain_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', plain_text)
        plain_text = re.sub(r'\*([^*]+)\*', r'\1', plain_text)
        
        # Clean up extra whitespace
        plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
        
        return plain_text.strip()
        
    except Exception as e:
        logger.error(f"Error converting to plain text: {str(e)}")
        return content


def create_json_export(state: BlogWriterState) -> str:
    """
    Create JSON export of the complete blog data.
    
    Args:
        state: Complete blog writer state
        
    Returns:
        JSON string representation
    """
    
    try:
        import json
        
        # Create exportable data structure
        export_data = {
            'blog_post': {
                'title': state.get('final_blog_result', {}).get('title', ''),
                'content_markdown': state.get('final_blog_result', {}).get('content_markdown', ''),
                'word_count': state.get('final_blog_result', {}).get('word_count', 0),
                'reading_time': state.get('final_blog_result', {}).get('estimated_reading_time', 0)
            },
            'seo_data': state.get('seo_metadata', {}),
            'quality_metrics': state.get('quality_metrics', {}),
            'links': {
                'internal': state.get('internal_links', []),
                'external': state.get('external_links', [])
            },
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'blog_idea': state.get('blog_idea', ''),
                'target_audience': state.get('target_audience', ''),
                'tone': state.get('tone', ''),
                'topic_analysis': state.get('topic_analysis', {}),
                'research_summary': state.get('research_summary', {})
            },
            'processing_info': {
                'debug_info': state.get('debug_info', []),
                'processing_time': state.get('final_blog_result', {}).get('processing_time_seconds', 0)
            }
        }
        
        return json.dumps(export_data, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Error creating JSON export: {str(e)}")
        return "{}"


def calculate_content_statistics(
    content: str,
    internal_links: List[Dict[str, Any]],
    external_links: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate comprehensive content statistics.
    
    Args:
        content: Final blog content
        internal_links: List of internal links
        external_links: List of external links
        
    Returns:
        Content statistics dictionary
    """
    
    try:
        # Basic counts
        word_count = len(content.split())
        character_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Count headings
        headings = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # Count lists
        bullet_points = len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE))
        numbered_items = len(re.findall(r'^\s*\d+\.\s', content, re.MULTILINE))
        
        # Count code blocks
        code_blocks = len(re.findall(r'```', content)) // 2
        
        # Link statistics
        total_links = len(internal_links) + len(external_links)
        
        return {
            'word_count': word_count,
            'character_count': character_count,
            'character_count_no_spaces': len(content.replace(' ', '')),
            'paragraph_count': paragraph_count,
            'heading_count': len(headings),
            'bullet_points': bullet_points,
            'numbered_items': numbered_items,
            'code_blocks': code_blocks,
            'total_links': total_links,
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'average_words_per_paragraph': round(word_count / paragraph_count, 1) if paragraph_count > 0 else 0,
            'reading_time_minutes': calculate_reading_time_basic(content)
        }
        
    except Exception as e:
        logger.error(f"Error calculating content statistics: {str(e)}")
        return {}


def create_processing_summary(debug_info: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create processing summary from debug information.
    
    Args:
        debug_info: List of debug information entries
        
    Returns:
        Processing summary
    """
    
    try:
        if not debug_info:
            return {}
        
        # Extract node execution information
        nodes_executed = []
        total_processing_time = 0
        
        for entry in debug_info:
            node_name = entry.get('node', 'unknown')
            timestamp = entry.get('timestamp', '')
            statistics = entry.get('statistics', {})
            
            nodes_executed.append({
                'node': node_name,
                'timestamp': timestamp,
                'key_metrics': statistics
            })
        
        # Calculate total processing steps
        processing_steps = len(nodes_executed)
        
        return {
            'total_processing_steps': processing_steps,
            'nodes_executed': [node['node'] for node in nodes_executed],
            'processing_timeline': nodes_executed,
            'workflow_completed': True,
            'errors_encountered': sum(1 for entry in debug_info if 'error' in str(entry).lower()),
            'warnings_issued': sum(1 for entry in debug_info if 'warning' in str(entry).lower())
        }
        
    except Exception as e:
        logger.error(f"Error creating processing summary: {str(e)}")
        return {}


def calculate_reading_time_basic(content: str, words_per_minute: int = 200) -> int:
    """
    Basic reading time calculation.
    
    Args:
        content: Text content
        words_per_minute: Reading speed
        
    Returns:
        Reading time in minutes
    """
    
    word_count = len(content.split())
    return max(1, round(word_count / words_per_minute)) 