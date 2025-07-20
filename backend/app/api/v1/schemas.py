# backend/app/api/v1/schemas.py
from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    """Cấu trúc cho body của yêu cầu chat."""
    query: str = Field(..., min_length=1)
    document_id: Optional[str] = Field(None)

class ChatResponse(BaseModel):
    """Cấu trúc cho body của phản hồi chat."""
    answer: str

class DocumentUploadResponse(BaseModel):
    """Cấu trúc cho phản hồi sau khi tải file lên."""
    message: str
    document_id: str
    filename: str

class DocumentDeleteResponse(BaseModel):
    """Cấu trúc cho phản hồi sau khi xóa file."""
    message: str
    document_id: str

class ClearAllResponse(BaseModel):
    """Cấu trúc cho phản hồi sau khi xóa toàn bộ dữ liệu."""
    message: str
    deleted_collections: int
    deleted_files: int

# Schema cho các tác vụ mới
class TaskRequest(BaseModel):
    """Cấu trúc yêu cầu chung cho các tác vụ."""
    document_id: Optional[str] = Field(None, description="ID của tài liệu muốn xử lý, nếu để trống sẽ dùng file mặc định")

class GenerateQuestionsRequest(TaskRequest):
    """Cấu trúc yêu cầu cho việc tạo câu hỏi."""
    num_questions: int = Field(5, gt=0, le=20, description="Số lượng câu hỏi muốn tạo")

class TaskResponse(BaseModel):
    """Cấu trúc phản hồi chung cho các tác vụ."""
    result: str
