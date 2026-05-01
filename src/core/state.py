from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ContentState(TypedDict):
    # Conversation history — append-only via add_messages reducer
    messages: Annotated[list[BaseMessage], add_messages]

    # Routing
    query: str
    query_type: str  # research | blog | linkedin | image | full_campaign | strategy

    # Agent outputs
    research_results: dict        # raw results + Claude analysis
    generated_content: str        # final content (blog/linkedin/research report)
    content_format: str           # blog | linkedin | research | image
    image_urls: list[str]         # DALL-E generated image URLs/paths

    # Metadata
    content_metadata: dict        # word count, hashtags, seo score, etc.
    seo_score: float
    quality_score: float
    error: Optional[str]
