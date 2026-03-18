import io

import pytest
from fastapi.testclient import TestClient

from src.app.main import app

@pytest.fixture(scope="module")
def client():
    # Использование TestClient в качестве контекстного менеджера with
    # гарантирует запуск событий lifespan (startup/shutdown) в FastAPI.
    # Это необходимо для того, чтобы инициализировался ProcessPoolExecutor
    # и складывался в app.state.process_pool
    with TestClient(app) as c:
        yield c

class TestExportEndpoint:
    """E2E тесты эндпоинта POST /public/report/export"""

    def test_valid_txt_returns_200(self, client):
        """Загрузка валидного .txt файла должна возвращать HTTP 200"""
        txt_content = b"hello world\nfoo bar baz\n"
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", io.BytesIO(txt_content), "text/plain")},
        )
        assert response.status_code == 200

    def test_response_content_type_is_xlsx(self, client):
        """Ответ должен иметь Content-Type xlsx"""
        txt_content = b"hello world\n"
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", io.BytesIO(txt_content), "text/plain")},
        )
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]

    def test_non_txt_returns_400(self, client):
        """Файл не с расширением .txt должен возвращать HTTP 400"""
        csv_content = "word,count\nдом,5\n".encode("utf-8")
        response = client.post(
            "/public/report/export",
            files={"file": ("data.csv", io.BytesIO(csv_content), "text/csv")},
        )
        assert response.status_code == 400

    def test_non_txt_error_message(self, client):
        """Тело ошибки 400 должно содержать понятное сообщение"""
        csv_content = b"word,count\n"
        response = client.post(
            "/public/report/export",
            files={"file": ("data.csv", io.BytesIO(csv_content), "text/csv")},
        )
        body = response.json()
        assert "detail" in body
        assert ".txt" in body["detail"]

    def test_response_body_is_not_empty(self, client):
        """Тело ответа (сам файл) не должно быть пустым"""
        txt_content = b"test\n"
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", io.BytesIO(txt_content), "text/plain")},
        )
        assert response.status_code == 200
        assert len(response.content) > 0

    def test_russian_text_processed_correctly(self, client):
        """Файл с русским текстом должен успешно обрабатываться"""
        txt_content = "житель жителем жителю\nдом домом\n".encode("utf-8")
        response = client.post(
            "/public/report/export",
            files={"file": ("test.txt", io.BytesIO(txt_content), "text/plain")},
        )
        assert response.status_code == 200

    def test_empty_txt_file_returns_200(self, client):
        """Пустой .txt файл должен возвращать HTTP 200 (пустой отчёт допустим)"""
        response = client.post(
            "/public/report/export",
            files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
        )
        assert response.status_code == 200
