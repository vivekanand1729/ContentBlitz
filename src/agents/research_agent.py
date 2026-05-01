from langchain_core.messages import HumanMessage
from src.core.config import config
from src.core.llm import get_llm
from src.core.state import ContentState

try:
    from tavily import TavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


ANALYSIS_PROMPT = """You are a senior research analyst. Based on the search results below, create a comprehensive research report.

Topic: {query}

Search Results:
{results}

Write a structured research report with these sections:
## Executive Summary
(2-3 sentence overview of the key findings)

## Key Findings
(5-7 bullet points with the most important insights)

## Detailed Analysis
(2-3 paragraphs with in-depth analysis, trends, and implications)

## Key Statistics & Data Points
(Bullet list of quantitative facts and figures)

## Sources
(List the URLs/sources cited)

Be factual, cite specific data, and maintain a professional analytical tone."""


class ResearchAgent:
    def __init__(self):
        self.llm = get_llm(max_tokens=4096)
        self.tavily = None
        if TAVILY_AVAILABLE and config.TAVILY_API_KEY:
            self.tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

    def _search(self, query: str) -> dict:
        if self.tavily:
            try:
                return self.tavily.search(
                    query=query,
                    search_depth=config.SEARCH_DEPTH,
                    max_results=config.MAX_SEARCH_RESULTS,
                    include_answer=True,
                    include_raw_content=False,
                )
            except Exception as e:
                return {"error": str(e), "results": [], "answer": ""}
        return {
            "results": [],
            "answer": f"No search API configured. Using training knowledge for: {query}",
        }

    def run(self, state: ContentState) -> dict:
        query = state.get("query", "")
        search_data = self._search(query)

        formatted = []
        if search_data.get("answer"):
            formatted.append(f"Search Summary: {search_data['answer']}\n")
        for r in search_data.get("results", []):
            formatted.append(
                f"Title: {r.get('title', 'N/A')}\n"
                f"URL: {r.get('url', 'N/A')}\n"
                f"Content: {r.get('content', 'N/A')[:500]}\n"
            )

        results_text = "\n---\n".join(formatted) if formatted else "No search results available."
        prompt = ANALYSIS_PROMPT.format(query=query, results=results_text)

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            analysis = response.content
        except Exception as e:
            analysis = f"Research analysis unavailable: {str(e)}"

        return {
            "research_results": {
                "raw_results": search_data.get("results", []),
                "search_answer": search_data.get("answer", ""),
                "analysis": analysis,
                "query": query,
            }
        }
