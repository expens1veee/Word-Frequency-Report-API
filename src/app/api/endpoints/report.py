import asyncio
import os
import shutil
import tempfile

from fastapi import APIRouter, Request, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from src.app.services.export import process_large_file_process

router = APIRouter()


def cleanup_files(*file_paths):
    """
    Удаление временных файлов с диска после их использования
    """
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


@router.post("/export")
async def export_report(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Эндпоинт для загрузки большого текстового файла и получения excel-отчета.
    Защищает основной цикл от блокировок при обработке гигабайтных файлов.
    """
    if not file.filename.endswith(".txt"):
         raise HTTPException(status_code=400, detail="Поддерживаются только текстовые файлы (.txt)")

    # Берём пул процессов, созданный в lifespan (main.py)
    process_pool = request.app.state.process_pool

    # Сохраняем загруженный файл во временный файл на диске, так как
    # не можем передавать файловые объекты между процессами
    # напрямую через ProcessPoolExecutor
    fd, temp_input_path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "wb") as f_out:
        shutil.copyfileobj(file.file, f_out)

    try:
        loop = asyncio.get_running_loop()
        # Запуск тяжелой синхронной задачи в пуле процессов
        report_path = await loop.run_in_executor(
            process_pool,
            process_large_file_process,
            temp_input_path
        )

        # Планируем удаление обоих файлов (входной текстовый и выходной Excel)
        # после того как FileResponse будет успешно отправлен клиенту
        background_tasks.add_task(cleanup_files, temp_input_path, report_path)

        return FileResponse(
            path=report_path,
            filename="report.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        cleanup_files(temp_input_path)
        raise HTTPException(status_code=500, detail=f"Не удалось обработать файл: {str(e)}")

