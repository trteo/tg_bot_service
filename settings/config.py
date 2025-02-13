from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DEV: bool = False

    POSTGRES_USER: str = ''
    POSTGRES_PASSWORD: SecretStr = ''
    POSTGRES_DATABASE: str = ''
    POSTGRES_HOST: str = ''
    POSTGRES_PORT: str = ''

    SUBSCRIBE_GROUP_ID: str = ''
    SUBSCRIBE_CHANNEL_ID: str = ''

    SUBSCRIBE_GROUP_LINK: str = ''
    SUBSCRIBE_CHANNEL_LINK: str = ''

    BOT_TOKEN: SecretStr = ''
    PAYMENT_TOKEN: SecretStr = ''

    class Config:
        env_file = Path(BASE_DIR, 'settings', 'env')


settings = Settings()


def get_db_url(db_name: str = settings.POSTGRES_DATABASE) -> str:
    return (
        f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD.get_secret_value()}@'
        f'{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{db_name}'
    )

