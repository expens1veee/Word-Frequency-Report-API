import os
from contextlib import asynccontextmanager
from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI
from src.app.api.endpoints import report


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом тяжелых ресурсов приложения
    """
    # Инициализация пула процессов при старте
    pool = ProcessPoolExecutor(max_workers=os.cpu_count() or 4)
    app.state.process_pool = pool
    yield
    # Завершение пула при остановке — корректно освобождает семафоры ОС
    pool.shutdown(wait=False, cancel_futures=True)


app = FastAPI(
    title="API Экспорта Текстовых Отчетов",
    description="API для экспорта статистики частотности слов из больших текстовых файлов.",
    lifespan=lifespan,
)

# Подключение роутера для обработки отчетов
app.include_router(report.router, prefix="/public/report", tags=["Отчеты"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
