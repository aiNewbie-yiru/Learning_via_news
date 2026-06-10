from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class WordBase(BaseModel):
    word: str
    definition: Optional[str] = None
    definition_cn: Optional[str] = None
    context_definition_cn: Optional[str] = None
    common_definition_cn: Optional[str] = None
    example_sentence: Optional[str] = None  # 第一例句：从文章原文抓取
    example_cn: Optional[str] = None
    example_source: Optional[str] = None
    example_sentence_2: Optional[str] = None  # 第二例句：AI生成
    example_sentence_2_cn: Optional[str] = None
    difficulty_level: Optional[str] = None
    part_of_speech: Optional[str] = None

class WordCreate(WordBase):
    article_id: int

class WordResponse(WordBase):
    id: int
    article_id: int

    class Config:
        from_attributes = True

class PhraseBase(BaseModel):
    phrase: str
    meaning: Optional[str] = None
    meaning_cn: Optional[str] = None
    example_sentence: Optional[str] = None
    example_cn: Optional[str] = None
    example_source: Optional[str] = None
    origin: Optional[str] = None

class PhraseCreate(PhraseBase):
    article_id: int

class PhraseResponse(PhraseBase):
    id: int
    article_id: int

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    user_name: Optional[str] = "Anonymous"

class CommentCreate(CommentBase):
    article_id: int

class CommentResponse(CommentBase):
    id: int
    article_id: int
    ai_response: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None

class ArticleCreate(ArticleBase):
    pass

class ArticleResponse(ArticleBase):
    id: int
    topic_label: Optional[str] = None
    topic_label_cn: Optional[str] = None
    published_at: datetime
    created_at: datetime
    words: List[WordResponse] = []
    phrases: List[PhraseResponse] = []
    comments: List[CommentResponse] = []

    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    id: int
    title: str
    topic_label: Optional[str] = None
    topic_label_cn: Optional[str] = None
    summary: Optional[str] = None
    source: Optional[str] = None
    published_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    article_id: int
    user_name: Optional[str] = "Anonymous"
