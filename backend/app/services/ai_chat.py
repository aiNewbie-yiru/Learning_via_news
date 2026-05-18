import requests
from typing import Optional
import re

from app.config import settings

class AIChatService:
    def __init__(self):
        self.api_key = settings.MINIMAX_API_KEY
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"

    def get_response(self, user_message: str, article_title: str = None, article_content: str = None) -> str:
        if not self.api_key:
            print("Warning: MINIMAX_API_KEY not set, using fallback response")
            return self._get_fallback_response(user_message)

        context = ""
        if article_title:
            context += f"Article: {article_title}\n\n"
        if article_content:
            context += f"Content excerpt: {article_content[:500]}...\n\n"

        system_prompt = """You are a friendly English learning assistant. Your role is to:
1. Help learners practice English by engaging in conversations
2. Provide encouraging feedback on their thoughts and opinions
3. Gently correct any grammatical errors when appropriate
4. Explain new vocabulary or expressions they might encounter
5. Ask follow-up questions to encourage more practice
6. Keep responses concise (2-4 sentences) and easy to understand

Always be patient, encouraging, and supportive. Use simple language to match the learner's level."""

        user_prompt = f"{context}Learner: {user_message}\n\nAssistant:"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "group_id": settings.MINIMAX_GROUP_ID,
            "model": "minimax-m2.7",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "reply" in result:
                return result["reply"].strip()
            elif result.get("choices") and len(result["choices"]) > 0:
                if "message" in result["choices"][0]:
                    return result["choices"][0]["message"].get("content", "").strip()
                else:
                    return str(result["choices"][0]).strip()
            elif "text" in result:
                return result["text"].strip()
            else:
                print(f"Unexpected API response format: {result}")
                return self._get_fallback_response(user_message)
        except requests.exceptions.RequestException as e:
            print(f"Minimax API request error: {e}")
            try:
                if response:
                    print(f"Response status: {response.status_code}")
                    print(f"Response content: {response.text[:500]}")
            except:
                pass
            return self._get_fallback_response(user_message)
        except Exception as e:
            print(f"Minimax API error: {e}")
            return self._get_fallback_response(user_message)

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
