# PRD.md - 产品需求文档

## 1. 产品概述

**产品名称**: 英语学习工具
**核心功能**: 从英文新闻中提取词汇，帮助用户学习和复习

### 用户核心流程

```
每日定时抓取新闻 → 提取词汇（按难度过滤）→ AI增强释义 → 用户收藏复习
```

---

## 2. 核心功能

### 2.1 新闻抓取

**职责**: 定时从 RSS 源抓取英文新闻，保存到数据库

**数据源**（config.py NEWS_SOURCES）:
- BBC RSS feeds（经济、政治、科技、环境、医疗等分类）
- CNN RSS feeds
- Reuters RSS feeds
- NewsAPI 作为备用（需要配置 NEWS_API_KEY）

**处理流程**:
1. `fetch_all_news()` 遍历所有 RSS 源，每个源最多5篇文章
2. `fetch_article_content(url)` 获取文章全文（取前1500字符，确保完整句子）
3. `get_random_article()` 随机选择一篇返回
4. `get_two_random_articles()` 随机选择2篇（尝试不同分类）

**异常处理**:
- RSS 解析失败 → 跳过该源
- 代理设置 → 从 `HTTPS_PROXY`/`HTTP_PROXY` 环境变量读取

---

### 2.2 词汇提取（核心功能）

**职责**: 从文章文本中提取词汇，按难度分级

**难度体系**:
```
Basic ⊂ CET4 ⊂ CET6 ⊂ TOEFL ⊂ GRE
```

| 等级 | 说明 | 词库大小 |
|------|------|----------|
| Basic | 初中级基础词汇 | ~347 |
| CET4 | 大学英语四级 | ~1770 |
| CET6 | 大学英语六级 | ~3380 |
| TOEFL | 托福词汇 | ~3998 |
| GRE | GRE词汇 | ~4364 |

**关键函数**:

1. `get_word_difficulty(word)` → 返回 "Basic"/"CET4"/"CET6"/"TOEFL"/"GRE"/None

2. `extract_words(text, min_difficulty="CET4")`:
   - 正则 `\b[a-zA-Z]{3,}\b` 提取3字符以上的词
   - 排除 Basic 词库（stop_words）
   - 只保留难度 ≥ min_difficulty 的词
   - 按难度从高到低排序
   - 返回: word, difficulty, count, register, roots

3. `extract_phrases(text)`:
   - 遍历 PHRASES 列表（目标扩充到 200-300 个短语）
   - 遍历 IDIOMS 列表（目标扩充到 100 个习语）
   - 返回匹配的短语/习语列表

4. `analyze_text(text, min_difficulty)`:
   - 合并 extract_words + extract_phrases

**词根词缀分析**:
- 前缀: un-, re-, pre-, dis-, in-, im-, ex-, sub-, super-, inter-, trans-, anti-, auto-, bio-, co-, de-, mis-, over-, post-, tele-
- 后缀: -able/-ible, -tion/-sion, -ment, -ness, -ful, -less, -ly, -er/-or, -ist, -ize/-ise, -ous/-ious
- 词根: spect, dict, port, struct, duct, scrib/script, ject, tract, form, mit/miss

**语域分类**: academic, formal, informal, technical, business, general

---

### 2.3 AI 词汇增强

**职责**: 调用 MiniMax API 为每个词汇生成详细释义

**增强内容**:
- definition: 英文定义（必须是该单词的真实英文释义，不是 "A word related to X" 这样的模板）
- definition_cn: 中文翻译（必须与 definition 对应，不是通用翻译）
- example_sentence: **第一例句**（从新闻原文中抓取该词所在句子，截取主谓宾结构，保留真实语境）
- example_cn: 第一例句的中文翻译（必须与 example_sentence 对应）
- example_sentence_2: **第二例句**（AI 生成同等难度的例句）
- example_sentence_2_cn: 第二例句的中文翻译（必须与 example_sentence_2 对应）
- example_source: 例句来源（新闻标题或 "AI Generated"）
- part_of_speech: 词性
- pronunciation: IPA 发音

**例句生成规则**:
1. **第一例句**（原始例句）:
   - 从新闻原文中找到该词出现的完整句子
   - **如果句子过长（>40词），截取主谓宾结构作为主干**
   - 保留包含目标词的从句/分词结构，不要截断到目标词之前
   - example_source = 新闻标题 + " - [新闻URL]"
2. **第二例句**（AI 生成）:
   - AI 生成一个与第一例句难度相近的例句
   - 用于展示该词的多种用法
   - 必须包含目标单词

**例句截断具体规则**:
- 如果句子 > 40 词，以目标词为中心，向前取 5 词，向后取 15 词
- 如果目标词在句首，向后取 20 词
- 如果目标词在句尾，向前取 20 词
- 截断处添加 "..." 表示省略

**fallback 模板（API 失败时使用）**:
```python
definition: f"A {difficulty} level word"  # 禁止使用
definition: f"{word.capitalize()} refers to a specific concept"  # 正确
example_cn: "这是例句的中文翻译"  # 必须与英文例句对应
```

**常见错误修复**:
- ❌ definition = "A word related to {word}" （禁止使用）
- ❌ example_cn = "理解 '{word}' 对于...至关重要" （通用翻译，不对应）
- ✅ definition = 真实英文释义
- ✅ example_cn = 对应英文例句的准确翻译

---

### 2.4 短语提取规则

**当前方案**: 维护短语/习语列表，文本匹配检测

**短语列表扩充目标**:
- PHRASES: 从 ~100 个扩充到 200-300 个常用短语
- IDIOMS: 从 ~70 个扩充到 ~100 个常用习语

**短语类型**:
- 动词短语: look into, look up, look forward to, put up with
- 介词短语: in terms of, with respect to, on behalf of
- 习语: break a leg, piece of cake, cost an arm and a leg

---

### 2.5 用户收藏与复习

**收藏内容**:
- FavoriteWord: 单词 + 释义 + 复习次数
- FavoritePhrase: 短语 + 含义 + 复习次数

**复习优先级**:
- 同一单词被收藏 **2次以上** → 高优先级
- 优先推送高频收藏单词
- 复习流程:
  1. GET `/api/favorites/review` 返回随机 flashcard（高优先级优先）
  2. 用户查看答案后 PUT `/api/favorites/review/{id}` 标记已复习
  3. review_count +1, last_reviewed_at 更新

**favorite_count 字段**:
- 每次用户从文章详情页收藏单词时，`favorite_count` +1
- 用于计算复习优先级

---

### 2.6 AI 聊天

**职责**: 用户可以对文章提问，获取 AI 回答

**实现**: MiniMax API 调用，失败时有 keyword-based fallback

---

## 3. 前端页面

### 页面布局

| 页面 | 路由 | 功能 |
|------|------|------|
| 文章选择 | `/` | 调用 `/api/articles/compare` 选择两篇 |
| 文章详情 | `/article/:id` | 显示文章内容、词汇列表（展示2个例句）、收藏按钮、评论区 |
| 收藏列表 | `/favorites` | 显示已收藏的单词和短语 |
| 复习 | `/review` | flashcard 复习界面（高优先级词优先） |

### 前端样式要求

**词汇卡片宽度**: words 模块宽度为页面宽度的 40%，确保例句不会跨行太长

**词汇展示结构**:
```
┌─────────────────────────────────────┐
│ gallery [TOEFL] [noun]              │
├─────────────────────────────────────┤
│ 📖 Definition                       │
│ a room or building for the display..│
│ 展示或展览艺术品的大厅或建筑         │
├─────────────────────────────────────┤
│ 💡 Example 1 (From article)         │
│ A viewing gallery will show...       │
│ 一个可以观看所有企鹅健康检查的...    │
├─────────────────────────────────────┤
│ 💡 Example 2 (AI Generated)          │
│ The museum's new gallery opened...   │
│ 博物馆的新画廊开张了...              │
└─────────────────────────────────────┘
```

**短语识别要求**:
- 短语列表应包含 2-3 个单词的组合（如 "aardvark" 是单词不是短语）
- 避免将单个单词误识别为短语
- 短语必须是真正的词组搭配 |

---

## 4. 定时任务

**scheduler.py**: 每天 `PUSH_HOUR:PUSH_MINUTE`（默认9:30）执行 `fetch_and_process_daily_news()`

**流程**:
1. 设置旧 today 文章 `is_today=False`
2. 抓取新随机文章
3. 保存到数据库，`is_today=True`
4. 调用 `word_extractor.analyze_text()` 提取词汇
5. 对每个词：
   - 从原文中抓取第一例句
   - 调用 `vocab_enhancer.enhance_word()` 获取 AI 生成内容（第二例句、中文释义等）
6. 保存到数据库

---

## 5. 数据表更新

### FavoriteWord 表新增字段

```sql
ALTER TABLE favorite_words ADD COLUMN favorite_count INTEGER DEFAULT 1;
```

---

## 6. 移除功能

### 用户偏好学习（已移除）

~~用户选择文章后，系统自动调整词汇难度阈值~~

**原因**: 实现价值不明显，增加复杂度，暂不开发。