"""
Content Database Tool

Mock content database with semantic search capabilities for finding relevant internal content.
This module provides functionality to search existing blog content and identify linking opportunities.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
from dataclasses import dataclass

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class ContentItem:
    """Represents a piece of content in the database"""
    id: str
    title: str
    slug: str
    url: str
    content_snippet: str
    category: str
    tags: List[str]
    published_date: datetime
    meta_description: str
    word_count: int
    
class ContentDatabase:
    """
    Mock content database with semantic search capabilities.
    
    In production, this would connect to your actual content management system
    or database. For now, it provides mock data for systematic review content.
    """
    
    def __init__(self):
        """Initialize the content database with mock data"""
        self._mock_content = self._create_mock_content()
    
    def _create_mock_content(self) -> List[ContentItem]:
        """Create mock content data for systematic review topics"""
        
        base_date = datetime.now() - timedelta(days=365)
        
        mock_content = [
            ContentItem(
                id="sr-001",
                title="Complete Guide to Systematic Review Methodology",
                slug="systematic-review-methodology-guide",
                url="/blog/systematic-review-methodology-guide",
                content_snippet="A systematic review is a research method that uses explicit, systematic methods to collate and synthesize research evidence. This comprehensive guide covers the eight essential steps of conducting a systematic review, from developing research questions to reporting results.",
                category="Core Methodology",
                tags=["systematic review", "methodology", "research", "evidence synthesis"],
                published_date=base_date + timedelta(days=30),
                meta_description="Learn the complete methodology for conducting systematic reviews with this step-by-step guide covering all eight essential phases.",
                word_count=2800
            ),
            ContentItem(
                id="sr-002", 
                title="PRISMA Guidelines: Best Practices for Systematic Review Reporting",
                slug="prisma-guidelines-systematic-review-reporting",
                url="/blog/prisma-guidelines-systematic-review-reporting",
                content_snippet="The PRISMA (Preferred Reporting Items for Systematic Reviews and Meta-Analyses) statement provides essential guidelines for transparent reporting of systematic reviews. Learn how to implement these standards in your research.",
                category="Quality Standards",
                tags=["PRISMA", "reporting", "guidelines", "transparency"],
                published_date=base_date + timedelta(days=45),
                meta_description="Master PRISMA guidelines for systematic review reporting with practical examples and implementation tips.",
                word_count=2200
            ),
            ContentItem(
                id="sr-003",
                title="Database Search Strategies for Systematic Reviews",
                slug="database-search-strategies-systematic-reviews",
                url="/blog/database-search-strategies-systematic-reviews",
                content_snippet="Effective database searching is crucial for comprehensive systematic reviews. This guide covers search strategy development, database selection, and optimization techniques for MEDLINE, Embase, and other key databases.",
                category="Search & Literature Management",
                tags=["database search", "search strategy", "MEDLINE", "Embase"],
                published_date=base_date + timedelta(days=60),
                meta_description="Master database search strategies for systematic reviews with expert tips for MEDLINE, Embase, and specialized databases.",
                word_count=3200
            ),
            ContentItem(
                id="sr-004",
                title="Study Selection Criteria and Screening Processes",
                slug="study-selection-criteria-screening-processes",
                url="/blog/study-selection-criteria-screening-processes",
                content_snippet="Developing clear inclusion and exclusion criteria is fundamental to systematic review quality. Learn how to create robust selection criteria and implement efficient screening processes using modern tools.",
                category="Study Selection & Quality",
                tags=["study selection", "screening", "inclusion criteria", "exclusion criteria"],
                published_date=base_date + timedelta(days=75),
                meta_description="Learn to develop robust study selection criteria and implement efficient screening processes for systematic reviews.",
                word_count=2600
            ),
            ContentItem(
                id="sr-005",
                title="Meta-Analysis Fundamentals: When and How to Combine Studies",
                slug="meta-analysis-fundamentals-combining-studies",
                url="/blog/meta-analysis-fundamentals-combining-studies",
                content_snippet="Meta-analysis allows quantitative synthesis of study results in systematic reviews. Learn when meta-analysis is appropriate, how to assess heterogeneity, and which statistical models to use.",
                category="Data & Analysis",
                tags=["meta-analysis", "statistical synthesis", "heterogeneity", "effect size"],
                published_date=base_date + timedelta(days=105),
                meta_description="Learn meta-analysis fundamentals including when to combine studies, assessing heterogeneity, and choosing appropriate statistical models.",
                word_count=4200
            ),
            ContentItem(
                id="et-001",
                title="Evidence Tables in Systematic Reviews: Essential Components and Structure",
                slug="evidence-tables-systematic-reviews-components",
                url="/blog/evidence-tables-systematic-reviews-components",
                content_snippet="Evidence tables are crucial tools for organizing and presenting study data in systematic reviews. Learn the essential components including study characteristics, participant demographics, interventions, outcomes, and quality assessments that make evidence tables effective.",
                category="Data & Analysis",
                tags=["evidence tables", "data extraction", "study characteristics", "systematic review tools"],
                published_date=base_date + timedelta(days=120),
                meta_description="Master the essential components and structure of evidence tables for systematic reviews with practical examples and templates.",
                word_count=2400
            ),
            ContentItem(
                id="et-002",
                title="Data Extraction Forms vs Evidence Tables: When to Use Each",
                slug="data-extraction-forms-vs-evidence-tables",
                url="/blog/data-extraction-forms-vs-evidence-tables",
                content_snippet="Understanding the difference between data extraction forms and evidence tables is crucial for systematic review methodology. Data extraction forms capture raw data, while evidence tables present synthesized information for readers.",
                category="Data & Analysis",
                tags=["data extraction", "evidence tables", "systematic review methodology", "data management"],
                published_date=base_date + timedelta(days=135),
                meta_description="Learn when to use data extraction forms versus evidence tables in systematic reviews and how they complement each other.",
                word_count=1800
            ),
            ContentItem(
                id="et-003",
                title="Software Tools for Creating Evidence Tables: RevMan, Covidence, and More",
                slug="software-tools-evidence-tables-revman-covidence",
                url="/blog/software-tools-evidence-tables-revman-covidence",
                content_snippet="Modern software tools can streamline evidence table creation for systematic reviews. Compare popular options including RevMan, Covidence, DistillerSR, and Excel templates to find the best fit for your research team.",
                category="Management & Tools",
                tags=["evidence table software", "RevMan", "Covidence", "DistillerSR", "systematic review tools"],
                published_date=base_date + timedelta(days=150),
                meta_description="Compare the best software tools for creating evidence tables in systematic reviews, including RevMan, Covidence, and DistillerSR.",
                word_count=3100
            ),
            ContentItem(
                id="et-004",
                title="Quality Assessment Integration in Evidence Tables",
                slug="quality-assessment-integration-evidence-tables",
                url="/blog/quality-assessment-integration-evidence-tables",
                content_snippet="Integrating quality assessment results into evidence tables provides readers with immediate context about study reliability. Learn how to incorporate GRADE assessments, risk of bias ratings, and quality scores effectively.",
                category="Study Selection & Quality",
                tags=["quality assessment", "evidence tables", "GRADE", "risk of bias", "study quality"],
                published_date=base_date + timedelta(days=165),
                meta_description="Learn to integrate quality assessment results into evidence tables using GRADE, risk of bias tools, and quality scoring systems.",
                word_count=2700
            ),
            ContentItem(
                id="et-005",
                title="Evidence Table Templates and Examples for Different Review Types",
                slug="evidence-table-templates-examples-review-types",
                url="/blog/evidence-table-templates-examples-review-types",
                content_snippet="Different types of systematic reviews require different evidence table structures. Explore templates and examples for intervention reviews, diagnostic accuracy studies, prognostic reviews, and qualitative evidence synthesis.",
                category="Core Methodology",
                tags=["evidence table templates", "review types", "intervention reviews", "diagnostic accuracy", "qualitative synthesis"],
                published_date=base_date + timedelta(days=180),
                meta_description="Download evidence table templates for different systematic review types including intervention, diagnostic, and qualitative reviews.",
                word_count=2900
            ),
            ContentItem(
                id="et-006",
                title="Common Mistakes in Evidence Table Design and How to Avoid Them",
                slug="common-mistakes-evidence-table-design",
                url="/blog/common-mistakes-evidence-table-design",
                content_snippet="Avoid common pitfalls in evidence table design that can confuse readers and reduce review impact. Learn about overcrowding, inconsistent formatting, missing key data, and poor column organization.",
                category="Quality Standards",
                tags=["evidence table design", "common mistakes", "best practices", "table formatting"],
                published_date=base_date + timedelta(days=195),
                meta_description="Avoid common evidence table design mistakes with expert tips on formatting, organization, and data presentation.",
                word_count=2200
            ),
            ContentItem(
                id="et-007",
                title="Presenting Complex Interventions in Evidence Tables",
                slug="presenting-complex-interventions-evidence-tables",
                url="/blog/presenting-complex-interventions-evidence-tables",
                content_snippet="Complex interventions with multiple components require careful presentation in evidence tables. Learn strategies for summarizing multi-component interventions, behavioral interventions, and implementation details clearly.",
                category="Data & Analysis",
                tags=["complex interventions", "evidence tables", "intervention description", "multi-component interventions"],
                published_date=base_date + timedelta(days=210),
                meta_description="Master the presentation of complex multi-component interventions in evidence tables with clear formatting strategies.",
                word_count=2600
            )
        ]
        
        return mock_content
    
    def search_content(
        self, 
        query: str, 
        max_results: int = 5,
        category_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search content database for relevant articles.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            category_filter: Optional category to filter by
            
        Returns:
            List of matching content items with relevance scores
        """
        
        logger.info(f"Searching content database for: '{query}'")
        
        # Filter by category if specified
        content_pool = self._mock_content
        if category_filter:
            content_pool = [
                item for item in content_pool 
                if item.category.lower() == category_filter.lower()
            ]
            logger.info(f"Filtered to category '{category_filter}': {len(content_pool)} items")
        
        # Perform keyword search
        results = self._keyword_search(query, content_pool, max_results)
        
        logger.info(f"Found {len(results)} relevant content items")
        
        return results
    
    def _keyword_search(
        self, 
        query: str, 
        content_pool: List[ContentItem], 
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Perform keyword-based search with TF-IDF-like scoring"""
        
        query_words = set(query.lower().split())
        
        scored_items = []
        
        for item in content_pool:
            # Combine searchable text
            searchable_text = f"{item.title} {item.content_snippet} {' '.join(item.tags)}".lower()
            search_words = set(searchable_text.split())
            
            # Calculate simple relevance score
            common_words = query_words.intersection(search_words)
            
            # Basic scoring: number of matching words / total query words
            word_score = len(common_words) / len(query_words) if query_words else 0
            
            # Bonus for title matches
            title_words = set(item.title.lower().split())
            title_matches = query_words.intersection(title_words)
            title_bonus = len(title_matches) * 0.3
            
            # Bonus for tag matches
            tag_words = set(' '.join(item.tags).lower().split())
            tag_matches = query_words.intersection(tag_words)
            tag_bonus = len(tag_matches) * 0.2
            
            total_score = word_score + title_bonus + tag_bonus
            
            if total_score > 0:
                scored_items.append((item, total_score))
        
        # Sort by score and return top results
        scored_items.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for item, score in scored_items[:max_results]:
            results.append({
                'id': item.id,
                'title': item.title,
                'url': item.url,
                'slug': item.slug,
                'content_snippet': item.content_snippet,
                'category': item.category,
                'tags': item.tags,
                'published_date': item.published_date.isoformat(),
                'meta_description': item.meta_description,
                'word_count': item.word_count,
                'relevance_score': score,
                'search_method': 'keyword'
            })
        
        return results
    
    def find_linking_opportunities(
        self, 
        current_content: str, 
        current_topic: str,
        max_links: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find opportunities to link to existing content from new content.
        
        Args:
            current_content: The content being written
            current_topic: Main topic of current content
            max_links: Maximum number of link suggestions
            
        Returns:
            List of linking opportunities with suggested anchor text
        """
        
        logger.info(f"Finding linking opportunities for topic: {current_topic}")
        
        # Extract key phrases from current content for better matching
        content_phrases = self._extract_key_phrases(current_content)
        
        # Search for related content
        all_opportunities = []
        
        # Search using main topic
        topic_results = self.search_content(current_topic, max_results=3)
        all_opportunities.extend(topic_results)
        
        # Search using extracted phrases
        for phrase in content_phrases[:3]:  # Top 3 phrases
            phrase_results = self.search_content(phrase, max_results=2)
            all_opportunities.extend(phrase_results)
        
        # Remove duplicates and rank opportunities
        unique_opportunities = {}
        for opp in all_opportunities:
            item_id = opp['id']
            if item_id not in unique_opportunities:
                unique_opportunities[item_id] = opp
            else:
                # Keep the one with higher relevance score
                if opp['relevance_score'] > unique_opportunities[item_id]['relevance_score']:
                    unique_opportunities[item_id] = opp
        
        # Convert to linking opportunities with suggested anchor text
        linking_opportunities = []
        for opp in list(unique_opportunities.values())[:max_links]:
            # Generate suggested anchor text
            anchor_suggestions = self._generate_anchor_text(opp, current_content)
            
            linking_opportunities.append({
                'target_id': opp['id'],
                'target_title': opp['title'],
                'target_url': opp['url'],
                'category': opp['category'],
                'suggested_anchors': anchor_suggestions,
                'relevance_score': opp['relevance_score'],
                'context_snippet': opp['content_snippet'][:200],
                'link_value': self._calculate_link_value(opp, current_topic)
            })
        
        # Sort by link value (relevance + strategic value)
        linking_opportunities.sort(key=lambda x: x['link_value'], reverse=True)
        
        logger.info(f"Found {len(linking_opportunities)} linking opportunities")
        
        return linking_opportunities
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content for search"""
        
        # Simple phrase extraction - in production this would use NLP libraries
        sentences = re.split(r'[.!?]+', content)
        phrases = []
        
        for sentence in sentences:
            words = sentence.strip().split()
            if 3 <= len(words) <= 6:  # Extract 3-6 word phrases
                phrases.append(' '.join(words))
        
        # Remove very common words/phrases
        common_stopwords = ['this is', 'there are', 'it is', 'they are', 'we can']
        phrases = [p for p in phrases if not any(stop in p.lower() for stop in common_stopwords)]
        
        return phrases[:10]  # Return top 10 phrases
    
    def _generate_anchor_text(self, opportunity: Dict[str, Any], current_content: str) -> List[str]:
        """Generate suggested anchor text for linking"""
        
        anchors = []
        
        # Use title words
        title_words = opportunity['title'].split()
        if len(title_words) <= 5:
            anchors.append(opportunity['title'])
        
        # Use key tags as anchor text
        for tag in opportunity['tags'][:2]:
            if len(tag.split()) <= 3:
                anchors.append(tag)
        
        # Generate topic-based anchors
        category = opportunity['category'].lower()
        if 'methodology' in category:
            anchors.extend(['systematic review methodology', 'review methods'])
        elif 'quality' in category:
            anchors.extend(['quality assessment', 'study quality'])
        elif 'search' in category:
            anchors.extend(['literature search', 'database search'])
        elif 'analysis' in category:
            anchors.extend(['data analysis', 'statistical analysis'])
        
        # Remove duplicates and limit
        unique_anchors = []
        for anchor in anchors:
            if anchor not in unique_anchors:
                unique_anchors.append(anchor)
        
        return unique_anchors[:3]
    
    def _calculate_link_value(self, opportunity: Dict[str, Any], current_topic: str) -> float:
        """Calculate strategic value of a link"""
        
        base_score = opportunity['relevance_score']
        
        # Bonus for complementary categories
        category_bonus = 0.0
        category = opportunity['category'].lower()
        
        if 'methodology' in category:
            category_bonus = 0.2  # High value for methodology links
        elif 'quality' in category:
            category_bonus = 0.15
        elif 'tools' in category:
            category_bonus = 0.1
        
        # Bonus for recent content
        pub_date = datetime.fromisoformat(opportunity['published_date'])
        days_old = (datetime.now() - pub_date).days
        recency_bonus = max(0, (365 - days_old) / 365 * 0.1)  # Up to 0.1 bonus for recent content
        
        return base_score + category_bonus + recency_bonus

    def get_content_categories(self) -> List[str]:
        """Get all available content categories"""
        categories = list(set(item.category for item in self._mock_content))
        return sorted(categories)
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about the content database"""
        return {
            'total_items': len(self._mock_content),
            'categories': self.get_content_categories(),
            'total_words': sum(item.word_count for item in self._mock_content),
            'date_range': {
                'oldest': min(item.published_date for item in self._mock_content).isoformat(),
                'newest': max(item.published_date for item in self._mock_content).isoformat()
            }
        }


# Create a global instance for easy import
content_db = ContentDatabase() 