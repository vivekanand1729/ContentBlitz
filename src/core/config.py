import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # LLM Settings — defaults to OpenAI; set LLM_PROVIDER=anthropic to use Claude
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Image Settings
    IMAGE_MODEL: str = os.getenv("IMAGE_MODEL", "dall-e-3")
    IMAGE_SIZE: str = os.getenv("IMAGE_SIZE", "1024x1024")
    IMAGE_QUALITY: str = os.getenv("IMAGE_QUALITY", "hd")
    IMAGES_DIR: str = os.getenv("IMAGES_DIR", "generated_images")

    # Research Settings
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    SEARCH_DEPTH: str = os.getenv("SEARCH_DEPTH", "advanced")

    # Content Settings
    BLOG_MIN_WORDS: int = int(os.getenv("BLOG_MIN_WORDS", "800"))
    LINKEDIN_MAX_CHARS: int = int(os.getenv("LINKEDIN_MAX_CHARS", "1600"))

    # App Info
    APP_TITLE: str = "ContentBlitz - AI Content Marketing Assistant"
    APP_VERSION: str = "1.0.0"

    @classmethod
    def validate(cls) -> list[str]:
        missing = []
        if cls.LLM_PROVIDER == "anthropic" and not cls.ANTHROPIC_API_KEY:
            missing.append("ANTHROPIC_API_KEY")
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY")
        if not cls.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY (for DALL-E 3 image generation)")
        if not cls.TAVILY_API_KEY:
            missing.append("TAVILY_API_KEY")
        return list(dict.fromkeys(missing))  # deduplicate


config = Config()
