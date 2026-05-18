from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from typing import List, Dict

from app.models import get_db, Article, Word, ArticleResponse, ArticleListResponse, HiddenWord
from app.services import news_scraper

router = APIRouter(prefix="/api/articles", tags=["articles"])

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

def serialize_article_for_comparison(article: Article, hidden_words: set) -> Dict:
    difficulty_order = {"TOEFL": 0, "GRE": 1, "CET6": 2, "CET4": 3, "Basic": 4}
    filtered_words = [w for w in article.words if w.word.lower() not in hidden_words]
    sorted_words = sorted(filtered_words, key=lambda w: difficulty_order.get(w.difficulty_level, 99))
    top_words = sorted_words[:15]

    return {
        "id": article.id,
        "title": article.title,
        "url": article.url,
        "category": getattr(article, 'category', '') or "",
        "source": article.source or "Unknown",
        "published_at": article.published_at.isoformat() if article.published_at else "",
        "summary": article.summary or "",
        "content": article.content or "",
        "difficulty_level": getattr(article, 'difficulty_level', '') or "CET6",
        "words": [
            {
                "id": w.id,
                "word": w.word,
                "definition": w.definition,
                "definition_cn": getattr(w, 'definition_cn', ''),
                "example_sentence": w.example_sentence,
                "example_cn": getattr(w, 'example_cn', ''),
                "example_source": getattr(w, 'example_source', ''),
                "difficulty_level": w.difficulty_level,
                "part_of_speech": w.part_of_speech,
                "pronunciation": getattr(w, 'pronunciation', '')
            } for w in top_words
        ] if top_words else [],
        "phrases": [
            {
                "id": p.id,
                "phrase": p.phrase,
                "meaning": p.meaning,
                "meaning_cn": getattr(p, 'meaning_cn', ''),
                "example_sentence": p.example_sentence,
                "example_cn": getattr(p, 'example_cn', ''),
                "example_source": getattr(p, 'example_source', '')
            } for p in article.phrases
        ] if article.phrases else []
    }

@router.get("/compare")
def get_articles_for_comparison(
    skip_id: int = Query(None, description="从此文章之后继续获取，用于跳过后补充候选文章"),
    limit: int = Query(4, ge=1, le=4, description="返回候选文章数量，选择页默认4篇"),
    db: Session = Depends(get_db)
):
    """
    获取已处理的文章供用户选择。

    架构约束：只返回数据库中已有词汇的文章，
    不直接从 RSS 返回（RSS 文章未经过词汇提取流程）。

    支持 skip_id 参数实现补位：
    - 不带 skip_id：返回最新的 limit 篇文章
    - 带 skip_id：返回 skip_id 之后的 limit 篇文章
    """
    # 获取已有词汇的文章 ID 列表
    subquery = db.query(Word.article_id).distinct()

    # 基础查询：只返回已处理的文章
    base_query = db.query(Article).options(
        selectinload(Article.words),
        selectinload(Article.phrases)
    ).filter(Article.id.in_(subquery))

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

    if not db_articles and not skip_id:
        db_articles = db.query(Article).options(
            selectinload(Article.words),
            selectinload(Article.phrases)
        ).order_by(Article.published_at.desc(), Article.id.desc()).limit(limit).all()

    if not db_articles:
        return []

    # 获取已隐藏的单词
    hidden_words = set(h.word for h in db.query(HiddenWord.word).all())

    return [serialize_article_for_comparison(article, hidden_words) for article in db_articles]

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

@router.get("/difficulty-preference")
def get_difficulty_preference(user_id: str = Query("default")):
    """获取用户难度偏好（功能已移除，返回默认值）"""
    return {
        "user_id": user_id,
        "difficulty": "CET4",
        "message": "User preference learning disabled"
    }

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
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

    return article

@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db.delete(article)
    db.commit()
    return {"message": f"Article '{article.title}' deleted successfully"}

@router.post("/words/{word_id}/hide")
def hide_word(word_id: int, db: Session = Depends(get_db)):
    """隐藏一个单词（用户点击叉后不再显示）"""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    # 检查是否已隐藏
    existing = db.query(HiddenWord).filter(HiddenWord.word == word.word.lower()).first()
    if not existing:
        hidden = HiddenWord(word=word.word.lower())
        db.add(hidden)
        db.commit()

    return {"message": f"Word '{word.word}' hidden", "word": word.word}
