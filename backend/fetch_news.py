import sys
sys.path.insert(0, '.')
from app.services.news_scraper import NewsScraper
from app.services.word_extractor import WordExtractor
from app.models import init_db, SessionLocal, Article, Word, Phrase
from datetime import datetime

# 初始化数据库
init_db()
db = SessionLocal()

# 抓取新闻
scraper = NewsScraper()
print('Fetching news...')
article_data = scraper.get_random_article()

if article_data:
    
    # 提取词汇和短语
    extractor = WordExtractor()
    words = extractor.extract_difficult_words(article_data['content'])
    phrases = extractor.extract_phrases(article_data['content'])
    
    # 创建文章
    article = Article(
        title=article_data['title'],
        content=article_data['content'],
        summary=article_data['summary'],
        source=article_data['source'],
        url=article_data['url'],
        published_at=datetime.now(),
        is_today=True
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    
    # 创建词汇
    for word_data in words:
        word = Word(
            article_id=article.id,
            word=word_data['word'],
            definition=word_data.get('definition'),
            example_sentence=word_data.get('example_sentence'),
            difficulty_level=word_data['difficulty_level'],
            part_of_speech=word_data.get('part_of_speech'),
            frequency=word_data['frequency']
        )
        db.add(word)
    
    # 创建短语
    for phrase_data in phrases:
        phrase = Phrase(
            article_id=article.id,
            phrase=phrase_data['phrase'],
            meaning=phrase_data.get('meaning'),
            example_sentence=phrase_data.get('example_sentence'),
            origin=phrase_data.get('origin')
        )
        db.add(phrase)
    
    db.commit()
    print(f'Successfully saved article: {article.title}')
    print(f'Words extracted: {len(words)}')
    print(f'Phrases extracted: {len(phrases)}')
else:
    print('No articles fetched')

db.close()