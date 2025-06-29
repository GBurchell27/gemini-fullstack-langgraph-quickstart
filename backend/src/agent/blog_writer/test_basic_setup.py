"""
Test script for basic blog writer setup

Run this to verify the foundation is working correctly.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agent.blog_writer import BlogWriterState, BlogRequest, blog_writer_graph
from agent.blog_writer.state import initialize_blog_writer_state

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_state_initialization():
    """Test state initialization"""
    print("\n" + "="*50)
    print("TEST 1: State Initialization")
    print("="*50)
    
    state = initialize_blog_writer_state(
        blog_idea="How to implement a REST API in Python using FastAPI",
        target_audience="intermediate developers",
        tone="technical",
        length="medium"
    )
    
    print(f"Blog idea: {state['blog_idea']}")
    print(f"Target audience: {state['target_audience']}")
    print(f"Tone: {state['tone']}")
    print(f"Length: {state['length']}")
    print(f"Current step: {state['current_step']}")
    print(f"Progress: {state['progress']}")
    print("✅ State initialization successful")
    
    return state


def test_input_validation():
    """Test input validation with schema"""
    print("\n" + "="*50)
    print("TEST 2: Input Validation")
    print("="*50)
    
    # Test valid input
    try:
        valid_request = BlogRequest(
            idea="How to build a machine learning model for sentiment analysis",
            target_audience="data scientists",
            tone="technical",
            length="long"
        )
        print("✅ Valid request passed validation")
        print(f"   Validated idea: {valid_request.idea[:50]}...")
    except Exception as e:
        print(f"❌ Valid request failed: {e}")
        
    # Test invalid input (too short)
    try:
        invalid_request = BlogRequest(
            idea="ML",  # Too short
            tone="casual"
        )
        print("❌ Invalid request should have failed")
    except Exception as e:
        print(f"✅ Invalid request correctly rejected: {e}")
        
    # Test invalid tone
    try:
        invalid_tone = BlogRequest(
            idea="How to use Python decorators effectively",
            tone="funny"  # Not allowed
        )
        print("❌ Invalid tone should have failed")
    except Exception as e:
        print(f"✅ Invalid tone correctly rejected: {e}")


def test_graph_execution():
    """Test basic graph execution"""
    print("\n" + "="*50)
    print("TEST 3: Graph Execution")
    print("="*50)
    
    if blog_writer_graph is None:
        print("❌ Graph not initialized")
        return
        
    # Create initial state
    initial_state = initialize_blog_writer_state(
        blog_idea="Best practices for Python error handling and logging",
        target_audience="Python developers",
        tone="professional",
        length="medium"
    )
    
    print("Executing graph...")
    
    try:
        # Execute the graph
        result = blog_writer_graph.invoke(initial_state)
        
        print(f"✅ Graph execution completed")
        print(f"   Final step: {result.get('current_step')}")
        print(f"   Progress: {result.get('progress')}")
        print(f"   Errors: {len(result.get('errors', []))}")
        
        if result.get('final_output'):
            print(f"   Output: {result['final_output']}")
            
        if result.get('errors'):
            print("   Errors encountered:")
            for error in result['errors']:
                print(f"     - {error}")
                
    except Exception as e:
        print(f"❌ Graph execution failed: {e}")
        logger.error("Graph execution error", exc_info=True)


def test_error_handling():
    """Test error handling"""
    print("\n" + "="*50)
    print("TEST 4: Error Handling")
    print("="*50)
    
    if blog_writer_graph is None:
        print("❌ Graph not initialized")
        return
        
    # Test with empty blog idea
    error_state = initialize_blog_writer_state(
        blog_idea=""  # This should trigger validation error
    )
    
    try:
        result = blog_writer_graph.invoke(error_state)
        
        if result.get('current_step') == 'failed':
            print("✅ Error correctly handled")
            print(f"   Errors: {result.get('errors', [])}")
        else:
            print("❌ Error not properly handled")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("BLOG WRITER BASIC SETUP TEST")
    print("="*50)
    
    # Run all tests
    test_state_initialization()
    test_input_validation()
    test_graph_execution()
    test_error_handling()
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED")
    print("="*50) 