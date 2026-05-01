"""
ContentBlitz — AI Content Marketing Assistant
Entry point for Streamlit (local and Streamlit Cloud).

Secret resolution order:
  1. Streamlit secrets  → st.secrets  (Streamlit Cloud dashboard or .streamlit/secrets.toml)
  2. .env file / shell  → os.environ / python-dotenv
  3. config.yaml        → defaults
"""

# ── Step 1: Streamlit import (triggers st.secrets loading) ──────────────────
import streamlit as st
import os
import sys
from pathlib import Path

# ── Step 2: Path setup (before project imports) ─────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── Step 3: Inject st.secrets into os.environ BEFORE project modules load ───
#    This must run before `from src.core.config import config`.
#    Config reads os.environ at instantiation; if the module hasn't been
#    imported yet, injection here ensures the correct values are picked up.
_SECRET_KEYS = [
    "OPENAI_API_KEY",
    "TAVILY_API_KEY",
    "OPENAI_MODEL",
]

try:
    for _k in _SECRET_KEYS:
        # Only inject if not already set by .env / shell (env takes precedence)
        if _k in st.secrets and not os.environ.get(_k):
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass  # st.secrets unavailable outside Streamlit context (e.g. tests)

# ── Step 4: Project imports (config now sees injected secrets) ───────────────
import uuid
from datetime import datetime
from langchain_core.messages import HumanMessage

from src.core.config import config

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem 2rem; border-radius: 12px;
    color: white; margin-bottom: 1.5rem;
}
.main-header h1 { margin: 0; font-size: 2rem; }
.main-header p  { margin: 0.3rem 0 0; opacity: 0.9; font-size: 1rem; }

.badge { display: inline-block; padding: 3px 10px; border-radius: 20px;
         font-size: 0.75rem; font-weight: 600; margin-bottom: 6px; }
.badge-blog      { background:#dbeafe; color:#1e40af; }
.badge-linkedin  { background:#dcfce7; color:#166534; }
.badge-research  { background:#fef3c7; color:#92400e; }
.badge-strategy  { background:#f3e8ff; color:#6b21a8; }
.badge-image     { background:#fee2e2; color:#991b1b; }
.badge-campaign  { background:#e0f2fe; color:#075985; }

.metric-row { display:flex; gap:8px; margin:8px 0; flex-wrap:wrap; }
.metric-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;
               padding:6px 12px; font-size:0.8rem; color:#475569; }

.setup-box { background:#fffbeb; border:1px solid #f59e0b; border-radius:10px;
             padding:1.2rem 1.5rem; margin-bottom:1rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
BADGE_MAP = {
    "blog":          ("📝 SEO Blog Post",      "badge-blog"),
    "linkedin":      ("💼 LinkedIn Post",       "badge-linkedin"),
    "research":      ("🔬 Research Report",     "badge-research"),
    "strategy":      ("🎯 Content Strategy",    "badge-strategy"),
    "image":         ("🎨 Generated Image",     "badge-image"),
    "full_campaign": ("🚀 Full Campaign",       "badge-campaign"),
}

QUICK_PROMPTS = {
    "🔬 Research":       "Research the latest trends in {topic} with statistics and key insights.",
    "📝 Blog Post":      "Write an SEO-optimized blog post about {topic} for content marketers.",
    "💼 LinkedIn Post":  "Create an engaging LinkedIn post about {topic} with hashtag strategy.",
    "🎨 Generate Image": "Generate a professional marketing image for {topic}.",
    "🚀 Full Campaign":  "Create a full content campaign for {topic}: research, blog, LinkedIn post, and image.",
}


def badge_html(content_type: str) -> str:
    label, css = BADGE_MAP.get(content_type, ("📄 Content", "badge-research"))
    return f'<span class="badge {css}">{label}</span>'


def metrics_html(meta: dict, seo: float, quality: float) -> str:
    parts = []
    if meta.get("word_count"):
        parts.append(f"📊 {meta['word_count']} words")
    if meta.get("char_count"):
        parts.append(f"📊 {meta['char_count']} chars")
    if seo:
        parts.append(f"🔍 SEO {seo}/100")
    if quality:
        parts.append(f"⭐ Quality {quality:.0f}/100")
    if meta.get("hashtag_count"):
        parts.append(f"# {meta['hashtag_count']} hashtags")
    if not parts:
        return ""
    cards = "".join(f'<span class="metric-card">{p}</span>' for p in parts)
    return f'<div class="metric-row">{cards}</div>'


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "workflow" not in st.session_state:
    st.session_state.workflow = None  # lazy — only created when keys are present


def _get_workflow():
    """Lazy-initialise workflow; returns None if keys are missing."""
    if st.session_state.workflow is None:
        from src.core.workflow import get_workflow
        st.session_state.workflow = get_workflow()
    return st.session_state.workflow


def _reset_workflow():
    st.session_state.workflow = None
    st.session_state.chat_history = []
    st.session_state.session_id = str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Setup / missing-keys guard
# ---------------------------------------------------------------------------
def _show_setup_banner(missing: list[str]) -> None:
    """Non-fatal banner shown when API keys are absent."""
    st.markdown(f"""
    <div class="setup-box">
        <strong>⚠️ API Keys Required</strong><br>
        Missing: <code>{"</code>, <code>".join(missing)}</code><br><br>
        Add them using <strong>one</strong> of these methods, then refresh the page:
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["☁️ Streamlit Cloud / Local secrets.toml", "🗂 .env file"])

    with tab1:
        st.markdown("**Local:** create `.streamlit/secrets.toml` in the project root:")
        st.code("""OPENAI_API_KEY = "sk-proj-..."
TAVILY_API_KEY = "tvly-dev-..."
""", language="toml")
        st.markdown("**Streamlit Cloud:** go to *App Settings → Secrets* and paste the same TOML.")

    with tab2:
        st.markdown("Edit `.env` in the project root:")
        st.code("""OPENAI_API_KEY=sk-proj-...
TAVILY_API_KEY=tvly-dev-...
""", language="bash")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {config.APP_ICON} ContentBlitz")
    st.caption(f"v{config.APP_VERSION} · `{st.session_state.session_id[:8]}`")
    st.divider()

    # API status
    st.markdown("### 🔑 API Status")
    missing = config.validate()
    if missing:
        for key in missing:
            st.warning(f"Missing: `{key}`")
    else:
        st.success("All keys set ✓ (OpenAI)")

    st.divider()

    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    topic = st.text_input("Topic", placeholder="e.g. AI in healthcare", key="quick_topic")
    for label, template in QUICK_PROMPTS.items():
        if st.button(label, key=f"btn_{label}", use_container_width=True, disabled=not config.is_ready):
            if topic:
                st.session_state.pending_message = template.format(topic=topic)
                st.rerun()
            else:
                st.warning("Enter a topic first")

    st.divider()

    # Session
    st.markdown("### 🗂 Session")
    st.metric("Messages", len(st.session_state.chat_history))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear", use_container_width=True):
            _reset_workflow()
            st.rerun()
    with col2:
        ai_msgs = [m for m in st.session_state.chat_history if m["role"] == "assistant"]
        if ai_msgs:
            all_content = "\n\n---\n\n".join(
                f"## {m.get('content_type','').title()}\n\n{m['content']}"
                for m in ai_msgs
            )
            st.download_button(
                "📥 Export",
                data=all_content.encode(),
                file_name=f"contentblitz_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    st.divider()
    st.markdown("### ℹ️ Agent Guide")
    with st.expander("Content types"):
        st.markdown("""
| Request | Pipeline |
|---------|---------|
| Research / report | Research → Strategy |
| Blog post | Research → Blog Writer |
| LinkedIn post | Research → LinkedIn Writer |
| Image / visual | Image Generator |
| Full campaign | All 6 agents |
""")

# ---------------------------------------------------------------------------
# Main area — header
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="main-header">
    <h1>{config.APP_ICON} ContentBlitz</h1>
    <p>AI Content Marketing Assistant · OpenAI + LangGraph + Tavily</p>
</div>
""", unsafe_allow_html=True)

# Setup banner (non-fatal — still renders rest of page)
if missing:
    _show_setup_banner(missing)

# Agent pipeline diagram
with st.expander("🤖 Multi-Agent Pipeline", expanded=False):
    st.code("""
User Query
    │
    ▼
┌─────────────────┐
│  Query Handler  │  ← Classifies intent & routes
└────────┬────────┘
         │
   ┌─────┴──────────────────┐
   ▼                        ▼
Research Agent         Image Generator
(Tavily + LLM)         (DALL-E 3)
   │
   ├─→ Content Strategist   (research reports, strategy briefs)
   ├─→ Blog Writer           (SEO blog posts)
   └─→ LinkedIn Writer       (social posts with hashtags)
    """, language="text")

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
if not st.session_state.chat_history:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#94a3b8;">
        <div style="font-size:3rem;">✍️</div>
        <h3 style="color:#64748b;">Start creating content</h3>
        <p>Ask me to research a topic, write a blog post, create a LinkedIn post,<br>
        generate an image, or run a full content campaign.</p>
        <br>
        <p><em>Examples:</em><br>
        "Write an SEO blog post about remote work productivity"<br>
        "Create a LinkedIn post about AI trends in 2025"<br>
        "Research sustainable packaging in e-commerce"</p>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            ct = msg.get("content_type", "research")
            st.markdown(badge_html(ct), unsafe_allow_html=True)
            mh = metrics_html(msg.get("metadata", {}), msg.get("seo_score", 0), msg.get("quality_score", 0))
            if mh:
                st.markdown(mh, unsafe_allow_html=True)
            st.markdown(msg["content"])
            for img_path in msg.get("image_paths", []):
                if os.path.exists(img_path):
                    st.image(img_path, caption="AI Generated Image", use_container_width=True)
            st.download_button(
                "📥 Export",
                data=msg["content"].encode(),
                file_name=f"{ct}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                key=f"export_{msg.get('id', uuid.uuid4())}",
            )

# ---------------------------------------------------------------------------
# Workflow runner
# ---------------------------------------------------------------------------
def _run(user_input: str) -> None:
    """Add user message, invoke workflow, append assistant response."""
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Guard: refuse gracefully if keys are not ready
    if not config.is_ready:
        st.session_state.chat_history.append({
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": (
                "⚠️ **API keys not configured.**\n\n"
                "Please add your `OPENAI_API_KEY` and `TAVILY_API_KEY` "
                "to `.streamlit/secrets.toml` (or `.env`) and refresh the page."
            ),
            "content_type": "research",
            "metadata": {}, "seo_score": 0, "quality_score": 0, "image_paths": [],
        })
        return

    try:
        wf = _get_workflow()
        result = wf.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": st.session_state.session_id}},
        )
        ct = result.get("content_format", result.get("query_type", "research"))
        st.session_state.chat_history.append({
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": result.get("generated_content", "No content generated."),
            "content_type": ct,
            "metadata": result.get("content_metadata", {}),
            "seo_score": result.get("seo_score", 0.0),
            "quality_score": result.get("quality_score", 0.0),
            "image_paths": result.get("image_urls", []),
        })
    except Exception as e:
        st.session_state.chat_history.append({
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": f"❌ **Error:** {str(e)}\n\nCheck your API keys and try again.",
            "content_type": "research",
            "metadata": {}, "seo_score": 0, "quality_score": 0, "image_paths": [],
        })


# Quick-action button trigger
if "pending_message" in st.session_state:
    pending = st.session_state.pop("pending_message")
    with st.spinner("⚡ Agents working..."):
        _run(pending)
    st.rerun()

# Chat input — disabled with hint when keys are missing
input_placeholder = (
    "⚠️ Add API keys to start (see setup instructions above)"
    if not config.is_ready
    else "Ask me to research, write a blog, LinkedIn post, generate an image, or full campaign..."
)

if user_input := st.chat_input(input_placeholder, disabled=not config.is_ready):
    with st.spinner("⚡ Agents working — this may take 15-30 seconds..."):
        _run(user_input)
    st.rerun()
