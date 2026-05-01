# ⚡ ContentBlitz — AI Content Marketing Assistant

A production-ready multi-agent AI system that generates research reports, SEO blog posts, LinkedIn posts, and marketing images from a single conversational interface.

🚀 **[Live Demo → contentblitz.streamlit.app](https://contentblitz.streamlit.app)**

## Architecture

```
User Query
    │
    ▼
┌──────────────────┐
│  Query Handler   │  Classifies intent → research | blog | linkedin | image | full_campaign
└────────┬─────────┘
         │
   ┌─────┴──────────────┐
   ▼                    ▼
Research Agent     Image Generator
(Tavily + GPT-4o)   (DALL-E 2)
   │
   ├─→ Content Strategist  (research reports & strategy briefs)
   ├─→ Blog Writer         (SEO-optimized long-form content)
   └─→ LinkedIn Writer     (professional social posts)
```

**LangGraph** orchestrates all agents with conversation memory across turns. Each session maintains full context via `MemorySaver`.

## Agents

| Agent | Responsibility |
|-------|---------------|
| Query Handler | Classifies user intent and routes to the correct pipeline |
| Deep Research | Tavily web search + GPT-4o analysis → structured research report |
| Content Strategist | Transforms research into actionable content briefs |
| SEO Blog Writer | Long-form articles with keyword optimization, H1/H2 structure, meta description |
| LinkedIn Post Writer | 1200-1600 char posts with hashtag strategy and engagement hooks |
| Image Generator | DALL-E 2 with LLM-enhanced prompts, saved locally |

## Setup

```bash
# 1. Clone / navigate to project
cd ContentBlitz

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env and add your keys:
#   OPENAI_API_KEY   — https://platform.openai.com
#   TAVILY_API_KEY   — https://tavily.com (free tier available)

# 5. Run
streamlit run src/web_app/streamlit_app.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | ✅ | — | GPT-4o for all LLM tasks + image generation |
| `TAVILY_API_KEY` | ✅ | — | Web research (free tier: 1000 req/month) |
| `OPENAI_MODEL` | ➖ | `gpt-4o` | LLM model |
| `IMAGE_MODEL` | ➖ | `dall-e-2` | Image model |
| `IMAGE_SIZE` | ➖ | `1024x1024` | Image dimensions |
| `MAX_SEARCH_RESULTS` | ➖ | `5` | Tavily results per query |
| `BLOG_MIN_WORDS` | ➖ | `800` | Minimum blog post length |

## Usage Examples

| What you type | What happens |
|---------------|-------------|
| "Research AI in healthcare trends 2025" | Research Agent → Content Strategist → structured report |
| "Write a blog post about remote work productivity" | Research Agent → Blog Writer → SEO article |
| "Create a LinkedIn post about sustainability in tech" | Research Agent → LinkedIn Writer → post with hashtags |
| "Generate a marketing image for a SaaS product launch" | Image Generator → DALL-E 2 image saved locally |
| "Full campaign: AI-powered customer service" | All 6 agents → research + strategy + blog + LinkedIn + image |

## Project Structure

```
ContentBlitz/
├── src/
│   ├── agents/
│   │   ├── query_handler.py       # Intent classification & routing
│   │   ├── research_agent.py      # Tavily search + GPT-4o analysis
│   │   ├── content_strategist.py  # Research → content brief
│   │   ├── blog_writer.py         # SEO blog generation
│   │   ├── linkedin_writer.py     # LinkedIn post generation
│   │   └── image_generator.py     # DALL-E 2 with prompt enhancement
│   ├── core/
│   │   ├── config.py              # Environment configuration
│   │   ├── state.py               # LangGraph TypedDict state
│   │   └── workflow.py            # Graph definition & routing logic
│   ├── utils/
│   │   ├── content_optimization.py  # SEO scoring, readability
│   │   └── quality_validation.py    # Content quality checks
│   └── web_app/
│       └── streamlit_app.py       # Chat UI with export
├── generated_images/              # DALL-E images saved here
├── requirements.txt
└── .env.example
```

## Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Orchestration | LangGraph 0.2 | Stateful multi-agent graphs with memory |
| LLM | GPT-4o | High-quality reasoning for content tasks |
| Research | Tavily AI | Purpose-built for LLM agents, includes answer synthesis |
| Images | DALL-E 2 | OpenAI image generation |
| UI | Streamlit | Rapid deployment, built-in chat components |
| Memory | LangGraph MemorySaver | Conversation context across turns |

## Alternatives

| Component | Used | Alternatives |
|-----------|------|-------------|
| LLM | GPT-4o | Claude Sonnet, Gemini 2.0 Flash |
| Orchestration | LangGraph | CrewAI, AutoGen |
| Research | Tavily | SERP API, Perplexity Sonar |
| Images | DALL-E 2 | DALL-E 3, Stability AI, Google Imagen |
| UI | Streamlit | Gradio, FastAPI + React |
