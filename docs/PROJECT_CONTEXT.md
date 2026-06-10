# PROJECT_CONTEXT.md - 项目运行上下文

## 1. 如何运行项目

### 启动命令

```bash
cd /Users/hljy/Documents/trae_projects/english_learning
./start.sh
```

当前开发环境也可以分别启动：

```bash
cd backend
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

cd frontend
npm run dev
```

### 访问地址

- 前端: http://localhost:3000
- 后端 API: http://127.0.0.1:8000
- API 文档: http://127.0.0.1:8000/docs

---

## 2. 当前产品形态

首页是“今日文章学习页”，不是文章选择页。

```text
顶部：今日 5 篇文章的 topic 标签
左侧：当前文章正文 + AI tutor
右侧：当前文章 Words / Phrases
```

Topic 标签字段：

- `Article.topic_label`: 2-3 个英文词
- `Article.topic_label_cn`: 中文 `#话题` 标签，`#` 后不超过 4 个汉字

首页请求：

```http
GET /api/articles/compare?limit=5
```

只返回今天且已经处理过词汇的文章，不再混入历史文章或 sample article。

---

## 3. 项目结构

```text
english_learning/
├── start.sh
├── backend/
│   ├── run.py
│   ├── requirements.txt
│   ├── .env
│   └── app/
│       ├── main.py
│       ├── config.py
│       ├── routers/
│       │   ├── articles.py
│       │   ├── favorites.py
│       │   ├── chat.py
│       │   └── comments.py
│       ├── models/
│       │   ├── database.py
│       │   └── schemas.py
│       └── services/
│           ├── news_scraper.py
│           ├── word_extractor.py
│           ├── vocab_enhancer.py
│           ├── ai_chat.py
│           └── scheduler.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── App.css
│       ├── components/CommentsSection.jsx
│       └── pages/
└── docs/
    ├── PRD.md
    ├── PROJECT_CONTEXT.md
    ├── DATA_SCHEMA.md
    └── TEST_CHECKLIST.md
```

---

## 4. 核心模块依赖

```text
scheduler.py
    ├── news_scraper.fetch_all_news()
    ├── vocab_enhancer.generate_topic_labels()
    ├── word_extractor.analyze_text()
    └── vocab_enhancer.enhance_word/enhance_phrase()

vocab_enhancer.py
    └── DeepSeek 主用，MiniMax 备用

ai_chat.py
    └── DeepSeek 主用，MiniMax 备用，本地 fallback

articles.py
    └── 返回今日文章池、补处理词汇、补 topic 标签
```

---

## 5. 关键配置

`.env` 关键项：

```env
DATABASE_URL=sqlite:///./data/english_learning.db

DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com

MINIMAX_API_KEY=
MINIMAX_GROUP_ID=
MINIMAX_MODEL=minimax-m2.7
MINIMAX_BASE_URL=https://api.minimax.chat/v1/text/chatcompletion_v2

OPENAI_PROXY_URL=
NEWS_PROXY_URL=http://127.0.0.1:7890

DAILY_ARTICLE_TARGET=5
VOCAB_WORD_LIMIT=15
VOCAB_PHRASE_LIMIT=3
VOCAB_MIN_DIFFICULTY=CET4

SCHEDULER_TIMEZONE=Asia/Shanghai
PUSH_HOUR=9
PUSH_MINUTE=30
```

代理策略：

- AI 请求看 `OPENAI_PROXY_URL`
- `OPENAI_PROXY_URL=` 为空时，Python requests 强制忽略系统代理并直连
- 新闻抓取看 `NEWS_PROXY_URL`
- BBC/CNN/Reuters 等 RSS 通常需要 `NEWS_PROXY_URL=http://127.0.0.1:7890`

---

## 6. 定时与启动补抓

每天默认 9:30 执行：

```python
fetch_and_process_daily_news()
```

行为：

1. 检查今天已经处理的文章数量
2. 如果少于 `DAILY_ARTICLE_TARGET`，继续抓取并处理缺口
3. 跳过已入库 URL，避免重复
4. 每篇文章生成 topic 标签、词汇、短语

后端启动时也会检查当天数量：

- 达到 5 篇：跳过
- 不足 5 篇：启动后约 2 秒自动补抓

---

## 7. 常见操作

### 检查后端健康

```bash
curl http://127.0.0.1:8000/health
```

### 手动补抓今日文章

```bash
curl -X POST http://127.0.0.1:8000/api/articles/fetch-now
```

### 补处理缺失 topic 标签

```bash
curl -X POST http://127.0.0.1:8000/api/articles/process-missing-topic-labels
```

### 补处理缺失词汇

```bash
curl -X POST http://127.0.0.1:8000/api/articles/process-missing-vocabulary
```

### 查看数据库内容

```bash
cd backend
./venv/bin/python check_db.py
```

---

## 8. 前端路由

| 页面 | 文件 | 说明 |
|---|---|---|
| 今日学习页 | `src/App.jsx` | 首页，topic 导航 + 文章 + 词汇 + AI tutor |
| 文章详情页 | `src/pages/ArticleDetail.jsx` | 详情路由保留 |
| 收藏列表 | `src/pages/Favorites.jsx` | 已收藏词汇和短语 |
| 复习页 | `src/pages/Review.jsx` | flashcard 复习 |

---

## 9. 验证命令

后端测试：

```bash
cd backend
./venv/bin/python -m pytest tests
```

前端构建：

```bash
cd frontend
npm run build
```

当前已验证：

- 后端测试 `44 passed`
- 前端 `npm run build` 通过
- `/api/articles/compare?limit=5` 返回 5 篇今日文章和 topic 标签
