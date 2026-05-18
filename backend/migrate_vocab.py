import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import init_db, SessionLocal, Article, Word, Phrase
from app.services import vocab_enhancer_service
from sqlalchemy import inspect


def table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def column_exists(engine, table_name, column_name):
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def migrate_database():
    print("Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        print("Database initialized.")
        
        articles = db.query(Article).all()
        print(f"Found {len(articles)} articles to process.")
        
        for idx, article in enumerate(articles):
            print(f"\nProcessing article {idx+1}/{len(articles)}: {article.title[:50]}...")
            
            # Process words
            for word in article.words:
                print(f"  Enhancing word: {word.word}")
                try:
                    enhanced = vocab_enhancer_service.enhance_word(
                        word=word.word,
                        difficulty=word.difficulty_level or "CET6",
                        part_of_speech=word.part_of_speech,
                        article_context=article.content
                    )
                    word.definition_cn = enhanced["definition_cn"]
                    word.example_cn = enhanced["example_cn"]
                    word.example_source = enhanced["example_source"]
                    if not word.definition:
                        word.definition = enhanced["definition"]
                    if not word.example_sentence:
                        word.example_sentence = enhanced["example_sentence"]
                    if not word.part_of_speech:
                        word.part_of_speech = enhanced["part_of_speech"]
                except Exception as e:
                    print(f"    Error enhancing word: {e}")
            
            # Process phrases
            for phrase in article.phrases:
                print(f"  Enhancing phrase: {phrase.phrase}")
                try:
                    enhanced = vocab_enhancer_service.enhance_phrase(
                        phrase=phrase.phrase,
                        meaning=phrase.meaning,
                        article_context=article.content
                    )
                    phrase.meaning_cn = enhanced["meaning_cn"]
                    phrase.example_cn = enhanced["example_cn"]
                    phrase.example_source = enhanced["example_source"]
                    if not phrase.meaning:
                        phrase.meaning = enhanced["meaning"]
                    if not phrase.example_sentence:
                        phrase.example_sentence = enhanced["example_sentence"]
                except Exception as e:
                    print(f"    Error enhancing phrase: {e}")
            
            db.commit()
            print(f"  Article {idx+1} completed.")
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate_database()
