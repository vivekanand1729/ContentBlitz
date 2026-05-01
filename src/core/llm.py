"""Shared LLM factory — returns a LangChain-compatible chat model."""
from langchain_core.language_models.chat_models import BaseChatModel
from src.core.config import config


def get_llm(max_tokens: int = 2048) -> BaseChatModel:
    """Return the configured LLM (OpenAI or Anthropic)."""
    if config.LLM_PROVIDER == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.ANTHROPIC_MODEL,
                api_key=config.ANTHROPIC_API_KEY,
                max_tokens=max_tokens,
            )
        except ImportError:
            pass  # fall through to OpenAI

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=config.OPENAI_MODEL,
        api_key=config.OPENAI_API_KEY,
        max_tokens=max_tokens,
    )
