# Word Frequency Report API

REST API сервис на **FastAPI** для анализа частотности словоформ в больших текстовых файлах с экспортом результата в **Excel**.

## Возможности

- Принимает текстовые файлы любого размера
- Лемматизация русских слов
- Экспорт результата в `.xlsx` с тремя столбцами: словоформа, общее количество, количество в каждой строке
- Потоковая обработка без загрузки файла в ОЗУ целиком (SQLite как промежуточное хранилище)
- Параллельная обработка через `ProcessPoolExecutor` — тяжёлые задачи не блокируют сервер

## Стек технологий

| Слой | Библиотека |
|---|---|
| Веб-фреймворк | [FastAPI](https://fastapi.tiangolo.com/) |
| Сервер | [Uvicorn](https://www.uvicorn.org/) |
| Лемматизация | [pymorphy3]([https://pymorphy3.readthedocs.io/](https://pypi.org/project/pymorphy3/)) |
| Excel | [openpyxl](https://openpyxl.readthedocs.io/) |
| Пакетный менеджер | [uv](https://docs.astral.sh/uv/) |

## Структура проекта

```
├── src/
│   ├── app/
│   │   ├── main.py                    # Точка входа FastAPI
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       └── report.py          # Эндпоинт POST /public/report/export
│   │   └── services/
│   │       ├── export.py              # Основная логика: чтение файла, SQLite, генератор
│   │       ├── lemmatizer.py          # Регулярки + pymorphy3 + lru_cache
│   │       └── excel.py               # Потоковая запись в .xlsx
│   └── scripts/
│       └── generate_test_file.py      # Утилита для генерации тестового файла
├── tests/
│   ├── conftest.py                    # Общие pytest-фикстуры
│   ├── test_api.py                    # E2E тесты HTTP-эндпоинта
│   ├── test_export.py                 # Тесты логики экспорта и Excel
│   └── test_lemmatizer.py             # Тесты лемматизатора
├── pyproject.toml                     # Зависимости и метаданные проекта
└── uv.lock                            # Зафиксированные версии зависимостей
```

## Быстрый старт

### 1. Установка `uv`

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**macOS (через Homebrew):**
```bash
brew install uv
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

После установки перезапустите терминал, чтобы команда `uv` стала доступна.

### 2. Клонирование и установка зависимостей

```bash
git clone <url-репозитория>
cd Word-Frequency-Report-API

# uv автоматически создаст виртуальное окружение .venv и установит все пакеты
uv sync
```

### 3. Запуск сервера

Запускать **только из корневой директории** проекта (`Word-Frequency-Report-API/`):

```bash
uv run uvicorn src.app.main:app --reload
```

Сервер запустится на `http://localhost:8000`.

## Использование API

### Swagger UI

Откройте в браузере: **`http://localhost:8000/docs`**

Там вы найдёте интерактивную документацию — можно загрузить файл прямо из браузера.

### curl

**macOS / Linux:**
```bash
curl -X POST \
  -F "file=@/путь/к/вашему/файлу.txt" \
  http://localhost:8000/public/report/export \
  --output report.xlsx
```

**Windows (PowerShell):**
```powershell
curl.exe -X POST `
  -F "file=@C:\путь\к\вашему\файлу.txt" `
  http://localhost:8000/public/report/export `
  --output report.xlsx
```

### Python (httpx)

```python
import httpx

with open("data.txt", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/public/report/export",
        files={"file": ("data.txt", f, "text/plain")},
    )

with open("report.xlsx", "wb") as out:
    out.write(response.content)
```

## Формат результата

Excel-файл содержит три столбца:

| Словоформа | Кол-во во всём документе | Кол-во в каждой из строк |
|---|---|---|
| житель | 12 | 3,0,1,0,0,2,... |
| книга | 5 | 0,1,0,2,... |

Третий столбец — строка из чисел через запятую, где каждое число соответствует строке исходного файла. Если строка превышает 32 000 символов (ограничение ячейки Excel), данные автоматически переносятся в следующий столбец со знаком `...(продолжение ->)`.

## Запуск тестов

```bash
uv run pytest tests/ -v
```

Тесты покрывают:
- Лемматизацию и нормализацию слов
- Полный цикл обработки файла (txt → SQLite → xlsx)
- Нарезку строк при превышении лимита ячейки Excel
- HTTP-эндпоинт (статус 200/400, Content-Type, пустой файл)


## Генерация тестового файла

Для проверки на больших данных можно сгенерировать тестовый файл нужного размера (в МБ):

```bash
# Создать файл размером 100 МБ
uv run python src/scripts/generate_test_file.py 100
```

Файл `test_data.txt` появится в текущей директории.
