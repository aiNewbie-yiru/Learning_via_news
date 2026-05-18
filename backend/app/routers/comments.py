from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import get_db, Comment, CommentCreate, CommentResponse, Article

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.get("/article/{article_id}", response_model=List[CommentResponse])
def get_comments(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    comments = db.query(Comment).filter(
        Comment.article_id == article_id
    ).order_by(Comment.created_at.asc()).all()
    return comments

@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == comment.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    db_comment = Comment(
        article_id=comment.article_id,
        user_name=comment.user_name or "Anonymous",
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    from app.services import ai_chat_service
    ai_response = ai_chat_service.get_response(
        user_message=comment.content,
        article_title=article.title,
        article_content=article.content
    )
    db_comment.ai_response = ai_response
    db.commit()
    db.refresh(db_comment)

    return db_comment
