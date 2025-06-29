"""
Web Research Node

Performs web searches using Google Search API to gather information for blog content.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
import re

from langchain_core.runnables import RunnableConfig
from langgraph.types import Send
from google.genai import Client

from ...state import BlogWriterState, WebSearchState, update_progress, add_error, add_warning
from ...schemas import ResearchResult
from ...prompts import get_current_date

# Set up logging
logger = logging.getLogger(__name__)

# Initialize Google GenAI client
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is not set")

genai_client = Client(api_key=os.getenv("GEMINI_API_KEY"))


def web_research_dispatcher(
    state: BlogWriterState,
    config: RunnableConfig
) -> List[Send]:
    """
    Dispatch web searches in parallel based on research plan.
    
    This node:
    1. Gets search queries from research plan
    2. Creates Send objects for parallel execution
    3. Respects search budget limits
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        List of Send objects for parallel web searches
    """
    
    logger.info("=" * 50)
    logger.info("STARTING WEB RESEARCH DISPATCHER")
    logger.info("=" * 50)
    
    # Get research plan
    research_plan = state.get('research_plan', {})
    search_queries = research_plan.get('search_queries', [])
    max_searches = state.get('max_web_searches', 5)
    
    if not search_queries:
        logger.warning("No search queries found in research plan")
        return []
    
    # Limit searches to budget
    queries_to_execute = search_queries[:max_searches]
    
    logger.info(f"Dispatching {len(queries_to_execute)} web searches")
    logger.info(f"Search budget: {max_searches}")
    
    if len(search_queries) > max_searches:
        logger.warning(f"Truncating {len(search_queries) - max_searches} queries due to budget limit")
        add_warning(
            state, 
            f"Limited to {max_searches} searches, skipping {len(search_queries) - max_searches} queries"
        )
    
    # Create Send objects for parallel execution
    sends = []
    for idx, query in enumerate(queries_to_execute):
        logger.debug(f"Dispatching search {idx+1}: {query}")
        sends.append(
            Send(
                "perform_web_search",
                {
                    "search_query": query,
                    "search_id": idx,
                    "blog_idea": state.get('blog_idea', ''),
                    "main_topic": state.get('topic_analysis', {}).get('main_topic', ''),
                    "research_questions": state.get('research_questions', [])
                }
            )
        )
    
    # Update progress
    update_progress(state, 'web_research', 0.4)
    
    return sends


def perform_web_search(
    state: WebSearchState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Perform a single web search using Google Search API.
    
    This node:
    1. Executes the search query
    2. Extracts relevant information
    3. Formats results for blog writing
    4. Stores results in state
    
    Args:
        state: Web search state with query
        config: LangGraph configuration
        
    Returns:
        Updated state with search results
    """
    
    search_query = state.get('search_query', '')
    search_id = state.get('search_id', 0)
    
    logger.info(f"Executing web search {search_id}: {search_query}")
    
    try:
        # Create search prompt
        current_date = get_current_date()
        search_prompt = f"""
Current Date: {current_date}

Search for information about: {search_query}

Context:
- Blog topic: {state.get('main_topic', '')}
- Blog idea: {state.get('blog_idea', '')}

Please find relevant, accurate, and recent information that would be useful for writing a comprehensive blog post.
Focus on:
1. Authoritative sources
2. Recent information (preferably from the last 2 years)
3. Practical examples and case studies
4. Expert opinions and best practices
"""
        
        # Execute search using Google Search tool
        response = genai_client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=search_prompt,
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0.3,  # Lower temperature for more focused results
            }
        )
        
        # Extract search results
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            # Extract grounding metadata
            grounding_metadata = getattr(candidate, 'grounding_metadata', None)
            sources = []
            
            if grounding_metadata and hasattr(grounding_metadata, 'grounding_chunks'):
                for chunk in grounding_metadata.grounding_chunks:
                    source_data = {
                        'url': '',
                        'title': '',
                        'snippet': ''
                    }
                    
                    # Extract URL
                    if hasattr(chunk, 'web') and hasattr(chunk.web, 'uri'):
                        source_data['url'] = chunk.web.uri
                    
                    # Extract title
                    if hasattr(chunk, 'web') and hasattr(chunk.web, 'title'):
                        source_data['title'] = chunk.web.title
                    
                    # Extract snippet (from retrieved_content)
                    if hasattr(chunk, 'retrieved_content') and hasattr(chunk.retrieved_content, 'text'):
                        source_data['snippet'] = chunk.retrieved_content.text[:500]  # Limit snippet length
                    
                    if source_data['url']:  # Only add if we have a URL
                        sources.append(source_data)
            
            # Get the generated summary
            summary = response.text if hasattr(response, 'text') else str(response)
            
            # Create research result
            result = {
                'query': search_query,
                'search_id': search_id,
                'summary': summary,
                'sources': sources,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            
            logger.info(f"Search {search_id} found {len(sources)} sources")
            logger.debug(f"Summary preview: {summary[:200]}...")
            
            # Extract key insights from the summary
            key_insights = extract_key_insights(summary, search_query)
            result['key_insights'] = key_insights
            
            return {
                'web_research_results': [result],
                'search_queries_executed': [search_query]
            }
            
        else:
            # No results found
            logger.warning(f"No results found for search {search_id}: {search_query}")
            
            result = {
                'query': search_query,
                'search_id': search_id,
                'summary': "No relevant results found for this query.",
                'sources': [],
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': "No search results returned"
            }
            
            return {
                'web_research_results': [result],
                'search_queries_executed': [search_query]
            }
            
    except Exception as e:
        error_msg = f"Error in web search {search_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Create error result
        result = {
            'query': search_query,
            'search_id': search_id,
            'summary': "",
            'sources': [],
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(e)
        }
        
        return {
            'web_research_results': [result],
            'search_queries_executed': [search_query],
            'errors': [error_msg]
        }


def extract_key_insights(summary: str, query: str) -> List[str]:
    """
    Extract key insights from search summary.
    
    Args:
        summary: The search result summary
        query: The original search query
        
    Returns:
        List of key insights
    """
    insights = []
    
    # Split by sentences
    sentences = re.split(r'[.!?]+', summary)
    
    # Look for sentences with key indicators
    insight_indicators = [
        'important', 'key', 'essential', 'critical', 'must', 'should',
        'best practice', 'recommend', 'avoid', 'ensure', 'consider',
        'tip', 'note', 'remember', 'crucial', 'significant'
    ]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Check if sentence contains insight indicators
        sentence_lower = sentence.lower()
        if any(indicator in sentence_lower for indicator in insight_indicators):
            # Clean up the sentence
            if len(sentence) > 20 and len(sentence) < 300:  # Reasonable length
                insights.append(sentence)
        
        # Also include sentences with numbers/statistics
        if re.search(r'\d+%|\d+\s*(percent|times|x)', sentence_lower):
            if len(sentence) > 20 and len(sentence) < 300:
                insights.append(sentence)
    
    # Limit to top 5 insights
    return insights[:5]


def aggregate_web_research(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Aggregate results from parallel web searches.
    
    This node:
    1. Collects all search results
    2. Deduplicates sources
    3. Creates summary statistics
    4. Updates progress
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with aggregated results
    """
    
    logger.info("=" * 50)
    logger.info("AGGREGATING WEB RESEARCH RESULTS")
    logger.info("=" * 50)
    
    web_results = state.get('web_research_results', [])
    
    if not web_results:
        logger.warning("No web research results to aggregate")
        update_progress(state, 'internal_research', 0.45)
        return state
    
    # Aggregate statistics
    total_searches = len(web_results)
    successful_searches = sum(1 for r in web_results if r.get('success', False))
    total_sources = sum(len(r.get('sources', [])) for r in web_results)
    
    # Collect all unique sources
    unique_sources = {}
    for result in web_results:
        for source in result.get('sources', []):
            url = source.get('url', '')
            if url and url not in unique_sources:
                unique_sources[url] = source
    
    # Collect all insights
    all_insights = []
    for result in web_results:
        insights = result.get('key_insights', [])
        all_insights.extend(insights)
    
    # Update state with aggregated data
    state['research_summary'] = {
        'total_searches': total_searches,
        'successful_searches': successful_searches,
        'failed_searches': total_searches - successful_searches,
        'total_sources': total_sources,
        'unique_sources': len(unique_sources),
        'sources': list(unique_sources.values()),
        'key_insights': all_insights[:15],  # Top 15 insights
        'timestamp': datetime.now().isoformat()
    }
    
    # Add to debug info
    state['debug_info'].append({
        'node': 'aggregate_web_research',
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'searches_executed': total_searches,
            'sources_found': total_sources,
            'unique_sources': len(unique_sources)
        }
    })
    
    logger.info(f"Aggregation complete:")
    logger.info(f"  - Searches executed: {total_searches}")
    logger.info(f"  - Successful searches: {successful_searches}")
    logger.info(f"  - Total sources found: {total_sources}")
    logger.info(f"  - Unique sources: {len(unique_sources)}")
    logger.info(f"  - Key insights: {len(all_insights)}")
    
    # Update progress
    update_progress(state, 'internal_research', 0.45)
    
    return state 