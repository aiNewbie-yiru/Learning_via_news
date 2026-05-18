from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db, Article, ChatRequest
from app.services import ai_chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == request.article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    response = ai_chat_service.get_response(
        user_message=request.message,
        article_title=article.title,
        article_content=article.content
    )

    return {
        "response": response,
        "article_id": request.article_id
    }
