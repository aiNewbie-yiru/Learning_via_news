import random
import re
from datetime import datetime
from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.models.database import User, get_db

ADJECTIVES = [
    "Brave", "Bright", "Calm", "Clever", "Fresh", "Gentle",
    "Happy", "Kind", "Lively", "Lucky", "Merry", "Sunny",
]

NOUNS = [
    "Bridge", "Cloud", "Forest", "Harbor", "Hill", "Learner",
    "Maple", "Meadow", "River", "Spark", "Stone", "Voyage",
]


def generate_default_nickname() -> str:
    return f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"


def normalize_client_id(client_id: Optional[str]) -> str:
    clean_client_id = (client_id or "").strip()
    if not clean_client_id:
        return "legacy-anonymous"

    if not re.fullmatch(r"[A-Za-z0-9_.:-]{6,120}", clean_client_id):
        return "legacy-anonymous"

    return clean_client_id


def normalize_nickname(nickname: Optional[str]) -> Optional[str]:
    clean_nickname = (nickname or "").strip()
    if not clean_nickname:
        return None
    return clean_nickname[:80]


def get_current_user(
    db: Session = Depends(get_db),
    x_client_id: Optional[str] = Header(None, alias="X-Client-Id"),
    x_client_source: Optional[str] = Header(None, alias="X-Client-Source"),
    x_client_nickname: Optional[str] = Header(None, alias="X-Client-Nickname"),
) -> User:
    client_id = normalize_client_id(x_client_id)
    nickname = normalize_nickname(x_client_nickname)
    source = (x_client_source or "web").strip()[:20] or "web"

    user = db.query(User).filter(User.client_id == client_id).first()
    if not user:
        user = User(
            client_id=client_id,
            nickname=nickname or generate_default_nickname(),
            source=source,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    changed = False
    if nickname and nickname != user.nickname:
        user.nickname = nickname
        changed = True
    if source and source != user.source:
        user.source = source
        changed = True

    if changed:
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)

    return user

