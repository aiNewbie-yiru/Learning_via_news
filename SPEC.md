# 英语学习工具 - 产品需求文档

## 1. 产品概述

这是一个基于新闻文章的英语词汇学习工具，通过抓取英文新闻、自动提取生词、 AI 释义帮助用户学习英语。

### 核心用户流程
1. 系统每日自动抓取两篇英文新闻
2. 从新闻中提取高于高中水平的词汇
3. 用户收藏词汇用于后续复习
4. 用户可以与 AI 对话讨论文章

---

## 2. 核心功能：词汇提取（word_extractor.py）

### 2.1 词汇难度分级体系

词汇分为 5 个难度等级，从低到高：

| 等级 | 名称 | 说明 | 词库大小 |
|------|------|------|----------|
| 0 | Basic | 初中级基础词汇（约3000词） | ~3000 |
| 1 | CET4 | 大学英语四级词汇（在Basic基础上扩展） | ~4500 |
| 2 | CET6 | 大学英语六级词汇（在CET4基础上扩展） | ~5500 |
| 3 | TOEFL | 托福词汇（在CET6基础上扩展） | ~7000 |
| 4 | GRE | GRE词汇（延伸，但词库未完整列出） | 未定 |

#### 词库继承关系
```
Basic ⊂ CET4 ⊂ CET6 ⊂ TOEFL ⊂ GRE
```
即 CET6 词库 = CET4 词库 ∪ 新增词  
TOEFL 词库 = CET6 词库 ∪ 新增词

**⚠️ 重要约束：修改词库时必须保持这种包含关系，否则会影响难度判断逻辑**

### 2.2 词汇提取规则（extract_words）

**输入参数：**
- `text`: 英文文章文本
- `min_difficulty`: 最低难度阈值（字符串，可选值：Basic, CET4, CET6, TOEFL）

**提取规则：**
1. 使用正则 `\b[a-zA-Z]{3,}\b` 提取所有长度≥3的单词
2. 转换为小写后统计词频（Counter）
3. **排除 Basic 词库中的词**（stop_words）
4. 对于每个词，获取其难度等级
5. 只保留难度 ≥ `min_difficulty` 的词
6. 返回结果按难度从高到低排序

**返回格式：**
```python
[
    {
        "word": "quantum",      # 单词小写
        "difficulty": "TOEFL",   # 难度等级
        "count": 3,             # 出现次数
        "register": "academic",# 语域（academic/formal/informal/technical/business/general）
        "roots": [...]          # 词根词缀信息（可选，如有）
    }
]
```

**难度比较逻辑：**
```python
difficulty_order = {"Basic": 0, "CET4": 1, "CET6": 2, "TOEFL": 3}
# 只有 difficulty_order[difficulty] >= difficulty_order[min_difficulty] 的词才会被保留
```

### 2.3 短语/习语提取（extract_phrases）

**输入参数：**
- `text`: 英文文章文本

**提取规则：**
1. 将文本转为小写
2. 遍历 PHRASES 列表（~100个短语），检测是否出现在文本中
3. 遍历 IDIOMS 列表（~70个习语），检测是否出现在文本中
4. 返回所有匹配的短语/习语

**返回格式：**
```python
[
    {"phrase": "come to terms with", "type": "phrase"},
    {"phrase": "break a leg", "type": "idiom"}
]
```

### 2.4 词根词缀分析（get_word_roots）

**数据库结构：**
- 前缀：`un-`, `re-`, `pre-`, `dis-`, `in-`, `im-`, `ex-`, `sub-`, `super-`, `inter-`, `trans-`, `anti-`, `auto-`, `bio-`, `co-`, `de-`, `mis-`, `over-`, `post-`, `tele-`
- 后缀：`-able/-ible`, `-tion/-sion`, `-ment`, `-ness`, `-ful`, `-less`, `-ly`, `-er/-or`, `-ist`, `-ize/-ise`, `-ous/-ious`
- 词根：`spect`, `dict`, `port`, `struct`, `duct`, `scrib/script`, `ject`, `tract`, `form`, `mit/miss`

**⚠️ 重要约束：前后缀判断依赖符号标识**
- 以前缀标识结尾的（如 `un-`）按前缀匹配
- 以后缀标识开头的（如 `-able`）按后缀匹配

### 2.5 语域分类（get_register）

词汇分为 5 种语域：academic, formal, informal, technical, business, general

---

## 3. 功能边界与异常处理

### 3.1 边界情况

| 场景 | 预期行为 |
|------|----------|
| 纯中文文本 | 返回空列表（正则无法匹配） |
| 纯标点符号 | 返回空列表 |
| 空字符串 | 返回空列表 |
| 少于3个字符的单词 | 不被提取（如 `an`, `to`, `be` 即使不在 Basic 中也会被排除） |
| 大写单词（如 `QUANTUM`） | 转为小写后匹配，视为 `quantum` |

### 3.2 min_difficulty 参数校验

| 输入值 | 行为 |
|--------|------|
| "Basic" | 提取 Basic 及以上难度（即所有词） |
| "CET4" | 提取 CET4 及以上难度 |
| "CET6" | 提取 CET6 及以上难度 |
| "TOEFL" | 提取 TOEFL 及以上难度 |
| 无效值（如 "XYZ"） | 默认按 CET4 处理（min_level=1） |

---

## 4. 数据结构

### 4.1 词库

- `BASIC_WORDS`: set，包含约 3000 个基础词（小写）
- `CET4_WORDS`: set，包含约 4500 个 CET4 词（小写）
- `CET6_WORDS`: set，包含 CET4 词 + 约 1000 个 CET6 额外词
- `TOEFL_WORDS`: set，包含 CET6 词 + 约 1500 个 TOEFL 额外词

**⚠️ 重要约束：词库使用 set 数据结构，任何修改必须保持为 set**

### 4.2 短语库

- `PHRASES`: list，约 100 个常见短语（以空格分隔的词组）
- `IDIOMS`: list，约 70 个常见习语

---

## 5. 需业务决策事项（TODO: 由产品/用户补充）

### 5.1 词汇分级标准
- [ ] 某个词是否属于 Basic/CET4/CET6 的判断标准是什么？（当前为硬编码列表）
- [ ] 是否需要从公开词库文件加载而非硬编码？
- [x] Basic 词库应使用“小学 + 初中 / 义务教育阶段英语词汇”。当前已接入机器可读初中词表代理资源 `backend/app/resources/compulsory_basic_words_junior_proxy.txt`；官方《义务教育英语课程标准（2022年版）》PDF 为扫描版，后续可人工整理官方词表后替换该代理资源。不要使用 NGSL 这类通用高频词表，也不要使用高中词表作为 Basic，否则会把 `academic`、`abnormal`、`abortion` 等高中或更高语域词错误下沉为 Basic。
- [x] 分级判断按“专属难度层”处理：`CET4 = 四级词表 - Basic`，`CET6 = 六级词表 - CET4 - Basic`，`TOEFL = 托福词表 - CET6 - CET4 - Basic`。展示和提取时使用专属难度，避免累计总词表导致简单词被误标。

### 5.2 提取阈值
- [ ] `min_difficulty` 的默认值应该是什么？
- [ ] 对于初学者（CET4 水平），默认应该提取什么级别的词？

### 5.3 词库维护
- [ ] 新增词汇的标准流程是什么？
- [ ] 谁负责维护词库列表？

### 5.4 词汇释义生成
- [ ] 调整 `enhance_word()` 的 prompt：`definition_cn` 不能再要求 “Chinese translation of the definition”，应直接生成中文短释义。
- [ ] `definition` 保留为短英文学习释义，避免复杂词典式长句。
- [ ] 中文释义优先输出原文语境义；如有一词多义，只额外输出 1 个最高频其他义项。
- [ ] 新增 words 字段：`context_definition_cn`（原文语境义）和 `common_definition_cn`（最高频其他义）。
- [ ] 前端展示合并后的简洁释义，例如：`clear，清理，清除；清楚的`，不要显示“原文义”“常用义”等标签文字。

---

## 6. 测试要求

### 6.1 必须覆盖的测试用例

1. **难度判断测试**
   - Basic 词（如 `the`, `have`）→ 返回 "Basic"
   - CET4 专有词（如 `abandon`, `academic`）→ 返回 "CET4"
   - CET6 专有词（如 `chronic`, `bureaucracy`）→ 返回 "CET6"
   - TOEFL 专有词（如 `quantum`, `paradigm`）→ 返回 "TOEFL"
   - 未收录词（如 `asdfgh`）→ 返回 None

2. **提取范围测试**
   - `min_difficulty="CET4"` 时：Basic 词不能出现，CET4/CET6/TOEFL 词必须出现
   - `min_difficulty="TOEFL"` 时：只保留 TOEFL 词

3. **边界情况测试**
   - 空字符串 → 返回空列表
   - 纯中文文本 → 返回空列表
   - 短词（<3字符）→ 不被提取
   - 大小写 → 转为小写处理

4. **短语提取测试**
   - 包含 `break a leg` 的文本 → 能提取出该 idiom
   - 包含 `come to terms with` 的文本 → 能提取出该 phrase

5. **词根词缀测试**
   - `unhappy` → 能识别出前缀 `un-`
   - `happiness` → 能识别出后缀 `-ness`

### 6.2 回归测试
- 每次修改 word_extractor.py 前，必须运行完整测试套件
- 测试不通过禁止发布

---

## 7. 文件结构

```
backend/
├── app/
│   └── services/
│       └── word_extractor.py   # 核心词汇提取模块
└── tests/
    └── test_word_extractor.py  # 测试套件
```
