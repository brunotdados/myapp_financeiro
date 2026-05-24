from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Mini App Financas"
    app_env: str = "local"

    gmail_imap_host: str = "imap.gmail.com"
    gmail_imap_port: int = 993

    bruno_email: str | None = None
    bruno_email_app_password: str | None = None

    mayara_email: str | None = None
    mayara_email_app_password: str | None = None

    nubank_gmail_query: str = Field(
        default="(from:nubank OR from:nubank.com.br OR subject:Nubank) newer_than:180d"
    )
    nubank_statement_subject: str = "Extrato da fatura do Cartão Nubank"
    nubank_email_limit: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
