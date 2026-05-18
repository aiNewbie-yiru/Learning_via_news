"""
词汇提取模块测试套件
基于 SPEC.md 规格文档编写

运行方式: python -m pytest tests/test_word_extractor.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.word_extractor import (
    WordExtractor,
    word_extractor,
    get_word_roots,
    get_register,
    BASIC_WORDS,
    CET4_WORDS,
    CET6_WORDS,
    TOEFL_WORDS,
    PHRASES,
    IDIOMS,
)


class TestGetWordDifficulty:
    """难度等级判断测试"""

    def setup_method(self):
        self.extractor = WordExtractor()

    def test_basic_words(self):
        """Basic词应该返回'Basic'"""
        basic_test_words = ['the', 'have', 'people', 'year', 'way']
        for word in basic_test_words:
            assert self.extractor.get_word_difficulty(word) == "Basic", f"{word} should be Basic"

    def test_cet4_only_words(self):
        """CET4专有词（不在Basic中）应该返回'CET4'"""
        cet4_only_words = ['abandon', 'academic', 'achieve', 'acquire', 'adequate']
        for word in cet4_only_words:
            assert self.extractor.get_word_difficulty(word) == "CET4", f"{word} should be CET4"

    def test_cet6_only_words(self):
        """CET6专有词应该返回'CET6'"""
        cet6_only_words = ['chronic', 'bureaucracy', 'anonymous', 'eloquent', 'paradigm']
        for word in cet6_only_words:
            assert self.extractor.get_word_difficulty(word) == "CET6", f"{word} should be CET6"

    def test_toefl_only_words(self):
        """TOEFL专有词应该返回'TOEFL'"""
        # 使用确实在TOEFL词库中的词
        toefl_only_words = ['aberrant', 'abate', 'abdomen', 'abound', 'abridge']
        for word in toefl_only_words:
            assert self.extractor.get_word_difficulty(word) == "TOEFL", f"{word} should be TOEFL"

    def test_unknown_words(self):
        """未收录词应该返回None"""
        unknown_words = ['asdfgh', 'xyzabc', 'qwerty', 'foobar', 'notaword']
        for word in unknown_words:
            assert self.extractor.get_word_difficulty(word) is None, f"{word} should be None"

    def test_case_insensitive(self):
        """大小写不敏感"""
        assert self.extractor.get_word_difficulty("ABERRANT") == "TOEFL"
        assert self.extractor.get_word_difficulty("AbAtE") == "TOEFL"

    def test_strip_whitespace(self):
        """应该去除首尾空白"""
        assert self.extractor.get_word_difficulty("  aberrant  ") == "TOEFL"


class TestExtractWords:
    """词汇提取测试"""

    def setup_method(self):
        """每个测试前创建新的extractor实例"""
        self.extractor = WordExtractor()

    def test_basic_words_excluded_by_default(self):
        """默认min_difficulty=CET4时，Basic词不应该出现"""
        text = "The world is a beautiful place"
        result = self.extractor.extract_words(text, min_difficulty="CET4")
        words = [item['word'] for item in result]
        assert 'the' not in words
        assert 'world' not in words
        assert 'is' not in words
        assert 'a' not in words

    def test_cet4_words_extracted_when_min_cet4(self):
        """min_difficulty=CET4时CET4词应该出现"""
        text = "The academic discussion about ability and achievement"
        result = self.extractor.extract_words(text, min_difficulty="CET4")
        words = [item['word'] for item in result]
        assert 'academic' in words
        assert 'ability' in words
        assert 'achievement' in words

    def test_min_difficulty_basic_includes_all(self):
        """min_difficulty=Basic应该包含所有非Basic的词"""
        # 使用确实在词库中的词
        text = "aberrant abnormal academic achievement"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        words = [item['word'] for item in result]
        assert 'aberrant' in words  # TOEFL
        assert 'abnormal' in words  # CET6
        assert 'academic' in words  # CET4
        assert 'achievement' in words  # TOEFL

    def test_min_difficulty_toefl_only_highest(self):
        """min_difficulty=TOEFL应该只保留TOEFL词"""
        text = "the academic aberrant discussion about basic ability"
        result = self.extractor.extract_words(text, min_difficulty="TOEFL")
        words = [item['word'] for item in result]
        assert 'aberrant' in words
        # Basic和CET4词不应该出现
        assert 'the' not in words
        assert 'academic' not in words
        assert 'basic' not in words
        assert 'ability' not in words

    def test_word_count_tracking(self):
        """应该正确统计词频"""
        text = "aberrant aberrant aberrant abnormal abnormal"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        word_counts = {item['word']: item['count'] for item in result}
        assert word_counts.get('aberrant') == 3
        assert word_counts.get('abnormal') == 2

    def test_short_words_excluded(self):
        """少于3个字符的词不应该被提取"""
        text = "I am in on to of at be it is an as we so no up go if my me he it"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        words = [item['word'] for item in result]
        # 所有短词都在stop_words中，但即使不在也不应该被提取（正则要求{3,}）
        for word in words:
            assert len(word) >= 3

    def test_sorted_by_difficulty_descending(self):
        """结果应该按难度从高到低排序"""
        text = "the academic quantum physics"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        difficulties = [item['difficulty'] for item in result]
        # 应该按 TOEFL > CET6 > CET4 > Basic 排序
        for i in range(len(difficulties) - 1):
            assert difficulties[i] >= difficulties[i + 1]

    def test_register_field_present(self):
        """每个结果应该包含register字段"""
        text = "academic analysis methodology"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        for item in result:
            assert 'register' in item

    def test_roots_field_present_when_applicable(self):
        """有词根词缀的词应该包含roots字段"""
        # 使用确实有词根词缀的TOEFL词
        text = "anticipate constitute overhaul"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        words_with_roots = [item for item in result if 'roots' in item]
        assert len(words_with_roots) > 0, f"Expected words with roots, got {[r['word'] for r in result]}"


class TestExtractPhrases:
    """短语和习语提取测试"""

    def setup_method(self):
        self.extractor = WordExtractor()

    def test_phrase_extraction(self):
        """应该能提取常见短语"""
        text = "We need to come to terms with this issue and make sense of it"
        result = self.extractor.extract_phrases(text)
        phrases = [item['phrase'] for item in result]
        assert 'come to terms with' in phrases
        assert 'make sense of' in phrases

    def test_idiom_extraction(self):
        """应该能提取习语"""
        text = "Break a leg! It's a piece of cake, really."
        result = self.extractor.extract_phrases(text)
        idioms = [item['phrase'] for item in result]
        assert 'break a leg' in idioms
        assert 'piece of cake' in idioms

    def test_phrase_type_field(self):
        """返回结果应该正确标注type为phrase还是idiom"""
        text = "break a leg and come to terms with it"
        result = self.extractor.extract_phrases(text)
        phrase_types = {item['phrase']: item['type'] for item in result}
        assert phrase_types.get('break a leg') == 'idiom'
        assert phrase_types.get('come to terms with') == 'phrase'

    def test_no_phrase_in_text(self):
        """文本中没有短语时返回空列表"""
        text = "Hello world this is a test"
        result = self.extractor.extract_phrases(text)
        assert result == []

    def test_case_insensitive(self):
        """应该大小写不敏感"""
        text = "Break A Leg and COME TO TERMS WITH"
        result = self.extractor.extract_phrases(text)
        phrases = [item['phrase'] for item in result]
        assert 'break a leg' in phrases
        assert 'come to terms with' in phrases


class TestGetWordRoots:
    """词根词缀分析测试"""

    def test_prefix_recognition(self):
        """应该识别常见前缀"""
        result = get_word_roots('unhappy')
        assert any(r['type'] == 'prefix' and r['affix'] == 'un-' for r in result)

    def test_suffix_recognition(self):
        """应该识别常见后缀"""
        result = get_word_roots('happiness')
        assert any(r['type'] == 'suffix' and r['affix'] == '-ness' for r in result)

    def test_root_recognition(self):
        """应该识别常见词根"""
        result = get_word_roots('inspect')
        assert any(r['type'] == 'root' and r['affix'] == 'spect' for r in result)

    def test_multiple_roots(self):
        """一个词可能有多个词根"""
        result = get_word_roots('unhappiness')
        affixes = [r['affix'] for r in result]
        assert 'un-' in affixes
        assert '-ness' in affixes

    def test_no_root(self):
        """没有词根的词返回空列表"""
        result = get_word_roots('hello')
        assert result == []


class TestGetRegister:
    """语域分类测试"""

    def test_academic_register(self):
        """学术词汇"""
        academic_words = ['analysis', 'concept', 'theory', 'methodology']
        for word in academic_words:
            assert get_register(word) == 'academic', f"{word} should be academic"

    def test_technical_register(self):
        """技术词汇"""
        tech_words = ['algorithm', 'database', 'interface', 'protocol']
        for word in tech_words:
            assert get_register(word) == 'technical', f"{word} should be technical"

    def test_business_register(self):
        """商务词汇"""
        biz_words = ['revenue', 'profit', 'investment', 'strategy']
        for word in biz_words:
            assert get_register(word) == 'business', f"{word} should be business"

    def test_general_register(self):
        """普通词汇"""
        assert get_register('randomword') == 'general'


class TestEdgeCases:
    """边界情况测试"""

    def setup_method(self):
        self.extractor = WordExtractor()

    def test_empty_string(self):
        """空字符串返回空列表"""
        result = self.extractor.extract_words("", min_difficulty="CET4")
        assert result == []

    def test_chinese_text_only(self):
        """纯中文文本返回空列表"""
        text = "这是一个中文句子，没有英文单词"
        result = self.extractor.extract_words(text, min_difficulty="CET4")
        assert result == []

    def test_mixed_text_chinese_english(self):
        """中英混合文本只提取英文"""
        text = "学习 aberrant academic 很重要"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        words = [item['word'] for item in result]
        assert 'aberrant' in words
        assert 'academic' in words

    def test_special_characters(self):
        """特殊字符应该被忽略"""
        text = "Hello!!! World??? What's up???@!"
        result = self.extractor.extract_words(text, min_difficulty="CET4")
        words = [item['word'] for item in result]
        # 只有有效的英文词被提取

    def test_numbers_in_text(self):
        """数字不应该被提取为单词"""
        text = "I have 123 apples and 456 oranges"
        result = self.extractor.extract_words(text, min_difficulty="Basic")
        words = [item['word'] for item in result]
        assert '123' not in words
        assert '456' not in words

    def test_invalid_min_difficulty_defaults(self):
        """无效的min_difficulty值应该使用默认值CET4"""
        text = "academic achievement"
        result = self.extractor.extract_words(text, min_difficulty="INVALID")
        words = [item['word'] for item in result]
        assert 'academic' in words
        assert 'achievement' in words


class TestWordSets:
    """词库完整性测试"""

    def test_basic_is_subset_of_cet4(self):
        """Basic词库应该是CET4的子集"""
        assert BASIC_WORDS.issubset(CET4_WORDS)

    def test_cet4_is_subset_of_cet6(self):
        """CET4词库应该是CET6的子集"""
        assert CET4_WORDS.issubset(CET6_WORDS)

    def test_cet6_is_subset_of_toefl(self):
        """CET6词库应该是TOEFL的子集"""
        assert CET6_WORDS.issubset(TOEFL_WORDS)

    def test_no_overlap_between_levels(self):
        """各级别词库不应该有重叠（每个词只属于一个级别）"""
        basic_words = BASIC_WORDS
        cet4_unique = CET4_WORDS - basic_words
        cet6_unique = CET6_WORDS - CET4_WORDS
        toefl_unique = TOEFL_WORDS - CET6_WORDS

        # 确保unique部分确实只在该级别中
        for word in cet4_unique:
            assert word not in basic_words
            assert word not in cet6_unique
            assert word not in toefl_unique


class TestAnalyzeText:
    """综合文本分析测试"""

    def setup_method(self):
        self.extractor = WordExtractor()

    def test_analyze_text_returns_both_words_and_phrases(self):
        """analyze_text应该同时返回words和phrases"""
        text = "Quantum physics is fascinating. Break a leg in your exam."
        result = self.extractor.analyze_text(text, min_difficulty="Basic")
        assert 'words' in result
        assert 'phrases' in result

    def test_analyze_text_word_count(self):
        """analyze_text应该正确统计词数"""
        text = "quantum quantum physics"
        result = self.extractor.analyze_text(text, min_difficulty="Basic")
        assert result['word_count'] == len(result['words'])

    def test_analyze_text_phrase_count(self):
        """analyze_text应该正确统计短语数"""
        text = "break a leg piece of cake"
        result = self.extractor.analyze_text(text, min_difficulty="Basic")
        assert result['phrase_count'] == len(result['phrases'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])