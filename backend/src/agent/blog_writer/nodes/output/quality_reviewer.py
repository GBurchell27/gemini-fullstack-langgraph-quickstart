"""
Quality Reviewer Node

Performs comprehensive quality analysis of the final blog content for quality, readability, and completeness.
"""

import os
import logging
import re
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.runnables import RunnableConfig
from google.genai import Client

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...schemas import QualityMetrics
from ...tools.seo_tools import (
    calculate_reading_time,
    analyze_heading_structure,
    validate_seo_metadata
)
from ...prompts import get_current_date

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")

genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))


CONTENT_QUALITY_ANALYSIS_PROMPT = """
Analyze this blog post for overall content quality and provide a comprehensive assessment.

Blog Title: {title}
Blog Content:
{content}

Target Audience: {target_audience}
Main Topic: {main_topic}
Word Count: {word_count}
Current Date: {current_date}

Evaluate the content across these dimensions:

1. Content Quality (1-10):
   - Depth and comprehensiveness of coverage
   - Accuracy and credibility of information
   - Value provided to the target audience
   - Clarity and organization of ideas

2. Writing Quality (1-10):
   - Grammar and spelling
   - Sentence structure and flow
   - Tone consistency
   - Professional writing standards

3. Engagement Factor (1-10):
   - Hook effectiveness in introduction
   - Readability and pacing
   - Use of examples and practical insights
   - Call-to-action effectiveness

4. Structure & Organization (1-10):
   - Logical flow of information
   - Effective use of headings and subheadings
   - Paragraph length and structure
   - Conclusion effectiveness

5. Completeness (1-10):
   - Topic coverage completeness
   - Answering reader questions
   - Actionable takeaways provided
   - Supporting evidence included

Respond with a JSON object:
{{
    "quality_scores": {{
        "content_quality": 8,
        "writing_quality": 8,
        "engagement_factor": 7,
        "structure_organization": 8,
        "completeness": 8
    }},
    "overall_score": 7.8,
    "strengths": [
        "Clear, well-structured content",
        "Good use of examples"
    ],
    "improvement_areas": [
        "Could benefit from more specific examples",
        "Conclusion could be stronger"
    ],
    "recommendations": [
        "Add more case studies for credibility",
        "Include specific action steps"
    ],
    "readability_assessment": "appropriate for target audience",
    "estimated_engagement_time": 8
}}
"""

READABILITY_ANALYSIS_PROMPT = """
Analyze the readability and accessibility of this blog content.

Content: {content}
Target Audience: {target_audience}

Evaluate:
1. Sentence length and complexity
2. Vocabulary appropriateness for audience
3. Paragraph structure
4. Use of transitions
5. Clarity of explanations

Provide specific recommendations for improving readability.

Respond with a JSON object:
{{
    "readability_score": 8,
    "reading_level": "professional",
    "average_sentence_length": 15,
    "complex_sentences_percentage": 20,
    "readability_issues": [
        "Some sentences are too long",
        "Technical jargon not explained"
    ],
    "readability_improvements": [
        "Break up long sentences",
        "Add definitions for technical terms"
    ],
    "accessibility_score": 7
}}
"""


def quality_reviewer_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Perform comprehensive quality analysis of the final blog content.
    
    This node:
    1. Analyzes content quality across multiple dimensions
    2. Evaluates readability and accessibility
    3. Reviews SEO optimization effectiveness
    4. Checks content completeness
    5. Provides improvement recommendations
    6. Generates quality metrics and scores
    
    Args:
        state: Current blog writer state with enhanced content
        config: LangGraph configuration
        
    Returns:
        Updated state with quality analysis
    """
    
    logger.info("=" * 50)
    logger.info("STARTING QUALITY REVIEW")
    logger.info("=" * 50)
    
    try:
        # Get final content
        final_content = state.get('content_with_links')
        if not final_content:
            final_content = state.get('assembled_content', '')
        
        if not final_content:
            logger.warning("No content found for quality review")
            add_warning(state, "No content available for quality review")
            return state
        
        # Get metadata and context
        content_strategy = state.get('content_strategy', {})
        title_options = content_strategy.get('title_options', [])
        selected_title = title_options[0] if title_options else state.get('blog_idea', 'Blog Post')
        
        topic_analysis = state.get('topic_analysis', {})
        main_topic = topic_analysis.get('main_topic', '')
        target_audience = state.get('target_audience', 'general')
        seo_metadata = state.get('seo_metadata', {})
        
        word_count = len(final_content.split())
        
        logger.info(f"Reviewing quality for: {selected_title}")
        logger.info(f"Content length: {word_count} words")
        logger.info(f"Target audience: {target_audience}")
        
        # Perform comprehensive quality analysis
        content_quality_analysis = analyze_content_quality(
            selected_title,
            final_content,
            target_audience,
            main_topic,
            word_count
        )
        
        # Perform readability analysis
        readability_analysis = analyze_readability(
            final_content,
            target_audience
        )
        
        # Analyze heading structure
        heading_analysis = analyze_heading_structure(final_content)
        
        # Validate SEO metadata
        seo_validation = validate_seo_metadata(seo_metadata) if seo_metadata else {}
        
        # Calculate technical metrics
        technical_metrics = calculate_technical_metrics(final_content)
        
        # Calculate overall quality score
        overall_quality_score = calculate_overall_quality_score(
            content_quality_analysis,
            readability_analysis,
            heading_analysis,
            seo_validation,
            technical_metrics
        )
        
        # Create comprehensive quality metrics
        quality_metrics = {
            'overall_score': overall_quality_score,
            'content_quality_score': content_quality_analysis.get('overall_score', 7),
            'readability_score': readability_analysis.get('readability_score', 7),
            'seo_score': seo_validation.get('percentage', 70) / 10,  # Convert to 1-10 scale
            'structure_score': calculate_structure_score(heading_analysis),
            'word_count': word_count,
            'reading_time_minutes': calculate_reading_time(final_content),
            'heading_count': heading_analysis.get('total_headings', 0),
            'internal_links_count': len(state.get('internal_links', [])),
            'external_links_count': len(state.get('external_links', [])),
            'strengths': content_quality_analysis.get('strengths', []),
            'improvement_areas': content_quality_analysis.get('improvement_areas', []),
            'recommendations': combine_recommendations(
                content_quality_analysis,
                readability_analysis,
                heading_analysis,
                seo_validation
            ),
            'quality_breakdown': content_quality_analysis.get('quality_scores', {}),
            'readability_details': readability_analysis,
            'seo_validation': seo_validation,
            'technical_metrics': technical_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        # Update state
        state['quality_metrics'] = quality_metrics
        
        # Add quality review statistics to debug info
        quality_stats = {
            'overall_quality_score': overall_quality_score,
            'content_quality': content_quality_analysis.get('overall_score', 7),
            'readability_score': readability_analysis.get('readability_score', 7),
            'seo_score': quality_metrics['seo_score'],
            'total_recommendations': len(quality_metrics['recommendations']),
            'word_count': word_count,
            'reading_time': quality_metrics['reading_time_minutes'],
            'timestamp': datetime.now().isoformat()
        }
        
        state['debug_info'].append({
            'node': 'quality_reviewer',
            'timestamp': datetime.now().isoformat(),
            'statistics': quality_stats
        })
        
        logger.info(f"Quality review complete:")
        logger.info(f"  - Overall quality score: {overall_quality_score:.1f}/10")
        logger.info(f"  - Content quality: {quality_stats['content_quality']:.1f}/10")
        logger.info(f"  - Readability: {quality_stats['readability_score']:.1f}/10")
        logger.info(f"  - SEO score: {quality_stats['seo_score']:.1f}/10")
        logger.info(f"  - Recommendations: {quality_stats['total_recommendations']}")
        
        # Update progress
        update_progress(state, 'quality_review', 0.95)
        
        return state
        
    except Exception as e:
        error_msg = f"Error in quality review: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg)
        return state


def analyze_content_quality(
    title: str,
    content: str,
    target_audience: str,
    main_topic: str,
    word_count: int
) -> Dict[str, Any]:
    """
    Analyze content quality using AI evaluation.
    
    Args:
        title: Blog title
        content: Blog content
        target_audience: Target audience
        main_topic: Main topic
        word_count: Word count
        
    Returns:
        Content quality analysis
    """
    
    try:
        # Limit content for prompt
        content_sample = content[:4000] if len(content) > 4000 else content
        
        prompt = CONTENT_QUALITY_ANALYSIS_PROMPT.format(
            title=title,
            content=content_sample,
            target_audience=target_audience,
            main_topic=main_topic,
            word_count=word_count,
            current_date=get_current_date()
        )
        
        model = genai_client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config={'temperature': 0.3, 'max_output_tokens': 1500}
        )
        
        response_text = model.text.strip()
        logger.debug(f"Content quality analysis response: {response_text[:500]}...")
        
        # Parse the response
        quality_analysis = parse_quality_analysis_response(response_text)
        
        return quality_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing content quality: {str(e)}")
        return {'overall_score': 7, 'quality_scores': {}, 'strengths': [], 'improvement_areas': []}


def analyze_readability(content: str, target_audience: str) -> Dict[str, Any]:
    """
    Analyze content readability.
    
    Args:
        content: Blog content
        target_audience: Target audience
        
    Returns:
        Readability analysis
    """
    
    try:
        # Basic readability metrics
        sentences = re.split(r'[.!?]+', content)
        total_sentences = len([s for s in sentences if s.strip()])
        
        words = content.split()
        total_words = len(words)
        
        average_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
        
        # Simple readability assessment
        readability_score = 8  # Default score
        
        if average_sentence_length > 25:
            readability_score -= 1
        elif average_sentence_length < 10:
            readability_score -= 0.5
        
        readability_analysis = {
            'readability_score': round(readability_score, 1),
            'reading_level': 'professional',
            'average_sentence_length': round(average_sentence_length, 1),
            'total_sentences': total_sentences,
            'total_words': total_words,
            'readability_issues': [],
            'readability_improvements': [],
            'accessibility_score': 8
        }
        
        # Add specific recommendations
        if average_sentence_length > 20:
            readability_analysis['readability_issues'].append('Average sentence length is high')
            readability_analysis['readability_improvements'].append('Consider breaking up long sentences')
        
        return readability_analysis
        
    except Exception as e:
        logger.error(f"Error analyzing readability: {str(e)}")
        return {'readability_score': 7, 'reading_level': 'general'}


def calculate_technical_metrics(content: str) -> Dict[str, Any]:
    """
    Calculate technical content metrics.
    
    Args:
        content: Blog content
        
    Returns:
        Technical metrics
    """
    
    try:
        # Count various elements
        word_count = len(content.split())
        character_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Count links
        internal_links = len(re.findall(r'\[([^\]]+)\]\([^)]+\)', content))
        
        # Count images (markdown format)
        images = len(re.findall(r'!\[([^\]]*)\]\([^)]+\)', content))
        
        # Count lists
        bullet_lists = len(re.findall(r'^\s*[-*+]\s', content, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.\s', content, re.MULTILINE))
        
        return {
            'word_count': word_count,
            'character_count': character_count,
            'paragraph_count': paragraph_count,
            'internal_links': internal_links,
            'images': images,
            'bullet_points': bullet_lists,
            'numbered_lists': numbered_lists,
            'avg_words_per_paragraph': round(word_count / paragraph_count, 1) if paragraph_count > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Error calculating technical metrics: {str(e)}")
        return {}


def calculate_structure_score(heading_analysis: Dict[str, Any]) -> float:
    """
    Calculate structure quality score based on heading analysis.
    
    Args:
        heading_analysis: Heading structure analysis
        
    Returns:
        Structure score (1-10)
    """
    
    try:
        score = 5  # Base score
        
        # Check for H1
        if heading_analysis.get('h1_count', 0) == 1:
            score += 2
        elif heading_analysis.get('h1_count', 0) > 1:
            score -= 1
        
        # Check for H2s
        h2_count = heading_analysis.get('h2_count', 0)
        if h2_count >= 2:
            score += 2
        elif h2_count == 1:
            score += 1
        
        # Check total headings
        total_headings = heading_analysis.get('total_headings', 0)
        if total_headings >= 4:
            score += 1
        
        return min(max(score, 1), 10)  # Clamp between 1-10
        
    except Exception:
        return 7


def calculate_overall_quality_score(
    content_analysis: Dict[str, Any],
    readability_analysis: Dict[str, Any],
    heading_analysis: Dict[str, Any],
    seo_validation: Dict[str, Any],
    technical_metrics: Dict[str, Any]
) -> float:
    """
    Calculate overall quality score from all analyses.
    
    Args:
        content_analysis: Content quality analysis
        readability_analysis: Readability analysis
        heading_analysis: Heading structure analysis
        seo_validation: SEO validation results
        technical_metrics: Technical metrics
        
    Returns:
        Overall quality score (1-10)
    """
    
    try:
        # Weight different components
        content_score = content_analysis.get('overall_score', 7) * 0.4
        readability_score = readability_analysis.get('readability_score', 7) * 0.3
        structure_score = calculate_structure_score(heading_analysis) * 0.2
        seo_score = (seo_validation.get('percentage', 70) / 10) * 0.1
        
        overall_score = content_score + readability_score + structure_score + seo_score
        
        return round(min(max(overall_score, 1), 10), 1)  # Clamp and round
        
    except Exception as e:
        logger.error(f"Error calculating overall quality score: {str(e)}")
        return 7.0


def combine_recommendations(
    content_analysis: Dict[str, Any],
    readability_analysis: Dict[str, Any],
    heading_analysis: Dict[str, Any],
    seo_validation: Dict[str, Any]
) -> List[str]:
    """
    Combine recommendations from all analyses.
    
    Args:
        content_analysis: Content quality analysis
        readability_analysis: Readability analysis
        heading_analysis: Heading structure analysis
        seo_validation: SEO validation results
        
    Returns:
        Combined list of recommendations
    """
    
    recommendations = []
    
    # Add content recommendations
    recommendations.extend(content_analysis.get('recommendations', []))
    
    # Add readability recommendations
    recommendations.extend(readability_analysis.get('readability_improvements', []))
    
    # Add heading recommendations
    recommendations.extend(heading_analysis.get('recommendations', []))
    
    # Add SEO recommendations
    recommendations.extend(seo_validation.get('recommendations', []))
    
    # Remove duplicates while preserving order
    unique_recommendations = []
    seen = set()
    for rec in recommendations:
        if rec not in seen:
            unique_recommendations.append(rec)
            seen.add(rec)
    
    return unique_recommendations


def parse_quality_analysis_response(response_text: str) -> Dict[str, Any]:
    """Parse the AI response for quality analysis."""
    
    try:
        import json
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            logger.warning("No JSON found in quality analysis response")
            return {'overall_score': 7, 'quality_scores': {}}
            
    except Exception as e:
        logger.error(f"Error parsing quality analysis response: {str(e)}")
        return {'overall_score': 7, 'quality_scores': {}} 