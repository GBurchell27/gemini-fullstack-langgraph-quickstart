"""
Blog Writer Schemas

Pydantic models for validation and structured output throughout the blog writing workflow.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
import json


# Input schemas
class BlogRequest(BaseModel):
    """Schema for blog creation request"""
    
    idea: str = Field(
        description="The main idea or topic for the blog post",
        min_length=10,
        max_length=500
    )
    target_audience: Optional[str] = Field(
        default="general",
        description="Target audience for the blog post"
    )
    tone: Optional[str] = Field(
        default="professional",
        description="Writing tone (professional, casual, technical, etc.)"
    )
    length: Optional[str] = Field(
        default="medium",
        description="Target length (short: 500-800, medium: 1000-1500, long: 2000+)"
    )
    
    @validator('idea')
    def validate_idea(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Blog idea must be at least 10 characters long")
        return v.strip()
    
    @validator('tone')
    def validate_tone(cls, v):
        allowed_tones = ['professional', 'casual', 'technical', 'conversational', 'academic']
        if v and v.lower() not in allowed_tones:
            raise ValueError(f"Tone must be one of: {', '.join(allowed_tones)}")
        return v.lower() if v else 'professional'
    
    @validator('length')
    def validate_length(cls, v):
        allowed_lengths = ['short', 'medium', 'long']
        if v and v.lower() not in allowed_lengths:
            raise ValueError(f"Length must be one of: {', '.join(allowed_lengths)}")
        return v.lower() if v else 'medium'


# Topic analysis schemas
class TopicAnalysis(BaseModel):
    """Schema for topic analysis results"""
    
    main_topic: str = Field(description="The main topic identified")
    subtopics: List[str] = Field(description="List of subtopics to cover")
    complexity: str = Field(description="Topic complexity level (low, medium, high)")
    research_questions: List[str] = Field(description="Generated research questions")
    target_keywords: List[str] = Field(description="Identified target keywords")
    audience_insights: Union[Dict[str, Any], str] = Field(
        description="Dictionary with keys: pain_points, solutions_seeking, detail_level, desired_action",
        example={
            "pain_points": "Key challenges the audience faces",
            "solutions_seeking": "What solutions they are looking for", 
            "detail_level": "Expected level of detail",
            "desired_action": "What action they should take"
        }
    )
    
    @validator('audience_insights', pre=True)
    def parse_audience_insights(cls, v):
        """Convert string to dict if needed and handle lists"""
        if isinstance(v, str):
            try:
                # Try to parse as JSON
                v = json.loads(v)
            except json.JSONDecodeError:
                # If it fails, create a default structure
                return {
                    "pain_points": v,
                    "solutions_seeking": "Information and guidance",
                    "detail_level": "Appropriate for audience",
                    "desired_action": "Apply learnings from the blog"
                }
        
        # If it's a dict, convert lists to strings
        if isinstance(v, dict):
            for key, value in v.items():
                if isinstance(value, list):
                    # Join list items into a string
                    v[key] = ", ".join(str(item) for item in value)
        
        return v


# Research schemas
class ResearchQuery(BaseModel):
    """Schema for research queries"""
    
    query: str = Field(description="The search query")
    purpose: str = Field(description="Purpose of this query")
    priority: int = Field(description="Priority level (1-5)", ge=1, le=5)


class ResearchResult(BaseModel):
    """Schema for research results"""
    
    source_url: str = Field(description="URL of the source")
    title: str = Field(description="Title of the source")
    snippet: str = Field(description="Relevant content snippet")
    relevance_score: float = Field(description="Relevance score (0-1)", ge=0, le=1)
    key_insights: List[str] = Field(description="Key insights extracted")
    timestamp: datetime = Field(default_factory=datetime.now)


# Research plan schemas
class ResearchTask(BaseModel):
    """Schema for individual research task"""
    task: str = Field(description="Description of the research task")
    priority: int = Field(description="Priority level (1-5, where 1 is highest)", ge=1, le=5)
    search_count: int = Field(default=1, description="Number of searches allocated", ge=1, le=5)


class ResearchPlan(BaseModel):
    """Schema for research planning and coordination"""
    
    research_strategy: str = Field(description="Overall research strategy")
    focus_areas: List[str] = Field(description="Key areas to focus research on")
    prioritized_tasks: List[ResearchTask] = Field(
        description="Research tasks with priority levels",
        example=[
            {"task": "Research microservices patterns", "priority": 1, "search_count": 3},
            {"task": "Find best practices for API gateways", "priority": 2, "search_count": 2}
        ]
    )
    resource_allocation: Union[Dict[str, Any], str] = Field(
        description="How to allocate searches across topics",
        example={"technical_depth": 5, "best_practices": 3, "examples": 2}
    )
    internal_content_opportunities: List[str] = Field(
        description="Opportunities to link to existing content"
    )
    search_queries: List[str] = Field(
        description="Prepared search queries for web research"
    )
    
    @validator('resource_allocation', pre=True)
    def parse_resource_allocation(cls, v):
        """Convert string to dict if needed"""
        if isinstance(v, str):
            # If it's a string, create a simple allocation based on the description
            # This is a fallback when LLM doesn't return proper structure
            return {
                "high_priority": 4,
                "medium_priority": 3,
                "low_priority": 1,
                "description": v
            }
        return v
    
    @validator('prioritized_tasks', pre=True)
    def validate_tasks(cls, v):
        """Ensure tasks are properly structured"""
        if not v:
            # If empty, create default tasks
            return [
                {"task": "Research core concepts and definitions", "priority": 1, "search_count": 3},
                {"task": "Find best practices and implementation examples", "priority": 2, "search_count": 2},
                {"task": "Identify common challenges and solutions", "priority": 3, "search_count": 1}
            ]
        
        # Fix any empty dictionaries
        fixed_tasks = []
        for i, task in enumerate(v):
            if not task or not isinstance(task, dict) or not task.get('task'):
                # Create a default task
                fixed_tasks.append({
                    "task": f"Research task {i+1}",
                    "priority": min(i+1, 5),
                    "search_count": max(1, 3-i)
                })
            else:
                # Ensure required fields exist
                task['priority'] = task.get('priority', i+1)
                task['search_count'] = task.get('search_count', 1)
                fixed_tasks.append(task)
        
        return fixed_tasks


# Content strategy schemas
class ContentOutline(BaseModel):
    """Schema for blog content outline"""
    
    title_options: List[str] = Field(description="Suggested blog titles", min_items=3)
    sections: List[Dict[str, Any]] = Field(description="Blog sections with details")
    key_messages: List[str] = Field(description="Key messages to convey")
    cta_suggestions: List[str] = Field(description="Call-to-action suggestions")
    estimated_word_count: int = Field(description="Estimated total word count")


class BlogSection(BaseModel):
    """Schema for individual blog sections"""
    
    type: str = Field(description="Section type (introduction, body, conclusion)")
    title: Optional[str] = Field(description="Section title (for body sections)")
    content: str = Field(description="Section content")
    word_count: int = Field(description="Word count for this section")
    keywords_used: List[str] = Field(description="Keywords incorporated")


# Linking schemas
class InternalLink(BaseModel):
    """Schema for internal links"""
    
    anchor_text: str = Field(description="The clickable text")
    target_url: str = Field(description="Target URL within the site")
    context: str = Field(description="Surrounding context")
    relevance_score: float = Field(description="Relevance score", ge=0, le=1)


class ExternalLink(BaseModel):
    """Schema for external links"""
    
    anchor_text: str = Field(description="The clickable text")
    target_url: str = Field(description="Target external URL")
    domain: str = Field(description="Domain of the target")
    authority_score: float = Field(description="Domain authority score", ge=0, le=1)
    is_competitor: bool = Field(default=False, description="Whether this is a competitor")


# SEO schemas
class SEOMetadata(BaseModel):
    """Schema for SEO metadata"""
    
    meta_title: str = Field(description="SEO title", max_length=60)
    meta_description: str = Field(description="SEO description", max_length=160)
    focus_keyword: str = Field(description="Primary focus keyword")
    secondary_keywords: List[str] = Field(description="Secondary keywords")
    tags: List[str] = Field(description="Blog tags")
    categories: List[str] = Field(description="Blog categories")
    schema_markup: Dict[str, Any] = Field(description="Structured data markup")
    
    @validator('meta_title')
    def validate_title_length(cls, v):
        if len(v) > 60:
            raise ValueError("Meta title should be under 60 characters")
        return v
    
    @validator('meta_description')
    def validate_description_length(cls, v):
        if len(v) > 160:
            raise ValueError("Meta description should be under 160 characters")
        return v


# Quality assessment schemas
class QualityMetrics(BaseModel):
    """Schema for content quality metrics"""
    
    readability_score: float = Field(description="Readability score (0-100)", ge=0, le=100)
    seo_score: float = Field(description="SEO optimization score (0-100)", ge=0, le=100)
    originality_score: float = Field(description="Content originality score (0-100)", ge=0, le=100)
    keyword_density: float = Field(description="Keyword density percentage", ge=0, le=10)
    issues_found: List[str] = Field(description="List of quality issues found")
    suggestions: List[str] = Field(description="Improvement suggestions")


# Output schemas
class BlogResult(BaseModel):
    """Schema for the final blog output"""
    
    title: str = Field(description="Final blog title")
    content_markdown: str = Field(description="Blog content in markdown format")
    content_html: Optional[str] = Field(description="Blog content in HTML format")
    seo_metadata: SEOMetadata = Field(description="SEO metadata")
    quality_metrics: QualityMetrics = Field(description="Quality assessment results")
    internal_links: List[InternalLink] = Field(description="Internal links added")
    external_links: List[ExternalLink] = Field(description="External links added")
    word_count: int = Field(description="Total word count")
    estimated_reading_time: int = Field(description="Estimated reading time in minutes")
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time_seconds: float = Field(description="Time taken to generate the blog")


# Error schemas
class ProcessingError(BaseModel):
    """Schema for processing errors"""
    
    step: str = Field(description="The step where error occurred")
    error_type: str = Field(description="Type of error")
    message: str = Field(description="Error message")
    timestamp: datetime = Field(default_factory=datetime.now)
    recoverable: bool = Field(description="Whether the error is recoverable")
    suggested_action: Optional[str] = Field(description="Suggested action to resolve") 