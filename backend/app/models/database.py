from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from app.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    source = Column(String(100))
    url = Column(String(500))
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_today = Column(Boolean, default=False)

    words = relationship("Word", back_populates="article", cascade="all, delete-orphan")
    phrases = relationship("Phrase", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    word = Column(String(100), nullable=False)
    definition = Column(Text)
    definition_cn = Column(Text)
    example_sentence = Column(Text)  # 第一例句：从文章原文抓取
    example_cn = Column(Text)
    example_source = Column(String(200))
    example_sentence_2 = Column(Text)  # 第二例句：AI生成
    example_sentence_2_cn = Column(Text)
    difficulty_level = Column(String(20))
    part_of_speech = Column(String(20))
    pronunciation = Column(String(100))

    article = relationship("Article", back_populates="words")

class Phrase(Base):
    __tablename__ = "phrases"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    phrase = Column(String(200), nullable=False)
    meaning = Column(Text)
    meaning_cn = Column(Text)
    example_sentence = Column(Text)
    example_cn = Column(Text)
    example_source = Column(String(200))
    origin = Column(Text)

    article = relationship("Article", back_populates="phrases")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    user_name = Column(String(100), default="Anonymous")
    content = Column(Text, nullable=False)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="comments")

class FavoriteWord(Base):
    __tablename__ = "favorite_words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False)
    definition = Column(Text)
    example_sentence = Column(Text)
    difficulty_level = Column(String(20))
    part_of_speech = Column(String(20))
    pronunciation = Column(String(100))
    article_title = Column(String(500))
    added_at = Column(DateTime, default=datetime.utcnow)
    review_count = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime)
    favorite_count = Column(Integer, default=1)  # 收藏次数，用于优先级排序

class FavoritePhrase(Base):
    __tablename__ = "favorite_phrases"

    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String(200), nullable=False)
    meaning = Column(Text)
    example_sentence = Column(Text)
    origin = Column(Text)
    article_title = Column(String(500))
    added_at = Column(DateTime, default=datetime.utcnow)
    review_count = Column(Integer, default=0)
    last_reviewed_at = Column(DateTime)

class HiddenWord(Base):
    __tablename__ = "hidden_words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False, unique=True)
    hidden_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_schema()

def ensure_sqlite_schema():
    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    required_columns = {
        "favorite_words": {
            "pronunciation": "VARCHAR(100)",
        },
    }

    with engine.begin() as connection:
        for table_name, columns in required_columns.items():
            existing_columns = {
                row[1]
                for row in connection.execute(text(f"PRAGMA table_info({table_name})"))
            }
            for column_name, column_type in columns.items():
                if column_name not in existing_columns:
                    connection.execute(
                        text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                    )
