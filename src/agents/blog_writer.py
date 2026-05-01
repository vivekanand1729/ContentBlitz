from langchain_core.messages import HumanMessage, AIMessage
from src.core.config import config
from src.core.llm import get_llm
from src.core.state import ContentState
from src.utils.content_optimization import calculate_seo_score


BLOG_PROMPT = """You are an expert SEO content writer. Write a comprehensive, search-optimized blog post.

Topic: {query}

Research & Context:
{research}

Requirements:
- Length: {min_words}+ words
- Start with: **Meta Description:** (1-2 sentences, max 160 chars)
- Then: # H1 Title (include the target keyword)
- Opening hook: compelling statistic, question, or bold statement
- Include a "## Key Takeaways" section near the top (bullet list)
- Use ## H2 and ### H3 subheadings throughout
- Keyword density: naturally integrate the topic keyword (1-2%)
- Include practical examples and actionable advice
- End with a clear call-to-action
- Professional but engaging tone — no filler content

Structure:
1. Meta Description
2. # H1 Title
3. Introduction with hook (150-200 words)
4. ## Key Takeaways
5. Main content sections with ## H2 headings (600-800 words total)
6. ## Practical Examples / Case Studies
7. ## Conclusion (with CTA)

Write the complete blog post now:"""


class BlogWriterAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=4096)

    def run(self, state: ContentState) -> dict:
        query = state.get("query", "")
        research = state.get("research_results", {})
        analysis = research.get("analysis", "")

        prompt = BLOG_PROMPT.format(
            query=query,
            research=analysis or "No prior research. Use your training knowledge.",
            min_words=config.BLOG_MIN_WORDS,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
        except Exception as e:
            content = f"Blog generation failed: {str(e)}"

        word_count = len(content.split())
        seo_score = calculate_seo_score(content, query)

        return {
            "generated_content": content,
            "content_format": "blog",
            "seo_score": seo_score,
            "content_metadata": {
                "word_count": word_count,
                "seo_score": seo_score,
                "content_type": "SEO Blog Post",
                "topic": query,
            },
            "messages": [AIMessage(content=content)],
        }
