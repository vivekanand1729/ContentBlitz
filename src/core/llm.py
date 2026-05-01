"""Shared LLM factory — returns a LangChain-compatible chat model."""
from langchain_core.language_models.chat_models import BaseChatModel
from src.core.config import config


def get_llm(max_tokens: int = 2048, fast: bool = False) -> BaseChatModel:
    """Return the configured LLM (OpenAI or Anthropic).

    fast=True uses the lightweight model defined in config.yaml llm_fast
    for cheap tasks like query classification.
    """
    if config.LLM_PROVIDER == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=config.ANTHROPIC_MODEL,
                api_key=config.ANTHROPIC_API_KEY,
                max_tokens=max_tokens,
                temperature=0.0 if fast else config.LLM_TEMPERATURE,
            )
        except ImportError:
            pass  # fall through to OpenAI

    from langchain_openai import ChatOpenAI
    model = config.FAST_MODEL if fast else config.OPENAI_MODEL
    return ChatOpenAI(
        model=model,
        api_key=config.OPENAI_API_KEY,
        max_tokens=max_tokens,
        temperature=0.0 if fast else config.LLM_TEMPERATURE,
    )
