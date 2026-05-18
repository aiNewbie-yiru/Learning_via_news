import sys
sys.path.insert(0, '.')
from app.models import init_db, SessionLocal, Article, Word, Phrase
from datetime import datetime

# 初始化数据库
init_db()
db = SessionLocal()

# 创建测试文章
test_article = Article(
    title="The Future of Artificial Intelligence in Everyday Life",
    content="""Artificial intelligence is transforming how we live and work. From smart home devices that anticipate our needs to personalized recommendations on streaming platforms, AI has become an integral part of modern life. Researchers are making significant breakthroughs in natural language processing, computer vision, and machine learning algorithms. As these technologies advance, they promise to solve complex challenges in healthcare, education, and environmental sustainability. However, we must also address important questions about privacy, ethics, and the future of work in an increasingly automated world.""",
    summary="Exploring how artificial intelligence is transforming daily life and what the future holds for this groundbreaking technology.",
    source="Tech Insights",
    url="https://example.com/future-ai",
    published_at=datetime.now(),
    is_today=True
)
db.add(test_article)
db.commit()
db.refresh(test_article)

# 创建测试词汇
test_words = [
    {"word": "artificial", "difficulty_level": "intermediate", "frequency": 2},
    {"word": "intelligence", "difficulty_level": "advanced", "frequency": 2},
    {"word": "transforming", "difficulty_level": "intermediate", "frequency": 1},
    {"word": "personalized", "difficulty_level": "intermediate", "frequency": 1},
    {"word": "platforms", "difficulty_level": "intermediate", "frequency": 1},
    {"word": "integral", "difficulty_level": "advanced", "frequency": 1},
    {"word": "breakthroughs", "difficulty_level": "advanced", "frequency": 1},
    {"word": "processing", "difficulty_level": "advanced", "frequency": 1},
    {"word": "algorithms", "difficulty_level": "advanced", "frequency": 1},
    {"word": "sustainability", "difficulty_level": "advanced", "frequency": 1},
    {"word": "address", "difficulty_level": "intermediate", "frequency": 1},
    {"word": "ethics", "difficulty_level": "advanced", "frequency": 1},
    {"word": "increasingly", "difficulty_level": "intermediate", "frequency": 1},
    {"word": "automated", "difficulty_level": "intermediate", "frequency": 1}
]

for word_data in test_words:
    word = Word(
        article_id=test_article.id,
        word=word_data['word'],
        definition=None,
        example_sentence=None,
        difficulty_level=word_data['difficulty_level'],
        part_of_speech=None
    )
    db.add(word)

# 创建测试短语
test_phrases = [
    {"phrase": "artificial intelligence", "meaning": "The simulation of human intelligence processes by machines, especially computer systems."},
    {"phrase": "smart home devices", "meaning": "Internet-connected household appliances and systems that can be controlled remotely or automatically."},
    {"phrase": "natural language processing", "meaning": "A branch of artificial intelligence that enables computers to understand, interpret, and generate human language."},
    {"phrase": "machine learning", "meaning": "A subset of artificial intelligence that allows systems to learn and improve from experience without being explicitly programmed."},
    {"phrase": "environmental sustainability", "meaning": "The practice of meeting current needs without compromising the ability of future generations to meet their own needs."}
]

for phrase_data in test_phrases:
    phrase = Phrase(
        article_id=test_article.id,
        phrase=phrase_data['phrase'],
        meaning=phrase_data['meaning'],
        example_sentence=None,
        origin=None
    )
    db.add(phrase)

db.commit()
print(f'Successfully created test article: {test_article.title}')
print(f'Words added: {len(test_words)}')
print(f'Phrases added: {len(test_phrases)}')

db.close()