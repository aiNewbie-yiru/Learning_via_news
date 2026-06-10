from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import logging
import random
from zoneinfo import ZoneInfo

from app.config import settings
from app.services.news_scraper import news_scraper
from app.services.word_extractor import word_extractor
from app.services.vocab_enhancer import vocab_enhancer_service
from app.services.article_quality import apply_content_quality_filters, is_usable_article_content
from app.models.database import SessionLocal, Article, Word, Phrase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)

def get_local_now() -> datetime:
    return datetime.now(ZoneInfo(settings.SCHEDULER_TIMEZONE))

def get_today_bounds() -> tuple[datetime, datetime]:
    today_start = get_local_now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    return today_start.replace(tzinfo=None), tomorrow_start.replace(tzinfo=None)

def has_article_for_today(db) -> bool:
    return count_articles_for_today(db) > 0

def count_articles_for_today(db) -> int:
    today_start, tomorrow_start = get_today_bounds()
    query = db.query(Article).filter(
        Article.published_at >= today_start,
        Article.published_at < tomorrow_start
    )
    return apply_content_quality_filters(query).count()

def get_existing_article_urls(db) -> set:
    return {
        url for (url,) in db.query(Article.url).filter(Article.url != None).all()
        if url
    }

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

def create_processed_article(db, article_data: dict) -> Article:
    logger.info(f"Fetched article: {article_data.get('title', '')[:50]}")

    article = Article(
        title=article_data.get("title", ""),
        content=article_data.get("content", ""),
        summary=article_data.get("summary", ""),
        source=article_data.get("source", ""),
        url=article_data.get("url", ""),
        published_at=get_local_now().replace(tzinfo=None),
        is_today=True
    )
    db.add(article)
    db.commit()
    db.refresh(article)

    topic_labels = vocab_enhancer_service.generate_topic_labels(
        title=article.title,
        summary=article.summary,
        content=article.content
    )
    article.topic_label = topic_labels.get("topic_label", "")
    article.topic_label_cn = topic_labels.get("topic_label_cn", "")
    db.commit()

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
            context_definition_cn=enhanced.get("context_definition_cn", ""),
            common_definition_cn=enhanced.get("common_definition_cn", ""),
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
    logger.info(f"Successfully processed article: {article.title}")
    return article

def fetch_and_process_daily_news(target_count: int = None):
    db = SessionLocal()
    try:
        logger.info(f"Starting daily news fetch at {get_local_now()}")

        target = target_count or settings.DAILY_ARTICLE_TARGET
        existing_today_count = count_articles_for_today(db)
        missing_count = max(0, target - existing_today_count)
        if missing_count == 0:
            logger.info("Today's article target already met: %s/%s", existing_today_count, target)
            return

        logger.info("Today's articles: %s/%s; fetching %s more", existing_today_count, target, missing_count)

        for article in db.query(Article).filter(Article.is_today == True).all():
            article.is_today = False
        db.commit()

        existing_urls = get_existing_article_urls(db)
        candidates = news_scraper.fetch_all_news()
        random.shuffle(candidates)
        created_count = 0

        for candidate in candidates:
            if created_count >= missing_count:
                break
            url = candidate.get("url", "")
            if not url or url in existing_urls:
                continue

            content = news_scraper.fetch_article_content(url)
            if not is_usable_article_content(content or ""):
                logger.info("Skipped article with unusable content: %s", candidate.get("title", ""))
                continue
            candidate["content"] = content

            create_processed_article(db, candidate)
            existing_urls.add(url)
            created_count += 1

        if created_count == 0:
            logger.error("Failed to fetch any new articles")
            return

        latest_today = db.query(Article).filter(
            Article.published_at >= get_today_bounds()[0],
            Article.published_at < get_today_bounds()[1]
        ).order_by(Article.published_at.desc()).first()
        if latest_today:
            latest_today.is_today = True
            db.commit()
        logger.info("Daily news fetch completed: created %s article(s)", created_count)

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
    schedule_startup_catchup_if_needed()

def schedule_startup_catchup_if_needed():
    if not settings.STARTUP_CATCHUP_ENABLED:
        logger.info("Startup catch-up fetch disabled by configuration")
        return

    db = SessionLocal()
    try:
        today_count = count_articles_for_today(db)
        if today_count >= settings.DAILY_ARTICLE_TARGET:
            logger.info(
                "Today's article target already met: %s/%s; startup catch-up skipped",
                today_count,
                settings.DAILY_ARTICLE_TARGET,
            )
            return

        run_at = get_local_now() + timedelta(seconds=2)
        scheduler.add_job(
            fetch_and_process_daily_news,
            trigger=DateTrigger(run_date=run_at),
            id="startup_catchup_fetch",
            name="Startup Catch-up News Fetch",
            replace_existing=True
        )
        logger.info(
            "Today's articles below target: %s/%s; startup catch-up fetch scheduled",
            today_count,
            settings.DAILY_ARTICLE_TARGET,
        )
    finally:
        db.close()

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
                context_definition_cn=enhanced.get("context_definition_cn", ""),
                common_definition_cn=enhanced.get("common_definition_cn", ""),
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
