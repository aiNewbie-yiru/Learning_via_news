import argparse
import sys

from app.models.database import SessionLocal, Article, Word, Phrase
from app.services.scheduler import process_article_vocabulary
from check_vocab_api import main as check_vocab_api


def parse_article_targets(targets):
    article_ids = []
    seen = set()

    for target in targets:
        for part in target.split(","):
            part = part.strip()
            if not part:
                continue

            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start = int(start_text)
                end = int(end_text)
                if start > end:
                    raise ValueError(f"Invalid range '{part}': start must be <= end")
                values = range(start, end + 1)
            else:
                values = [int(part)]

            for article_id in values:
                if article_id not in seen:
                    article_ids.append(article_id)
                    seen.add(article_id)

    return article_ids


def regenerate_article_vocabulary(article_id: int) -> int:
    db = SessionLocal()
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            print(f"Article {article_id} not found")
            return 1

        word_count = db.query(Word).filter(Word.article_id == article_id).count()
        phrase_count = db.query(Phrase).filter(Phrase.article_id == article_id).count()

        print(f"Regenerating vocabulary for article {article_id}: {article.title}")
        print(f"Deleting {word_count} words and {phrase_count} phrases")

        db.query(Word).filter(Word.article_id == article_id).delete(synchronize_session=False)
        db.query(Phrase).filter(Phrase.article_id == article_id).delete(synchronize_session=False)
        db.commit()

        process_article_vocabulary(article_id, db)

        new_word_count = db.query(Word).filter(Word.article_id == article_id).count()
        new_phrase_count = db.query(Phrase).filter(Phrase.article_id == article_id).count()
        print(f"Done. Created {new_word_count} words and {new_phrase_count} phrases")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"Failed to regenerate vocabulary: {exc}")
        return 1
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate vocabulary for one or more articles using current extraction limits."
    )
    parser.add_argument(
        "article_targets",
        nargs="+",
        help="Article IDs or ranges to regenerate, e.g. 7, 1-5, or 1,3,5",
    )
    args = parser.parse_args()

    try:
        article_ids = parse_article_targets(args.article_targets)
    except ValueError as exc:
        print(f"Invalid article target: {exc}")
        return 1

    if not article_ids:
        print("No article IDs provided")
        return 1

    print("Checking vocabulary API before deleting existing vocabulary...")
    if check_vocab_api() != 0:
        print("Vocabulary API check failed. Existing vocabulary was not changed.")
        return 1

    failures = 0
    for article_id in article_ids:
        print("")
        result = regenerate_article_vocabulary(article_id)
        if result != 0:
            failures += 1

    if failures:
        print(f"\nCompleted with {failures} failure(s)")
        return 1

    print(f"\nCompleted successfully for {len(article_ids)} article(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
