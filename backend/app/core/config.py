# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """
    Quản lý tập trung các cài đặt của ứng dụng.
    Tải các biến từ file .env và môi trường hệ thống.
    """
    # Xác định thư mục gốc của dự án để các đường dẫn luôn đúng
    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))

    # Thêm chú thích kiểu `: str` cho tất cả các trường
    VECTOR_STORE_PATH: str = Field(default=os.path.join(PROJECT_ROOT, "data/vector_store"))
    UPLOAD_PATH: str = Field(default=os.path.join(PROJECT_ROOT, "data/uploaded_docs"))
    
    EMBEDDING_MODEL_NAME: str = "paraphrase-multilingual-mpnet-base-v2" #"all-MiniLM-L12-v2"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:1b" #    Đổi sang mô hình bạn đang sử dụng
    
    # Thêm chú thích kiểu `: int` cho các trường số
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 400

    class Config:
        # Đường dẫn đến file .env, nằm ở thư mục backend
        env_file = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")), ".env")
        env_file_encoding = 'utf-8'

# Tạo một thực thể (instance) duy nhất của Settings để sử dụng trong toàn bộ ứng dụng
settings = Settings()

# Đảm bảo các thư mục cần thiết tồn tại khi ứng dụng khởi động
os.makedirs(settings.VECTOR_STORE_PATH, exist_ok=True)
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
