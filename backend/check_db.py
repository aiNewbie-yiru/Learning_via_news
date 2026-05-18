import sys
sys.path.insert(0, '.')
from app.models import init_db, SessionLocal, Article, Word, Phrase

# 初始化数据库
init_db()
db = SessionLocal()

# 检查数据
print("=== Articles ===")
articles = db.query(Article).all()
for article in articles:
    print(f"ID: {article.id}, Title: {article.title}")
    
    # 检查词汇
    print("  Words:")
    words = db.query(Word).filter(Word.article_id == article.id).all()
    for word in words:
        print(f"    - {word.word}")
    
    # 检查短语
    print("  Phrases:")
    phrases = db.query(Phrase).filter(Phrase.article_id == article.id).all()
    for phrase in phrases:
        print(f"    - {phrase.phrase}")

db.close()