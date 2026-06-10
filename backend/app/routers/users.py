from typing import Dict, Optional

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.models.database import User, get_db
from app.services.user_identity import get_current_user, normalize_nickname

router = APIRouter(prefix="/api/users", tags=["users"])


def serialize_user(user: User) -> Dict:
    return {
        "id": user.id,
        "client_id": user.client_id,
        "nickname": user.nickname,
        "source": user.source,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@router.put("/me")
def update_me(
    payload: Dict[str, Optional[str]] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    nickname = normalize_nickname(payload.get("nickname"))
    if nickname:
        current_user.nickname = nickname
        db.commit()
        db.refresh(current_user)

    return serialize_user(current_user)

