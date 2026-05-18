#!/usr/bin/env python3

import sys
sys.path.insert(0, '/Users/hljy/Documents/trae_projects/english_learning/backend')

from app.models.database import SessionLocal, Article, Word, Phrase
from datetime import datetime

def create_test_data():
    db = SessionLocal()
    
    try:
        # 删除旧的测试文章
        db.query(Article).delete()
        db.query(Word).delete()
        db.query(Phrase).delete()
        db.commit()
        print("Cleaned up existing data")
        
        # 创建测试文章1 - 经济类
        article1 = Article(
            title='Global Economy Faces New Challenges in 2024',
            content='The global economy is facing significant challenges as inflation rates continue to rise and supply chains remain disrupted. Central banks around the world are implementing tighter monetary policies to combat rising prices. Many economists predict that these measures will help stabilize the economy in the long term, but short-term pain is expected. Businesses are adapting to these new conditions by investing in technology and improving operational efficiency.',
            summary='Analysis of current economic trends and challenges.',
            source='BBC News',
            url='https://www.bbc.com/news/business',
            published_at=datetime.now(),
            is_today=True
        )
        db.add(article1)
        db.commit()
        db.refresh(article1)
        
        # 添加词汇
        words1 = [
            {'word': 'inflation', 'definition': 'a general increase in prices and fall in the purchasing value of money', 'example': 'High inflation has affected consumer spending.', 'difficulty': 'CET4', 'pos': 'noun'},
            {'word': 'monetary', 'definition': 'relating to money or currency', 'example': 'The central bank announced new monetary policies.', 'difficulty': 'CET6', 'pos': 'adjective'},
            {'word': 'disrupted', 'definition': 'interrupted or broken up', 'example': 'Supply chains were disrupted by the pandemic.', 'difficulty': 'CET4', 'pos': 'adjective'},
            {'word': 'stabilize', 'definition': 'make or become stable', 'example': 'Efforts are being made to stabilize the market.', 'difficulty': 'CET4', 'pos': 'verb'},
            {'word': 'operational', 'definition': 'relating to the way a business or organization works', 'example': 'Operational efficiency has improved.', 'difficulty': 'CET6', 'pos': 'adjective'}
        ]
        
        for w in words1:
            word = Word(
                article_id=article1.id,
                word=w['word'],
                definition=w['definition'],
                example_sentence=w['example'],
                difficulty_level=w['difficulty'],
                part_of_speech=w['pos']
            )
            db.add(word)
        
        # 添加短语
        phrases1 = [
            {'phrase': 'supply chains', 'meaning': 'the sequence of processes involved in the production and distribution of a commodity', 'example': 'Global supply chains have been severely affected.', 'origin': 'business terminology'},
            {'phrase': 'long term', 'meaning': 'over an extended period', 'example': 'Investments should focus on long-term growth.', 'origin': 'common phrase'}
        ]
        
        for p in phrases1:
            phrase = Phrase(
                article_id=article1.id,
                phrase=p['phrase'],
                meaning=p['meaning'],
                example_sentence=p['example'],
                origin=p['origin']
            )
            db.add(phrase)
        
        # 创建测试文章2 - 科技类
        article2 = Article(
            title='Artificial Intelligence Transforms Healthcare Industry',
            content='Artificial intelligence is revolutionizing the healthcare industry, with applications ranging from diagnostic imaging to personalized medicine. Machine learning algorithms can analyze medical data more quickly and accurately than human doctors in many cases. This technology has the potential to improve patient outcomes and reduce healthcare costs significantly. However, concerns remain about data privacy and the ethical implications of AI in medicine.',
            summary='How AI is changing healthcare delivery.',
            source='CNN Tech',
            url='https://www.cnn.com/tech',
            published_at=datetime.now(),
            is_today=False
        )
        db.add(article2)
        db.commit()
        db.refresh(article2)
        
        # 添加词汇
        words2 = [
            {'word': 'revolutionizing', 'definition': 'changing something completely', 'example': 'AI is revolutionizing many industries.', 'difficulty': 'CET6', 'pos': 'verb'},
            {'word': 'diagnostic', 'definition': 'relating to the identification of a disease', 'example': 'Diagnostic imaging helps detect illnesses.', 'difficulty': 'CET6', 'pos': 'adjective'},
            {'word': 'algorithm', 'definition': 'a set of rules for solving a problem', 'example': 'Machine learning algorithms improve over time.', 'difficulty': 'CET4', 'pos': 'noun'},
            {'word': 'ethical', 'definition': 'relating to moral principles', 'example': 'Ethical concerns must be addressed.', 'difficulty': 'CET4', 'pos': 'adjective'},
            {'word': 'implications', 'definition': 'consequences or effects', 'example': 'The implications of AI are far-reaching.', 'difficulty': 'CET6', 'pos': 'noun'}
        ]
        
        for w in words2:
            word = Word(
                article_id=article2.id,
                word=w['word'],
                definition=w['definition'],
                example_sentence=w['example'],
                difficulty_level=w['difficulty'],
                part_of_speech=w['pos']
            )
            db.add(word)
        
        # 添加短语
        phrases2 = [
            {'phrase': 'personalized medicine', 'meaning': 'medical treatment tailored to individual patients', 'example': 'Personalized medicine improves treatment outcomes.', 'origin': 'medical terminology'},
            {'phrase': 'patient outcomes', 'meaning': 'results of medical treatment for patients', 'example': 'Better patient outcomes are the goal.', 'origin': 'medical terminology'}
        ]
        
        for p in phrases2:
            phrase = Phrase(
                article_id=article2.id,
                phrase=p['phrase'],
                meaning=p['meaning'],
                example_sentence=p['example'],
                origin=p['origin']
            )
            db.add(phrase)
        
        db.commit()
        
        print(f'Created {db.query(Article).count()} articles')
        print(f'Created {db.query(Word).count()} words')
        print(f'Created {db.query(Phrase).count()} phrases')
        print('Test data created successfully!')
        
    except Exception as e:
        print(f'Error creating test data: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_test_data()
