import requests
import logging
from typing import List, Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class AIChatService:
    def __init__(self):
        self.deepseek_api_key = settings.DEEPSEEK_API_KEY or settings.OPENAI_API_KEY
        self.deepseek_model = settings.DEEPSEEK_MODEL or settings.OPENAI_MODEL
        self.deepseek_base_url = (settings.DEEPSEEK_BASE_URL or settings.OPENAI_BASE_URL).rstrip("/")
        self.openai_proxy_url = settings.OPENAI_PROXY_URL
        self.minimax_api_key = settings.MINIMAX_API_KEY
        self.minimax_base_url = settings.MINIMAX_BASE_URL
        self.minimax_model = settings.MINIMAX_MODEL

    def _has_key(self, api_key: str) -> bool:
        return bool(api_key and not api_key.startswith("your-"))

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

    def _format_conversation_history(self, conversation_history: Optional[List[Dict]]) -> str:
        if not conversation_history:
            return ""

        lines = []
        for turn in conversation_history[-20:]:
            learner_text = (turn.get("learner") or "").strip()
            assistant_text = (turn.get("assistant") or "").strip()
            if learner_text:
                lines.append(f"Learner: {learner_text}")
            if assistant_text:
                lines.append(f"Assistant: {assistant_text}")

        if not lines:
            return ""
        return "Conversation history:\n" + "\n".join(lines) + "\n\n"

    def get_response(
        self,
        user_message: str,
        article_title: str = None,
        article_content: str = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> str:
        context = ""
        if article_title:
            context += f"Article: {article_title}\n\n"
        if article_content:
            context += f"Content excerpt: {article_content[:500]}...\n\n"
        context += self._format_conversation_history(conversation_history)

        system_prompt = """You are a warm, honest English learning assistant. Be direct and pedagogically useful, not automatically approving.

Core response rules:
1. Do not automatically praise or agree with the learner.
2. Avoid formulaic openers such as "Great question," "You're absolutely right," and "Yes, that's correct."
3. If the learner asks a question, answer directly first.
4. If the learner makes a language mistake, provide the corrected version and one brief reason.
5. If the learner's understanding is correct, confirm briefly and add useful nuance.
6. If the learner is partly right or wrong, correct it clearly and kindly without over-apologizing or over-praising.
7. If the learner shares an opinion, respond to the idea and, when helpful, suggest a more natural English expression.
8. When explaining a word or phrase, give the meaning in context first.
9. For figurative or extended meanings, explain the core literal image and show how the meaning grows from it using a vivid, concrete analogy.
10. If the learner writes mostly English but includes one or two Chinese words or phrases, treat the Chinese as a likely vocabulary gap. First suggest natural English equivalents for the Chinese part, then continue the reply.
11. If the learner clearly ends the conversation, stop normal Q&A and provide a compact daily learning summary based on the conversation history. Use this bullet-point format:
   Today's Learning Summary
   - Words and phrases you asked about: word/phrase — meaning; example sentence.
   - Chinese expressions you used in English: Chinese expression → natural English equivalent; meaning; example sentence.
   - Grammar and natural expression notes: original wording → improved wording; brief reason.
   - Conversation reflection: briefly review any opinions exchanged like a thoughtful friend, with encouragement, thanks, and appreciation. End with one simple blessing wishing the learner a fresh start to the day.
   Omit any section with no useful items. Keep each bullet short.
12. Keep ordinary replies concise: usually 2-4 sentences and under 120 English words. A closing daily summary may be longer but should stay scannable and bullet-based.
13. Use simple learner-friendly English. Use brief Chinese only when it helps explain a word, phrase, semantic extension, or Chinese vocabulary gap.
14. Ask a follow-up question only when it naturally helps practice.
15. Finish with a complete sentence. Do not write long lists or long explanations except for the requested closing daily summary."""

        user_prompt = f"{context}Learner: {user_message}\n\nAssistant:"

        if self._has_key(self.deepseek_api_key):
            try:
                return self._get_deepseek_response(system_prompt, user_prompt)
            except Exception as e:
                logger.warning("DeepSeek chat failed, trying MiniMax fallback: %s", e)
        else:
            logger.warning("DEEPSEEK_API_KEY/OPENAI_API_KEY not set, trying MiniMax fallback")

        if self._has_key(self.minimax_api_key):
            try:
                return self._get_minimax_response(system_prompt, user_prompt)
            except Exception as e:
                logger.warning("MiniMax chat failed, using local fallback: %s", e)

        return self._get_fallback_response(user_message)

    def _get_deepseek_response(self, system_prompt: str, user_prompt: str) -> str:
        completions_url = self.deepseek_base_url
        if not completions_url.endswith("/chat/completions"):
            completions_url = f"{completions_url}/chat/completions"

        response = self._post(
            completions_url,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.deepseek_api_key}",
            },
            json={
                "model": self.deepseek_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "thinking": {"type": "disabled"},
                "max_tokens": 450,
                "temperature": 0.7,
            },
            timeout=30,
            proxies=self._get_openai_proxies(),
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"].get("content", "").strip()

    def _get_minimax_response(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.minimax_api_key}"
        }

        payload = {
            "group_id": settings.MINIMAX_GROUP_ID,
            "model": self.minimax_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 450,
            "temperature": 0.7
        }

        response = self._post(self.minimax_base_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        if "reply" in result:
            return result["reply"].strip()
        if result.get("choices") and len(result["choices"]) > 0:
            if "message" in result["choices"][0]:
                return result["choices"][0]["message"].get("content", "").strip()
            return str(result["choices"][0]).strip()
        if "text" in result:
            return result["text"].strip()

        raise RuntimeError(f"Unexpected MiniMax response format: {result}")

    def _get_fallback_response(self, user_message: str) -> str:
        message_lower = user_message.lower()

        if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! Keep practicing and you'll improve a lot. What's your thoughts on today's article?"

        if any(word in message_lower for word in ['confused', 'difficult', 'hard', 'understand']):
            return "Don't worry! Learning takes time. Which part would you like me to explain? I'm here to help!"

        if any(word in message_lower for word in ['interesting', 'cool', 'awesome', 'great']):
            return "I'm glad you found it interesting! Expressing enthusiasm is great for language learning. Would you like to discuss it more?"

        if any(word in message_lower for word in ['boring', 'not good', 'bad']):
            return "That's okay! Not every topic interests everyone. Try reading about what you enjoy - that makes learning more fun!"

        return "That's interesting! Keep sharing your thoughts in English. Practice makes perfect! Would you like to tell me more about this topic?"

ai_chat_service = AIChatService()
