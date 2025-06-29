"""
Test script for Blog Writer API integration

This tests the blog writer through the LangGraph API endpoints.
"""

import requests
import json
import time
import logging
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_BASE_URL = "http://localhost:2024"  # Default LangGraph API port


def test_blog_writer_api():
    """Test the blog writer through LangGraph API"""
    
    print("\n" + "="*50)
    print("BLOG WRITER API TEST")
    print("="*50)
    
    # Test data
    blog_request = {
        "blog_idea": "How to build a scalable microservices architecture with Python",
        "target_audience": "senior developers",
        "tone": "technical",
        "length": "medium"
    }
    
    print(f"\nTest Request:")
    print(json.dumps(blog_request, indent=2))
    
    try:
        # Create a thread for the conversation
        print("\n1. Creating thread...")
        thread_response = requests.post(
            f"{API_BASE_URL}/threads",
            headers={"Content-Type": "application/json"}
        )
        
        if thread_response.status_code != 200:
            print(f"❌ Failed to create thread: {thread_response.status_code}")
            print(thread_response.text)
            return
            
        thread = thread_response.json()
        thread_id = thread.get('thread_id')
        print(f"✅ Thread created: {thread_id}")
        
        # Invoke the blog writer
        print("\n2. Invoking blog writer...")
        invoke_url = f"{API_BASE_URL}/threads/{thread_id}/runs"
        
        invoke_payload = {
            "assistant_id": "blog_writer",
            "input": blog_request
        }
        
        invoke_response = requests.post(
            invoke_url,
            headers={"Content-Type": "application/json"},
            json=invoke_payload
        )
        
        if invoke_response.status_code != 200:
            print(f"❌ Failed to invoke blog writer: {invoke_response.status_code}")
            print(invoke_response.text)
            return
            
        run = invoke_response.json()
        run_id = run.get('run_id')
        print(f"✅ Blog writer invoked: {run_id}")
        
        # Poll for status
        print("\n3. Polling for results...")
        max_polls = 30  # 30 seconds max
        poll_count = 0
        
        while poll_count < max_polls:
            time.sleep(1)
            poll_count += 1
            
            status_response = requests.get(
                f"{API_BASE_URL}/threads/{thread_id}/runs/{run_id}"
            )
            
            if status_response.status_code != 200:
                print(f"❌ Failed to get status: {status_response.status_code}")
                return
                
            status = status_response.json()
            run_status = status.get('status')
            
            print(f"   Status: {run_status} (poll {poll_count}/{max_polls})")
            
            if run_status in ['success', 'error']:
                break
                
        # Get final result
        print("\n4. Final result:")
        if run_status == 'success':
            result_response = requests.get(
                f"{API_BASE_URL}/threads/{thread_id}/runs/{run_id}"
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                output = result.get('output', {})
                
                print("✅ Blog creation successful!")
                print(f"   Current step: {output.get('current_step')}")
                print(f"   Progress: {output.get('progress')}")
                print(f"   Errors: {len(output.get('errors', []))}")
                
                if output.get('final_output'):
                    print(f"   Final output: {json.dumps(output['final_output'], indent=2)}")
            else:
                print(f"❌ Failed to get result: {result_response.status_code}")
        else:
            print(f"❌ Blog creation failed with status: {run_status}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        logger.error("API test error", exc_info=True)


def test_direct_graph_invoke():
    """Test invoking the graph directly (fallback test)"""
    
    print("\n" + "="*50)
    print("DIRECT GRAPH INVOCATION TEST")
    print("="*50)
    
    try:
        from agent.blog_writer import blog_writer_graph
        from agent.blog_writer.state import initialize_blog_writer_state
        
        # Create initial state
        initial_state = initialize_blog_writer_state(
            blog_idea="Best practices for API design in Python",
            target_audience="backend developers",
            tone="technical",
            length="medium"
        )
        
        print("Invoking graph directly...")
        result = blog_writer_graph.invoke(initial_state)
        
        print("✅ Direct invocation successful!")
        print(f"   Final step: {result.get('current_step')}")
        print(f"   Progress: {result.get('progress')}")
        
        if result.get('final_output'):
            print(f"   Output: {json.dumps(result['final_output'], indent=2)}")
            
    except Exception as e:
        print(f"❌ Direct invocation failed: {e}")
        logger.error("Direct invocation error", exc_info=True)


if __name__ == "__main__":
    print("\nStarting Blog Writer API tests...")
    print("Make sure the LangGraph API server is running on port 2024")
    print("Run with: langgraph up")
    
    # Try API test first
    test_blog_writer_api()
    
    # Also test direct invocation
    test_direct_graph_invoke() 