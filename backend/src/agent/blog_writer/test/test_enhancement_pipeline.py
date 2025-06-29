"""
Test Enhancement Pipeline

Tests the enhancement and output generation pipeline.
"""

import pytest
import sys
import os

# Add the blog_writer module to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state import BlogWriterState
from nodes.enhancement.internal_linking import internal_linking_node
from nodes.enhancement.external_linking import external_linking_node
from nodes.enhancement.seo_optimizer import seo_optimizer_node


def test_internal_linking_node():
    """Test internal linking node functionality."""
    print("\n" + "="*50)
    print("TESTING INTERNAL LINKING NODE")
    print("="*50)
    
    # Create test state with assembled content
    state = BlogWriterState(
        blog_idea="How to conduct systematic reviews",
        target_audience="researchers",
        tone="professional",
        assembled_content="""# How to Conduct Systematic Reviews

## Introduction

Systematic reviews are a critical component of evidence-based research. They provide a comprehensive and unbiased summary of existing research on a particular topic.

## Methodology

The methodology for systematic reviews involves several key steps including search strategy development, study selection, and data extraction.

## Conclusion

Following a rigorous systematic review methodology ensures reliable and reproducible results.""",
        internal_content_matches=[
            {
                'id': 'sr_guide_1',
                'title': 'Systematic Review Protocol Development',
                'url': '/systematic-review-protocol',
                'category': 'Core Methodology',
                'relevance_score': 0.9,
                'content': 'Guide to developing robust systematic review protocols...'
            }
        ],
        topic_analysis={
            'main_topic': 'systematic reviews',
            'target_keywords': ['systematic review', 'methodology', 'evidence-based research']
        },
        debug_info=[]
    )
    
    # Test internal linking node
    try:
        result_state = internal_linking_node(state, None)
        
        print(f"✓ Internal linking completed")
        print(f"✓ Current step: {result_state.get('current_step')}")
        print(f"✓ Content with links created: {bool(result_state.get('content_with_links'))}")
        print(f"✓ Internal links: {len(result_state.get('internal_links', []))}")
        
        # Check that next step is set correctly
        assert result_state.get('current_step') == 'external_linking'
        
        return result_state
        
    except Exception as e:
        print(f"✗ Internal linking failed: {str(e)}")
        raise


def test_external_linking_node():
    """Test external linking node functionality."""
    print("\n" + "="*50)
    print("TESTING EXTERNAL LINKING NODE")
    print("="*50)
    
    # Create test state with internal links
    state = BlogWriterState(
        blog_idea="How to conduct systematic reviews",
        target_audience="researchers",
        tone="professional",
        content_with_links="""# How to Conduct Systematic Reviews

## Introduction

Systematic reviews are a critical component of evidence-based research. They provide a comprehensive and unbiased summary of existing research on a particular topic.

## Methodology

The methodology for [systematic reviews](/systematic-review-protocol "Systematic Review Protocol Development") involves several key steps including search strategy development, study selection, and data extraction.

## Conclusion

Following a rigorous systematic review methodology ensures reliable and reproducible results.""",
        web_research_results=[
            {
                'title': 'PRISMA Guidelines',
                'url': 'https://prisma-statement.org',
                'snippet': 'Guidelines for systematic reviews and meta-analyses',
                'relevance_score': 0.95
            }
        ],
        topic_analysis={
            'main_topic': 'systematic reviews',
            'target_keywords': ['systematic review', 'methodology', 'evidence-based research']
        },
        research_summary={
            'key_insights': ['PRISMA guidelines are essential', 'Quality assessment is critical']
        },
        debug_info=[]
    )
    
    # Test external linking node
    try:
        result_state = external_linking_node(state, None)
        
        print(f"✓ External linking completed")
        print(f"✓ Current step: {result_state.get('current_step')}")
        print(f"✓ External links: {len(result_state.get('external_links', []))}")
        
        # Check that next step is set correctly
        assert result_state.get('current_step') == 'final_output'
        
        return result_state
        
    except Exception as e:
        print(f"✗ External linking failed: {str(e)}")
        raise


def test_seo_optimizer_node():
    """Test SEO optimizer node functionality."""
    print("\n" + "="*50)
    print("TESTING SEO OPTIMIZER NODE")
    print("="*50)
    
    # Create test state with enhanced content
    state = BlogWriterState(
        blog_idea="How to conduct systematic reviews",
        target_audience="researchers",
        tone="professional",
        content_with_links="""# How to Conduct Systematic Reviews

## Introduction

Systematic reviews are a critical component of evidence-based research.""",
        content_strategy={
            'title_options': [
                'How to Conduct Systematic Reviews: A Complete Guide',
                'Systematic Review Methodology for Researchers'
            ]
        },
        topic_analysis={
            'main_topic': 'systematic reviews',
            'target_keywords': ['systematic review', 'methodology', 'evidence-based research', 'PRISMA', 'meta-analysis']
        },
        debug_info=[]
    )
    
    # Test SEO optimizer node
    try:
        result_state = seo_optimizer_node(state, None)
        
        print(f"✓ SEO optimization completed")
        print(f"✓ SEO metadata created: {bool(result_state.get('seo_metadata'))}")
        
        seo_metadata = result_state.get('seo_metadata', {})
        print(f"✓ Meta title: {seo_metadata.get('meta_title', 'N/A')}")
        print(f"✓ Meta description: {seo_metadata.get('meta_description', 'N/A')[:50]}...")
        print(f"✓ URL slug: {seo_metadata.get('url_slug', 'N/A')}")
        print(f"✓ Focus keyword: {seo_metadata.get('focus_keyword', 'N/A')}")
        
        # Check that SEO metadata is properly created
        assert seo_metadata.get('meta_title')
        assert seo_metadata.get('meta_description')
        assert seo_metadata.get('url_slug')
        
        return result_state
        
    except Exception as e:
        print(f"✗ SEO optimization failed: {str(e)}")
        raise


def test_enhancement_pipeline_integration():
    """Test the complete enhancement pipeline integration."""
    print("\n" + "="*60)
    print("TESTING COMPLETE ENHANCEMENT PIPELINE")
    print("="*60)
    
    # Start with assembled content state
    initial_state = BlogWriterState(
        blog_idea="How to conduct systematic reviews",
        target_audience="researchers",
        tone="professional",
        assembled_content="""# How to Conduct Systematic Reviews

## Introduction

Systematic reviews are a critical component of evidence-based research. They provide a comprehensive and unbiased summary of existing research on a particular topic.

## Methodology

The methodology for systematic reviews involves several key steps including search strategy development, study selection, and data extraction.

## Conclusion

Following a rigorous systematic review methodology ensures reliable and reproducible results.""",
        content_strategy={
            'title_options': [
                'How to Conduct Systematic Reviews: A Complete Guide'
            ]
        },
        topic_analysis={
            'main_topic': 'systematic reviews',
            'target_keywords': ['systematic review', 'methodology', 'evidence-based research']
        },
        internal_content_matches=[
            {
                'id': 'sr_guide_1',
                'title': 'Systematic Review Protocol Development', 
                'url': '/systematic-review-protocol',
                'category': 'Core Methodology',
                'relevance_score': 0.9,
                'content': 'Guide to developing robust systematic review protocols...'
            }
        ],
        web_research_results=[
            {
                'title': 'PRISMA Guidelines',
                'url': 'https://prisma-statement.org',
                'snippet': 'Guidelines for systematic reviews and meta-analyses',
                'relevance_score': 0.95
            }
        ],
        research_summary={
            'key_insights': ['PRISMA guidelines are essential']
        },
        debug_info=[]
    )
    
    try:
        # Step 1: Internal linking
        print("\n1. Running internal linking...")
        state_after_internal = internal_linking_node(initial_state, None)
        print(f"   ✓ Internal links added: {len(state_after_internal.get('internal_links', []))}")
        
        # Step 2: External linking
        print("\n2. Running external linking...")
        state_after_external = external_linking_node(state_after_internal, None)
        print(f"   ✓ External links added: {len(state_after_external.get('external_links', []))}")
        
        # Step 3: SEO optimization
        print("\n3. Running SEO optimization...")
        final_state = seo_optimizer_node(state_after_external, None)
        print(f"   ✓ SEO metadata created: {bool(final_state.get('seo_metadata'))}")
        
        # Final validation
        print(f"\n🎉 ENHANCEMENT PIPELINE COMPLETE!")
        print(f"   - Final content length: {len(final_state.get('content_with_links', ''))}")
        print(f"   - Internal links: {len(final_state.get('internal_links', []))}")
        print(f"   - External links: {len(final_state.get('external_links', []))}")
        print(f"   - SEO metadata: {bool(final_state.get('seo_metadata'))}")
        print(f"   - Debug entries: {len(final_state.get('debug_info', []))}")
        
        return final_state
        
    except Exception as e:
        print(f"✗ Enhancement pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    print("Starting Enhancement Pipeline Tests...")
    
    try:
        # Run individual tests
        test_internal_linking_node()
        test_external_linking_node()
        test_seo_optimizer_node()
        
        # Run integration test
        test_enhancement_pipeline_integration()
        
        print(f"\n✅ All enhancement pipeline tests passed!")
        
    except Exception as e:
        print(f"\n❌ Tests failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 