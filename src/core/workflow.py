from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.core.state import ContentState
from src.agents.query_handler import QueryHandlerAgent
from src.agents.research_agent import ResearchAgent
from src.agents.content_strategist import ContentStrategistAgent
from src.agents.blog_writer import BlogWriterAgent
from src.agents.linkedin_writer import LinkedInWriterAgent
from src.agents.image_generator import ImageGeneratorAgent


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def route_after_classify(state: ContentState) -> str:
    """Route from query classification to first processing node."""
    qt = state.get("query_type", "research")
    if qt == "image":
        return "image_generator"
    return "research"


def route_after_research(state: ContentState) -> str:
    """Route from research to the appropriate content writer."""
    qt = state.get("query_type", "research")
    routing = {
        "blog": "blog_writer",
        "linkedin": "linkedin_writer",
        "full_campaign": "content_strategy",
        "strategy": "content_strategy",
    }
    return routing.get(qt, "content_strategy")


def route_after_strategy(state: ContentState) -> str:
    qt = state.get("query_type", "research")
    if qt == "full_campaign":
        return "blog_writer"
    return "end"


def route_after_blog(state: ContentState) -> str:
    qt = state.get("query_type", "research")
    if qt == "full_campaign":
        return "linkedin_writer"
    return "end"


def route_after_linkedin(state: ContentState) -> str:
    qt = state.get("query_type", "research")
    if qt == "full_campaign":
        return "image_generator"
    return "end"


# ---------------------------------------------------------------------------
# Workflow factory
# ---------------------------------------------------------------------------

def create_workflow():
    """Build and compile the LangGraph multi-agent workflow."""
    query_handler = QueryHandlerAgent()
    researcher = ResearchAgent()
    strategist = ContentStrategistAgent()
    blog_writer = BlogWriterAgent()
    linkedin_writer = LinkedInWriterAgent()
    image_gen = ImageGeneratorAgent()

    graph = StateGraph(ContentState)

    # Register nodes
    graph.add_node("classify_query", query_handler.run)
    graph.add_node("research", researcher.run)
    graph.add_node("content_strategy", strategist.run)
    graph.add_node("blog_writer", blog_writer.run)
    graph.add_node("linkedin_writer", linkedin_writer.run)
    graph.add_node("image_generator", image_gen.run)

    # Entry point
    graph.add_edge(START, "classify_query")

    # classify_query → research OR image_generator
    graph.add_conditional_edges(
        "classify_query",
        route_after_classify,
        {
            "research": "research",
            "image_generator": "image_generator",
        },
    )

    # research → blog_writer | linkedin_writer | content_strategy
    graph.add_conditional_edges(
        "research",
        route_after_research,
        {
            "blog_writer": "blog_writer",
            "linkedin_writer": "linkedin_writer",
            "content_strategy": "content_strategy",
        },
    )

    # content_strategy → blog_writer (full_campaign) | END
    graph.add_conditional_edges(
        "content_strategy",
        route_after_strategy,
        {
            "blog_writer": "blog_writer",
            "end": END,
        },
    )

    # blog_writer → linkedin_writer (full_campaign) | END
    graph.add_conditional_edges(
        "blog_writer",
        route_after_blog,
        {
            "linkedin_writer": "linkedin_writer",
            "end": END,
        },
    )

    # linkedin_writer → image_generator (full_campaign) | END
    graph.add_conditional_edges(
        "linkedin_writer",
        route_after_linkedin,
        {
            "image_generator": "image_generator",
            "end": END,
        },
    )

    # image_generator always terminates
    graph.add_edge("image_generator", END)

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# Singleton workflow instance
_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow
