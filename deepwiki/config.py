from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from pathlib import Path
parent = Path(__file__).parent.parent

class Settings(BaseSettings):
    """Configuration settings for DeepWiki."""
    model_config = SettingsConfigDict(
        env_file= parent / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    # Deepseek model settings
    model_name: str = Field("deepseek-chat", description="Name of the Deepseek model to use")
    deepseek_api_key: str = Field(None, description="API key for Deepseek model", env="DEEPSEEK_API_KEY")
    temperature: float = Field(0.7, description="Temperature for model responses")
    max_tokens: int = Field(2048, description="Maximum number of tokens for model responses")

    # LLM settings for local inference
    use_local: bool = Field(False, description="Use local LLM")
    local_model_path: str = Field(None, description="Path to the local model directory")


    # Repository settings
    temp_dir: Path = Field(
        default= parent / 'tmp/deepwiki_repos',
        description="Temporary directory for storing fetched repositories"
    )
    clone_timeout: int = Field(
        default=300,
        description="Timeout for cloning repositories in seconds"
    )

    excluded_dirs: list = Field(
        ["node_modules", ".git", "__pycache__", "venv", "dist", "build"],
        description="Directories to exclude from processing"
    )
    excluded_extensions: list = Field(
        [".lock", ".log", ".tmp", ".cache", ".gitignore"],
        description="File extensions to exclude from processing"
    )

settings = Settings()