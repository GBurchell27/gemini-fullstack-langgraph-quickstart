"""
Test script for Research Coordinator functionality

Run this to test Milestone 2 Step 2.2 implementation.
"""

import os
import logging
import sys
import json
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agent.blog_writer import blog_writer_graph
from agent.blog_writer.state import initialize_blog_writer_state

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_research_coordinator():
    """Test the research coordinator with various scenarios"""
    
    print("\n" + "="*50)
    print("RESEARCH COORDINATOR TEST")
    print("="*50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Complex Technical Topic',
            'idea': 'Building a production-ready microservices architecture with Python: API gateway patterns, service mesh, distributed tracing, and deployment strategies',
            'audience': 'senior backend engineers',
            'tone': 'technical',
            'length': 'long',
            'expected_complexity': 'high'
        },
        {
            'name': 'Simple Tutorial',
            'idea': 'How to create your first Python web scraper using BeautifulSoup',
            'audience': 'beginners',
            'tone': 'casual',
            'length': 'medium',
            'expected_complexity': 'low'
        },
        {
            'name': 'Business Strategy',
            'idea': 'Implementing OKRs in a remote-first startup: best practices and common pitfalls',
            'audience': 'startup founders and managers',
            'tone': 'professional',
            'length': 'medium',
            'expected_complexity': 'medium'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"TEST: {test_case['name']}")
        print(f"{'='*50}")
        print(f"Idea: {test_case['idea'][:80]}...")
        print(f"Expected complexity: {test_case['expected_complexity']}")
        
        # Create initial state
        initial_state = initialize_blog_writer_state(
            blog_idea=test_case['idea'],
            target_audience=test_case['audience'],
            tone=test_case['tone'],
            length=test_case['length']
        )
        
        try:
            # Execute the graph
            print("\nExecuting graph...")
            start_time = time.time()
            result = blog_writer_graph.invoke(initial_state)
            end_time = time.time()
            
            print(f"Execution time: {end_time - start_time:.2f} seconds")
            
            # Check results
            if result.get('current_step') == 'completed':
                print("\n[SUCCESS] Research coordination successful!")
                
                # Display topic analysis summary
                topic_analysis = result.get('topic_analysis', {})
                print(f"\nTopic Analysis Summary:")
                print(f"  Main Topic: {topic_analysis.get('main_topic', 'N/A')}")
                print(f"  Complexity: {topic_analysis.get('complexity', 'N/A')}")
                print(f"  Subtopics: {len(topic_analysis.get('subtopics', []))}")
                
                # Display research plan
                research_plan = result.get('research_plan', {})
                if research_plan:
                    print(f"\nResearch Plan:")
                    print(f"  Strategy: {research_plan.get('strategy', 'N/A')}")
                    
                    print(f"\n  Focus Areas ({len(research_plan.get('focus_areas', []))}):")
                    for i, area in enumerate(research_plan.get('focus_areas', [])[:3]):
                        print(f"    {i+1}. {area}")
                        
                    print(f"\n  Resource Allocation:")
                    for area, count in list(research_plan.get('resource_allocation', {}).items())[:3]:
                        print(f"    - {area}: {count} searches")
                        
                    print(f"\n  Search Queries ({len(research_plan.get('search_queries', []))}):")
                    for i, query in enumerate(research_plan.get('search_queries', [])[:3]):
                        print(f"    {i+1}. {query}")
                
                # Display research tasks
                research_tasks = result.get('research_tasks', [])
                if research_tasks:
                    print(f"\n  Prioritized Tasks ({len(research_tasks)}):")
                    for i, task in enumerate(research_tasks[:3]):
                        print(f"    {i+1}. {task.get('task', 'N/A')} (Priority: {task.get('priority', 'N/A')})")
                
                # Show final output
                final_output = result.get('final_output', {})
                print(f"\nFinal Status: {final_output.get('status')}")
                print(f"Progress: {result.get('progress', 0) * 100:.0f}%")
                    
            else:
                print(f"\n[FAILED] Research coordination failed")
                print(f"Current step: {result.get('current_step')}")
                print(f"Errors: {result.get('errors', [])}")
                
        except Exception as e:
            print(f"\n[ERROR] Test failed with error: {e}")
            logger.error("Test error", exc_info=True)


def test_edge_cases():
    """Test edge cases and error handling"""
    
    print(f"\n{'='*50}")
    print("EDGE CASE TESTS")
    print(f"{'='*50}")
    
    # Test 1: Topic with minimal research questions
    print("\nTest 1: Simple topic that might generate few research questions")
    simple_state = initialize_blog_writer_state(
        blog_idea="Hello World program in Python"
    )
    
    try:
        result = blog_writer_graph.invoke(simple_state)
        if result.get('current_step') == 'completed':
            research_plan = result.get('research_plan', {})
            print(f"[SUCCESS] Handled simple topic gracefully")
            print(f"   Generated {len(research_plan.get('search_queries', []))} search queries")
        else:
            print(f"[FAILED] Failed to handle simple topic")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        
    # Test 2: Very complex multi-faceted topic
    print("\nTest 2: Very complex topic requiring extensive research")
    complex_state = initialize_blog_writer_state(
        blog_idea="Complete guide to building a SaaS platform: architecture, security, scalability, monitoring, deployment, pricing strategies, and customer acquisition",
        length="long"
    )
    
    try:
        result = blog_writer_graph.invoke(complex_state)
        if result.get('current_step') == 'completed':
            research_plan = result.get('research_plan', {})
            print(f"[SUCCESS] Handled complex topic successfully")
            print(f"   Focus areas: {len(research_plan.get('focus_areas', []))}")
            # Calculate total allocation only from numeric values
            allocation = research_plan.get('resource_allocation', {})
            numeric_values = [v for v in allocation.values() if isinstance(v, (int, float))]
            total_allocation = sum(numeric_values) if numeric_values else 0
            print(f"   Total resource allocation: {total_allocation}")
        else:
            print(f"[FAILED] Failed to handle complex topic")
    except Exception as e:
        print(f"[ERROR] Error: {e}")


def display_full_state_debug(state):
    """Display full state for debugging"""
    print("\n" + "-"*50)
    print("FULL STATE DEBUG:")
    print("-"*50)
    
    # Skip large content fields
    skip_fields = ['final_output', 'debug_info', 'blog_sections']
    
    for key, value in state.items():
        if key in skip_fields:
            print(f"{key}: <truncated>")
        elif isinstance(value, list) and len(value) > 3:
            print(f"{key}: [{len(value)} items] - First 3: {value[:3]}")
        elif isinstance(value, dict) and len(str(value)) > 200:
            print(f"{key}: <dict with {len(value)} keys>")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("BLOG WRITER - RESEARCH COORDINATOR TEST")
    print("Milestone 2, Step 2.2")
    print("="*50)
    
    # Make sure we have API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n[ERROR] GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key before running this test")
        sys.exit(1)
    
    # Run tests
    test_research_coordinator()
    test_edge_cases()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED")
    print("Check the logs above for detailed results")
    print("="*50) 