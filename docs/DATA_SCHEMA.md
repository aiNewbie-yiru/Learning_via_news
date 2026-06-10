# DATA_SCHEMA.md - 数据结构文档

## 1. 数据库概览

- **类型**: SQLite
- **路径**: `backend/data/english_learning.db`
- **ORM**: SQLAlchemy
- **模型定义**: `backend/app/models/database.py`

---

## 2. 数据表结构

### 2.1 articles 表

新闻文章表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| title | String(500) | 文章标题 |
| content | Text | 文章正文（最多约1500字符） |
| summary | Text | 文章摘要 |
| source | String(100) | 来源（BBC/CNN/Reuters） |
| url | String(500) | 原文链接 |
| published_at | DateTime | 发布时间 |
| created_at | DateTime | 创建时间 |
| is_today | Boolean | 是否为今日文章 |

**关联**:
- `words`: 一对多 → Word 表
- `phrases`: 一对多 → Phrase 表
- `comments`: 一对多 → Comment 表

---

### 2.2 words 表

从文章中提取的词汇

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| article_id | Integer (FK) | 关联文章 ID |
| word | String(100) | 单词（小写） |
| definition | Text | 英文定义 |
| definition_cn | Text | 中文短释义（面向用户展示，不是英文 definition 的机翻） |
| context_definition_cn | Text | **计划新增**：原文语境下的中文义项 |
| common_definition_cn | Text | **计划新增**：一词多义时最高频的其他中文义项 |
| example_sentence | Text | **第一例句**：从新闻原文抓取 |
| example_cn | Text | 第一例句中文翻译 |
| example_source | String(200) | 例句来源 |
| example_sentence_2 | Text | **第二例句**：AI 生成 |
| example_sentence_2_cn | Text | 第二例句中文翻译 |
| difficulty_level | String(20) | 难度等级（Basic/CET4/CET6/TOEFL） |
| part_of_speech | String(20) | 词性 |
| pronunciation | String(100) | IPA 发音 |

**关联**: `article` → Article 表

**重要**：所有 article 必须有关联的 words/phrases，没有词汇的文章是无效的。

---

### 2.3 phrases 表

从文章中提取的短语和习语

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| article_id | Integer (FK) | 关联文章 ID |
| phrase | String(200) | 短语内容 |
| meaning | Text | 英文含义 |
| meaning_cn | Text | 中文含义 |
| example_sentence | Text | 例句 |
| example_cn | Text | 例句中文翻译 |
| example_source | String(200) | 例句来源 |
| origin | Text | 习语来源 |

**关联**: `article` → Article 表

---

### 2.4 comments 表

用户评论和 AI 回复

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| article_id | Integer (FK) | 关联文章 ID |
| user_name | String(100) | 用户名（默认 Anonymous） |
| content | Text | 评论内容 |
| ai_response | Text | AI 回复 |
| created_at | DateTime | 创建时间 |

**关联**: `article` → Article 表

---

### 2.5 favorite_words 表

用户收藏的单词

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| word | String(100) | 单词 |
| definition | Text | 定义 |
| example_sentence | Text | 例句 |
| difficulty_level | String(20) | 难度等级 |
| part_of_speech | String(20) | 词性 |
| pronunciation | String(100) | 发音 |
| article_title | String(500) | 来源文章标题 |
| added_at | DateTime | 收藏时间 |
| review_count | Integer | 复习次数（默认0） |
| last_reviewed_at | DateTime | 最后复习时间 |
| favorite_count | Integer | 被收藏次数（用于优先级排序，默认1） |

---

### 2.6 favorite_phrases 表

用户收藏的短语

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer (PK) | 主键 |
| phrase | String(200) | 短语 |
| meaning | Text | 含义 |
| example_sentence | Text | 例句 |
| origin | Text | 来源 |
| article_title | String(500) | 来源文章标题 |
| added_at | DateTime | 收藏时间 |
| review_count | Integer | 复习次数（默认0） |
| last_reviewed_at | DateTime | 最后复习时间 |

---

## 3. 数据关系图

```
Article (1) ──── (N) Word
       │
       ├─── (N) Phrase
       │
       └─── (N) Comment

FavoriteWord: 独立表，用户收藏的单词
FavoritePhrase: 独立表，用户收藏的短语
```

---

## 4. 数据流转

### 4.1 每日新闻抓取流程

```
RSS Feed → NewsScraper → Article 表
                          ↓
                    word_extractor.analyze_text()
                          ↓
              ┌──────────┴──────────┐
              ↓                      ↓
         Word 表              Phrase 表
              ↓                      ↓
        vocab_enhancer         vocab_enhancer
         (AI 增强)               (AI 增强)
```

### 4.2 用户收藏流程

```
文章详情页 → 点击收藏 → favorites.py → FavoriteWord/FavoritePhrase 表
```

### 4.3 复习流程

```
Review 页面 → GET /favorites/review → FavoriteWord/FavoritePhrase
                            ↓
                    PUT /favorites/review/{id}
                            ↓
                    更新 review_count, last_reviewed_at
```

### 4.4 文章选择流程（compare）

```
GET /api/articles/compare
        ↓
从数据库获取已处理的文章（包含 words 和 phrases）
        ↓
返回给前端
```

**重要**：`/compare` 接口必须返回**已处理过的文章**，即数据库中已有 words/phrases 的 article。直接从 RSS 抓取的原始数据不能返回给用户（因为没有词汇）。

---

## 5. 数据库迁移规则

### 5.1 修改 model 后的必须步骤

当修改 `backend/app/models/database.py` 中的任何 model 定义后：

1. **停止服务**
2. **执行迁移脚本**（见下方）
3. **重启服务**
4. **运行验证测试**

### 5.2 迁移脚本模板

```bash
cd backend
./venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('data/english_learning.db')
cur = conn.cursor()

# 对照 models/database.py 中的定义，检查每一列是否都存在
# 例如添加新列：
# cur.execute('ALTER TABLE table_name ADD COLUMN new_column TYPE')

conn.commit()
conn.close()
print('Migration completed!')
"
```

### 5.3 验证数据库 schema 匹配 model

```bash
cd backend
./venv/bin/python -c "
import sys
sys.path.insert(0, '.')
from app.models.database import Base, engine

# 获取数据库实际表结构
from sqlalchemy import inspect
inspector = inspect(engine)

# 对照检查每个表
for table_name in ['articles', 'words', 'phrases', 'comments', 'favorite_words', 'favorite_phrases']:
    actual_cols = [col['name'] for col in inspector.get_columns(table_name)]
    print(f'{table_name}: {actual_cols}')
"
```

---

## 6. API Schema（Pydantic）

定义在 `backend/app/models/schemas.py`

### 请求/响应模型

| Schema | 用途 |
|--------|------|
| WordBase/Create/Response | 词汇 CRUD |
| PhraseBase/Create/Response | 短语 CRUD |
| CommentBase/Create/Response | 评论 CRUD |
| ArticleBase/Create/Response | 文章 CRUD |
| ArticleListResponse | 文章列表（不含 content） |
| ChatRequest | 聊天请求 |

---

## 7. 架构约束

### 7.1 文章必须有词汇

**任何返回给前端的 article，必须包含对应的 words 和 phrases。**

- `/api/articles/{id}` - 必须加载 article.words 和 article.phrases
- `/api/articles/compare` - 只返回**数据库中已有词汇的文章**
- `/api/articles/today` - 只返回**数据库中已有词汇的文章**

如果某文章缺少词汇，必须先调用 `process_article_vocabulary()` 处理后才能返回。

### 7.2 数据一致性

- article 被删除时，关联的 words/phrases 也被删除（cascade）
- favorite_words/favorite_phrases 是独立表，不受 article 删除影响