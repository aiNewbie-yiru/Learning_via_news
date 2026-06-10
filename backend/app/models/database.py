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
    topic_label = Column(String(50))
    topic_label_cn = Column(String(20))
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_today = Column(Boolean, default=False)

    words = relationship("Word", back_populates="article", cascade="all, delete-orphan")
    phrases = relationship("Phrase", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(120), nullable=False, unique=True, index=True)
    nickname = Column(String(80), nullable=False)
    source = Column(String(20), default="web")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    word = Column(String(100), nullable=False)
    definition = Column(Text)
    definition_cn = Column(Text)
    context_definition_cn = Column(Text)
    common_definition_cn = Column(Text)
    example_sentence = Column(Text)  # 第一例句：从文章原文抓取
    example_cn = Column(Text)
    example_source = Column(String(200))
    example_sentence_2 = Column(Text)  # 第二例句：AI生成
    example_sentence_2_cn = Column(Text)
    difficulty_level = Column(String(20))
    part_of_speech = Column(String(20))
    pronunciation = Column(String(100))

    article = relationship("Article", back_populates="words")

class WordLookupCache(Base):
    __tablename__ = "word_lookup_cache"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    word = Column(String(100), nullable=False, index=True)
    definition = Column(Text)
    definition_cn = Column(Text)
    context_definition_cn = Column(Text)
    common_definition_cn = Column(Text)
    example_sentence = Column(Text)
    example_cn = Column(Text)
    example_source = Column(String(200))
    example_sentence_2 = Column(Text)
    example_sentence_2_cn = Column(Text)
    difficulty_level = Column(String(20))
    part_of_speech = Column(String(20))
    pronunciation = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    user_name = Column(String(100), default="Anonymous")
    content = Column(Text, nullable=False)
    ai_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    article = relationship("Article", back_populates="comments")

class FavoriteWord(Base):
    __tablename__ = "favorite_words"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    word = Column(String(100), nullable=False)
    definition = Column(Text)
    definition_cn = Column(Text)
    context_definition_cn = Column(Text)
    common_definition_cn = Column(Text)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    word = Column(String(100), nullable=False)
    hidden_at = Column(DateTime, default=datetime.utcnow)

class HiddenPhrase(Base):
    __tablename__ = "hidden_phrases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    phrase = Column(String(200), nullable=False)
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
        "articles": {
            "topic_label": "VARCHAR(50)",
            "topic_label_cn": "VARCHAR(20)",
        },
        "comments": {
            "user_id": "INTEGER",
        },
        "favorite_words": {
            "user_id": "INTEGER",
            "pronunciation": "VARCHAR(100)",
            "definition_cn": "TEXT",
            "context_definition_cn": "TEXT",
            "common_definition_cn": "TEXT",
        },
        "favorite_phrases": {
            "user_id": "INTEGER",
        },
        "words": {
            "context_definition_cn": "TEXT",
            "common_definition_cn": "TEXT",
        },
        "hidden_words": {
            "user_id": "INTEGER",
        },
        "hidden_phrases": {
            "user_id": "INTEGER",
        },
    }

    with engine.begin() as connection:
        legacy_user_id = ensure_legacy_user(connection)
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

        for table_name in ("comments", "favorite_words", "favorite_phrases", "hidden_words", "hidden_phrases"):
            connection.execute(
                text(f"UPDATE {table_name} SET user_id = :user_id WHERE user_id IS NULL"),
                {"user_id": legacy_user_id},
            )

        migrate_hidden_table_for_users(connection, "hidden_words", "word", legacy_user_id)
        migrate_hidden_table_for_users(connection, "hidden_phrases", "phrase", legacy_user_id)

        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_favorite_words_user_word ON favorite_words (user_id, word)"
        ))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_favorite_phrases_user_phrase ON favorite_phrases (user_id, phrase)"
        ))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_hidden_words_user_word ON hidden_words (user_id, word)"
        ))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_hidden_phrases_user_phrase ON hidden_phrases (user_id, phrase)"
        ))
        connection.execute(text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_word_lookup_cache_article_word ON word_lookup_cache (article_id, word)"
        ))

def ensure_legacy_user(connection=None):
    if connection is None:
        with engine.begin() as new_connection:
            return ensure_legacy_user(new_connection)

    row = connection.execute(
        text("SELECT id FROM users WHERE client_id = :client_id"),
        {"client_id": "legacy-anonymous"},
    ).first()
    if row:
        return row[0]

    connection.execute(
        text(
            "INSERT INTO users (client_id, nickname, source, created_at, updated_at) "
            "VALUES (:client_id, :nickname, :source, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
        ),
        {
            "client_id": "legacy-anonymous",
            "nickname": "Legacy Learner",
            "source": "legacy",
        },
    )
    row = connection.execute(
        text("SELECT id FROM users WHERE client_id = :client_id"),
        {"client_id": "legacy-anonymous"},
    ).first()
    return row[0]

def migrate_hidden_table_for_users(connection, table_name, value_column, legacy_user_id):
    columns = [row[1] for row in connection.execute(text(f"PRAGMA table_info({table_name})"))]
    index_rows = connection.execute(text(f"PRAGMA index_list({table_name})")).fetchall()
    has_single_value_unique = False
    for index_row in index_rows:
        is_unique = bool(index_row[2])
        if not is_unique:
            continue
        index_name = index_row[1]
        index_columns = [
            info_row[2]
            for info_row in connection.execute(text(f"PRAGMA index_info({index_name})"))
        ]
        if index_columns == [value_column]:
            has_single_value_unique = True
            break

    if "user_id" in columns and not has_single_value_unique:
        return

    temp_table = f"{table_name}_user_migration"
    connection.execute(text(f"DROP TABLE IF EXISTS {temp_table}"))
    connection.execute(text(
        f"CREATE TABLE {temp_table} ("
        "id INTEGER PRIMARY KEY, "
        "user_id INTEGER, "
        f"{value_column} VARCHAR(200) NOT NULL, "
        "hidden_at DATETIME"
        ")"
    ))

    select_user_id = "user_id" if "user_id" in columns else f"{legacy_user_id}"
    connection.execute(text(
        f"INSERT INTO {temp_table} (id, user_id, {value_column}, hidden_at) "
        f"SELECT id, COALESCE({select_user_id}, {legacy_user_id}), {value_column}, hidden_at FROM {table_name}"
    ))
    connection.execute(text(f"DROP TABLE {table_name}"))
    connection.execute(text(f"ALTER TABLE {temp_table} RENAME TO {table_name}"))
