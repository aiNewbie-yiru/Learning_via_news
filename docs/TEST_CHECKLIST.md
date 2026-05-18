# TEST_CHECKLIST.md - 测试检查清单

每次修改代码后必须运行以下检查，确保功能未被破坏。

---

## 1. 词汇提取模块 (word_extractor.py)

### 必须测试的用例

**难度判断 (`get_word_difficulty`)**:
- [ ] `the` → "Basic"
- [ ] `abandon` → "CET4"
- [ ] `chronic` → "CET6"
- [ ] `quantum` → "TOEFL"
- [ ] `xyzabc` → None
- [ ] 大小写不敏感（`ABANDON` → "CET4"）
- [ ] 首尾空白被去除（`  abandon  ` → "CET4"）

**词库包含关系验证**:
- [ ] `BASIC_WORDS.issubset(CET4_WORDS)` — Basic 是 CET4 的子集
- [ ] `CET4_WORDS.issubset(CET6_WORDS)` — CET4 是 CET6 的子集
- [ ] `CET6_WORDS.issubset(TOEFL_WORDS)` — CET6 是 TOEFL 的子集
- [ ] `TOEFL_WORDS.issubset(GRE_WORDS)` — TOEFL 是 GRE 的子集
- [ ] 各级别之间没有重叠词（每个词只属于一个级别）

---

## 2. 数据库 Schema 验证（测试前必做）

**目的**: 确保数据库表结构与 `models/database.py` 中的模型定义一致，避免运行时错误。

```bash
cd backend
./venv/bin/python -c "
from app.models.database import Base, engine
from sqlalchemy import inspect

inspector = inspect(engine)
for table_name in ['articles', 'words', 'phrases', 'comments', 'favorite_words', 'favorite_phrases']:
    actual_cols = [col['name'] for col in inspector.get_columns(table_name)]
    print(f'{table_name}: {actual_cols}')
"
```

**检查项**:
- [ ] `words` 表包含 `definition_cn`, `example_cn`, `example_sentence_2`, `example_sentence_2_cn`
- [ ] `phrases` 表包含 `meaning_cn`, `example_cn`
- [ ] `favorite_words` 表包含 `favorite_count`
- [ ] 所有表的主键和外键存在

**如果列缺失**: 执行迁移脚本（见 DATA_SCHEMA.md Section 5.2）

---

## 3. API 集成测试（核心验证）

**目的**: 确保所有返回文章的 API 都包含词汇数据。

### 测试 /compare 端点
```bash
curl http://localhost:8000/api/articles/compare
```
**验证条件**:
- [ ] 返回 2 篇文章
- [ ] 每篇文章必须包含 `words` 数组（长度 > 0）
- [ ] 每篇文章必须包含 `phrases` 数组（长度 > 0）
- [ ] 如果返回空数组，说明数据库中没有已处理的文章

### 测试 /today 端点
```bash
curl http://localhost:8000/api/articles/today
```
**验证条件**:
- [ ] 返回的文章包含 `words` 和 `phrases`
- [ ] 如果词汇为空，会自动触发 `process_article_vocabulary()`

### 测试 /{id} 端点
```bash
curl http://localhost:8000/api/articles/1
```
**验证条件**:
- [ ] 文章包含完整的 `words` 和 `phrases`
- [ ] 如果词汇为空，会自动处理

---

## 4. 架构约束验证

**核心规则**: 任何返回给前端的 article，必须包含对应的 words 和 phrases。

- [ ] `/compare` 只返回数据库中已有词汇的文章（不直接从 RSS 返回）
- [ ] `/today` 如果文章没有词汇，自动触发处理
- [ ] `process_article_vocabulary()` 是所有文章返回前的必经流程

---

## 5. 新闻抓取模块 (news_scraper.py)

### 手动测试

在浏览器或 Postman 中测试：

1. **获取今日文章**:
   ```
   GET http://localhost:8000/api/articles/today
   ```
   - 应返回一篇文章，包含 title, content, words, phrases

2. **获取对比文章**:
   ```
   GET http://localhost:8000/api/articles/compare
   ```
   - 应返回2篇文章，**每篇都必须有词汇数据**

3. **手动触发抓取**:
   ```
   POST http://localhost:8000/api/articles/fetch-now
   ```
   - 检查数据库中是否新增了文章

---

## 6. 收藏功能

- [ ] POST `/api/favorites/words/{word_id}` → 收藏单词
- [ ] DELETE `/api/favorites/words/{word_id}` → 取消收藏
- [ ] GET `/api/favorites/words` → 获取收藏列表
- [ ] 同样测试 phrases

---

## 7. 复习功能

- [ ] GET `/api/favorites/review` → 返回随机 flashcards
- [ ] PUT `/api/favorites/review/{id}` → 标记已复习（review_count +1）

---

## 8. AI 增强（vocab_enhancer.py）

**注意**: 需要有效的 MiniMax API Key

- [ ] `enhance_word()` 返回完整的增强数据
- [ ] `enhance_phrase()` 返回完整的增强数据
- [ ] API 失败时有 fallback 模板

---

## 9. 定时任务（scheduler.py）

- [ ] 启动时 scheduler 正确注册任务
- [ ] 任务在指定时间执行
- [ ] 异常时正确记录日志

---

## 10. 运行测试的命令

```bash
cd backend

# 1. 测试前必须先验证数据库 schema 与 model 匹配
./venv/bin/python -c "
from app.models.database import Base, engine
from sqlalchemy import inspect
inspector = inspect(engine)
for table_name in ['articles', 'words', 'phrases', 'comments', 'favorite_words', 'favorite_phrases']:
    actual_cols = [col['name'] for col in inspector.get_columns(table_name)]
    print(f'{table_name}: {actual_cols}')
"

# 2. 运行词汇提取单元测试
./venv/bin/python -m pytest tests/test_word_extractor.py -v

# 3. 测试词库完整性（包含 GRE）
./venv/bin/python -c "
from app.services.word_extractor import BASIC_WORDS, CET4_WORDS, CET6_WORDS, TOEFL_WORDS, GRE_WORDS
assert BASIC_WORDS.issubset(CET4_WORDS), 'Basic not subset of CET4'
assert CET4_WORDS.issubset(CET6_WORDS), 'CET4 not subset of CET6'
assert CET6_WORDS.issubset(TOEFL_WORDS), 'CET6 not subset of TOEFL'
assert TOEFL_WORDS.issubset(GRE_WORDS), 'TOEFL not subset of GRE'
print('All subset checks passed!')
"

# 4. 验证 /compare 端点返回的文章都有词汇
./venv/bin/python -c "
import requests
resp = requests.get('http://localhost:8000/api/articles/compare')
articles = resp.json()
for a in articles:
    has_words = len(a.get('words', [])) > 0
    has_phrases = len(a.get('phrases', [])) > 0
    print(f\"Article {a['id']}: words={has_words}, phrases={has_phrases}\")
"
```

---

## 11. 回归测试标准

### 通过条件

1. 数据库 schema 验证通过（表结构与 model 一致）
2. 所有单元测试通过
3. 词库包含关系验证通过（Basic ⊂ CET4 ⊂ CET6 ⊂ TOEFL ⊂ GRE）
4. API 端点返回正确状态码
5. **所有返回文章的 API，文章必须包含 words 和 phrases**
6. 词汇提取逻辑未被改变

### 失败时的处理

**如果任何测试失败，禁止发布/合并代码。**

1. 找出失败的测试
2. 确认是修改导致的还是原本就存在问题
3. 如果是 schema 问题：运行数据库迁移脚本
4. 如果是 API 问题：检查 `process_article_vocabulary()` 是否被正确调用
5. 修复问题或回滚修改
6. 重新运行测试直到通过

---

## 12. 修改高风险区域时的额外检查

### 修改 word_extractor.py 词库时
- [ ] 运行全部词库完整性测试
- [ ] 检查 `get_word_difficulty` 逻辑未被改变
- [ ] 确认 `extract_words` 的 `min_difficulty` 比较逻辑正确

### 修改 scheduler.py 时
- [ ] 确认 `fetch_and_process_daily_news()` 流程未改变
- [ ] 检查 `process_article_vocabulary()` 逻辑未改变

### 修改 database.py 模型时
- [ ] 运行 schema 验证确认表结构匹配
- [ ] 如果表结构不匹配，执行数据库迁移脚本
- [ ] 测试关联查询（article.words, article.phrases）正常
- [ ] 测试 cascade 删除（删除文章时 words/phrases 也被删除）

### 修改 API 路由时
- [ ] 测试所有端点返回正确的 JSON 格式
- [ ] 确认 schema 验证正常工作