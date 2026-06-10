# PRD.md - 产品需求文档

## 1. 产品概述

**产品名称**: 英语学习工具

**核心功能**: 每天抓取英文新闻，自动提取并增强词汇，用户在首页直接完成阅读、查词、收藏和 AI tutor 练习。

### 用户核心流程

```
启动/定时补抓今日新闻 -> AI 生成话题标签 -> 提取词汇与短语 -> AI 增强释义 -> 首页阅读学习 -> 收藏与复习
```

---

## 2. 首页学习流

### 2.1 首页形态

首页从“文章选择页”改为“今日文章学习页”：

```text
顶部：Today's Topics
[SpaceX IPO #航天] [Fuel Freeze #燃油] [Robot Race #无人车] ...

主体：
左侧：当前文章正文 + AI tutor
右侧：当前文章 Words / Phrases 词汇栏
```

### 2.2 Topic 标签

每篇今日文章需要两个短标签：

- `topic_label`: 英文 topic hook，2-3 个英文词，Title Case，尽量吸引人且准确
- `topic_label_cn`: 中文话题标签，格式 `#话题`，`#` 后不超过 4 个汉字

示例：

```json
{
  "topic_label": "SpaceX IPO",
  "topic_label_cn": "#航天"
}
```

生成规则：

1. 输入文章 title、summary、content 前 500 字符
2. AI 返回 JSON
3. 存入 `articles.topic_label` 和 `articles.topic_label_cn`
4. 首页顶部展示 5 个 topic，用户点击切换当前文章
5. 如果缺失标签，前端 fallback 到标题前三个词和 `#新闻`

### 2.3 文章与词汇布局

左侧文章区：

- 新闻来源
- 难度标签
- 文章标题
- 日期和原文链接
- 正文
- AI tutor / Discussion 区域

右侧词汇区：

- `Words` tab
- `Phrases` tab
- 词汇卡片支持收藏
- 右侧在桌面端 sticky，移动端堆叠显示

### 2.4 首页视觉呈现

首页仍然是直接阅读页，不做“新闻卡片 -> 阅读按钮 -> 详情页”的二级入口。用户进入首页后，应直接看到当前文章的完整阅读体验。

页面结构保持：

```text
顶部：5 个 Today Topics 小标题，点击切换当天文章
主体：带新闻背景图和蒙版的当前文章全文 + 右侧 Words/Phrases 词汇栏
```

视觉规则：

- 每篇文章尽量绑定一张相关新闻图，优先从新闻原文抓取。
- 背景图用于当前文章阅读区，不新增额外“阅读按钮”。
- 正文、标题、来源、日期等文字直接排在背景图之上。
- 背景图上必须覆盖深色或渐变蒙版，保证文字可读。
- 暂不做人物脸部检测或自动避让；统一依靠蒙版和排版保证可读性。
- 文字排版可以根据屏幕尺寸变化，但不能遮挡右侧词汇栏。
- 如果新闻没有图片，使用分类默认图或纯色渐变 fallback，页面不能报错。

图片来源优先级：

1. 新闻原文 `og:image`
2. RSS `media:thumbnail` / `media:content`
3. 文章正文中的第一张有效图片
4. 分类默认图

分类默认图规则：

| 分类 | 默认图 |
|---|---|
| politics | `back_pictures/pexels-aaron-johnson-189853-5733167.jpg` |
| technology | `back_pictures/technology.jpg` |
| economy / trade | NYSE 交易大厅图 |
| energy | 风电 + 太阳能图 |
| environment / climate | 洪水 / 气候灾害图 |
| health / medicine | 医生讨论病例图 |
| world | 城市天际线图 |

注意：分类默认图只在文章没有可用新闻原图时使用。若用户提供的默认图包含第三方水印或版权标识，开发阶段可作为占位参考，正式版本必须替换为拥有使用权的图片。

建议文章表新增字段：

```sql
ALTER TABLE articles ADD COLUMN image_url VARCHAR(1000);
ALTER TABLE articles ADD COLUMN image_source VARCHAR(200);
ALTER TABLE articles ADD COLUMN image_alt VARCHAR(500);
```

### 2.5 正文内联单词注释

目标：让用户阅读原文时，直接在原文对应单词下方看到该单词在当前语境中的中文含义，而不是把所有单词注释放在整篇文章下方。

展示规则：

- 只对 `article.words` 中的单词做正文内联注释；短语暂时仍保留在右侧 `Phrases` tab，不做跨词内联标注。
- 注释放在原文中命中的对应单词下方，形成“英文单词在上、中文语境义在下”的局部阅读单元。
- 注释内容只显示该单词在当前原文语境下的对应中文意思，优先使用 `definition_cn` 中最贴合 `example_sentence` / 原文上下文的一个短义项。
- 注释文字必须简短，推荐 1-6 个汉字或一个极短中文短语；不展示完整词典释义、英文定义、例句、发音、难度等信息。
- 注释使用圆角矩形填充，放在单词下方，不能挤压到前后行造成重叠；移动端需要自动换行并保持正文可读。
- 不同词性使用不同颜色，以便用户快速识别词性。颜色用于注释矩形，不改变原文正文主色。
- 右侧 `Words` tab 继续保留完整词汇卡片，用于查看完整释义、词性、发音、例句、收藏等信息；正文内联注释只承担快速阅读辅助。

匹配规则：

- 单词匹配应大小写不敏感，但展示时保留原文大小写。
- 只匹配完整单词边界，避免把 `trade` 错标到 `trademark` 这类更长单词中。
- 同一个词在正文中多次出现时，不默认复用同一个中文义项；每个出现位置都应以所在句子和上下文判断当前语境义。
- 如果当前数据暂时只能提供一个 `definition_cn`，也必须把它当作候选义项，优先选取最贴合该出现位置上下文的短义项，不能直接展示完整释义列表。
- 如果原文中出现复数、过去式、进行式等常见形态，允许映射到 `words.word` 的基础词形；若无法可靠匹配，不强行标注。
- 当多个词条可能匹配同一段文本时，优先使用更长、更具体的匹配；当前阶段 `Words` 只处理单词，短语不参与抢占匹配。

词性颜色规则：

| 词性 | 适用值 | 注释颜色语义 |
|---|---|---|
| 名词 | `noun`, `n.` | 蓝色系 |
| 动词 | `verb`, `v.` | 绿色系 |
| 形容词 | `adjective`, `adj.` | 紫色系 |
| 副词 | `adverb`, `adv.` | 橙色系 |
| 介词/连词/其他 | `prep.`, `conj.`, `phrase`, unknown | 灰色系 |

交互规则：

- 鼠标悬停或点击内联注释时，可以高亮右侧 `Words` tab 中对应词卡；若右侧栏不在视口内，不强制滚动。
- 点击原文中的被注释单词，可以打开或定位到右侧对应词卡，便于收藏和查看完整信息。
- 如果某个词没有可用的 `definition_cn` 或词性，仍可显示基础中文义项；颜色使用 unknown 灰色系。

---

## 3. 新闻抓取

**职责**: 从 RSS 源抓取英文新闻，保存到数据库，并补足每天目标文章数量。

### 数据源

- BBC RSS feeds
- CNN RSS feeds
- Reuters RSS feeds
- NewsAPI 作为备用，需要配置 `NEWS_API_KEY`

### 每日目标

配置项：

```env
DAILY_ARTICLE_TARGET=5
```

系统每天目标抓取并处理 5 篇文章。若启动后发现当天不足 5 篇，会自动补抓剩余数量。

### 处理流程

1. `fetch_all_news()` 遍历 RSS 源
2. 跳过已入库 URL，避免重复
3. 获取正文，截取前 1500 字符且尽量保留完整句子
4. 为文章生成 topic 标签
5. 提取词汇和短语
6. 调用 AI 增强词汇和短语
7. 保存文章、词汇、短语

### 代理策略

新闻抓取使用独立配置：

```env
NEWS_PROXY_URL=http://127.0.0.1:7890
```

新闻代理与 AI 代理分离，避免互相影响。

---

## 4. 词汇提取

**职责**: 从文章文本中提取词汇，按难度分级。

**难度体系**:

```text
Basic < CET4 < CET6 < TOEFL < GRE
```

关键函数：

- `get_word_difficulty(word)`
- `extract_words(text, min_difficulty="CET4")`
- `extract_phrases(text)`
- `analyze_text(text, min_difficulty)`

词汇选择规则：

- 只保留难度不低于 `VOCAB_MIN_DIFFICULTY` 的词
- 按难度和出现次数排序
- 每篇文章最多处理 `VOCAB_WORD_LIMIT` 个单词
- 每篇文章最多处理 `VOCAB_PHRASE_LIMIT` 个短语

---

## 5. AI 增强

### 5.1 词汇和短语增强

主链路：

```text
DeepSeek -> MiniMax 备用 -> 本地 fallback
```

配置：

```env
DEEPSEEK_API_KEY=
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com

MINIMAX_API_KEY=
MINIMAX_GROUP_ID=
MINIMAX_MODEL=minimax-m2.7
MINIMAX_BASE_URL=https://api.minimax.chat/v1/text/chatcompletion_v2
```

AI 请求代理：

```env
OPENAI_PROXY_URL=
```

为空时 AI 请求强制直连，不读取系统 `HTTP_PROXY/HTTPS_PROXY`。

增强内容：

- 英文释义
- 中文释义
- 原文语境中文义项
- 最高频其他中文义项
- 文章原句
- AI 生成第二例句
- 词性
- IPA 发音
- 短语释义和例句

词汇释义规则：

- `definition`: 可以保留英文释义，但必须更短、更适合学习者；不要生成复杂、绕口的词典式长句。
- `definition_cn`: 不是英文 `definition` 的翻译，而是直接面向中文用户的短中文释义。
- 中文释义优先给该单词在原文语境中的意思。
- 如果一词多义，只额外给 1 个最高频、最常用的其他义项。
- 不列多个低频义项，不写长句，不输出解释性废话。
- 后续数据结构增加 `context_definition_cn` 和 `common_definition_cn`：
  - `context_definition_cn`: 原文语境义
  - `common_definition_cn`: 最高频其他义
- 前端展示给用户时合并为简洁形式，不添加“原文义”“常用义”等标签文字。示例：`clear，清理，清除；清楚的`。

### 5.2 AI tutor

AI tutor 保留在文章下方。用户围绕当前文章发言，系统调用聊天服务回复。

约束：

- 优先 DeepSeek
- MiniMax 备用
- 本地 keyword fallback
- 回复 2-4 句
- 120 英文词以内
- 必须完整收句，避免 UI 显示截断

---

## 6. 收藏与复习

### 收藏

用户可以在词汇栏收藏：

- 单词
- 短语

收藏保存来源文章、释义、例句、难度、词性和发音等信息。

### 复习

现有复习基础：

- `review_count`
- `last_reviewed_at`
- `favorite_count`

复习流程：

1. GET `/api/favorites/review` 返回 flashcard
2. 用户查看答案
3. PUT `/api/favorites/review/{id}` 标记已复习
4. 更新复习次数和最后复习时间

后续可扩展：

- `mastery_level`
- `next_review_at`
- 认识 / 模糊 / 不认识 三档反馈

---

## 7. API

### 文章

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/articles/compare?limit=5` | 返回今天已处理词汇的文章，首页使用 |
| GET | `/api/articles/today` | 返回当前 today 文章 |
| GET | `/api/articles/{id}` | 返回文章详情 |
| POST | `/api/articles/fetch-now` | 手动抓取并处理今日文章 |
| POST | `/api/articles/process-missing-vocabulary` | 补处理缺失词汇 |
| POST | `/api/articles/process-missing-topic-labels` | 补生成 topic 标签 |

### 收藏和复习

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/favorites/words` | 单词收藏列表 |
| POST | `/api/favorites/words/{word_id}` | 收藏单词 |
| DELETE | `/api/favorites/words/{id}` | 删除收藏单词 |
| GET | `/api/favorites/phrases` | 短语收藏列表 |
| POST | `/api/favorites/phrases/{phrase_id}` | 收藏短语 |
| GET | `/api/favorites/review` | 获取复习卡片 |

### AI tutor / comments

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/comments/article/{article_id}` | 获取文章讨论 |
| POST | `/api/comments/` | 提交评论并获取 AI tutor 回复 |

---

## 8. 定时任务

`scheduler.py` 每天 `PUSH_HOUR:PUSH_MINUTE` 执行。

默认：

```env
PUSH_HOUR=9
PUSH_MINUTE=30
SCHEDULER_TIMEZONE=Asia/Shanghai
```

启动补抓：

- 后端启动时检查当天文章数量
- 如果少于 `DAILY_ARTICLE_TARGET`，启动后约 2 秒安排一次补抓任务
- 如果已经达到目标，跳过补抓

---

## 9. 数据表更新

### Article 表新增字段

```sql
ALTER TABLE articles ADD COLUMN topic_label VARCHAR(50);
ALTER TABLE articles ADD COLUMN topic_label_cn VARCHAR(20);
```

### FavoriteWord 表字段

```sql
ALTER TABLE favorite_words ADD COLUMN favorite_count INTEGER DEFAULT 1;
ALTER TABLE favorite_words ADD COLUMN pronunciation VARCHAR(100);
```

---

## 10. 暂不做

- 用户偏好学习自动调节难度
- 首页 skip 卡片选择器
- 复杂间隔重复算法
