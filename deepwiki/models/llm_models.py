from deepwiki.config import settings
from langchain_core.language_models.chat import BaseChatModel
from langchain_deepseek import ChatDeepSeek

def get_llm_model(use_local: bool = False) -> BaseChatModel:
    if use_local:
        pass
    else:
        return ChatDeepSeek(
            model=settings.model_name,
            api_key=settings.deepseek_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            timeout=settings.timeout,
        )