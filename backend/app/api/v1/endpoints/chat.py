# backend/app/api/v1/endpoints/chat.py
from fastapi import APIRouter, Depends, HTTPException
from ....services.rag_pipeline import RAGPipeline
from ....services.vector_store import VectorStoreManager
from ..schemas import ChatRequest, ChatResponse

router = APIRouter()

def get_rag_pipeline() -> RAGPipeline:
    vsm = VectorStoreManager()
    return RAGPipeline(vector_store_manager=vsm)

@router.post("/chat", response_model=ChatResponse)
async def handle_chat(
    request: ChatRequest, 
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Endpoint để xử lý các yêu cầu chat.
    Nhận câu hỏi và document_id (tùy chọn) để trả lời.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống.")
    
    try:
        # Truyền document_id từ request vào pipeline
        answer = pipeline.ask(request.query, document_id=request.document_id)
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"Lỗi trong quá trình xử lý chat: {e}")
        raise HTTPException(status_code=500, detail="Đã có lỗi xảy ra trong hệ thống.")
