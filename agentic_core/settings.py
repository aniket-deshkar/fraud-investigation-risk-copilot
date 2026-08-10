from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
