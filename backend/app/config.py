from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Dict, List, ClassVar

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "English Learning Tool"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/english_learning.db"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-mini"
    OPENAI_PROXY_URL: str = "http://127.0.0.1:7890"
    MINIMAX_API_KEY: str = ""
    MINIMAX_GROUP_ID: str = ""

    NEWS_API_KEY: str = ""
    NEWS_API_ENABLED: bool = False

    VOCAB_WORD_LIMIT: int = 15
    VOCAB_PHRASE_LIMIT: int = 3
    VOCAB_MIN_DIFFICULTY: str = "CET4"

    SCHEDULER_TIMEZONE: str = "Asia/Shanghai"
    PUSH_HOUR: int = 9
    PUSH_MINUTE: int = 30

    NEWS_SOURCES: ClassVar[Dict[str, List[str]]] = {
        "economy": [
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "http://rss.cnn.com/rss/edition_markets.rss",
            "https://feeds.reuters.com/reuters/businessNews"
        ],
        "politics": [
            "https://feeds.bbci.co.uk/news/politics/rss.xml",
            "http://rss.cnn.com/rss/edition_world.rss"
        ],
        "energy": [
            "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "http://rss.cnn.com/rss/edition_technology.rss"
        ],
        "environment": [
            "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "https://feeds.nationalgeographic.com/News/News_Environment"
        ],
        "trade": [
            "https://feeds.bbci.co.uk/news/business/rss.xml",
            "https://feeds.reuters.com/reuters/businessNews"
        ],
        "medicine": [
            "https://feeds.bbci.co.uk/news/health/rss.xml",
            "http://rss.cnn.com/rss/edition_health.rss"
        ],
        "health": [
            "https://feeds.bbci.co.uk/news/health/rss.xml",
            "http://rss.cnn.com/rss/edition_health.rss"
        ],
        "technology": [
            "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "http://rss.cnn.com/rss/edition_technology.rss"
        ],
        "world": [
            "https://feeds.bbci.co.uk/news/world/rss.xml",
            "http://rss.cnn.com/rss/edition_world.rss"
        ]
    }

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
