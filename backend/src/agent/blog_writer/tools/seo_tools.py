"""
SEO Tools

Utility functions for SEO optimization including:
- Keyword density analysis
- Meta tag validation
- Schema markup generation
- URL slug creation
"""

import re
from typing import Dict, Any, List
from urllib.parse import quote


def calculate_keyword_density(content: str, keyword: str) -> float:
    """
    Calculate keyword density as a percentage.
    
    Args:
        content: Text content to analyze
        keyword: Keyword to calculate density for
        
    Returns:
        Keyword density as percentage
    """
    if not content or not keyword:
        return 0.0
    
    # Count total words
    words = content.split()
    total_words = len(words)
    
    if total_words == 0:
        return 0.0
    
    # Count keyword occurrences (case insensitive, whole words only)
    keyword_pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
    keyword_count = len(re.findall(keyword_pattern, content.lower()))
    
    # Calculate density
    density = (keyword_count / total_words) * 100
    return round(density, 2)


def validate_meta_title(title: str) -> Dict[str, Any]:
    """
    Validate meta title for SEO best practices.
    
    Args:
        title: Meta title to validate
        
    Returns:
        Validation results dictionary
    """
    length = len(title)
    
    validation = {
        'title': title,
        'length': length,
        'is_valid': True,
        'warnings': [],
        'recommendations': []
    }
    
    # Check length
    if length < 30:
        validation['warnings'].append('Title is too short (under 30 characters)')
        validation['is_valid'] = False
    elif length > 60:
        validation['warnings'].append('Title is too long (over 60 characters)')
        validation['is_valid'] = False
    elif length > 55:
        validation['warnings'].append('Title might be truncated in search results')
    
    # Check for optimal length
    if 50 <= length <= 60:
        validation['recommendations'].append('Title length is optimal for SEO')
    
    return validation


def validate_meta_description(description: str) -> Dict[str, Any]:
    """
    Validate meta description for SEO best practices.
    
    Args:
        description: Meta description to validate
        
    Returns:
        Validation results dictionary
    """
    length = len(description)
    
    validation = {
        'description': description,
        'length': length,
        'is_valid': True,
        'warnings': [],
        'recommendations': []
    }
    
    # Check length
    if length < 120:
        validation['warnings'].append('Description is too short (under 120 characters)')
        validation['is_valid'] = False
    elif length > 160:
        validation['warnings'].append('Description is too long (over 160 characters)')
        validation['is_valid'] = False
    
    # Check for optimal length
    if 150 <= length <= 160:
        validation['recommendations'].append('Description length is optimal for SEO')
    
    return validation


def create_url_slug(title: str) -> str:
    """
    Create SEO-friendly URL slug from title.
    
    Args:
        title: Title to convert to slug
        
    Returns:
        URL-friendly slug
    """
    if not title:
        return ""
    
    # Convert to lowercase
    slug = title.lower()
    
    # Remove special characters except spaces and hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit length
    if len(slug) > 60:
        slug = slug[:60].rstrip('-')
    
    return slug


def analyze_heading_structure(content: str) -> Dict[str, Any]:
    """
    Analyze heading structure for SEO and readability.
    
    Args:
        content: Markdown content to analyze
        
    Returns:
        Heading structure analysis
    """
    # Find all headings
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    headings = re.findall(heading_pattern, content, re.MULTILINE)
    
    analysis = {
        'total_headings': len(headings),
        'h1_count': 0,
        'h2_count': 0,
        'h3_count': 0,
        'h4_count': 0,
        'h5_count': 0,
        'h6_count': 0,
        'structure': [],
        'issues': [],
        'recommendations': []
    }
    
    for heading_level, heading_text in headings:
        level = len(heading_level)
        analysis[f'h{level}_count'] += 1
        analysis['structure'].append({
            'level': level,
            'text': heading_text,
            'length': len(heading_text)
        })
    
    # Check for SEO issues
    if analysis['h1_count'] == 0:
        analysis['issues'].append('No H1 heading found')
    elif analysis['h1_count'] > 1:
        analysis['issues'].append('Multiple H1 headings found (should be only one)')
    
    if analysis['h2_count'] == 0 and analysis['total_headings'] > 1:
        analysis['issues'].append('No H2 headings found for content structure')
    
    # Recommendations
    if analysis['total_headings'] < 3:
        analysis['recommendations'].append('Consider adding more headings for better content structure')
    
    return analysis


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes.
    
    Args:
        content: Text content
        words_per_minute: Average reading speed (default 200 WPM)
        
    Returns:
        Reading time in minutes
    """
    if not content:
        return 0
    
    # Count words
    word_count = len(content.split())
    
    # Calculate reading time
    reading_time = max(1, round(word_count / words_per_minute))
    
    return reading_time


def extract_keywords_from_content(content: str, min_word_length: int = 3) -> List[str]:
    """
    Extract potential keywords from content.
    
    Args:
        content: Text content to analyze
        min_word_length: Minimum word length to consider
        
    Returns:
        List of potential keywords
    """
    if not content:
        return []
    
    # Remove markdown and special characters
    clean_content = re.sub(r'[#*\[\](){}]', '', content)
    
    # Split into words
    words = re.findall(r'\b\w+\b', clean_content.lower())
    
    # Filter by length and common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'this', 'that', 'these', 'those', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
        'can', 'it', 'they', 'we', 'you', 'he', 'she', 'him', 'her', 'his', 'hers', 'our', 'your',
        'their', 'them', 'us', 'me', 'my', 'mine', 'its', 'from', 'into', 'onto', 'up', 'down',
        'out', 'off', 'over', 'under', 'above', 'below', 'between', 'through', 'during', 'before',
        'after', 'while', 'when', 'where', 'why', 'how', 'what', 'which', 'who', 'whom', 'whose'
    }
    
    # Filter words
    keywords = [
        word for word in words 
        if len(word) >= min_word_length and word not in stop_words
    ]
    
    # Count frequency and return most common
    from collections import Counter
    word_counts = Counter(keywords)
    
    # Return top keywords
    return [word for word, count in word_counts.most_common(20)]


def validate_seo_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate complete SEO metadata for quality.
    
    Args:
        metadata: SEO metadata dictionary
        
    Returns:
        Validation results
    """
    validation = {
        'is_valid': True,
        'score': 0,
        'max_score': 10,
        'issues': [],
        'recommendations': []
    }
    
    # Validate meta title
    meta_title = metadata.get('meta_title', '')
    if meta_title:
        title_validation = validate_meta_title(meta_title)
        if title_validation['is_valid']:
            validation['score'] += 2
        else:
            validation['issues'].extend(title_validation['warnings'])
    else:
        validation['issues'].append('Meta title is missing')
    
    # Validate meta description
    meta_description = metadata.get('meta_description', '')
    if meta_description:
        desc_validation = validate_meta_description(meta_description)
        if desc_validation['is_valid']:
            validation['score'] += 2
        else:
            validation['issues'].extend(desc_validation['warnings'])
    else:
        validation['issues'].append('Meta description is missing')
    
    # Check URL slug
    url_slug = metadata.get('url_slug', '')
    if url_slug:
        validation['score'] += 1
    else:
        validation['issues'].append('URL slug is missing')
    
    # Check focus keyword
    focus_keyword = metadata.get('focus_keyword', '')
    if focus_keyword:
        validation['score'] += 1
    else:
        validation['issues'].append('Focus keyword is missing')
    
    # Check additional keywords
    additional_keywords = metadata.get('additional_keywords', [])
    if additional_keywords and len(additional_keywords) >= 3:
        validation['score'] += 1
    else:
        validation['recommendations'].append('Add more related keywords for better SEO')
    
    # Check schema markup
    schema_markup = metadata.get('schema_markup', '')
    if schema_markup:
        validation['score'] += 2
    else:
        validation['recommendations'].append('Add schema markup for better search visibility')
    
    # Check Open Graph data
    og_title = metadata.get('og_title', '')
    og_description = metadata.get('og_description', '')
    if og_title and og_description:
        validation['score'] += 1
    else:
        validation['recommendations'].append('Add Open Graph tags for social media optimization')
    
    # Determine overall validity
    validation['is_valid'] = len(validation['issues']) == 0
    validation['percentage'] = (validation['score'] / validation['max_score']) * 100
    
    return validation 