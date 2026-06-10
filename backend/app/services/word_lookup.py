import re
from datetime import datetime
from typing import Dict, Tuple

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.database import Article, Word, WordLookupCache


def normalize_lookup_word(raw_word: str) -> str:
    normalized = re.sub(r"^[^A-Za-z]+|[^A-Za-z]+$", "", (raw_word or "").strip()).lower()
    if not re.fullmatch(r"[a-z][a-z'-]{1,49}", normalized):
        raise HTTPException(status_code=400, detail="Invalid word")
    return normalized


def serialize_lookup_cache(cache: WordLookupCache) -> Dict:
    return {
        "lookup_id": cache.id,
        "word": cache.word,
        "definition": cache.definition,
        "definition_cn": cache.definition_cn,
        "context_definition_cn": cache.context_definition_cn,
        "common_definition_cn": cache.common_definition_cn,
        "example_sentence": cache.example_sentence,
        "example_cn": cache.example_cn,
        "example_source": cache.example_source,
        "example_sentence_2": cache.example_sentence_2,
        "example_sentence_2_cn": cache.example_sentence_2_cn,
        "difficulty_level": cache.difficulty_level,
        "part_of_speech": cache.part_of_speech,
        "pronunciation": cache.pronunciation,
    }


def _copy_word_to_lookup(word: Word) -> WordLookupCache:
    return WordLookupCache(
        article_id=word.article_id,
        word=word.word.lower(),
        definition=word.definition,
        definition_cn=word.definition_cn,
        context_definition_cn=word.context_definition_cn,
        common_definition_cn=word.common_definition_cn,
        example_sentence=word.example_sentence,
        example_cn=word.example_cn,
        example_source=word.example_source,
        example_sentence_2=word.example_sentence_2,
        example_sentence_2_cn=word.example_sentence_2_cn,
        difficulty_level=word.difficulty_level,
        part_of_speech=word.part_of_speech,
        pronunciation=word.pronunciation,
    )


def ensure_word_lookup(article_id: int, raw_word: str, db: Session) -> Tuple[Article, WordLookupCache, str]:
    normalized = normalize_lookup_word(raw_word)
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    cache = db.query(WordLookupCache).filter(
        WordLookupCache.article_id == article_id,
        func.lower(WordLookupCache.word) == normalized,
    ).first()
    if cache:
        return article, cache, "lookup_cache"

    existing_word = db.query(Word).filter(
        Word.article_id == article_id,
        func.lower(Word.word) == normalized,
    ).first()
    if existing_word:
        cache = _copy_word_to_lookup(existing_word)
        db.add(cache)
        db.commit()
        db.refresh(cache)
        return article, cache, "word_list"

    from app.services.vocab_enhancer import vocab_enhancer_service

    enhanced = vocab_enhancer_service.enhance_word(
        word=normalized,
        difficulty=getattr(article, "difficulty_level", None) or "CET6",
        article_context=article.content or "",
    )

    cache = WordLookupCache(
        article_id=article_id,
        word=normalized,
        definition=enhanced.get("definition", ""),
        definition_cn=enhanced.get("definition_cn", ""),
        context_definition_cn=enhanced.get("context_definition_cn", ""),
        common_definition_cn=enhanced.get("common_definition_cn", ""),
        example_sentence=enhanced.get("example_sentence", ""),
        example_cn=enhanced.get("example_cn", ""),
        example_source=enhanced.get("example_source", "Common Usage"),
        example_sentence_2=enhanced.get("example_sentence_2", ""),
        example_sentence_2_cn=enhanced.get("example_sentence_2_cn", ""),
        difficulty_level=enhanced.get("difficulty_level", "CET6") or "CET6",
        part_of_speech=enhanced.get("part_of_speech", ""),
        pronunciation=enhanced.get("pronunciation", ""),
    )
    db.add(cache)
    db.commit()
    db.refresh(cache)
    return article, cache, "generated"


def ensure_article_word_from_lookup(article_id: int, raw_word: str, db: Session) -> Tuple[Word, str]:
    _, cache, lookup_source = ensure_word_lookup(article_id, raw_word, db)
    existing_word = db.query(Word).filter(
        Word.article_id == article_id,
        func.lower(Word.word) == cache.word.lower(),
    ).first()
    if existing_word:
        return existing_word, "existing"

    word = Word(
        article_id=article_id,
        word=cache.word,
        definition=cache.definition,
        definition_cn=cache.definition_cn,
        context_definition_cn=cache.context_definition_cn,
        common_definition_cn=cache.common_definition_cn,
        example_sentence=cache.example_sentence,
        example_cn=cache.example_cn,
        example_source=cache.example_source,
        example_sentence_2=cache.example_sentence_2,
        example_sentence_2_cn=cache.example_sentence_2_cn,
        difficulty_level=cache.difficulty_level,
        part_of_speech=cache.part_of_speech,
        pronunciation=cache.pronunciation,
    )
    db.add(word)
    cache.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(word)
    return word, lookup_source
