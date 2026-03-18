import random
import sys

random.seed(52)

# Набор случайных русских слов в различных морфологических формах
words = [
    "житель", "жителем", "жителю", "жителей",
    "дом", "домом", "дома", "дому",
    "работа", "работой", "работе", "работу",
    "книга", "книгой", "книгу", "книги",
    "человек", "человеком", "людям", "людьми",
    "быстрый", "быстрая", "быстрое", "быстрым",
    "бежать", "бежит", "бежал", "бежали",
    "красивый", "красивая", "красиво", "красота"
]

def generate(filename, size_mb):
    """
    Генерирует тестовый текстовый документ заданного размера,
    используя набор слов-заглушек. Позволяет проверить работу 
    лемматизатора и производительность при парсинге больших объемов данных
    """
    target_bytes = size_mb * 1024 * 1024
    written = 0
    with open(filename, 'w', encoding='utf-8') as f:
        while written < target_bytes:
            # Генерация строки со случайным количеством слов
            line_words = [random.choice(words) for _ in range(random.randint(5, 50))]
            line = " ".join(line_words) + "\n"
            f.write(line)
            written += len(line.encode('utf-8'))
            
    print(f"Файл {filename} успешно сгенерирован. Размер: {written / (1024*1024):.2f} MB")

if __name__ == "__main__":
    size = int(sys.argv[1]) if len(sys.argv) > 1 else 10 # По умолчанию 10 МБ
    generate("test_data.txt", size)
