from llama_index.core.bridge.pydantic import BaseModel
from pydantic_settings import BaseSettings
from dataclasses import dataclass
from pydantic import BaseModel
import dotenv 
dotenv.load_dotenv()
import os
from src.prompt import (LLM_SYSTEM_PROMPT)

class Settings(BaseSettings):
    QDRANT_URL: str = "http://qdrant:6333"
    GEMINI_API_KEY: str
    
    class Config:
        env_file = ".env"
# base pydantic model
class QdrantPayload(BaseModel):
    """
    Payload for the vector

    Args:
        document_id (str): Document ID
        text (str): Text content, required to be able to be used with llama_index
        vector_id (str): Vector ID
    """

    document_id: str
    text: str
    vector_id: str

class LLMConfig(BaseModel):
    api_key: str
    model_name: str
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 2048
    system_prompt: str = "You are a helpful assistant."

class Config:
    OPENAI_CONFIG = LLMConfig(
        api_key=os.environ.get('OPENAI_API_KEY'),
        model_name="GPT",
        model_id="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens= 2048,
        system_prompt=LLM_SYSTEM_PROMPT
    )

    GEMINI_CONFIG = LLMConfig(
        api_key=os.environ.get('GOOGLE_API_KEY'),
        model_name="Gemini",
        model_id="models/gemini-1.5-flash",
        temperature=0.8,
        max_tokens = 2048,
        system_prompt=LLM_SYSTEM_PROMPT
    )
    CLAUDE_CONFIG = LLMConfig(
        api_key=os.environ.get('ANTHROPIC_API_KEY'),
        model_name="Claude",
        model_id="claude-3-haiku-20240307",
        temperature=0.7,
        max_tokens=4000,
        system_prompt=LLM_SYSTEM_PROMPT
    )
