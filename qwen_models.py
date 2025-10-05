import os
from typing import Literal, Optional

from pydantic_ai.models import KnownModelName
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings
from typing_extensions import TypeAliasType

api_key = os.environ.get("BAILIAN_API_KEY", "")

KnownModelName = TypeAliasType(
    'KnownModelName',
    Literal[
        "qwen-plus",
        "qwen-turbo",
        "qwen-max"
    ]
)

def qwen(model_name: KnownModelName| str, settings: Optional[ModelSettings] = None) -> OpenAIChatModel:
    return OpenAIChatModel(str(model_name), provider=OpenAIProvider(
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key,        
    ), settings=settings)

