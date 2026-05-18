# PROJECT_CONTEXT.md - 项目运行上下文

## 1. 如何运行项目

### 启动命令

```bash
cd /Users/hljy/Documents/trae_projects/english_learning
./start.sh
```

**start.sh 做了什么**:
1. 启动 backend: `cd backend && venv/bin/python run.py`
2. 启动 frontend: `cd frontend && npm run dev`
3. 设置代理: `HTTPS_PROXY=http://127.0.0.1:7890`

### 访问地址

- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

---

## 2. 项目结构

```
english_learning/
├── SPEC.md              # 产品需求文档
├── start.sh             # 启动脚本
├── backend/
│   ├── run.py           # 后端入口
│   ├── requirements.txt # Python 依赖
│   ├── .env             # 环境变量（包含 API keys）
│   └── app/
│       ├── main.py      # FastAPI 应用定义
│       ├── config.py    # 配置（Settings）
│       ├── routers/     # API 路由
│       │   ├── articles.py   # 文章相关 API
│       │   ├── favorites.py   # 收藏相关 API
│       │   ├── chat.py       # AI 聊天 API
│       │   └── comments.py    # 评论 API
│       ├── models/
│       │   ├── database.py   # SQLAlchemy 模型
│       │   └── schemas.py   # Pydantic schemas
│       └── services/
│           ├── news_scraper.py   # 新闻抓取
│           ├── word_extractor.py # 词汇提取
│           ├── vocab_enhancer.py # AI 词汇增强
│           ├── ai_chat.py        # AI 聊天
│           └── scheduler.py      # 定时任务
├── frontend/
│   ├── package.json
│   ├── vite.config.js   # 代理配置
│   └── src/
│       ├── App.jsx
│       └── pages/
└── docs/
    ├── PRD.md           # 产品需求文档
    ├── PROJECT_CONTEXT.md  # 本文档
    ├── DATA_SCHEMA.md   # 数据结构文档
    └── TEST_CHECKLIST.md   # 测试检查清单
```

---

## 3. 核心模块依赖关系

```
scheduler.py (定时任务编排)
    ├── news_scraper.get_random_article()
    ├── word_extractor.analyze_text()
    └── vocab_enhancer.enhance_word/enhance_phrase()

vocab_enhancer.py (AI 增强)
    └── calls MiniMax API

articles.py (API 路由)
    ├── news_scraper.get_two_random_articles()
    └── user_difficulty_preferences (内存 dict)

favorites.py (API 路由)
    └── 数据库 FavoriteWord/FavoritePhrase 表
```

---

## 4. 关键配置

### config.py

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| DATABASE_URL | `sqlite:///data/english_learning.db` | 数据库路径 |
| MINIMAX_API_KEY | (硬编码在 .env) | MiniMax API 密钥 |
| PUSH_HOUR | 9 | 定时任务执行小时 |
| PUSH_MINUTE | 30 | 定时任务执行分钟 |
| SCHEDULER_TIMEZONE | Asia/Shanghai | 时区 |

### NEWS_SOURCES

按分类配置了 BBC/ CNN/ Reuters RSS 源。如果某个 RSS 源失效，该分类的新闻会减少。

---

## 5. 前端代理配置

**vite.config.js**:
```javascript
proxy: {
  '/api': 'http://localhost:8000'
}
```

如果后端端口从 8000 改为其他值，必须同步修改这里。

---

## 6. 内存状态（重启会丢失）

### user_difficulty_preferences (articles.py)

```python
user_difficulty_preferences = {
    "default": "CET4"
}
```

存储用户选择的文章难度偏好，重启后恢复默认值。

---

## 7. 常见操作

### 手动抓取新闻

```bash
cd backend
./venv/bin/python fetch_news.py
```

### 查看数据库内容

```bash
cd backend
./venv/bin/python check_db.py
```

### 更新今日文章

```bash
cd backend
./venv/bin/python update_today_article.py
```

### 重新处理词汇（修复缺失的 AI 释义）

```bash
cd backend
./venv/bin/python migrate_vocab.py
```

---

## 8. 前端路由

| 页面 | 文件 |
|------|------|
| 文章选择页 | App.jsx |
| 文章详情页 | pages/ArticleDetail.jsx |
| 收藏列表 | pages/Favorites.jsx |
| 复习页面 | pages/Review.jsx |

---

## 9. 环境要求

- Python 3.9+
- Node.js 18+
- SQLite (无需单独安装)
- 代理: http://127.0.0.1:7890 (用于访问外网 RSS)