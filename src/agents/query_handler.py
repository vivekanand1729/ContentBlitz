from langchain_core.messages import HumanMessage, AIMessage
from src.core.llm import get_llm
from src.core.state import ContentState


CLASSIFICATION_PROMPT = """You are a content routing expert. Analyze the user's request and classify it into EXACTLY one of these categories:

- research    → User wants a comprehensive research report, analysis, or information deep-dive
- blog        → User wants an SEO-optimized blog post or article
- linkedin    → User wants a LinkedIn post or professional social content
- image       → User wants an image, visual, or graphic created
- full_campaign → User wants multiple content formats together (blog + LinkedIn + image + research)
- strategy    → User wants a content strategy, plan, or recommendations

Previous conversation context (if any):
{history}

Current request: {query}

Respond with ONLY the category name (lowercase). No explanation, no punctuation."""


class QueryHandlerAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=16, fast=True)

    def run(self, state: ContentState) -> dict:
        messages = state.get("messages", [])
        last_message = messages[-1].content if messages else ""

        history_summary = ""
        if len(messages) > 1:
            parts = []
            for msg in messages[:-1][-6:]:
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                parts.append(f"{role}: {msg.content[:200]}")
            history_summary = "\n".join(parts)

        prompt = CLASSIFICATION_PROMPT.format(
            history=history_summary or "None",
            query=last_message,
        )

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            query_type = response.content.strip().lower().strip(".,;")
        except Exception:
            query_type = "research"

        valid_types = {"research", "blog", "linkedin", "image", "full_campaign", "strategy"}
        if query_type not in valid_types:
            query_type = "research"

        return {
            "query": last_message,
            "query_type": query_type,
        }
