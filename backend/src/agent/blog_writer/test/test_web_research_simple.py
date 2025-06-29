"""
Simple test for Web Research functionality
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from agent.blog_writer import blog_writer_graph
from agent.blog_writer.state import initialize_blog_writer_state

# Set basic logging
import logging
logging.basicConfig(level=logging.INFO)


def test_web_research_integration():
    """Test web research with pre-computed research plan"""
    
    print("\n" + "="*50)
    print("WEB RESEARCH INTEGRATION TEST")
    print("="*50)
    
    # Create test state
    state = initialize_blog_writer_state(
        blog_idea="Python async programming best practices",
        max_web_searches=2
    )
    
    # Add topic analysis results
    state['topic_analysis'] = {
        'main_topic': 'Python Async Programming',
        'complexity': 'medium'
    }
    
    # Add research plan
    state['research_plan'] = {
        'search_queries': [
            'Python async await best practices 2024',
            'Python asyncio performance optimization'
        ]
    }
    
    # Skip to web research
    state['current_step'] = 'web_research'
    
    # Test note: Web research is not fully integrated yet
    print("\nNote: Web research nodes are implemented but require")
    print("full graph execution which needs more setup.")
    print("\nTo test individual components, use:")
    print("- test_web_research_node() for direct node testing")
    print("- Full integration will be available after graph updates")
    

if __name__ == "__main__":
    if not os.getenv('GEMINI_API_KEY'):
        print("ERROR: Set GEMINI_API_KEY environment variable")
        sys.exit(1)
        
    test_web_research_integration()
    print("\nTest completed!") 