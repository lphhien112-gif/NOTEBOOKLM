# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import chat, documents, tasks
from .core.config import settings

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Offline RAG API",
    description="API cho phép hỏi-đáp trên tài liệu cá nhân sử dụng mô hình ngôn ngữ chạy cục bộ.",
    version="1.0.0"
)

# Cấu hình CORS (Cross-Origin Resource Sharing)
# Cho phép frontend (chạy trên một port khác) có thể gọi đến backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Thêm các router từ các module endpoint
app.include_router(chat.router, prefix="/api/v1", tags=["1. Chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["2. Documents"])
app.include_router(tasks.router, prefix="/api/v1", tags=["3. Tasks"]) # Thêm router mới

@app.on_event("startup")
async def startup_event():
    """
    Các hành động cần thực hiện khi ứng dụng khởi động.
    Đây là nơi tốt để khởi tạo các tài nguyên nặng.
    """
    print("--- Ứng dụng đang khởi động ---")
    # Mẫu Singleton trong các service đảm bảo chúng chỉ được khởi tạo một lần
    from .services.vector_store import VectorStoreManager
    from .services.rag_pipeline import RAGPipeline
    
    # Lệnh gọi này sẽ kích hoạt việc khởi tạo các instance singleton
    vsm = VectorStoreManager()
    RAGPipeline(vector_store_manager=vsm)
    
    print(f"Mô hình LLM đang sử dụng: {settings.OLLAMA_MODEL}")
    print(f"Mô hình Embedding đang sử dụng: {settings.EMBEDDING_MODEL_NAME}")
    print("--- Khởi động hoàn tất, API đã sẵn sàng ---")

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint gốc để kiểm tra API có đang chạy không."""
    return {"message": "Chào mừng đến với API RAG Offline!"}
