import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scheduler import select_hardest_words


def test_select_hardest_words_prioritizes_difficulty_then_frequency():
    words = [
        {"word": "academic", "difficulty": "CET4", "count": 10},
        {"word": "abnormal", "difficulty": "CET6", "count": 1},
        {"word": "aberrant", "difficulty": "TOEFL", "count": 1},
        {"word": "bureaucracy", "difficulty": "CET6", "count": 3},
        {"word": "ability", "difficulty": "CET4", "count": 99},
    ]

    selected = select_hardest_words(words, 3)

    assert [item["word"] for item in selected] == [
        "aberrant",
        "bureaucracy",
        "abnormal",
    ]
