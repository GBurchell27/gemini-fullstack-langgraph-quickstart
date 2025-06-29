"""
Focused test for Research Coordinator functionality

This test verifies that the research coordinator properly:
1. Creates research strategies
2. Prioritizes tasks
3. Allocates resources
4. Generates search queries
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agent.blog_writer.state import BlogWriterState
from agent.blog_writer.nodes.research_coordinator import research_coordinator_node
from langchain_core.runnables import RunnableConfig
import json


def test_research_coordinator_direct():
    """Test the research coordinator node directly"""
    
    print("\n" + "="*50)
    print("RESEARCH COORDINATOR DIRECT TEST")
    print("="*50)
    
    # Test cases with different complexities
    test_cases = [
        {
            'name': 'Simple Technical Blog',
            'state': {
                'topic_analysis': {
                    'main_topic': 'Python List Comprehensions',
                    'subtopics': ['Basic Syntax', 'Use Cases', 'Performance'],
                    'complexity': 'low'
                },
                'research_questions': [
                    'What are list comprehensions in Python?',
                    'When should you use list comprehensions?',
                    'How do list comprehensions compare to loops in performance?'
                ],
                'target_keywords': ['python list comprehension', 'list comprehension tutorial'],
                'length': 'medium',
                'max_web_searches': 5
            }
        },
        {
            'name': 'Complex Architecture Blog',
            'state': {
                'topic_analysis': {
                    'main_topic': 'Microservices Architecture',
                    'subtopics': ['API Gateway', 'Service Discovery', 'Load Balancing', 'Monitoring'],
                    'complexity': 'high'
                },
                'research_questions': [
                    'What are the key components of microservices architecture?',
                    'How do API gateways work in microservices?',
                    'What are service discovery patterns?',
                    'How to implement distributed tracing?',
                    'What are best practices for microservices security?'
                ],
                'target_keywords': ['microservices', 'api gateway', 'service mesh'],
                'length': 'long',
                'max_web_searches': 8
            }
        }
    ]
    
    config = RunnableConfig()
    
    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"TEST: {test_case['name']}")
        print(f"{'='*50}")
        
        # Create state
        state = BlogWriterState(
            current_step='research_coordination',
            debug_info=[],
            errors=[],
            **test_case['state']
        )
        
        # Run the node
        try:
            result = research_coordinator_node(state, config)
            
            # Check results
            if result.get('research_plan'):
                plan = result['research_plan']
                print(f"\n[SUCCESS] Research plan created!")
                print(f"\nStrategy: {plan.get('strategy', 'N/A')[:100]}...")
                print(f"\nFocus Areas ({len(plan.get('focus_areas', []))}):")
                for i, area in enumerate(plan.get('focus_areas', [])[:3], 1):
                    print(f"  {i}. {area}")
                
                print(f"\nResource Allocation:")
                allocation = plan.get('resource_allocation', {})
                for key, value in allocation.items():
                    if key != 'description':
                        print(f"  - {key}: {value}")
                
                print(f"\nSearch Queries ({len(plan.get('search_queries', []))}):")
                for i, query in enumerate(plan.get('search_queries', [])[:3], 1):
                    print(f"  {i}. {query}")
                
                # Check tasks
                tasks = result.get('research_tasks', [])
                if tasks:
                    print(f"\nPrioritized Tasks ({len(tasks)}):")
                    for i, task in enumerate(tasks[:3], 1):
                        print(f"  {i}. {task.get('task', 'N/A')} (Priority: {task.get('priority', 'N/A')})")
                
            else:
                print(f"\n[FAILED] No research plan created")
                print(f"Errors: {result.get('errors', [])}")
                
        except Exception as e:
            print(f"\n[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()


def test_edge_cases():
    """Test edge cases and error scenarios"""
    
    print(f"\n{'='*50}")
    print("EDGE CASE TESTS")
    print(f"{'='*50}")
    
    config = RunnableConfig()
    
    # Test 1: Empty research questions
    print("\nTest 1: Empty research questions")
    state = BlogWriterState(
        current_step='research_coordination',
        topic_analysis={
            'main_topic': 'Test Topic',
            'complexity': 'low'
        },
        research_questions=[],  # Empty!
        target_keywords=['test'],
        debug_info=[],
        errors=[]
    )
    
    try:
        result = research_coordinator_node(state, config)
        if result.get('current_step') == 'failed':
            print("[SUCCESS] Properly handled empty research questions")
        else:
            print("[FAILED] Should have failed with empty research questions")
    except Exception as e:
        print(f"[ERROR] Unexpected exception: {e}")
    
    # Test 2: Very long list of research questions
    print("\nTest 2: Many research questions")
    state = BlogWriterState(
        current_step='research_coordination',
        topic_analysis={
            'main_topic': 'Comprehensive SaaS Guide',
            'complexity': 'high'
        },
        research_questions=[f"Question {i}" for i in range(20)],  # 20 questions!
        target_keywords=['saas'] * 10,
        max_web_searches=5,  # Limited searches
        debug_info=[],
        errors=[]
    )
    
    try:
        result = research_coordinator_node(state, config)
        if result.get('research_plan'):
            plan = result['research_plan']
            queries = plan.get('search_queries', [])
            print(f"[SUCCESS] Handled many questions gracefully")
            print(f"  Generated {len(queries)} search queries from 20 questions")
            print(f"  Max searches respected: {len(queries) <= 5}")
        else:
            print("[FAILED] Should have created a plan despite many questions")
    except Exception as e:
        print(f"[ERROR] Unexpected exception: {e}")


def test_output_format():
    """Test that output format matches expected schema"""
    
    print(f"\n{'='*50}")
    print("OUTPUT FORMAT TEST")
    print(f"{'='*50}")
    
    config = RunnableConfig()
    
    state = BlogWriterState(
        current_step='research_coordination',
        topic_analysis={
            'main_topic': 'REST API Design',
            'subtopics': ['HTTP Methods', 'Status Codes', 'Best Practices'],
            'complexity': 'medium'
        },
        research_questions=[
            'What are REST API design principles?',
            'How to handle authentication in REST APIs?',
            'What are common REST API patterns?'
        ],
        target_keywords=['rest api', 'api design'],
        length='medium',
        max_web_searches=5,
        debug_info=[],
        errors=[]
    )
    
    try:
        result = research_coordinator_node(state, config)
        
        # Validate output structure
        plan = result.get('research_plan', {})
        tasks = result.get('research_tasks', [])
        
        print("\nValidating output structure:")
        
        # Check research plan fields
        required_plan_fields = ['strategy', 'focus_areas', 'resource_allocation', 
                               'internal_content_opportunities', 'search_queries', 'timestamp']
        for field in required_plan_fields:
            if field in plan:
                print(f"  [SUCCESS] '{field}' present")
            else:
                print(f"  [FAILED] '{field}' missing")
        
        # Check research tasks structure
        if tasks and len(tasks) > 0:
            print(f"\n  [SUCCESS] Research tasks created: {len(tasks)}")
            task = tasks[0]
            required_task_fields = ['task', 'priority', 'search_count']
            for field in required_task_fields:
                if field in task:
                    print(f"  [SUCCESS] Task field '{field}' present")
                else:
                    print(f"  [FAILED] Task field '{field}' missing")
        else:
            print("  [FAILED] No research tasks created")
            
        # Check data types
        print("\nValidating data types:")
        print(f"  Strategy is string: {isinstance(plan.get('strategy'), str)}")
        print(f"  Focus areas is list: {isinstance(plan.get('focus_areas'), list)}")
        print(f"  Search queries is list: {isinstance(plan.get('search_queries'), list)}")
        print(f"  Resource allocation is dict: {isinstance(plan.get('resource_allocation'), dict)}")
        
    except Exception as e:
        print(f"\n[ERROR] Validation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "="*50)
    print("FOCUSED RESEARCH COORDINATOR TEST")
    print("="*50)
    
    # Make sure we have API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n[ERROR] GEMINI_API_KEY environment variable not set")
        sys.exit(1)
    
    # Run tests
    test_research_coordinator_direct()
    test_edge_cases()
    test_output_format()
    
    print("\n" + "="*50)
    print("ALL FOCUSED TESTS COMPLETED")
    print("="*50) 