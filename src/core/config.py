import os
from pathlib import Path
from dotenv import load_dotenv

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

load_dotenv()

_ROOT = Path(__file__).resolve().parent.parent.parent
_YAML_PATH = _ROOT / "config.yaml"


def _load_yaml() -> dict:
    if YAML_AVAILABLE and _YAML_PATH.exists():
        with open(_YAML_PATH) as f:
            return yaml.safe_load(f) or {}
    return {}


_yaml = _load_yaml()


def _y(*keys, default=None):
    node = _yaml
    for k in keys:
        if not isinstance(node, dict):
            return default
        node = node.get(k, default)
    return node


class Config:
    """
    Config reads environment variables at *instantiation* time, not class-definition
    time. This means st.secrets values injected into os.environ before the first
    import of this module are picked up correctly.
    """

    APP_VERSION = "1.0.0"

    def __init__(self):
        # API Keys — secrets source priority: st.secrets (injected) → .env → default ""
        self.ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
        self.TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

        # LLM
        self.LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", _y("llm", "provider", default="openai"))
        self.ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
        self.OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", _y("llm", "model", default="gpt-4o"))
        self.LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", _y("llm", "temperature", default=0.7)))
        self.LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", _y("llm", "max_tokens", default=4096)))

        # Fast/cheap model for lightweight tasks (classification, routing)
        self.FAST_MODEL: str = os.getenv("FAST_MODEL", _y("llm_fast", "model", default="gpt-4o-mini"))

        # Image Generation
        self.IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", _y("image_generation", "model", default="dall-e-3"))
        self.IMAGE_SIZE: str = os.getenv("IMAGE_SIZE", _y("image_generation", "size", default="1024x1024"))
        self.IMAGE_QUALITY: str = os.getenv("IMAGE_QUALITY", _y("image_generation", "quality", default="hd"))
        self.IMAGES_DIR: str = os.getenv("IMAGES_DIR", _y("image_generation", "output_dir", default="generated_images"))

        # Research
        self.MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", _y("research", "max_results", default=5)))
        self.SEARCH_DEPTH: str = os.getenv("SEARCH_DEPTH", _y("research", "search_depth", default="advanced"))

        # Content
        self.BLOG_MIN_WORDS: int = int(os.getenv("BLOG_MIN_WORDS", _y("content", "blog", "min_words", default=800)))
        self.LINKEDIN_MAX_CHARS: int = int(os.getenv("LINKEDIN_MAX_CHARS", _y("content", "linkedin", "max_chars", default=1600)))
        self.SEO_SCORE_THRESHOLD: float = float(_y("content", "seo_score_threshold", default=60))
        self.QUALITY_SCORE_THRESHOLD: float = float(_y("content", "quality_score_threshold", default=60))

        # UI
        self.APP_TITLE: str = _y("ui", "page_title", default="ContentBlitz")
        self.APP_ICON: str = _y("ui", "page_icon", default="⚡")

    def validate(self) -> list[str]:
        """Return list of missing required API keys."""
        missing = []
        if self.LLM_PROVIDER == "anthropic" and not self.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if self.LLM_PROVIDER == "openai" and not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY (required for DALL-E 3)")
        if not self.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        return list(dict.fromkeys(missing))

    @property
    def is_ready(self) -> bool:
        return len(self.validate()) == 0


# Singleton — instantiated once, after any st.secrets injection that happened
# before this module was first imported.
config = Config()
