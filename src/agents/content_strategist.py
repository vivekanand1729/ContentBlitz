from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import get_llm
from src.core.state import ContentState


STRATEGY_PROMPT = """You are a content strategist. Transform the research below into a clear, reader-friendly content brief.

Original Query: {query}

Research Analysis:
{analysis}

Create a structured content brief with:

## Topic Overview
(Clear 2-3 sentence explanation of the topic for a general audience)

## Why This Matters
(Business/marketing relevance and why content creators should cover this)

## Content Angles
(5 unique angles or perspectives for creating content on this topic)

## Target Audience
(Who should read/engage with content on this topic)

## Key Messages
(3-5 core messages that should be conveyed in any content)

## Content Recommendations
(Specific recommendations for blog posts, LinkedIn posts, and visuals)

Keep it actionable, clear, and marketing-focused."""


class ContentStrategistAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=2048)

    def run(self, state: ContentState) -> dict:
        query = state.get("query", "")
        research = state.get("research_results", {})
        analysis = research.get("analysis", "No research available.")

        prompt = STRATEGY_PROMPT.format(query=query, analysis=analysis)

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
        except Exception as e:
            content = f"Content strategy generation failed: {str(e)}"

        return {
            "generated_content": content,
            "content_format": "strategy",
            "content_metadata": {
                "word_count": len(content.split()),
                "content_type": "Content Strategy Brief",
            },
            "messages": [AIMessage(content=content)],
        }
