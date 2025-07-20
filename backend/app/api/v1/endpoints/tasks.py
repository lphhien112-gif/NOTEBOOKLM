# backend/app/api/v1/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException
from ....services.rag_pipeline import RAGPipeline
from ....services.vector_store import VectorStoreManager
from ..schemas import TaskRequest, GenerateQuestionsRequest, TaskResponse

router = APIRouter()

def get_rag_pipeline() -> RAGPipeline:
    vsm = VectorStoreManager()
    return RAGPipeline(vector_store_manager=vsm)

@router.post("/tasks/summarize", response_model=TaskResponse)
async def summarize_document(
    request: TaskRequest, 
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Endpoint để tóm tắt toàn bộ một tài liệu."""
    try:
        summary = pipeline.summarize_document(document_id=request.document_id)
        return TaskResponse(result=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/generate-questions", response_model=TaskResponse)
async def generate_review_questions(
    request: GenerateQuestionsRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Endpoint để tạo các câu hỏi ôn tập từ một tài liệu."""
    try:
        questions = pipeline.generate_questions(
            num_questions=request.num_questions,
            document_id=request.document_id
        )
        return TaskResponse(result=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/extract-keywords", response_model=TaskResponse)
async def extract_keywords(
    request: TaskRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """Endpoint để trích xuất từ khóa và chủ đề chính từ một tài liệu."""
    try:
        keywords_and_topics = pipeline.extract_keywords_and_topics(document_id=request.document_id)
        return TaskResponse(result=keywords_and_topics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
