from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import get_llm
from src.core.state import ContentState
from src.utils.content_optimization import extract_hashtags


LINKEDIN_PROMPT = """You are a LinkedIn content expert who creates high-performing professional posts.

Topic: {query}

Research & Context:
{research}

Create an engaging LinkedIn post that:
- Length: 1200-1600 characters (optimal LinkedIn range)
- Opens with a POWERFUL hook (first line must stop the scroll — make it bold, surprising, or provocative)
- Uses short paragraphs (1-3 lines each) with blank line breaks for readability
- Tells a story or shares a compelling insight backed by data
- Includes specific insight, statistic, or lesson from the research
- Ends with an engaging question or strong call-to-action
- Professional yet personal tone — like advice from a trusted colleague
- Naturally incorporates 8-12 relevant hashtags at the end
- No generic corporate speak — make it human

Format:
[Hook — 1 powerful sentence]

[2-3 short paragraphs with core content]

[Key insight or lesson]

[Question or CTA]

#hashtag1 #hashtag2 ... #hashtag10

Write the complete LinkedIn post now:"""


class LinkedInWriterAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=1024)

    def run(self, state: ContentState) -> dict:
        query = state.get("query", "")
        research = state.get("research_results", {})
        analysis = research.get("analysis", "")

        prompt = LINKEDIN_PROMPT.format(
            query=query,
            research=analysis or "No prior research. Use your training knowledge.",
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content
        except Exception as e:
            content = f"LinkedIn post generation failed: {str(e)}"

        hashtags = extract_hashtags(content)
        return {
            "generated_content": content,
            "content_format": "linkedin",
            "content_metadata": {
                "char_count": len(content),
                "word_count": len(content.split()),
                "hashtag_count": len(hashtags),
                "hashtags": hashtags,
                "content_type": "LinkedIn Post",
                "topic": query,
            },
            "messages": [AIMessage(content=content)],
        }
