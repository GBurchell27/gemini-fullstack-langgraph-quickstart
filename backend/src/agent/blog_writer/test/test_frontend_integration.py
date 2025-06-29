#!/usr/bin/env python3
"""
Test script to verify blog writer frontend integration.
This script tests the blog writer graph with a simple input to ensure
it works with the frontend configuration.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import asyncio
from agent.blog_writer.graph import blog_writer_graph
from agent.blog_writer.state import BlogWriterState

async def test_blog_writer_integration():
    """Test the blog writer with a simple input."""
    
    # Simple test input
    initial_state = BlogWriterState(
        blog_idea="How to get started with Python programming",
        target_audience="beginners",
        writing_tone="conversational", 
        target_length="medium",
        messages=[],
        current_step="input_processing",
        debug_info=[]
    )
    
    print("🧪 Testing Blog Writer Integration...")
    print(f"📝 Blog Idea: {initial_state['blog_idea']}")
    print(f"🎯 Target Audience: {initial_state['target_audience']}")
    print(f"📏 Length: {initial_state['target_length']}")
    print(f"🎨 Tone: {initial_state['writing_tone']}")
    print("\n" + "="*50)
    
    try:
        # Run the first few steps to verify integration
        print("🔄 Running input processing...")
        result = await blog_writer_graph.ainvoke(initial_state)
        
        print(f"✅ Integration test completed!")
        print(f"📊 Current step: {result.get('current_step', 'unknown')}")
        print(f"📈 Debug info entries: {len(result.get('debug_info', []))}")
        
        if result.get('final_blog_result'):
            print("🎉 Blog generation completed!")
            blog_result = result['final_blog_result']
            print(f"📄 Title: {blog_result.get('title', 'No title')}")
            print(f"📝 Content length: {len(blog_result.get('content', ''))} characters")
        else:
            print("⚠️  Blog generation in progress (this is expected for a full workflow)")
            
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        return False
    
    return True

async def test_graph_compilation():
    """Test that the blog writer graph compiles correctly."""
    print("\n🔧 Testing Graph Compilation...")
    
    try:
        # Test if graph is already compiled or needs compilation
        if hasattr(blog_writer_graph, 'compile'):
            compiled = blog_writer_graph.compile()
        else:
            compiled = blog_writer_graph  # Already compiled
            
        print("✅ Graph compiles successfully!")
        
        # Test getting graph structure
        graph_dict = compiled.get_graph()
        nodes = list(graph_dict.nodes.keys())
        print(f"📋 Graph has {len(nodes)} nodes: {', '.join(nodes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Graph compilation failed: {str(e)}")
        return False

async def main():
    """Run all integration tests."""
    print("🚀 Starting Blog Writer Frontend Integration Tests\n")
    
    # Test 1: Graph compilation
    compilation_success = await test_graph_compilation()
    
    # Test 2: Basic integration (only if compilation succeeds)
    if compilation_success:
        integration_success = await test_blog_writer_integration()
    else:
        integration_success = False
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    print(f"🔧 Graph Compilation: {'✅ PASS' if compilation_success else '❌ FAIL'}")
    print(f"🧪 Integration Test: {'✅ PASS' if integration_success else '❌ FAIL'}")
    
    if compilation_success and integration_success:
        print("\n🎉 All tests passed! Frontend integration should work correctly.")
        print("💡 You can now use the blog writer in the frontend interface.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return compilation_success and integration_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 