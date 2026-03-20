import os
import sqlite3
import tempfile

from src.app.services.excel import generate_excel
from src.app.services.lemmatizer import extract_and_lemmatize


def process_large_file_process(input_file_path: str) -> str:
    """
    Функция выполняется в отдельном процессе.
    Построчно читает файл, извлекает слова, использует SQLite для агрегации 
    частотности, чтобы избежать ошибки MemoryError на огромных файлах.
    Затем передает данные в генератор excel
    
    Возвращает абсолютный путь к сгенерированному excel-файлу
    """
    # Создаем временную БД SQLite на диске
    db_fd, db_path = tempfile.mkstemp(suffix=".sqlite3")
    os.close(db_fd)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Создаем таблицу для частотности слов в каждой строке
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_counts (
            word TEXT,
            line_no INTEGER,
            count INTEGER
        )
    ''')
    cursor.execute('CREATE INDEX idx_word_line ON word_counts(word, line_no)')
    
    line_no = 0
    batch_size = 5000
    batch_data = []
    
    # Чтение большого файла чанками
    with open(input_file_path, 'rb') as f:
        for line_bytes in f:
            line_no += 1
            # Попытка декодировать строку в UTF-8, запасной вариант windows-1251
            try:
                line_text = line_bytes.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    line_text = line_bytes.decode('windows-1251')
                except UnicodeDecodeError:
                    line_text = line_bytes.decode('utf-8', errors='ignore')
                    
            word_counts_in_line = extract_and_lemmatize(line_text)
            
            for word, count in word_counts_in_line.items():
                batch_data.append((word, line_no, count))
                
            # Запись батчами для оптимизации I/O
            if len(batch_data) >= batch_size:
                cursor.executemany(
                    'INSERT INTO word_counts (word, line_no, count) VALUES (?, ?, ?)',
                    batch_data
                )
                batch_data.clear()
                
    if batch_data:
        cursor.executemany(
            'INSERT INTO word_counts (word, line_no, count) VALUES (?, ?, ?)',
            batch_data
        )
    conn.commit()
    
    num_total_lines = line_no
    
    def data_generator():
        """
        Генератор строк для записи в excel
        Группирует данные по словам и суммирует общее количество
        """
        cursor.execute('SELECT word, line_no, SUM(count) FROM word_counts GROUP BY word, line_no ORDER BY word, line_no')
        
        current_word = None
        current_records = []
        
        def process_word(word_form, records):
            total_sum = sum(c for _, c in records)
            parts = []
            last_line = 0
            for l_no, c in records:
                if l_no > last_line + 1:
                    parts.extend(['0'] * (l_no - last_line - 1))
                parts.append(str(c))
                last_line = l_no
            
            # Заполняем нулями до конца файла, если слово не встретилось в последних строках
            if last_line < num_total_lines:
                parts.extend(['0'] * (num_total_lines - last_line))

            # Ограничение excel - 32767 символов на ячейку.
            # Для гигабайтных файлов строка может превысить это значение
            LIMIT = 32000
            result_row = [word_form, total_sum]
            current_chunk = []
            current_len = 0
            
            for p in parts:
                len_p = len(p) + 1  # длина числа + запятая
                # Если добавление текущего числа превысит лимит ячейки
                if current_len + len_p > LIMIT:
                    chunk_str = ",".join(current_chunk) + " ...(продолжение ->)"
                    result_row.append(chunk_str)
                    # Начинаем новый чанк
                    current_chunk = [p]
                    current_len = len(p)
                else:
                    current_chunk.append(p)
                    if current_len == 0:
                        current_len += len(p)
                    else:
                        current_len += len_p
                        
            # Добавляем оставшееся
            if current_chunk:
                result_row.append(",".join(current_chunk))
                
            return tuple(result_row)

        for row in cursor:
            word, l_no, c = row
            if current_word is None:
                current_word = word
                
            if word != current_word:
                yield process_word(current_word, current_records)
                current_word = word
                current_records = []
                
            current_records.append((l_no, c))
            
        if current_word is not None:
            yield process_word(current_word, current_records)
            
    # Запускаем генерацию Excel из генератора SQLite
    excel_path = generate_excel(data_generator())
    
    conn.close()
    
    # Очистка базы данных SQLite во временной директории ОС
    try:
        os.remove(db_path)
    except Exception:
        pass
        
    return excel_path
