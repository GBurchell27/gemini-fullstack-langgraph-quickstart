"""
Internal Research Node

Performs internal content research using the content database to find relevant existing content
and identify linking opportunities for the blog being written.
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime

from langchain_core.runnables import RunnableConfig

from ...state import BlogWriterState, update_progress, add_error, add_warning
from ...tools.content_db import content_db
from ...prompts import get_current_date

# Set up logging
logger = logging.getLogger(__name__)


def internal_research_node(
    state: BlogWriterState,
    config: RunnableConfig
) -> BlogWriterState:
    """
    Perform internal content research to find related existing content.
    
    This node:
    1. Searches internal content database for related articles
    2. Identifies linking opportunities
    3. Finds complementary content
    4. Stores results for content creation phase
    
    Args:
        state: Current blog writer state
        config: LangGraph configuration
        
    Returns:
        Updated state with internal research results
    """
    
    logger.info("=" * 50)
    logger.info("STARTING INTERNAL CONTENT RESEARCH NODE")
    logger.info("=" * 50)
    
    try:
        # Get data from previous nodes
        topic_analysis = state.get('topic_analysis', {})
        research_plan = state.get('research_plan', {})
        main_topic = topic_analysis.get('main_topic', '')
        
        # Validate inputs
        if not topic_analysis or not main_topic:
            error_msg = "Missing topic analysis or main topic for internal research"
            logger.error(error_msg)
            add_error(state, error_msg)
            state['current_step'] = 'failed'
            return state
            
        logger.info(f"Performing internal research for: {main_topic}")
        
        # Get content categories for filtering
        available_categories = content_db.get_content_categories()
        logger.info(f"Available content categories: {available_categories}")
        
        # Search for related content using multiple strategies
        internal_matches = []
        
        # 1. Search by main topic
        main_topic_results = content_db.search_content(
            query=main_topic,
            max_results=5
        )
        internal_matches.extend(main_topic_results)
        logger.info(f"Found {len(main_topic_results)} matches for main topic")
        
        # 2. Search by subtopics
        subtopics = topic_analysis.get('subtopics', [])
        for subtopic in subtopics[:3]:  # Top 3 subtopics
            subtopic_results = content_db.search_content(
                query=subtopic,
                max_results=3
            )
            internal_matches.extend(subtopic_results)
            logger.info(f"Found {len(subtopic_results)} matches for subtopic: {subtopic}")
        
        # 3. Search by research questions (converted to queries)
        research_questions = state.get('research_questions', [])
        for question in research_questions[:3]:  # Top 3 questions
            # Convert question to search query by removing question words
            query = _convert_question_to_query(question)
            if query:
                question_results = content_db.search_content(
                    query=query,
                    max_results=2
                )
                internal_matches.extend(question_results)
                logger.info(f"Found {len(question_results)} matches for question query: {query}")
        
        # 4. Search by internal content opportunities from research plan
        internal_opportunities = research_plan.get('internal_content_opportunities', [])
        for opportunity in internal_opportunities[:3]:
            opp_results = content_db.search_content(
                query=opportunity,
                max_results=2
            )
            internal_matches.extend(opp_results)
            logger.info(f"Found {len(opp_results)} matches for opportunity: {opportunity}")
        
        # Remove duplicates and rank results
        unique_matches = _deduplicate_and_rank_matches(internal_matches)
        
        # Store results in state
        state['internal_content_matches'] = unique_matches
        
        # Generate linking opportunities for future use
        # For this, we'll use a sample content snippet based on the topic
        sample_content = _generate_sample_content(topic_analysis)
        linking_opportunities = content_db.find_linking_opportunities(
            current_content=sample_content,
            current_topic=main_topic,
            max_links=5
        )
        
        # Store linking opportunities
        state['internal_links'] = [
            {
                'target_id': opp['target_id'],
                'target_title': opp['target_title'],
                'target_url': opp['target_url'],
                'anchor_text': opp['suggested_anchors'][0] if opp['suggested_anchors'] else opp['target_title'],
                'relevance_score': opp['relevance_score'],
                'category': opp['category']
            }
            for opp in linking_opportunities
        ]
        
        # Generate summary statistics
        categories_found = list(set(match['category'] for match in unique_matches))
        total_word_count = sum(match['word_count'] for match in unique_matches)
        avg_relevance = sum(match['relevance_score'] for match in unique_matches) / len(unique_matches) if unique_matches else 0
        
        # Create internal research summary
        internal_summary = {
            'total_matches': len(unique_matches),
            'categories_covered': categories_found,
            'total_existing_words': total_word_count,
            'average_relevance': avg_relevance,
            'linking_opportunities': len(linking_opportunities),
            'content_coverage': _analyze_content_coverage(unique_matches, topic_analysis),
            'timestamp': datetime.now().isoformat()
        }
        
        # Store summary in research_summary (merge with existing)
        if 'research_summary' not in state:
            state['research_summary'] = {}
        
        state['research_summary']['internal_research'] = internal_summary
        
        # Add debug info
        state['debug_info'].append({
            'node': 'internal_research',
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'matches_found': len(unique_matches),
                'categories': categories_found[:3],  # Top 3 categories
                'avg_relevance': round(avg_relevance, 3),
                'linking_opportunities': len(linking_opportunities)
            }
        })
        
        # Log results
        logger.info(f"Internal research completed:")
        logger.info(f"  - Total matches found: {len(unique_matches)}")
        logger.info(f"  - Categories covered: {categories_found}")
        logger.info(f"  - Average relevance score: {avg_relevance:.3f}")
        logger.info(f"  - Linking opportunities: {len(linking_opportunities)}")
        logger.info(f"  - Total existing content words: {total_word_count}")
        
        # Log top matches for debugging
        logger.debug("Top internal matches:")
        for i, match in enumerate(unique_matches[:3]):
            logger.debug(f"  {i+1}. {match['title']} (relevance: {match['relevance_score']:.3f})")
        
        # Update progress and next step
        update_progress(state, 'content_strategy', 0.6)
        
        logger.info("INTERNAL RESEARCH COMPLETED SUCCESSFULLY")
        
        return state
        
    except Exception as e:
        error_msg = f"Unexpected error in internal research: {str(e)}"
        logger.error(error_msg, exc_info=True)
        add_error(state, error_msg, {'exception': str(e), 'type': type(e).__name__})
        state['current_step'] = 'failed'
        return state


def _convert_question_to_query(question: str) -> str:
    """Convert a research question to a search query"""
    
    # Remove common question words
    question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'is', 'are', 'can', 'should', 'do', 'does']
    
    # Split and filter words
    words = question.lower().split()
    filtered_words = [word.rstrip('?') for word in words if word.rstrip('?') not in question_words]
    
    # Keep only meaningful words (length > 2)
    meaningful_words = [word for word in filtered_words if len(word) > 2]
    
    return ' '.join(meaningful_words[:5])  # Max 5 words for focused search


def _deduplicate_and_rank_matches(matches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicates and rank matches by relevance"""
    
    # Use a dictionary to deduplicate by ID
    unique_matches = {}
    
    for match in matches:
        match_id = match['id']
        if match_id not in unique_matches:
            unique_matches[match_id] = match
        else:
            # Keep the match with higher relevance score
            if match['relevance_score'] > unique_matches[match_id]['relevance_score']:
                unique_matches[match_id] = match
    
    # Convert back to list and sort by relevance
    ranked_matches = list(unique_matches.values())
    ranked_matches.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    return ranked_matches[:10]  # Limit to top 10 matches


def _generate_sample_content(topic_analysis: Dict[str, Any]) -> str:
    """Generate a sample content snippet for linking analysis"""
    
    main_topic = topic_analysis.get('main_topic', '')
    subtopics = topic_analysis.get('subtopics', [])
    
    # Create a sample paragraph based on topic analysis
    sample_content = f"""
    This comprehensive guide explores {main_topic} and its key components. 
    We'll cover essential aspects including {', '.join(subtopics[:3])} and best practices for implementation.
    Understanding these concepts is crucial for effective research methodology and quality outcomes.
    The systematic approach ensures reliable results and transparent reporting throughout the process.
    """
    
    return sample_content


def _analyze_content_coverage(matches: List[Dict[str, Any]], topic_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze how well existing content covers the current topic"""
    
    if not matches:
        return {
            'coverage_score': 0.0,
            'gaps_identified': topic_analysis.get('subtopics', []),
            'well_covered_areas': []
        }
    
    # Analyze coverage by subtopics
    subtopics = topic_analysis.get('subtopics', [])
    covered_subtopics = []
    
    for subtopic in subtopics:
        subtopic_lower = subtopic.lower()
        for match in matches:
            # Check if subtopic is mentioned in title, content, or tags
            match_text = f"{match['title']} {match['content_snippet']} {' '.join(match['tags'])}".lower()
            if any(word in match_text for word in subtopic_lower.split()):
                covered_subtopics.append(subtopic)
                break
    
    coverage_score = len(covered_subtopics) / len(subtopics) if subtopics else 0.0
    gaps = [topic for topic in subtopics if topic not in covered_subtopics]
    
    return {
        'coverage_score': coverage_score,
        'gaps_identified': gaps,
        'well_covered_areas': covered_subtopics,
        'content_distribution': {
            category: len([m for m in matches if m['category'] == category])
            for category in set(match['category'] for match in matches)
        }
    } 