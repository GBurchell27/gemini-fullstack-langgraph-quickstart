"""
Blog Writer API Utilities

Helper functions and utilities for the blog writer API endpoints.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

# In-memory job storage (replace with database in production)
BLOG_JOBS: Dict[str, Dict[str, Any]] = {}

logger = logging.getLogger(__name__)


def create_job_id() -> str:
    """Generate a unique job ID"""
    return f"blog_{uuid4().hex[:12]}"


def save_job(job_id: str, data: Dict[str, Any]) -> None:
    """Save job data to storage"""
    BLOG_JOBS[job_id] = {
        **data,
        'updated_at': datetime.now().isoformat()
    }
    logger.info(f"Saved job {job_id}: {data.get('status', 'unknown')}")


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve job data from storage"""
    return BLOG_JOBS.get(job_id)


def list_jobs() -> Dict[str, Dict[str, Any]]:
    """List all jobs (for debugging)"""
    return BLOG_JOBS


def format_blog_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the incoming request data for the blog writer graph.
    
    Args:
        request_data: Raw request data from API
        
    Returns:
        Formatted data for the blog writer state
    """
    return {
        'blog_idea': request_data.get('idea', ''),
        'target_audience': request_data.get('target_audience', 'general'),
        'tone': request_data.get('tone', 'professional'),
        'length': request_data.get('length', 'medium'),
        'errors': [],
        'warnings': [],
        'debug_info': [],
        'current_step': 'input_processing',
        'progress': 0.0
    }


def format_progress_response(state: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """
    Format the progress response for API consumption.
    
    Args:
        state: Current blog writer state
        job_id: Job identifier
        
    Returns:
        Formatted progress response
    """
    return {
        'job_id': job_id,
        'status': 'failed' if state.get('current_step') == 'failed' else 'processing',
        'current_step': state.get('current_step', 'unknown'),
        'progress': state.get('progress', 0.0),
        'errors': state.get('errors', []),
        'warnings': state.get('warnings', []),
        'message': _get_progress_message(state)
    }


def format_result_response(state: Dict[str, Any], job_id: str) -> Dict[str, Any]:
    """
    Format the final result for API consumption.
    
    Args:
        state: Final blog writer state
        job_id: Job identifier
        
    Returns:
        Formatted result response
    """
    if state.get('current_step') == 'failed':
        return {
            'job_id': job_id,
            'status': 'failed',
            'errors': state.get('errors', []),
            'final_output': state.get('final_output', {})
        }
        
    return {
        'job_id': job_id,
        'status': 'completed',
        'blog': {
            'title': state.get('meta_title', 'Untitled'),
            'content': state.get('markdown_content', ''),
            'seo_metadata': state.get('seo_metadata', {}),
            'quality_score': state.get('quality_score', 0.0),
            'word_count': _count_words(state.get('markdown_content', '')),
            'internal_links': state.get('internal_links', []),
            'external_links': state.get('external_links', [])
        },
        'debug_info': state.get('debug_info', []) if state.get('debug_mode') else None
    }


def _get_progress_message(state: Dict[str, Any]) -> str:
    """Get human-readable progress message based on current step"""
    step_messages = {
        'input_processing': 'Validating and processing your blog idea...',
        'topic_analysis': 'Analyzing the topic and identifying key themes...',
        'research_coordination': 'Planning research strategy...',
        'web_research': 'Conducting web research...',
        'competitor_analysis': 'Analyzing competitor content...',
        'internal_research': 'Searching internal content...',
        'research_synthesis': 'Synthesizing research findings...',
        'content_strategy': 'Creating content strategy and outline...',
        'content_writing': 'Writing blog content...',
        'content_assembly': 'Assembling blog sections...',
        'internal_linking': 'Adding internal links...',
        'external_linking': 'Adding external references...',
        'seo_optimization': 'Optimizing for SEO...',
        'markdown_conversion': 'Converting to markdown format...',
        'quality_review': 'Performing quality review...',
        'output_generation': 'Generating final output...',
        'completed': 'Blog creation completed!',
        'failed': 'Blog creation failed due to errors.'
    }
    
    current_step = state.get('current_step', 'unknown')
    return step_messages.get(current_step, f'Processing step: {current_step}')


def _count_words(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())


# Example webhook handler (for future implementation)
def send_webhook_notification(job_id: str, webhook_url: str, data: Dict[str, Any]) -> None:
    """
    Send webhook notification about job status.
    
    Args:
        job_id: Job identifier
        webhook_url: URL to send notification to
        data: Data to send
    """
    # TODO: Implement webhook notifications
    logger.info(f"Would send webhook for job {job_id} to {webhook_url}")
    pass 