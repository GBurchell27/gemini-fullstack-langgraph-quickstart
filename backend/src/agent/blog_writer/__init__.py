"""
SEO Blog Writer System for LangGraph

This module implements a multi-agent blog writing system that:
- Analyzes blog topics and generates research questions
- Conducts web and internal content research
- Creates structured blog content with SEO optimization
- Adds internal and external linking
- Generates markdown output with metadata
"""

from .state import BlogWriterState
from .schemas import BlogRequest, BlogResult

# Graph will be imported after other modules are loaded
__all__ = ['BlogWriterState', 'BlogRequest', 'BlogResult', 'blog_writer_graph']

# Import graph after other modules
try:
    from .graph import blog_writer_graph
except ImportError as e:
    print(f"Warning: Could not import blog_writer_graph: {e}")
    blog_writer_graph = None 