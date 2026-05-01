# ⚡ ContentBlitz — AI Content Marketing Assistant

A production-ready multi-agent AI system that generates research reports, SEO blog posts, LinkedIn posts, and marketing images from a single conversational interface.

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
(Tavily + Claude)   (DALL-E 3)
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
| Deep Research | Tavily web search + Claude analysis → structured research report |
| Content Strategist | Transforms research into actionable content briefs |
| SEO Blog Writer | Long-form articles with keyword optimization, H1/H2 structure, meta description |
| LinkedIn Post Writer | 1200-1600 char posts with hashtag strategy and engagement hooks |
| Image Generator | DALL-E 3 with LLM-enhanced prompts, saved locally |

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
#   ANTHROPIC_API_KEY  — https://console.anthropic.com
#   OPENAI_API_KEY     — https://platform.openai.com (for DALL-E 3)
#   TAVILY_API_KEY     — https://tavily.com (free tier available)

# 5. Run
streamlit run src/web_app/streamlit_app.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | ✅ | — | Claude Sonnet 4.6 for all LLM tasks |
| `OPENAI_API_KEY` | ✅ | — | DALL-E 3 image generation |
| `TAVILY_API_KEY` | ✅ | — | Web research (free tier: 1000 req/month) |
| `ANTHROPIC_MODEL` | ➖ | `claude-sonnet-4-6` | LLM model |
| `IMAGE_MODEL` | ➖ | `dall-e-3` | Image model |
| `IMAGE_QUALITY` | ➖ | `hd` | `standard` or `hd` |
| `MAX_SEARCH_RESULTS` | ➖ | `5` | Tavily results per query |
| `BLOG_MIN_WORDS` | ➖ | `800` | Minimum blog post length |

## Usage Examples

| What you type | What happens |
|---------------|-------------|
| "Research AI in healthcare trends 2025" | Research Agent → Content Strategist → structured report |
| "Write a blog post about remote work productivity" | Research Agent → Blog Writer → SEO article |
| "Create a LinkedIn post about sustainability in tech" | Research Agent → LinkedIn Writer → post with hashtags |
| "Generate a marketing image for a SaaS product launch" | Image Generator → DALL-E 3 image saved locally |
| "Full campaign: AI-powered customer service" | All 6 agents → research + strategy + blog + LinkedIn + image |

## Project Structure

```
ContentBlitz/
├── src/
│   ├── agents/
│   │   ├── query_handler.py       # Intent classification & routing
│   │   ├── research_agent.py      # Tavily search + Claude analysis
│   │   ├── content_strategist.py  # Research → content brief
│   │   ├── blog_writer.py         # SEO blog generation
│   │   ├── linkedin_writer.py     # LinkedIn post generation
│   │   └── image_generator.py     # DALL-E 3 with prompt enhancement
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
| LLM | Claude Sonnet 4.6 | Superior reasoning for content tasks |
| Research | Tavily AI | Purpose-built for LLM agents, includes answer synthesis |
| Images | DALL-E 3 | Best-in-class marketing image quality |
| UI | Streamlit | Rapid deployment, built-in chat components |
| Memory | LangGraph MemorySaver | Conversation context across turns |

## Alternatives

| Component | Used | Alternatives |
|-----------|------|-------------|
| LLM | Claude Sonnet 4.6 | GPT-4o, Gemini 2.0 Flash |
| Orchestration | LangGraph | CrewAI, AutoGen |
| Research | Tavily | SERP API, Perplexity Sonar |
| Images | DALL-E 3 | Stability AI, Google Imagen |
| UI | Streamlit | Gradio, FastAPI + React |
