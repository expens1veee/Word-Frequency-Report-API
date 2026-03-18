import os
import tempfile

import pytest


@pytest.fixture
def small_text_file():
    """Создает временный текстовый файл с предсказуемым содержимым"""
    content = (
        "житель жителем жителю\n"
        "дом домом дому дом\n"
        "работа и снова работа\n"
    )
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    yield path
    os.unlink(path)


@pytest.fixture
def non_txt_file():
    """Создает временный файл НЕ с расширением .txt для проверки валидации"""
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("word,count\nдом,5")
    yield path
    os.unlink(path)
