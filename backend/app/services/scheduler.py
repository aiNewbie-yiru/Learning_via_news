from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.config import settings
from app.services.news_scraper import news_scraper
from app.services.word_extractor import word_extractor
from app.services.vocab_enhancer import vocab_enhancer_service
from app.models.database import SessionLocal, Article, Word, Phrase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)

def select_hardest_words(words, limit: int):
    difficulty_order = {"Basic": 0, "CET4": 1, "CET6": 2, "TOEFL": 3, "GRE": 4}
    return sorted(
        words,
        key=lambda word: (
            -difficulty_order.get(word.get("difficulty", "CET4"), 1),
            -word.get("count", 0),
            word.get("word", "")
        )
    )[:limit]

def fetch_and_process_daily_news():
    db = SessionLocal()
    try:
        logger.info(f"Starting daily news fetch at {datetime.now()}")

        today_articles = db.query(Article).filter(
            Article.is_today == True
        ).all()
        for article in today_articles:
            article.is_today = False
        db.commit()

        article_data = news_scraper.get_random_article()
        if not article_data:
            logger.error("Failed to fetch article")
            return

        logger.info(f"Fetched article: {article_data.get('title', '')[:50]}")

        article = Article(
            title=article_data.get("title", ""),
            content=article_data.get("content", ""),
            summary=article_data.get("summary", ""),
            source=article_data.get("source", ""),
            url=article_data.get("url", ""),
            published_at=datetime.now(),
            is_today=True
        )
        db.add(article)
        db.commit()
        db.refresh(article)

        extracted = word_extractor.analyze_text(article.content, min_difficulty=settings.VOCAB_MIN_DIFFICULTY)
        words_to_process = select_hardest_words(extracted["words"], settings.VOCAB_WORD_LIMIT)
        phrases_to_process = extracted["phrases"][:settings.VOCAB_PHRASE_LIMIT]
        logger.info(
            "Extracted %s words and %s phrases; processing hardest %s words and %s phrases",
            len(extracted["words"]),
            len(extracted["phrases"]),
            len(words_to_process),
            len(phrases_to_process),
        )

        for word_data in words_to_process:
            word_text = word_data.get("word", "")
            difficulty = word_data.get("difficulty", "CET4")

            # Call AI to enhance the word
            enhanced = vocab_enhancer_service.enhance_word(
                word=word_text,
                difficulty=difficulty,
                article_context=article.content
            )

            word = Word(
                article_id=article.id,
                word=word_text,
                definition=enhanced.get("definition", ""),
                definition_cn=enhanced.get("definition_cn", ""),
                example_sentence=enhanced.get("example_sentence", ""),
                example_cn=enhanced.get("example_cn", ""),
                example_source=enhanced.get("example_source", "Common Usage"),
                example_sentence_2=enhanced.get("example_sentence_2", ""),
                example_sentence_2_cn=enhanced.get("example_sentence_2_cn", ""),
                difficulty_level=difficulty,
                part_of_speech=enhanced.get("part_of_speech", "noun"),
                pronunciation=enhanced.get("pronunciation", "")
            )
            db.add(word)

        for phrase_data in phrases_to_process:
            phrase_text = phrase_data.get("phrase", "")
            
            # Call AI to enhance the phrase
            enhanced = vocab_enhancer_service.enhance_phrase(
                phrase=phrase_text,
                article_context=article.content
            )
            
            phrase = Phrase(
                article_id=article.id,
                phrase=phrase_text,
                meaning=enhanced.get("meaning", ""),
                meaning_cn=enhanced.get("meaning_cn", ""),
                example_sentence=enhanced.get("example_sentence", ""),
                example_cn=enhanced.get("example_cn", ""),
                example_source=enhanced.get("example_source", "Common Usage"),
                origin="Common English expression"
            )
            db.add(phrase)

        db.commit()
        logger.info(f"Successfully processed article: {article.title}")

    except Exception as e:
        logger.error(f"Error in scheduled task: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    trigger = CronTrigger(
        hour=settings.PUSH_HOUR,
        minute=settings.PUSH_MINUTE,
        timezone=settings.SCHEDULER_TIMEZONE
    )

    scheduler.add_job(
        fetch_and_process_daily_news,
        trigger=trigger,
        id="daily_news_fetch",
        name="Daily News Fetch at 9:30 AM",
        replace_existing=True
    )

    scheduler.start()
    logger.info(f"Scheduler started. Will run daily at {settings.PUSH_HOUR}:{settings.PUSH_MINUTE:02d}")

def stop_scheduler():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")

def run_now():
    fetch_and_process_daily_news()

def process_article_vocabulary(article_id: int, db):
    """处理指定文章的词汇提取"""
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            logger.error(f"Article {article_id} not found")
            return

        if article.words or article.phrases:
            logger.info(f"Article {article_id} already has vocabulary, skipping")
            return

        logger.info(f"Processing vocabulary for article: {article.title}")

        extracted = word_extractor.analyze_text(article.content, min_difficulty=settings.VOCAB_MIN_DIFFICULTY)
        words_to_process = select_hardest_words(extracted["words"], settings.VOCAB_WORD_LIMIT)
        phrases_to_process = extracted["phrases"][:settings.VOCAB_PHRASE_LIMIT]
        logger.info(
            "Extracted %s words and %s phrases; processing hardest %s words and %s phrases",
            len(extracted["words"]),
            len(extracted["phrases"]),
            len(words_to_process),
            len(phrases_to_process),
        )

        for word_data in words_to_process:
            word_text = word_data.get("word", "")
            difficulty = word_data.get("difficulty", "CET4")

            enhanced = vocab_enhancer_service.enhance_word(
                word=word_text,
                difficulty=difficulty,
                article_context=article.content
            )

            word = Word(
                article_id=article.id,
                word=word_text,
                definition=enhanced.get("definition", ""),
                definition_cn=enhanced.get("definition_cn", ""),
                example_sentence=enhanced.get("example_sentence", ""),
                example_cn=enhanced.get("example_cn", ""),
                example_source=enhanced.get("example_source", "Common Usage"),
                example_sentence_2=enhanced.get("example_sentence_2", ""),
                example_sentence_2_cn=enhanced.get("example_sentence_2_cn", ""),
                difficulty_level=difficulty,
                part_of_speech=enhanced.get("part_of_speech", "noun"),
                pronunciation=enhanced.get("pronunciation", "")
            )
            db.add(word)

        for phrase_data in phrases_to_process:
            phrase_text = phrase_data.get("phrase", "")

            enhanced = vocab_enhancer_service.enhance_phrase(
                phrase=phrase_text,
                article_context=article.content
            )

            phrase = Phrase(
                article_id=article.id,
                phrase=phrase_text,
                meaning=enhanced.get("meaning", ""),
                meaning_cn=enhanced.get("meaning_cn", ""),
                example_sentence=enhanced.get("example_sentence", ""),
                example_cn=enhanced.get("example_cn", ""),
                example_source=enhanced.get("example_source", "Common Usage"),
                origin="Common English expression"
            )
            db.add(phrase)

        db.commit()
        logger.info(f"Successfully processed vocabulary for article: {article.title}")

    except Exception as e:
        logger.error(f"Error processing vocabulary for article {article_id}: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
