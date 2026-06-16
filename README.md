# Learning via News | 通过新闻学英语

Learning via News is a full-stack English learning tool that turns daily English news into a guided reading, vocabulary, and AI tutor experience.

通过新闻学英语是一个全栈英语学习工具：每天抓取英文新闻，自动提取重点词汇和短语，并提供 AI Tutor、收藏和复习功能，让用户在真实语境中学习英语。

---

## 中文介绍

### 项目亮点

- **每日新闻学习**：自动抓取 BBC、CNN、Reuters 等英文新闻源，生成当天学习文章。
- **今日主题导航**：首页展示当天 5 篇文章的英文主题和中文话题标签，点击即可切换阅读。
- **词汇与短语提取**：从文章中自动提取重点单词和实用短语，并按难度分级。
- **AI 增强释义**：为词汇生成中文释义、英文释义、例句、发音和语境解释。
- **正文内联注释**：在文章正文中直接显示重点单词的中文语境义，减少阅读中断。
- **AI Tutor 对话**：围绕当前文章进行英文讨论、理解检查和表达练习。
- **收藏与复习**：收藏单词和短语，后续集中复习。
- **自动定时任务**：后端启动后会检查当天文章数量，不足时自动补抓；默认每天 9:30 自动更新。

### 技术栈

| 模块 | 技术 |
|---|---|
| 前端 | React, Vite, React Router |
| 后端 | FastAPI, SQLAlchemy, APScheduler |
| 数据库 | SQLite |
| 新闻抓取 | RSS, Requests, BeautifulSoup, Feedparser |
| AI 能力 | DeepSeek 主用，MiniMax 备用 |

### 项目结构

```text
english_learning/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── routers/         # API routes
│   │   ├── services/        # news, vocabulary, AI tutor, scheduler
│   │   ├── models/          # database models and schemas
│   │   └── config.py
│   ├── requirements.txt
│   └── run.py
├── frontend/                # React + Vite frontend
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── App.jsx
│   └── package.json
├── miniprogram/             # WeChat mini program prototype
├── docs/                    # product and technical documents
├── back_pictures/           # fallback article images
└── start.sh                 # local startup script
```

### 快速开始

#### 1. 克隆项目

```bash
git clone https://github.com/aiNewbie-yiru/Learning_via_news.git
cd Learning_via_news
```

#### 2. 后端环境

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

在 `backend/.env` 中配置你的 AI API Key 和代理：

```env
DATABASE_URL=sqlite:///./data/english_learning.db

DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com

MINIMAX_API_KEY=your-minimax-api-key-here
MINIMAX_GROUP_ID=your-minimax-group-id-here
MINIMAX_MODEL=minimax-m2.7

OPENAI_PROXY_URL=
NEWS_PROXY_URL=http://127.0.0.1:7890

DAILY_ARTICLE_TARGET=5
VOCAB_WORD_LIMIT=15
VOCAB_PHRASE_LIMIT=3
VOCAB_MIN_DIFFICULTY=CET4
```

#### 3. 前端环境

```bash
cd ../frontend
npm install
```

#### 4. 启动项目

在项目根目录运行：

```bash
./start.sh
```

也可以分别启动：

```bash
# backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# frontend
cd frontend
npm run dev
```

访问地址：

- 前端页面：http://localhost:3000
- 后端 API：http://127.0.0.1:8000
- API 文档：http://127.0.0.1:8000/docs

### 常用 API

| 功能 | 方法 | 地址 |
|---|---|---|
| 健康检查 | GET | `/health` |
| 今日文章 | GET | `/api/articles/compare?limit=5` |
| 手动抓取新闻 | POST | `/api/articles/fetch-now` |
| 补处理话题标签 | POST | `/api/articles/process-missing-topic-labels` |
| 补处理词汇 | POST | `/api/articles/process-missing-vocabulary` |
| AI Tutor 对话 | POST | `/api/chat` |
| 收藏管理 | GET/POST/DELETE | `/api/favorites` |

### 开发备注

- `backend/.env` 不应提交到 GitHub，仓库只保留 `.env.example`。
- 新闻抓取可能需要代理，默认可通过 `NEWS_PROXY_URL=http://127.0.0.1:7890` 配置。
- AI 请求和新闻请求使用独立代理配置，便于分别调试。
- 首次启动时如果当天文章不足，后端会自动补抓并处理词汇。

---

## English

### Overview

Learning via News is a full-stack English learning app built around real-world news. It fetches daily English articles, extracts useful words and phrases, enriches them with AI-generated explanations, and turns each article into an interactive reading session.

The goal is simple: help learners improve vocabulary, reading comprehension, and discussion skills through authentic news contexts.

### Features

- **Daily news pipeline**: fetches articles from sources such as BBC, CNN, and Reuters.
- **Today topics**: shows daily topic tabs with English hooks and Chinese tags.
- **Vocabulary extraction**: identifies important words and phrases from each article.
- **AI-enhanced explanations**: generates Chinese definitions, English explanations, examples, pronunciation hints, and context-aware notes.
- **Inline word annotations**: displays short Chinese meanings directly under matched words in the article text.
- **AI Tutor**: supports article-based conversation, comprehension checks, and speaking/writing practice.
- **Favorites and review**: saves useful words and phrases for later review.
- **Scheduled updates**: checks and fills the daily article pool automatically, with a default update time of 9:30.

### Tech Stack

| Layer | Stack |
|---|---|
| Frontend | React, Vite, React Router |
| Backend | FastAPI, SQLAlchemy, APScheduler |
| Database | SQLite |
| News Fetching | RSS, Requests, BeautifulSoup, Feedparser |
| AI Providers | DeepSeek as primary provider, MiniMax as fallback |

### Quick Start

#### 1. Clone the repository

```bash
git clone https://github.com/aiNewbie-yiru/Learning_via_news.git
cd Learning_via_news
```

#### 2. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` with your own API keys and proxy settings:

```env
DATABASE_URL=sqlite:///./data/english_learning.db

DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com

MINIMAX_API_KEY=your-minimax-api-key-here
MINIMAX_GROUP_ID=your-minimax-group-id-here
MINIMAX_MODEL=minimax-m2.7

OPENAI_PROXY_URL=
NEWS_PROXY_URL=http://127.0.0.1:7890

DAILY_ARTICLE_TARGET=5
VOCAB_WORD_LIMIT=15
VOCAB_PHRASE_LIMIT=3
VOCAB_MIN_DIFFICULTY=CET4
```

#### 3. Set up the frontend

```bash
cd ../frontend
npm install
```

#### 4. Run the app

From the project root:

```bash
./start.sh
```

Or run backend and frontend separately:

```bash
# backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# frontend
cd frontend
npm run dev
```

URLs:

- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

### Useful Endpoints

| Feature | Method | Endpoint |
|---|---|---|
| Health check | GET | `/health` |
| Today's articles | GET | `/api/articles/compare?limit=5` |
| Fetch news manually | POST | `/api/articles/fetch-now` |
| Process missing topic labels | POST | `/api/articles/process-missing-topic-labels` |
| Process missing vocabulary | POST | `/api/articles/process-missing-vocabulary` |
| AI Tutor chat | POST | `/api/chat` |
| Favorites | GET/POST/DELETE | `/api/favorites` |

### Notes

- Do not commit `backend/.env`; use `backend/.env.example` as the template.
- News fetching may require a proxy. Configure it with `NEWS_PROXY_URL`.
- AI requests and news requests use separate proxy settings.
- On startup, the backend initializes the database and automatically checks whether today's article pool needs to be filled.

### License

This project is currently for personal learning and experimentation. Add a license before public distribution if needed.
