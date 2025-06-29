"""
Test script for Topic Analyzer functionality

Run this to test Milestone 2 Step 2.1 implementation.
"""

import os
import logging
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agent.blog_writer import blog_writer_graph
from agent.blog_writer.state import initialize_blog_writer_state

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_topic_analyzer():
    """Test the topic analyzer with various blog ideas"""
    
    print("\n" + "="*50)
    print("TOPIC ANALYZER TEST")
    print("="*50)
    
    # Test cases
    test_cases = [
        {
            'name': 'Technical Blog',
            'idea': 'How to build a scalable microservices architecture with Python, covering API gateways, service discovery, and distributed tracing',
            'audience': 'senior backend developers',
            'tone': 'technical',
            'length': 'long'
        },
        {
            'name': 'Beginner-Friendly Blog',
            'idea': 'Getting started with Python programming for absolute beginners',
            'audience': 'beginners with no coding experience',
            'tone': 'casual',
            'length': 'medium'
        },
        {
            'name': 'Business Blog',
            'idea': 'Best practices for implementing agile methodology in remote teams',
            'audience': 'project managers and team leads',
            'tone': 'professional',
            'length': 'medium'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n{'='*50}")
        print(f"TEST: {test_case['name']}")
        print(f"{'='*50}")
        print(f"Idea: {test_case['idea'][:80]}...")
        print(f"Audience: {test_case['audience']}")
        print(f"Tone: {test_case['tone']}")
        
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
            result = blog_writer_graph.invoke(initial_state)
            
            # Check results
            if result.get('current_step') == 'completed':
                print("\n✅ Topic analysis successful!")
                
                # Display topic analysis results
                topic_analysis = result.get('topic_analysis', {})
                if topic_analysis:
                    print(f"\nMain Topic: {topic_analysis.get('main_topic', 'N/A')}")
                    print(f"Complexity: {topic_analysis.get('complexity', 'N/A')}")
                    
                    print("\nSubtopics:")
                    for i, subtopic in enumerate(topic_analysis.get('subtopics', [])[:3]):
                        print(f"  {i+1}. {subtopic}")
                        
                    print(f"\nAudience Insights:")
                    insights = topic_analysis.get('audience_insights', {})
                    if isinstance(insights, dict):
                        for key, value in list(insights.items())[:3]:
                            print(f"  - {key}: {value}")
                    else:
                        print(f"  {insights}")
                
                # Display research questions
                questions = result.get('research_questions', [])
                print(f"\nResearch Questions Generated: {len(questions)}")
                for i, question in enumerate(questions[:3]):
                    print(f"  {i+1}. {question}")
                    
                # Display keywords
                keywords = result.get('target_keywords', [])
                print(f"\nTarget Keywords: {keywords[:5]}")
                
                # Show final output
                if result.get('final_output'):
                    print(f"\nFinal Status: {result['final_output'].get('status')}")
                    
            else:
                print(f"\n❌ Topic analysis failed")
                print(f"Current step: {result.get('current_step')}")
                print(f"Errors: {result.get('errors', [])}")
                
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            logger.error("Test error", exc_info=True)


def test_error_handling():
    """Test error handling with invalid inputs"""
    
    print(f"\n{'='*50}")
    print("ERROR HANDLING TEST")
    print(f"{'='*50}")
    
    # Test with very short idea
    print("\nTest 1: Very short blog idea")
    error_state = initialize_blog_writer_state(
        blog_idea="AI"  # Too short
    )
    
    try:
        result = blog_writer_graph.invoke(error_state)
        if result.get('current_step') == 'failed':
            print("✅ Error correctly handled in input processor")
        else:
            print("❌ Error not caught properly")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    # Test with empty Gemini API key (save and restore)
    print("\nTest 2: Missing API key handling")
    original_key = os.environ.get('GEMINI_API_KEY')
    
    try:
        # Temporarily remove API key
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
            
        valid_state = initialize_blog_writer_state(
            blog_idea="How to implement OAuth2 authentication in a REST API"
        )
        
        result = blog_writer_graph.invoke(valid_state)
        if result.get('current_step') == 'failed':
            print("✅ Missing API key handled gracefully")
        else:
            print("❌ Missing API key not handled properly")
            
    finally:
        # Restore API key
        if original_key:
            os.environ['GEMINI_API_KEY'] = original_key


if __name__ == "__main__":
    print("\n" + "="*50)
    print("BLOG WRITER - TOPIC ANALYZER TEST")
    print("Milestone 2, Step 2.1")
    print("="*50)
    
    # Make sure we have API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n❌ ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key before running this test")
        sys.exit(1)
    
    # Run tests
    test_topic_analyzer()
    test_error_handling()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED")
    print("="*50) 