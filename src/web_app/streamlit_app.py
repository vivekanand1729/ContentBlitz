import streamlit as st
import uuid
import os
import sys
from pathlib import Path
from datetime import datetime
from langchain_core.messages import HumanMessage

# Ensure project root is on path when running from any directory
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.config import config
from src.core.workflow import get_workflow

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ContentBlitz",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0; opacity: 0.9; font-size: 1rem; }

    /* Content type badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .badge-blog      { background: #dbeafe; color: #1e40af; }
    .badge-linkedin  { background: #dcfce7; color: #166534; }
    .badge-research  { background: #fef3c7; color: #92400e; }
    .badge-strategy  { background: #f3e8ff; color: #6b21a8; }
    .badge-image     { background: #fee2e2; color: #991b1b; }
    .badge-campaign  { background: #e0f2fe; color: #075985; }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 8px;
        margin: 8px 0;
        flex-wrap: wrap;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px 12px;
        font-size: 0.8rem;
        color: #475569;
    }

    /* Chat messages */
    .stChatMessage { border-radius: 12px !important; }

    /* Sidebar quick actions */
    .quick-action { font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    # List of {role, content, content_type, metadata, image_paths}
    st.session_state.chat_history = []

if "workflow" not in st.session_state:
    st.session_state.workflow = get_workflow()

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
BADGE_MAP = {
    "blog": ("📝 SEO Blog Post", "badge-blog"),
    "linkedin": ("💼 LinkedIn Post", "badge-linkedin"),
    "research": ("🔬 Research Report", "badge-research"),
    "strategy": ("🎯 Content Strategy", "badge-strategy"),
    "image": ("🎨 Generated Image", "badge-image"),
    "full_campaign": ("🚀 Full Campaign", "badge-campaign"),
}

QUICK_PROMPTS = {
    "🔬 Deep Research": "Research the latest trends in {topic} and provide a comprehensive analysis with statistics.",
    "📝 SEO Blog": "Write an SEO-optimized blog post about {topic} targeting content marketers.",
    "💼 LinkedIn Post": "Create an engaging LinkedIn post about {topic} with hashtag strategy.",
    "🎨 Generate Image": "Generate a professional marketing image for {topic}.",
    "🚀 Full Campaign": "Create a full content campaign for {topic}: research, blog post, LinkedIn post, and image.",
}


def content_type_badge(content_type: str) -> str:
    label, css_class = BADGE_MAP.get(content_type, ("📄 Content", "badge-research"))
    return f'<span class="badge {css_class}">{label}</span>'


def render_metadata(metadata: dict, seo_score: float, quality_score: float) -> str:
    parts = []
    if metadata.get("word_count"):
        parts.append(f"📊 {metadata['word_count']} words")
    if metadata.get("char_count"):
        parts.append(f"📊 {metadata['char_count']} chars")
    if seo_score:
        parts.append(f"🔍 SEO: {seo_score}/100")
    if quality_score:
        parts.append(f"⭐ Quality: {quality_score:.0f}/100")
    if metadata.get("hashtag_count"):
        parts.append(f"# {metadata['hashtag_count']} hashtags")
    if not parts:
        return ""
    cards = "".join(f'<span class="metric-card">{p}</span>' for p in parts)
    return f'<div class="metric-row">{cards}</div>'


def run_workflow(user_input: str) -> dict:
    """Invoke the LangGraph workflow and return the final state."""
    workflow = st.session_state.workflow
    thread_config = {"configurable": {"thread_id": st.session_state.session_id}}
    result = workflow.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=thread_config,
    )
    return result


def export_content(content: str, filename_prefix: str) -> bytes:
    return content.encode("utf-8")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚡ ContentBlitz")
    st.caption(f"v{config.APP_VERSION} · Session `{st.session_state.session_id[:8]}`")

    st.divider()

    # API status
    st.markdown("### 🔑 API Status")
    missing_keys = config.validate()
    if missing_keys:
        for key in missing_keys:
            st.warning(f"Missing: `{key}`")
    else:
        st.success("All APIs configured ✓")

    st.divider()

    # Quick action templates
    st.markdown("### ⚡ Quick Actions")
    topic = st.text_input("Topic", placeholder="e.g. AI in healthcare", key="quick_topic")

    for label, template in QUICK_PROMPTS.items():
        if st.button(label, key=f"btn_{label}", use_container_width=True):
            if topic:
                st.session_state.pending_message = template.format(topic=topic)
                st.rerun()
            else:
                st.warning("Enter a topic first")

    st.divider()

    # Session controls
    st.markdown("### 🗂 Session")
    st.metric("Messages", len(st.session_state.chat_history))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.workflow = get_workflow()
            st.rerun()
    with col2:
        if st.session_state.chat_history:
            all_content = "\n\n---\n\n".join(
                f"## {msg.get('content_type', 'Content').title()}\n\n{msg['content']}"
                for msg in st.session_state.chat_history
                if msg["role"] == "assistant"
            )
            st.download_button(
                "📥 Export",
                data=export_content(all_content, "contentblitz_export"),
                file_name=f"contentblitz_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    st.divider()
    st.markdown("### ℹ️ Agent Guide")
    with st.expander("Content types"):
        st.markdown(
            """
| Request | Agent Used |
|---------|-----------|
| Research / report | Research + Strategy |
| Blog post | Research + Blog Writer |
| LinkedIn post | Research + LinkedIn Writer |
| Image / visual | Image Generator |
| Full campaign | All 6 agents |
"""
        )

# ---------------------------------------------------------------------------
# Main area — header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <h1>⚡ ContentBlitz</h1>
        <p>AI Content Marketing Assistant · Powered by Claude + LangGraph</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Agent pipeline diagram
with st.expander("🤖 Multi-Agent Pipeline", expanded=False):
    st.markdown(
        """
        ```
        User Query
            │
            ▼
        ┌─────────────────┐
        │  Query Handler  │  ← Classifies intent & routes
        └────────┬────────┘
                 │
         ┌───────┼───────┐
         ▼       ▼       ▼
      Research  Image   Direct
       Agent    Gen     Route
         │
    ┌────┴──────────────┐
    │                   │
    ▼                   ▼
 Blog Writer      LinkedIn Writer
    │                   │
    └────────┬──────────┘
             ▼
      Content Strategist
             │
             ▼
        Final Output
        ```
        """
    )

# ---------------------------------------------------------------------------
# Chat history display
# ---------------------------------------------------------------------------
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.markdown(
            """
            <div style="text-align:center; padding: 3rem 1rem; color: #94a3b8;">
                <div style="font-size: 3rem;">✍️</div>
                <h3 style="color: #64748b;">Start creating content</h3>
                <p>Ask me to research a topic, write a blog post, create a LinkedIn post,<br>
                generate an image, or run a full content campaign.</p>
                <br>
                <p><strong>Examples:</strong><br>
                "Write an SEO blog post about remote work productivity"<br>
                "Create a LinkedIn post about AI trends in 2025"<br>
                "Research sustainable packaging in e-commerce"</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        else:
            with st.chat_message("assistant"):
                content_type = msg.get("content_type", "research")
                metadata = msg.get("metadata", {})
                seo_score = msg.get("seo_score", 0)
                quality_score = msg.get("quality_score", 0)
                image_paths = msg.get("image_paths", [])

                # Badge and metrics
                st.markdown(content_type_badge(content_type), unsafe_allow_html=True)
                meta_html = render_metadata(metadata, seo_score, quality_score)
                if meta_html:
                    st.markdown(meta_html, unsafe_allow_html=True)

                # Main content
                st.markdown(msg["content"])

                # Inline images
                for img_path in image_paths:
                    if os.path.exists(img_path):
                        st.image(img_path, caption="AI Generated Image", use_container_width=True)

                # Per-message export
                col_exp, col_copy = st.columns([1, 4])
                with col_exp:
                    st.download_button(
                        "📥 Export",
                        data=msg["content"].encode("utf-8"),
                        file_name=f"{content_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        key=f"export_{msg.get('id', uuid.uuid4())}",
                    )

# ---------------------------------------------------------------------------
# Input handling
# ---------------------------------------------------------------------------

# Handle quick-action button triggers
if "pending_message" in st.session_state:
    pending = st.session_state.pop("pending_message")
    st.session_state.chat_history.append({"role": "user", "content": pending})
    with st.spinner("⚡ Agents are working..."):
        try:
            result = run_workflow(pending)
            content_type = result.get("content_format", result.get("query_type", "research"))
            generated = result.get("generated_content", "No content generated.")
            image_paths = result.get("image_urls", [])
            metadata = result.get("content_metadata", {})
            seo = result.get("seo_score", 0.0)
            quality = result.get("quality_score", 0.0)

            st.session_state.chat_history.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": generated,
                "content_type": content_type,
                "metadata": metadata,
                "seo_score": seo,
                "quality_score": quality,
                "image_paths": image_paths,
            })
        except Exception as e:
            st.session_state.chat_history.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": f"❌ Error: {str(e)}\n\nPlease check your API keys and try again.",
                "content_type": "research",
                "metadata": {},
                "seo_score": 0,
                "quality_score": 0,
                "image_paths": [],
            })
    st.rerun()

# Main chat input
if user_input := st.chat_input("Ask me to research, write a blog, LinkedIn post, generate an image, or run a full campaign..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.spinner("⚡ Agents are working — this may take 15-30 seconds..."):
        try:
            result = run_workflow(user_input)
            content_type = result.get("content_format", result.get("query_type", "research"))
            generated = result.get("generated_content", "No content generated.")
            image_paths = result.get("image_urls", [])
            metadata = result.get("content_metadata", {})
            seo = result.get("seo_score", 0.0)
            quality = result.get("quality_score", 0.0)

            st.session_state.chat_history.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": generated,
                "content_type": content_type,
                "metadata": metadata,
                "seo_score": seo,
                "quality_score": quality,
                "image_paths": image_paths,
            })
        except Exception as e:
            st.session_state.chat_history.append({
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": f"❌ Error: {str(e)}\n\nPlease check your API keys in your `.env` file.",
                "content_type": "research",
                "metadata": {},
                "seo_score": 0,
                "quality_score": 0,
                "image_paths": [],
            })

    st.rerun()
