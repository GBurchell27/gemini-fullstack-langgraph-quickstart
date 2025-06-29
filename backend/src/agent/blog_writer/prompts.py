"""
Blog Writer Prompts

Centralized prompts for all blog writer nodes.
"""

from datetime import datetime


def get_current_date() -> str:
    """Get current date in a readable format"""
    return datetime.now().strftime("%B %d, %Y")


# Topic Analysis Prompts
TOPIC_ANALYZER_PROMPT = """
You are an expert blog content strategist. Analyze the following blog idea and provide a comprehensive topic analysis.

Current Date: {current_date}
Blog Idea: {blog_idea}
Target Audience: {target_audience}
Tone: {tone}

Provide a detailed analysis including:

1. **Main Topic**: Clearly identify the core topic
2. **Subtopics**: List 3-5 important subtopics that should be covered
3. **Complexity Level**: Assess as 'low', 'medium', or 'high' based on:
   - Technical depth required
   - Audience expertise needed
   - Breadth of subject matter
   
4. **Research Questions**: Generate 5-10 specific research questions that need to be answered to write this blog comprehensively

5. **Target Keywords**: Identify 5-8 relevant keywords/phrases for SEO, including:
   - 1 primary keyword
   - 2-3 secondary keywords
   - 3-4 long-tail keywords

6. **Audience Insights**: Provide insights about the target audience as a dictionary with these keys:
   - "pain_points": What are their main pain points?
   - "solutions_seeking": What solutions are they looking for?
   - "detail_level": What level of detail do they expect?
   - "desired_action": What action should they take after reading?

Return your analysis in a structured format, ensuring audience_insights is a dictionary with the above keys.
"""

# Research Coordination Prompts
RESEARCH_COORDINATOR_PROMPT = """
Based on the topic analysis, create a detailed research plan.

Topic Analysis:
{topic_analysis}

Blog Length: {length}
Max Web Searches Available: {max_searches}

Create a prioritized research plan that includes:

1. **High Priority Queries** (essential information):
   - Core concepts and definitions
   - Current best practices
   - Key statistics and data

2. **Medium Priority Queries** (supporting information):
   - Examples and case studies
   - Common challenges and solutions
   - Industry trends

3. **Low Priority Queries** (nice-to-have):
   - Advanced techniques
   - Future predictions
   - Related topics

For each query, specify:
- The exact search query to use
- Why this information is important
- What type of content we're looking for (tutorials, research papers, news, etc.)

Also provide resource_allocation as a dictionary with numeric values, for example:
{{"technical_details": 4, "best_practices": 3, "examples": 2}}

Optimize the queries for web search effectiveness.
"""

# Content Strategy Prompts
CONTENT_STRATEGIST_PROMPT = """
You are a content strategist creating a detailed blog outline.

Research Summary:
{research_summary}

Blog Requirements:
- Target Audience: {target_audience}
- Tone: {tone}
- Length: {length} (target: {word_count} words)

Create a comprehensive content strategy including:

1. **Title Options**: Provide 3-5 compelling titles that:
   - Include the primary keyword
   - Are engaging and click-worthy
   - Accurately represent the content
   - Are under 60 characters

2. **Blog Outline**: Create a detailed outline with:
   - Introduction (hook, problem statement, preview)
   - Main sections (3-6 sections with subsections)
   - Conclusion (summary, key takeaways, CTA)

3. **Key Messages**: List 3-5 key messages/takeaways

4. **Call-to-Action Suggestions**: Provide 2-3 CTA options based on the content and audience

5. **Content Distribution**: Suggest word count for each section

Make sure the outline flows logically and covers all important aspects from the research.
"""

# Content Writing Prompts
INTRODUCTION_WRITER_PROMPT = """
Write an engaging introduction for this blog post.

Title: {title}
Target Audience: {target_audience}
Tone: {tone}
Key Points to Cover: {key_points}

The introduction should:
1. Start with a compelling hook (question, statistic, story, or bold statement)
2. Clearly state the problem or topic
3. Explain why this matters to the reader
4. Preview what they'll learn
5. Be approximately 150-200 words

Make it engaging and relevant to the target audience.
"""

BODY_SECTION_WRITER_PROMPT = """
Write a comprehensive section for this blog post.

Section Title: {section_title}
Section Outline: {section_outline}
Research Data: {research_data}
Target Keywords: {keywords}
Tone: {tone}

Requirements:
1. Cover all points in the outline
2. Include relevant data, statistics, or examples from research
3. Use clear subheadings if needed
4. Naturally incorporate keywords
5. Maintain the specified tone
6. Target length: {target_words} words

Write in a clear, engaging style that provides value to the reader.
"""

CONCLUSION_WRITER_PROMPT = """
Write a strong conclusion for this blog post.

Title: {title}
Key Messages: {key_messages}
Main Points Covered: {main_points}
Call-to-Action Options: {cta_options}

The conclusion should:
1. Summarize the key takeaways (without being repetitive)
2. Reinforce the value provided
3. Include a clear, compelling call-to-action
4. Leave the reader with something to think about
5. Be approximately 150-200 words

Make it memorable and action-oriented.
"""

# SEO Optimization Prompts
SEO_OPTIMIZER_PROMPT = """
Optimize this blog post for SEO.

Blog Title: {title}
Blog Content: {content}
Target Keywords: {keywords}

Provide:

1. **Meta Title** (max 60 characters):
   - Include primary keyword
   - Be compelling and accurate

2. **Meta Description** (max 160 characters):
   - Include primary keyword naturally
   - Summarize the value proposition
   - Include a soft CTA

3. **Tags** (5-8 relevant tags)

4. **Categories** (2-3 relevant categories)

5. **Keyword Analysis**:
   - Current keyword density
   - Suggestions for improvement

6. **Schema Markup** suggestions for better SERP display

Focus on natural optimization that provides value to readers while improving search visibility.
"""

# Quality Review Prompts
QUALITY_REVIEWER_PROMPT = """
Review this blog post for quality and completeness.

Blog Content:
{content}

Target Audience: {target_audience}
Tone: {tone}
Word Count Target: {target_word_count}
Actual Word Count: {actual_word_count}

Evaluate:

1. **Content Quality**:
   - Accuracy of information
   - Completeness of coverage
   - Value to target audience
   - Logical flow and structure

2. **Writing Quality**:
   - Clarity and readability
   - Grammar and style
   - Tone consistency
   - Engagement level

3. **SEO Optimization**:
   - Keyword usage (natural vs forced)
   - Meta data quality
   - Internal/external link quality

4. **Technical Aspects**:
   - Proper formatting
   - Link validity
   - Word count adherence

Provide:
- Overall quality score (0-100)
- List of issues found
- Specific improvement suggestions
- Readability score estimate

Be thorough but constructive in your feedback.
""" 