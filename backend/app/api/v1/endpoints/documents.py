# backend/app/api/v1/endpoints/documents.py
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
import shutil
import uuid
import os
from pathlib import Path
from ....core.config import settings
from ....services.vector_store import VectorStoreManager
from ....services.rag_pipeline import RAGPipeline
from ..schemas import DocumentUploadResponse, DocumentDeleteResponse, ClearAllResponse

router = APIRouter()

def get_vsm() -> VectorStoreManager:
    return VectorStoreManager()

def get_rag_pipeline() -> RAGPipeline:
    vsm = VectorStoreManager()
    return RAGPipeline(vector_store_manager=vsm)

def process_document_in_background(file_path: str, document_id: str, vsm: VectorStoreManager):
    print(f"Tác vụ nền: Bắt đầu xử lý tài liệu {document_id}")
    try:
        vsm.add_document(file_path, document_id)
        print(f"Tác vụ nền: Hoàn tất xử lý tài liệu {document_id}")
    except Exception as e:
        print(f"Tác vụ nền: Lỗi khi xử lý tài liệu {document_id}: {e}")

@router.post("/documents", response_model=DocumentUploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    vsm: VectorStoreManager = Depends(get_vsm),
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    try:
        original_filename = Path(file.filename).name
        if original_filename.lower().endswith('.doc.doc'):
            cleaned_filename = original_filename[:-4]
        elif original_filename.lower().endswith('.docx.docx'):
             cleaned_filename = original_filename[:-5]
        else:
            cleaned_filename = original_filename
        
        document_id = str(uuid.uuid4())
        final_filename = f"{document_id}_{cleaned_filename}"
        file_path = Path(settings.UPLOAD_PATH) / final_filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        background_tasks.add_task(process_document_in_background, str(file_path), document_id, vsm)
        
        # Gọi hàm để thiết lập file mặc định mới
        pipeline.set_last_uploaded_document_id(document_id)

        return DocumentUploadResponse(
            message="Tệp đã được chấp nhận và đang được xử lý trong nền.",
            document_id=document_id,
            filename=cleaned_filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể lưu file: {e}")

@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    vsm: VectorStoreManager = Depends(get_vsm)
):
    try:
        vsm.delete_document(document_id)
        for filename in os.listdir(settings.UPLOAD_PATH):
            if filename.startswith(document_id):
                os.remove(os.path.join(settings.UPLOAD_PATH, filename))
                print(f"Đã xóa file gốc: {filename}")
                break
        
        return DocumentDeleteResponse(
            message="Tài liệu đã được xóa thành công.",
            document_id=document_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa tài liệu: {e}")

@router.delete("/clear-all", response_model=ClearAllResponse)
async def clear_all_documents(vsm: VectorStoreManager = Depends(get_vsm)):
    """Endpoint để xóa toàn bộ dữ liệu trong vector store và các file đã tải lên."""
    try:
        result = vsm.clear_all_data()
        return ClearAllResponse(
            message="Toàn bộ dữ liệu đã được xóa thành công.",
            deleted_collections=result["deleted_collections"],
            deleted_files=result["deleted_files"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa toàn bộ dữ liệu: {e}")
    return ClearAllResponse(
        message="Toàn bộ dữ liệu đã được xóa thành công.",      
        deleted_collections=0,
        deleted_files=0
    )
    