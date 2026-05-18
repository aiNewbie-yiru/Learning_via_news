import os
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import random

from app.config import settings

PROXY = os.getenv("HTTPS_PROXY") or os.getenv("https_proxy") or os.getenv("HTTP_PROXY") or os.getenv("http_proxy")

class NewsScraper:
    def __init__(self):
        self.sources = settings.NEWS_SOURCES
        self.news_api_key = settings.NEWS_API_KEY
        self.news_api_enabled = settings.NEWS_API_ENABLED
        self.proxies = {
            "http": PROXY,
            "https": PROXY
        } if PROXY else None

    def fetch_news_api(self, category: str = "general") -> List[Dict]:
        if not self.news_api_key or not self.news_api_enabled:
            return []
        
        try:
            url = f"https://newsapi.org/v2/top-headlines"
            params = {
                "country": "us",
                "category": category,
                "apiKey": self.news_api_key,
                "pageSize": 10
            }
            
            response = requests.get(url, params=params, proxies=self.proxies, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            articles = []
            
            for item in data.get("articles", []):
                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "published": item.get("publishedAt", ""),
                    "summary": item.get("description", ""),
                    "source": item.get("source", {}).get("name", "NewsAPI")
                })
            
            return articles
        except Exception as e:
            print(f"Error fetching from NewsAPI: {e}")
            return []

    def fetch_rss_feed(self, url: str) -> List[Dict]:
        articles = []
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/xml"
            }
            
            response = requests.get(url, headers=headers, proxies=self.proxies, timeout=15)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            for entry in feed.entries[:5]:
                article = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": self.clean_html(entry.get("summary", "")),
                    "source": feed.feed.get("title", "Unknown")
                }
                articles.append(article)
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {e}")
        
        return articles

    def truncate_to_complete_sentence(self, text: str, max_length: int = 3000) -> str:
        """截取文本到最大长度，但确保以完整句子结尾"""
        if len(text) <= max_length:
            return text
        
        truncated = text[:max_length + 200]
        
        # 定义句子结束符号
        sentence_enders = ['. ', '? ', '! ', '。', '？', '！']
        
        # 从后往前找最后一个完整句子
        last_end_pos = -1
        for ender in sentence_enders:
            pos = truncated.rfind(ender)
            if pos > last_end_pos:
                last_end_pos = pos
        
        if last_end_pos != -1:
            # 返回完整句子（包含结束符）
            return truncated[:last_end_pos + len(ender)]
        else:
            # 如果找不到句子结束符，直接截取到max_length
            return text[:max_length]

    def fetch_article_content(self, url: str) -> Optional[str]:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, proxies=self.proxies, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")

            paragraphs = soup.find_all("p")
            content = " ".join([p.get_text() for p in paragraphs])

            if content:
                return self.truncate_to_complete_sentence(content, 1500)
            return None
        except Exception as e:
            print(f"Error fetching article content: {e}")
            return None

    def clean_html(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text()

    def fetch_all_news(self) -> List[Dict]:
        all_articles = []

        for category, urls in self.sources.items():
            for url in urls:
                try:
                    articles = self.fetch_rss_feed(url)
                    for article in articles:
                        article["category"] = category
                    all_articles.extend(articles)
                except Exception as e:
                    print(f"Error fetching from {url}: {e}")

        if not all_articles and self.news_api_enabled and self.news_api_key:
            print("RSS feeds unavailable, falling back to NewsAPI...")
            all_articles = self.fetch_news_api()

        all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        return all_articles

    def get_random_article(self) -> Optional[Dict]:
        articles = self.fetch_all_news()
        if not articles:
            return None

        article = random.choice(articles)

        content = self.fetch_article_content(article["url"])
        if content:
            article["content"] = content
        else:
            article["content"] = article.get("summary", "")

        return article

    def get_two_random_articles(self) -> List[Dict]:
        articles = self.fetch_all_news()
        if len(articles) < 2:
            return []

        selected = []
        used_categories = set()
        
        random.shuffle(articles)
        
        for article in articles:
            category = article.get("category", "")
            if category not in used_categories or len(selected) < 2:
                content = self.fetch_article_content(article["url"])
                if content:
                    article["content"] = content
                else:
                    article["content"] = article.get("summary", "")
                
                selected.append(article)
                used_categories.add(category)
                
                if len(selected) >= 2:
                    break

        return selected

news_scraper = NewsScraper()
