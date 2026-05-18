from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict

from app.models.database import get_db, FavoriteWord, FavoritePhrase, Word, Phrase, Article

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

@router.post("/words/{word_id}")
def add_favorite_word(word_id: int, db: Session = Depends(get_db)):
    """收藏一个单词"""
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    article = db.query(Article).filter(Article.id == word.article_id).first()
    article_title = article.title if article else ""

    existing = db.query(FavoriteWord).filter(FavoriteWord.word == word.word).first()
    if existing:
        # 已存在则增加收藏次数
        existing.favorite_count += 1
        existing.review_count = 0  # 重置复习次数
        existing.last_reviewed_at = None
        db.commit()
        return {"message": "Word already in favorites, favorite_count increased", "favorite_count": existing.favorite_count}

    favorite = FavoriteWord(
        word=word.word,
        definition=word.definition,
        example_sentence=word.example_sentence,
        difficulty_level=word.difficulty_level,
        part_of_speech=word.part_of_speech,
        pronunciation=word.pronunciation,
        article_title=article_title,
        favorite_count=1
    )
    db.add(favorite)
    db.commit()
    return {"message": f"Word '{word.word}' added to favorites"}

@router.delete("/words/{word_id}")
def remove_favorite_word(word_id: int, db: Session = Depends(get_db)):
    """取消收藏一个单词"""
    favorite = db.query(FavoriteWord).filter(FavoriteWord.id == word_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite word not found")
    
    db.delete(favorite)
    db.commit()
    return {"message": f"Word '{favorite.word}' removed from favorites"}

@router.get("/words")
def get_favorite_words(db: Session = Depends(get_db)):
    """获取所有收藏的单词"""
    words = db.query(FavoriteWord).order_by(FavoriteWord.added_at.desc()).all()
    return words

@router.post("/phrases/{phrase_id}")
def add_favorite_phrase(phrase_id: int, db: Session = Depends(get_db)):
    """收藏一个短语"""
    phrase = db.query(Phrase).filter(Phrase.id == phrase_id).first()
    if not phrase:
        raise HTTPException(status_code=404, detail="Phrase not found")
    
    article = db.query(Article).filter(Article.id == phrase.article_id).first()
    article_title = article.title if article else ""
    
    existing = db.query(FavoritePhrase).filter(FavoritePhrase.phrase == phrase.phrase).first()
    if existing:
        return {"message": "Phrase already in favorites"}
    
    favorite = FavoritePhrase(
        phrase=phrase.phrase,
        meaning=phrase.meaning,
        example_sentence=phrase.example_sentence,
        origin=phrase.origin,
        article_title=article_title
    )
    db.add(favorite)
    db.commit()
    return {"message": f"Phrase '{phrase.phrase}' added to favorites"}

@router.delete("/phrases/{phrase_id}")
def remove_favorite_phrase(phrase_id: int, db: Session = Depends(get_db)):
    """取消收藏一个短语"""
    favorite = db.query(FavoritePhrase).filter(FavoritePhrase.id == phrase_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite phrase not found")
    
    db.delete(favorite)
    db.commit()
    return {"message": f"Phrase '{favorite.phrase}' removed from favorites"}

@router.get("/phrases")
def get_favorite_phrases(db: Session = Depends(get_db)):
    """获取所有收藏的短语"""
    phrases = db.query(FavoritePhrase).order_by(FavoritePhrase.added_at.desc()).all()
    return phrases

@router.get("/review")
def get_review_items(
    item_type: str = Query("all", enum=["all", "words", "phrases"]),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """获取复习项（高优先级优先：favorite_count > 1 的排前面）"""
    result = []

    if item_type == "words" or item_type == "all":
        # 优先取 favorite_count > 1 的（被多次收藏的），再取其他的
        high_priority = db.query(FavoriteWord).filter(FavoriteWord.favorite_count > 1).order_by(func.random()).limit(limit).all()
        remaining = limit - len(high_priority)
        if remaining > 0:
            other = db.query(FavoriteWord).filter(FavoriteWord.favorite_count <= 1).order_by(func.random()).limit(remaining).all()
        else:
            other = []

        all_words = high_priority + other
        for word in all_words:
            result.append({
                "id": word.id,
                "type": "word",
                "item": word.word,
                "definition": word.definition,
                "example_sentence": word.example_sentence,
                "difficulty_level": word.difficulty_level,
                "part_of_speech": word.part_of_speech,
                "review_count": word.review_count,
                "favorite_count": word.favorite_count
            })
    
    if item_type == "phrases" or item_type == "all":
        phrases = db.query(FavoritePhrase).order_by(func.random()).limit(limit).all()
        for phrase in phrases:
            result.append({
                "id": phrase.id,
                "type": "phrase",
                "item": phrase.phrase,
                "definition": phrase.meaning,
                "example_sentence": phrase.example_sentence,
                "origin": phrase.origin,
                "review_count": phrase.review_count
            })
    
    return result[:limit]

@router.put("/review/{item_id}")
def mark_reviewed(
    item_id: int,
    item_type: str = Body(..., embed=True, enum=["word", "phrase"]),
    db: Session = Depends(get_db)
):
    """标记复习完成"""
    if item_type == "word":
        favorite = db.query(FavoriteWord).filter(FavoriteWord.id == item_id).first()
    else:
        favorite = db.query(FavoritePhrase).filter(FavoritePhrase.id == item_id).first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Item not found")
    
    favorite.review_count += 1
    favorite.last_reviewed_at = datetime.now()
    db.commit()
    
    return {"message": "Review recorded", "review_count": favorite.review_count}

@router.get("/stats")
def get_favorites_stats(db: Session = Depends(get_db)):
    """获取单词本统计信息"""
    word_count = db.query(FavoriteWord).count()
    phrase_count = db.query(FavoritePhrase).count()
    
    total_reviews = 0
    avg_reviews_per_word = 0
    if word_count > 0:
        total_word_reviews = db.query(func.sum(FavoriteWord.review_count)).scalar() or 0
        total_reviews += total_word_reviews
        avg_reviews_per_word = total_word_reviews / word_count
    
    avg_reviews_per_phrase = 0
    if phrase_count > 0:
        total_phrase_reviews = db.query(func.sum(FavoritePhrase.review_count)).scalar() or 0
        total_reviews += total_phrase_reviews
        avg_reviews_per_phrase = total_phrase_reviews / phrase_count
    
    return {
        "word_count": word_count,
        "phrase_count": phrase_count,
        "total_items": word_count + phrase_count,
        "total_reviews": total_reviews,
        "avg_reviews_per_word": round(avg_reviews_per_word, 2),
        "avg_reviews_per_phrase": round(avg_reviews_per_phrase, 2)
    }
