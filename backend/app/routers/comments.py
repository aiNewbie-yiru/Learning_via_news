from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models import get_db, Comment, CommentCreate, CommentResponse, Article, User
from app.services.user_identity import get_current_user, normalize_nickname

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
def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    article = db.query(Article).filter(Article.id == comment.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    nickname = normalize_nickname(comment.user_name)
    if nickname and nickname != current_user.nickname:
        current_user.nickname = nickname
        db.commit()
        db.refresh(current_user)

    db_comment = Comment(
        user_id=current_user.id,
        article_id=comment.article_id,
        user_name=nickname or current_user.nickname,
        content=comment.content
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)

    conversation_history = []
    previous_comments = db.query(Comment).filter(
        Comment.article_id == comment.article_id,
        Comment.id != db_comment.id
    ).order_by(Comment.created_at.asc()).all()
    for previous_comment in previous_comments:
        conversation_history.append({
            "learner": previous_comment.content,
            "assistant": previous_comment.ai_response or "",
        })

    from app.services import ai_chat_service
    ai_response = ai_chat_service.get_response(
        user_message=comment.content,
        article_title=article.title,
        article_content=article.content,
        conversation_history=conversation_history
    )
    db_comment.ai_response = ai_response
    db.commit()
    db.refresh(db_comment)

    return db_comment
