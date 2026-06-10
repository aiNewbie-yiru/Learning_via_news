import re

from sqlalchemy import func

from app.config import settings
from app.models.database import Article, Word


BOILERPLATE_PATTERNS = (
    "copyright",
    "all rights reserved",
    "not responsible for the content of external sites",
    "read about our approach to external linking",
    "more on this story",
)


def is_usable_article_content(content: str) -> bool:
    normalized = re.sub(r"\s+", " ", content or "").strip()
    if len(normalized) < settings.MIN_ARTICLE_CONTENT_LENGTH:
        return False

    lower_content = normalized.lower()
    if any(pattern in lower_content for pattern in BOILERPLATE_PATTERNS):
        return False

    return True


def apply_content_quality_filters(query):
    query = query.filter(func.length(func.trim(Article.content)) >= settings.MIN_ARTICLE_CONTENT_LENGTH)
    for pattern in BOILERPLATE_PATTERNS:
        query = query.filter(~func.lower(Article.content).contains(pattern))
    return query


def apply_learning_quality_filters(query):
    return apply_content_quality_filters(query).join(Word).group_by(Article.id).having(
        func.count(Word.id) >= settings.MIN_ARTICLE_WORD_COUNT
    )
