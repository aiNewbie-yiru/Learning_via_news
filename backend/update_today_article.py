import sys
sys.path.insert(0, '.')
from app.models import init_db, SessionLocal, Article

# 初始化数据库
init_db()
db = SessionLocal()

# 更新文章
article1 = db.query(Article).filter(Article.id == 1).first()
if article1:
    article1.is_today = False

article2 = db.query(Article).filter(Article.id == 2).first()
if article2:
    article2.is_today = True

db.commit()
print("Updated articles:")
print(f"Article 1 is_today: {article1.is_today if article1 else 'Not found'}")
print(f"Article 2 is_today: {article2.is_today if article2 else 'Not found'}")

db.close()