"""Shared LLM factory — returns a LangChain-compatible chat model."""
from langchain_core.language_models.chat_models import BaseChatModel
from src.core.config import config


def get_llm(max_tokens: int = 2048, fast: bool = False) -> BaseChatModel:
    from langchain_openai import ChatOpenAI
    model = config.FAST_MODEL if fast else config.OPENAI_MODEL
    return ChatOpenAI(
        model=model,
        api_key=config.OPENAI_API_KEY,
        max_tokens=max_tokens,
        temperature=0.0 if fast else config.LLM_TEMPERATURE,
    )
