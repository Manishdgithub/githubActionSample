import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Enterprise Production Hub"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./prod_hub.db")
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY", "super-insecure-default-change-me-immediately-12345"
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    third_party_payment_webhook_url: str = os.getenv(
        "WEBHOOK_URL", "https://httpbin.org/post"
    )


settings = Settings()
