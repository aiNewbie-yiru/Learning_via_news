from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import List, Dict

from app.models import get_db, Article, Word, Phrase, ArticleResponse, ArticleListResponse, HiddenWord, HiddenPhrase, User
from app.services import news_scraper
from app.services.article_quality import apply_learning_quality_filters
from app.services.scheduler import get_today_bounds
from app.services.user_identity import get_current_user
from app.services.word_lookup import ensure_article_word_from_lookup, ensure_word_lookup, serialize_lookup_cache

router = APIRouter(prefix="/api/articles", tags=["articles"])

def serialize_word(word: Word) -> Dict:
    return {
        "id": word.id,
        "word": word.word,
        "definition": word.definition,
        "definition_cn": getattr(word, 'definition_cn', ''),
        "context_definition_cn": getattr(word, 'context_definition_cn', ''),
        "common_definition_cn": getattr(word, 'common_definition_cn', ''),
        "example_sentence": word.example_sentence,
        "example_cn": getattr(word, 'example_cn', ''),
        "example_source": getattr(word, 'example_source', ''),
        "example_sentence_2": getattr(word, 'example_sentence_2', ''),
        "example_sentence_2_cn": getattr(word, 'example_sentence_2_cn', ''),
        "difficulty_level": word.difficulty_level,
        "part_of_speech": word.part_of_speech,
        "pronunciation": getattr(word, 'pronunciation', '')
    }

@router.get("/", response_model=List[ArticleListResponse])
def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    articles = db.query(Article).order_by(Article.published_at.desc()).offset(skip).limit(limit).all()
    return articles

@router.get("/today", response_model=ArticleResponse)
def get_today_article(db: Session = Depends(get_db)):
    article = db.query(Article).options(
        selectinload(Article.words),
        selectinload(Article.phrases),
        selectinload(Article.comments)
    ).filter(Article.is_today == True).first()
    if not article:
        article = db.query(Article).options(
            selectinload(Article.words),
            selectinload(Article.phrases),
            selectinload(Article.comments)
        ).order_by(Article.published_at.desc()).first()
    if not article:
        raise HTTPException(status_code=404, detail="No article found")
    return article

@router.post("/fetch-now")
def fetch_article_now(db: Session = Depends(get_db)):
    from app.services.scheduler import fetch_and_process_daily_news
    fetch_and_process_daily_news()
    return {"message": "Article fetch initiated"}

def serialize_article_for_comparison(article: Article, hidden_words: set, hidden_phrases: set) -> Dict:
    difficulty_order = {"TOEFL": 0, "GRE": 1, "CET6": 2, "CET4": 3, "Basic": 4}
    filtered_words = [w for w in article.words if w.word.lower() not in hidden_words]
    filtered_phrases = [p for p in article.phrases if p.phrase.lower() not in hidden_phrases]
    sorted_words = sorted(filtered_words, key=lambda w: difficulty_order.get(w.difficulty_level, 99))
    top_words = sorted_words[:15]

    return {
        "id": article.id,
        "title": article.title,
        "topic_label": article.topic_label or "",
        "topic_label_cn": article.topic_label_cn or "",
        "url": article.url,
        "category": getattr(article, 'category', '') or "",
        "source": article.source or "Unknown",
        "published_at": article.published_at.isoformat() if article.published_at else "",
        "summary": article.summary or "",
        "content": article.content or "",
        "difficulty_level": getattr(article, 'difficulty_level', '') or "CET6",
        "words": [serialize_word(w) for w in top_words] if top_words else [],
        "phrases": [
            {
                "id": p.id,
                "phrase": p.phrase,
                "meaning": p.meaning,
                "meaning_cn": getattr(p, 'meaning_cn', ''),
                "example_sentence": p.example_sentence,
                "example_cn": getattr(p, 'example_cn', ''),
                "example_source": getattr(p, 'example_source', '')
            } for p in filtered_phrases
        ] if filtered_phrases else []
    }

@router.get("/compare")
def get_articles_for_comparison(
    skip_id: int = Query(None, description="从此文章之后继续获取，用于跳过后补充候选文章"),
    limit: int = Query(5, ge=1, le=5, description="返回今天文章数量，首页默认5篇"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取已处理的文章供用户选择。

    架构约束：只返回数据库中已有词汇的文章，
    不直接从 RSS 返回（RSS 文章未经过词汇提取流程）。

    支持 skip_id 参数实现补位：
    - 不带 skip_id：返回最新的 limit 篇文章
    - 带 skip_id：返回 skip_id 之后的 limit 篇文章
    """
    today_start, tomorrow_start = get_today_bounds()

    # 基础查询：只返回今天正文和词汇都足够的文章，避免混入摘要、版权页或样例文章。
    base_query = db.query(Article).options(
        selectinload(Article.words),
        selectinload(Article.phrases)
    ).filter(
        Article.published_at >= today_start,
        Article.published_at < tomorrow_start
    )
    base_query = apply_learning_quality_filters(base_query)

    if skip_id:
        skipped_article = db.query(Article).filter(Article.id == skip_id).first()
        if skipped_article:
            db_articles = base_query.filter(
                (Article.published_at < skipped_article.published_at) |
                ((Article.published_at == skipped_article.published_at) & (Article.id < skipped_article.id))
            ).order_by(Article.published_at.desc(), Article.id.desc()).limit(limit).all()
        else:
            db_articles = base_query.order_by(Article.published_at.desc(), Article.id.desc()).limit(limit).all()
    else:
        db_articles = base_query.order_by(Article.published_at.desc(), Article.id.desc()).limit(limit).all()

    if not db_articles:
        return []

    # 获取已隐藏的单词
    hidden_words = set(
        h.word for h in db.query(HiddenWord.word).filter(HiddenWord.user_id == current_user.id).all()
    )
    hidden_phrases = set(
        h.phrase for h in db.query(HiddenPhrase.phrase).filter(HiddenPhrase.user_id == current_user.id).all()
    )

    return [serialize_article_for_comparison(article, hidden_words, hidden_phrases) for article in db_articles]

@router.post("/feedback")
def submit_difficulty_feedback(payload: Dict = Body(...)):
    """记录用户反馈（用户偏好学习功能已移除）"""
    article_id = payload.get("preferred_article_id") or payload.get("article_id")
    action = payload.get("action", "select")
    user_id = payload.get("user_id", "default")
    if not article_id:
        raise HTTPException(status_code=400, detail="article_id is required")

    return {
        "message": "Feedback received (user preference learning disabled)",
        "article_id": article_id,
        "action": action,
        "user_id": user_id
    }

@router.post("/process-missing-vocabulary")
def process_missing_vocabulary(db: Session = Depends(get_db)):
    """处理所有没有词汇的文章"""
    from app.services.scheduler import process_article_vocabulary

    articles_without_vocab = db.query(Article).outerjoin(Word).filter(
        Word.id == None
    ).all()

    processed_count = 0
    for article in articles_without_vocab:
        process_article_vocabulary(article.id, db)
        processed_count += 1

    return {
        "message": f"Processed {processed_count} articles",
        "articles_found": len(articles_without_vocab),
        "articles_processed": processed_count
    }

@router.post("/process-missing-topic-labels")
def process_missing_topic_labels(db: Session = Depends(get_db)):
    from app.services.vocab_enhancer import vocab_enhancer_service

    today_start, tomorrow_start = get_today_bounds()
    articles = db.query(Article).filter(
        Article.published_at >= today_start,
        Article.published_at < tomorrow_start,
        ((Article.topic_label == None) | (Article.topic_label == ""))
    ).all()

    processed_count = 0
    for article in articles:
        labels = vocab_enhancer_service.generate_topic_labels(
            title=article.title,
            summary=article.summary,
            content=article.content
        )
        article.topic_label = labels.get("topic_label", "")
        article.topic_label_cn = labels.get("topic_label_cn", "")
        processed_count += 1

    db.commit()
    return {
        "message": f"Processed {processed_count} topic labels",
        "articles_found": len(articles),
        "articles_processed": processed_count
    }

@router.get("/difficulty-preference")
def get_difficulty_preference(user_id: str = Query("default")):
    """获取用户难度偏好（功能已移除，返回默认值）"""
    return {
        "user_id": user_id,
        "difficulty": "CET4",
        "message": "User preference learning disabled"
    }

@router.post("/{article_id}/lookup-word")
def lookup_article_word(
    article_id: int,
    payload: Dict = Body(...),
    db: Session = Depends(get_db)
):
    """按用户点击实时查词；只写入查词缓存，不自动加入右侧 Words。"""
    article, cache, lookup_source = ensure_word_lookup(article_id, payload.get("word"), db)
    existing_word = db.query(Word).filter(
        Word.article_id == article_id,
        func.lower(Word.word) == cache.word.lower()
    ).first()

    return {
        **serialize_lookup_cache(cache),
        "lookup_source": lookup_source,
        "article_id": article.id,
        "word_id": existing_word.id if existing_word else None,
        "in_word_list": existing_word is not None,
    }

@router.post("/{article_id}/add-word")
def add_article_word(
    article_id: int,
    payload: Dict = Body(...),
    db: Session = Depends(get_db)
):
    """把已查词的缓存结果加入文章右侧 Words；没有缓存时先查词再加入。"""
    word, lookup_source = ensure_article_word_from_lookup(article_id, payload.get("word"), db)
    return {
        **serialize_word(word),
        "lookup_source": lookup_source,
        "in_word_list": True,
    }

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = db.query(Article).options(
        selectinload(Article.words),
        selectinload(Article.phrases),
        selectinload(Article.comments)
    ).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    if not article.words and not article.phrases:
        from app.services.scheduler import process_article_vocabulary
        process_article_vocabulary(article.id, db)
        db.refresh(article)

    hidden_words = set(
        h.word for h in db.query(HiddenWord.word).filter(HiddenWord.user_id == current_user.id).all()
    )
    hidden_phrases = set(
        h.phrase for h in db.query(HiddenPhrase.phrase).filter(HiddenPhrase.user_id == current_user.id).all()
    )

    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "summary": article.summary,
        "source": article.source,
        "url": article.url,
        "topic_label": article.topic_label,
        "topic_label_cn": article.topic_label_cn,
        "published_at": article.published_at,
        "created_at": article.created_at,
        "words": [w for w in article.words if w.word.lower() not in hidden_words],
        "phrases": [p for p in article.phrases if p.phrase.lower() not in hidden_phrases],
        "comments": article.comments,
    }

@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()
    return {"message": f"Article '{article.title}' deleted successfully"}

@router.post("/words/{word_id}/hide")
def hide_word(
    word_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """隐藏一个单词（用户点击叉后不再显示）"""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    # 检查是否已隐藏
    existing = db.query(HiddenWord).filter(
        HiddenWord.user_id == current_user.id,
        HiddenWord.word == word.word.lower()
    ).first()
    if not existing:
        hidden = HiddenWord(user_id=current_user.id, word=word.word.lower())
        db.add(hidden)
        db.commit()

    return {"message": f"Word '{word.word}' hidden", "word": word.word}

@router.post("/phrases/{phrase_id}/hide")
def hide_phrase(
    phrase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """隐藏一个短语（用户点击叉后不再显示）"""
    phrase = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not phrase:
        raise HTTPException(status_code=404, detail="Phrase not found")

    normalized_phrase = phrase.phrase.lower()
    existing = db.query(HiddenPhrase).filter(
        HiddenPhrase.user_id == current_user.id,
        HiddenPhrase.phrase == normalized_phrase
    ).first()
    if not existing:
        hidden = HiddenPhrase(user_id=current_user.id, phrase=normalized_phrase)
        db.add(hidden)
        db.commit()

    return {"message": f"Phrase '{phrase.phrase}' hidden", "phrase": phrase.phrase}
