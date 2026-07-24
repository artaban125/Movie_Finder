"""애플리케이션 환경 변수 설정."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parent / ".env"


@dataclass(frozen=True)
class Settings:
    movie_api_key: str
    kobis_api_base_url: str


def load_settings() -> Settings:
    """backend/.env를 로드하고 애플리케이션 설정을 반환한다."""
    load_dotenv(ENV_FILE)
    return Settings(
        movie_api_key=os.getenv("MOVIE_API_KEY", ""),
        kobis_api_base_url=os.getenv("KOBIS_API_BASE_URL", ""),
    )


settings = load_settings()
