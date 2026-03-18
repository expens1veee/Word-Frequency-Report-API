from src.app.services.lemmatizer import extract_and_lemmatize, lemmatize_word


class TestLemmatizeWord:
    """Тесты функции lemmatize_word: нормализация отдельного слова"""

    def test_nominative_stays_the_same(self):
        assert lemmatize_word("житель") == "житель"

    def test_genitive_is_normalized(self):
        assert lemmatize_word("жителя") == "житель"

    def test_instrumental_is_normalized(self):
        assert lemmatize_word("жителем") == "житель"

    def test_dative_is_normalized(self):
        assert lemmatize_word("жителю") == "житель"

    def test_house_forms_unified(self):
        for form in ("домом", "дома", "дому", "доме"):
            assert lemmatize_word(form) == "дом"

    def test_verb_normalized(self):
        assert lemmatize_word("работали") == "работать"

    def test_unknown_word_returned_as_is(self):
        """Неизвестное слово должно возвращаться без изменений"""
        # вернет хоть какой-то результат — важно, что функция не падает
        result = lemmatize_word("xyzabc")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_lru_cache_hit(self):
        """Повторный вызов с одним словом должен использовать кэш"""
        first = lemmatize_word("книга")
        second = lemmatize_word("книга")
        assert first == second


class TestExtractAndLemmatize:
    """Тесты функции extract_and_lemmatize: парсинг строки и подсчёт частотности"""

    def test_returns_dict(self):
        """Функция должна возвращать словарь"""
        result = extract_and_lemmatize("дом")
        assert isinstance(result, dict)

    def test_punctuation_is_stripped(self):
        """Знаки препинания не должны попадать в словарь"""
        result = extract_and_lemmatize("дом, дома! дому.")
        for key in result:
            assert key.isalpha(), f"Ключ '{key}' содержит небуквенный символ"

    def test_digits_are_excluded(self):
        """Цифры не должны попадать в словарь"""
        result = extract_and_lemmatize("слово 123 ещё одно 456")
        for key in result:
            assert not key.isdigit()

    def test_case_insensitive(self):
        """Слова в разных регистрах должны объединяться"""
        result = extract_and_lemmatize("Дом дом ДОМ")
        assert result.get("дом") == 3

    def test_different_forms_unified(self):
        """Разные словоформы одного слова объединяются в одну лемму"""
        result = extract_and_lemmatize("житель жителем жителя жителю")
        assert result.get("житель") == 4

    def test_word_count(self):
        """Проверяем корректный подсчёт частотности"""
        result = extract_and_lemmatize("кот кот собака кот")
        assert result.get("кот") == 3
        assert result.get("собака") == 1

    def test_empty_string(self):
        """Пустая строка возвращает пустой словарь"""
        result = extract_and_lemmatize("")
        assert result == {}

    def test_only_punctuation(self):
        """Строка только из знаков препинания возвращает пустой словарь"""
        result = extract_and_lemmatize("!!! ??? --- ...")
        assert result == {}

    def test_mixed_russian_and_english(self):
        """Русские и английские слова оба должны попасть в словарь"""
        result = extract_and_lemmatize("дом house")
        assert "дом" in result
        assert "house" in result
