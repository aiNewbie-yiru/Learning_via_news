import json
import re
import logging
from typing import Dict, Any

import requests

from app.config import settings

logger = logging.getLogger(__name__)

FALLBACK_DEFINITIONS = {
    "Basic": "a common word used in everyday language",
    "CET4": "a word commonly found in daily conversations and texts",
    "CET6": "an academic word frequently used in formal contexts",
    "TOEFL": "an advanced word essential for academic success",
    "GRE": "a sophisticated word used in complex academic discourse"
}


class VocabEnhancerService:
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY or settings.OPENAI_API_KEY
        self.model = settings.DEEPSEEK_MODEL or settings.OPENAI_MODEL
        self.base_url = (settings.DEEPSEEK_BASE_URL or settings.OPENAI_BASE_URL).rstrip("/")
        self.openai_proxy_url = settings.OPENAI_PROXY_URL
        self.minimax_api_key = settings.MINIMAX_API_KEY
        self.minimax_group_id = settings.MINIMAX_GROUP_ID
        self.minimax_model = settings.MINIMAX_MODEL
        self.minimax_base_url = settings.MINIMAX_BASE_URL

    def _has_api_key(self) -> bool:
        return bool(self.api_key and not self.api_key.startswith("your-"))

    def _has_minimax_api_key(self) -> bool:
        return bool(self.minimax_api_key and not self.minimax_api_key.startswith("your-"))

    def _get_openai_proxies(self):
        if not self.openai_proxy_url:
            return None
        return {
            "http": self.openai_proxy_url,
            "https": self.openai_proxy_url,
        }

    def _post(self, url: str, **kwargs):
        session = requests.Session()
        if not self.openai_proxy_url:
            session.trust_env = False
        return session.post(url, **kwargs)

    def _create_openai_json_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        if not self._has_api_key():
            raise RuntimeError("DEEPSEEK_API_KEY or OPENAI_API_KEY is not configured")

        completions_url = self.base_url
        if not completions_url.endswith("/chat/completions"):
            completions_url = f"{completions_url}/chat/completions"

        response = self._post(
            completions_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                ],
                "thinking": {"type": "disabled"},
                "response_format": {"type": "json_object"},
                "max_tokens": max_tokens,
                "temperature": 0.2,
            },
            timeout=45,
            proxies=self._get_openai_proxies(),
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            body = response.text[:500]
            raise RuntimeError(f"Vocabulary API HTTP {response.status_code}: {body}") from exc
        result = response.json()
        content = result["choices"][0]["message"]["content"] or "{}"
        return json.loads(content)

    def _create_minimax_json_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        if not self._has_minimax_api_key():
            raise RuntimeError("MINIMAX_API_KEY is not configured")

        response = self._post(
            self.minimax_base_url,
            headers={
                "Authorization": f"Bearer {self.minimax_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "group_id": self.minimax_group_id,
                "model": self.minimax_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": 0.2,
            },
            timeout=45,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            body = response.text[:500]
            raise RuntimeError(f"MiniMax API HTTP {response.status_code}: {body}") from exc

        result = response.json()
        content = self._extract_minimax_content(result)
        return self._parse_json_content(content)

    def _extract_minimax_content(self, result: Dict[str, Any]) -> str:
        if "reply" in result:
            return result["reply"]
        if result.get("choices") and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "message" in choice:
                return choice["message"].get("content", "")
            return str(choice)
        if "text" in result:
            return result["text"]
        raise RuntimeError(f"Unexpected MiniMax response format: {result}")

    def _parse_json_content(self, content: str) -> Dict[str, Any]:
        content = (content or "").strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", content, re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    def _create_json_completion(self, system_prompt: str, user_prompt: str, max_tokens: int = 500) -> Dict[str, Any]:
        if self._has_api_key():
            try:
                return self._create_openai_json_completion(system_prompt, user_prompt, max_tokens=max_tokens)
            except Exception as e:
                logger.warning("DeepSeek vocabulary request failed, trying MiniMax fallback: %s", e)
        else:
            logger.warning("DEEPSEEK_API_KEY/OPENAI_API_KEY not set, trying MiniMax fallback")

        return self._create_minimax_json_completion(system_prompt, user_prompt, max_tokens=max_tokens)

    def extract_example_from_context(self, word: str, context: str, max_length: int = 40) -> Dict[str, str]:
        """
        从文章上下文中提取该词所在的句子作为第一例句
        如果句子过长，截取主谓宾结构
        """
        if not context or not word:
            return {"sentence": "", "source": ""}

        # 找到单词在上下文中的所有出现位置
        word_lower = word.lower()
        sentences = re.split(r'(?<=[.!?])\s+', context)
        word_pattern = re.compile(rf"\b{re.escape(word_lower)}\b", re.IGNORECASE)

        for sent in sentences:
            if word_pattern.search(sent):
                # 找到包含该词的句子
                sentence = sent.strip()

                # 如果句子过长，截取主谓宾结构
                if len(sentence.split()) > max_length:
                    sentence = self._truncate_to_main_structure(sentence, word, max_length)

                return {
                    "sentence": sentence,
                    "source": "From article"
                }

        return {"sentence": "", "source": ""}

    def _truncate_to_main_structure(self, sentence: str, word: str, max_words: int = 40) -> str:
        """
        截取句子的主谓宾结构，保留包含目标词的部分
        """
        words = sentence.split()
        if len(words) <= max_words:
            return sentence

        # 找到目标词的位置
        word_lower = word.lower()
        word_pattern = re.compile(rf"\b{re.escape(word_lower)}\b", re.IGNORECASE)
        word_positions = [i for i, w in enumerate(words) if word_pattern.search(w)]

        if not word_positions:
            return ' '.join(words[:max_words]) + "..."

        # 以目标词为中心，扩展到max_words
        target_pos = word_positions[0]
        start = max(0, target_pos - 5)
        end = min(len(words), target_pos + 15)

        result = words[start:end]
        if start > 0:
            result = ["..."] + result
        if end < len(words):
            result = result + ["..."]

        return ' '.join(result)

    def enhance_word(self, word: str, difficulty: str = "CET6", part_of_speech: str = None, article_context: str = None) -> Dict[str, Any]:
        # 第一步：从文章上下文中提取第一例句
        extracted_example = self.extract_example_from_context(word, article_context) if article_context else {"sentence": "", "source": ""}

        if not self._has_api_key() and not self._has_minimax_api_key():
            logger.warning("DEEPSEEK_API_KEY/OPENAI_API_KEY and MINIMAX_API_KEY not set, using fallback vocabulary response")
            fallback = self._get_fallback_word(word, difficulty)
            fallback["example_sentence"] = extracted_example["sentence"]
            fallback["example_source"] = extracted_example["source"]
            return fallback

        system_prompt = """You are a professional English vocabulary expert designing concise explanations for Chinese-speaking English learners.

You will receive a word and its original context sentence from a news article. Your task is to generate ONE additional example sentence that matches the word's difficulty level.

Return a JSON object with the following structure:
{
    "definition": "Short, learner-friendly English meaning of the word in this context",
    "definition_cn": "Short Chinese meaning for display, not a translation of the English definition",
    "context_definition_cn": "Very short Chinese meaning in the original news sentence",
    "common_definition_cn": "One very short, high-frequency other Chinese meaning, or empty string if not useful",
    "example_sentence_2": "A high-quality second example sentence that matches the word's difficulty level",
    "example_sentence_2_cn": "Chinese translation of the second example sentence",
    "part_of_speech": "Part of speech (noun, verb, adjective, adverb, etc.)",
    "pronunciation": "International Phonetic Alphabet (IPA) pronunciation in US English, e.g., /ˈɡæləri/"
}

Important requirements:
1. The English definition must be short and direct; avoid long dictionary-style sentences.
2. definition_cn must be a direct Chinese vocabulary meaning, not a machine translation of definition.
3. context_definition_cn must prioritize the meaning in the original news sentence.
4. context_definition_cn and common_definition_cn should each be 1-8 Chinese characters when possible, or one very short Chinese phrase.
5. If the word has multiple meanings, common_definition_cn should include only ONE high-frequency other meaning.
6. Do not list many meanings. Do not write long Chinese explanation sentences. Avoid parenthetical explanations unless essential.
7. definition_cn should combine the Chinese meanings for display, e.g. "清理，清除；清楚的". Do not include labels like "原文义" or "常用义".
8. The second example sentence should have SIMILAR difficulty to the original context sentence.
9. If the original is from news (formal), keep the second example also formal/academic.
10. If the original is simple, keep the second example also simple.
11. The example sentence MUST contain the target word.
12. Keep the example sentence natural and native-sounding.
13. Provide accurate IPA pronunciation in US English with slashes, e.g., /ˈɡæləri/.

Return ONLY the JSON, no extra text."""

        context_info = f"\nOriginal sentence from news: {extracted_example['sentence']}" if extracted_example['sentence'] else ""
        pos_info = f"\nPart of speech: {part_of_speech}" if part_of_speech else ""

        user_prompt = f"Word: {word}\nDifficulty level: {difficulty}{pos_info}{context_info}"

        try:
            parsed = self._create_json_completion(system_prompt, user_prompt, max_tokens=500)
            return {
                "definition": parsed.get("definition", ""),
                "definition_cn": parsed.get("definition_cn", ""),
                "context_definition_cn": parsed.get("context_definition_cn", ""),
                "common_definition_cn": parsed.get("common_definition_cn", ""),
                "example_sentence": extracted_example["sentence"],
                "example_source": extracted_example["source"] or "Common Usage",
                "example_sentence_2": parsed.get("example_sentence_2", ""),
                "example_sentence_2_cn": parsed.get("example_sentence_2_cn", ""),
                "part_of_speech": parsed.get("part_of_speech", part_of_speech or ""),
                "pronunciation": parsed.get("pronunciation", "")
            }
        except Exception as e:
            logger.error("Vocabulary enhancer error for '%s': %s", word, e)
            raise RuntimeError(f"Vocabulary enhancer failed for '{word}'") from e

    def enhance_phrase(self, phrase: str, meaning: str = None, article_context: str = None) -> Dict[str, Any]:
        if not self._has_api_key() and not self._has_minimax_api_key():
            logger.warning("DEEPSEEK_API_KEY/OPENAI_API_KEY and MINIMAX_API_KEY not set, using fallback phrase response")
            return self._get_fallback_phrase(phrase, meaning)

        system_prompt = """You are a professional English vocabulary expert. Your task is to provide rich, accurate, and native-level phrase information for English learners.

You will receive a phrase and optional context, and you need to return a JSON object with the following structure:
{
    "meaning": "English explanation of the phrase",
    "meaning_cn": "Chinese translation of the meaning",
    "example_sentence": "A high-quality example sentence",
    "example_cn": "Chinese translation of the example sentence",
    "example_source": "Source of the example (e.g., 'From: The Shawshank Redemption', 'From: BBC News') or 'Common Usage'"
}

Important requirements:
1. Example sentences should be natural and native-sounding
2. Use real, authentic examples from movies, books, news whenever possible
3. The example sentence MUST contain the target phrase
4. If provided, consider the article context to make examples more relevant

Return ONLY the JSON, no extra text."""

        context_info = f"\nArticle context: {article_context[:300]}..." if article_context else ""
        meaning_info = f"\nCurrent meaning: {meaning}" if meaning else ""

        user_prompt = f"Phrase: {phrase}{meaning_info}{context_info}"

        try:
            parsed = self._create_json_completion(system_prompt, user_prompt, max_tokens=500)
            return {
                "meaning": parsed.get("meaning", meaning or ""),
                "meaning_cn": parsed.get("meaning_cn", ""),
                "example_sentence": parsed.get("example_sentence", ""),
                "example_cn": parsed.get("example_cn", ""),
                "example_source": parsed.get("example_source", "Common Usage")
            }
        except Exception as e:
            logger.error("Vocabulary phrase enhancer error for '%s': %s", phrase, e)
            raise RuntimeError(f"Vocabulary phrase enhancer failed for '{phrase}'") from e

    def generate_topic_labels(self, title: str, summary: str = None, content: str = None) -> Dict[str, str]:
        system_prompt = """You create short topic labels for an English learning news app.

Return ONLY a JSON object:
{
  "topic_label": "2-3 English words in Title Case",
  "topic_label_cn": "#中文话题"
}

Rules:
1. topic_label must be catchy, accurate, and at most 3 English words.
2. topic_label_cn must start with # and be at most 4 Chinese characters after #.
3. Do not use punctuation except the # prefix.
4. Avoid vague labels like News, Update, Story, Article."""

        excerpt = (content or "")[:500]
        user_prompt = f"Title: {title}\nSummary: {summary or ''}\nContent excerpt: {excerpt}"

        try:
            parsed = self._create_json_completion(system_prompt, user_prompt, max_tokens=120)
            return self._normalize_topic_labels(
                parsed.get("topic_label", ""),
                parsed.get("topic_label_cn", ""),
                title
            )
        except Exception as e:
            logger.warning("Topic label generation failed for '%s': %s", title, e)
            return self._fallback_topic_labels(title)

    def _normalize_topic_labels(self, topic_label: str, topic_label_cn: str, title: str) -> Dict[str, str]:
        topic_label = re.sub(r"[^A-Za-z0-9\s]", "", topic_label or "").strip()
        words = topic_label.split()[:3]
        if not words:
            return self._fallback_topic_labels(title)

        normalized_en = " ".join(word[:1].upper() + word[1:] for word in words)[:30].strip()

        cn_chars = re.findall(r"[\u4e00-\u9fff]", topic_label_cn or "")
        normalized_cn = f"#{''.join(cn_chars[:4])}" if cn_chars else "#新闻"
        if normalized_cn == "#":
            normalized_cn = "#新闻"

        return {
            "topic_label": normalized_en,
            "topic_label_cn": normalized_cn
        }

    def _fallback_topic_labels(self, title: str) -> Dict[str, str]:
        words = re.findall(r"[A-Za-z0-9]+", title or "")[:3]
        return {
            "topic_label": " ".join(words) or "Daily News",
            "topic_label_cn": "#新闻"
        }

    def _get_fallback_word(self, word: str, difficulty: str) -> Dict[str, Any]:
        # 通用释义模板（不包含目标词，避免生成不自然的内容）
        examples = {
            "Basic": f"{word.capitalize()} is commonly used in daily life.",
            "CET4": f"The word '{word}' appears frequently in everyday English.",
            "CET6": f"The concept of '{word}' is often discussed in academic settings.",
            "TOEFL": f"Understanding '{word}' is crucial for academic success.",
            "GRE": f"The nuanced meaning of '{word}' appears in advanced texts."
        }

        pronunciations = {
            "gallery": "/ˈɡæləri/",
            "roof": "/ruːf/",
            "pregnant": "/ˈpreɡnənt/",
            "concept": "/ˈkɑːnsept/",
            "understanding": "/ˌʌndərˈstændɪŋ/"
        }

        return {
            "definition": FALLBACK_DEFINITIONS.get(difficulty, FALLBACK_DEFINITIONS["CET4"]),
            "definition_cn": "",
            "context_definition_cn": "",
            "common_definition_cn": "",
            "example_sentence": examples.get(difficulty, examples["CET4"]),
            "example_cn": "",
            "example_source": "Common Usage",
            "part_of_speech": "noun",
            "pronunciation": pronunciations.get(word.lower(), "")
        }

    def _get_fallback_word_with_first_example(self, word: str, difficulty: str, extracted_example: Dict) -> Dict[str, Any]:
        """带第一例句的fallback（第一例句来自文章原文）"""
        base = self._get_fallback_word(word, difficulty)
        second_examples = {
            "Basic": f"{word.capitalize()} is commonly used in daily life.",
            "CET4": f"The word '{word}' appears frequently in everyday English.",
            "CET6": f"The concept of '{word}' is often discussed in academic settings.",
            "TOEFL": f"Understanding '{word}' is crucial for academic success.",
            "GRE": f"The nuanced meaning of '{word}' appears in advanced texts."
        }
        base["example_sentence"] = extracted_example.get("sentence", "")
        base["example_source"] = extracted_example.get("source", "Common Usage")
        # 第一例句来自文章，没有中文翻译（避免生成不准确的翻译）
        base["example_cn"] = ""
        base["example_sentence_2"] = second_examples.get(difficulty, second_examples["CET4"])
        base["example_sentence_2_cn"] = ""
        return base

    def _get_fallback_phrase(self, phrase: str, meaning: str = None) -> Dict[str, Any]:
        return {
            "meaning": meaning or f"An expression meaning {phrase}",
            "meaning_cn": f"{phrase} 的意思",
            "example_sentence": f"We often use the phrase '{phrase}' in English.",
            "example_cn": f"我们在英语中经常使用 '{phrase}' 这个短语。",
            "example_source": "Common Usage"
        }


vocab_enhancer_service = VocabEnhancerService()
