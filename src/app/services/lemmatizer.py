import re
from collections import Counter
from functools import lru_cache

import pymorphy3

# Инициализация морфологического анализатора на уровне модуля.
# При использовании ProcessPoolExecutor это произойдет один раз для каждого воркера
morph = pymorphy3.MorphAnalyzer()

# Регулярное выражение для поиска русских и опционально английских букв в качестве слов
WORD_PATTERN = re.compile(r'[а-яА-ЯёЁa-zA-Z]+')

@lru_cache(maxsize=10000)
def lemmatize_word(word: str) -> str:
    """
    Получение нормальной формы слова с использованием кэширования LruCache
    """
    parsed = morph.parse(word)
    if parsed:
        return parsed[0].normal_form
    return word

def extract_and_lemmatize(text: str) -> dict:
    """
    Извлекает все слова из переданной строки текста, нормализует их,
    и возвращает словарь
    """
    words = WORD_PATTERN.findall(text.lower())
    
    lemmatized = []
    for word in words:
        lemmatized.append(lemmatize_word(word))
            
    return dict(Counter(lemmatized))
