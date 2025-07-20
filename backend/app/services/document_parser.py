# backend/app/services/document_parser.py
import os
import sys
from typing import List
from langchain.schema.document import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..core.config import settings

# --- BẮT ĐẦU CẬP NHẬT: Thêm logic xử lý riêng cho file .doc trên Windows ---
def _load_doc_with_win32(file_path: str) -> List[Document]:
    """
    Sử dụng thư viện pywin32 để nhờ MS Word đọc file .doc.
    Chỉ hoạt động trên Windows và yêu cầu có cài đặt MS Word.
    """
    import win32com.client as win32
    from langchain.docstore.document import Document

    try:
        word = win32.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(file_path)
        content = doc.Content.Text
        doc.Close()
        word.Quit()
        
        # Tạo một đối tượng Document của LangChain từ nội dung đã đọc
        return [Document(page_content=content, metadata={"source": os.path.basename(file_path)})]
    except Exception as e:
        print(f"Lỗi khi dùng win32com để đọc file .doc: {e}")
        # Đảm bảo Word được đóng lại nếu có lỗi
        if 'word' in locals() and word is not None:
            word.Quit()
        return []

# --- KẾT THÚC CẬP NHẬT ---

def load_and_split_document(file_path: str) -> List[Document]:
    """
    Tải một tài liệu từ đường dẫn file, chọn loader phù hợp dựa trên
    phần mở rộng của file và chia nhỏ nó thành các chunk.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    print(f"Đang xử lý file có phần mở rộng: {file_extension}")
    
    documents = []
    
    # --- BẮT ĐẦU CẬP NHẬT: Thêm luồng xử lý riêng cho .doc ---
    # Chọn loader phù hợp
    if file_extension == ".pdf":
        loader = PyPDFLoader(file_path, extract_images=False)
        documents = loader.load()
    elif file_extension == ".txt":
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
    elif file_extension == ".docx":
        # .docx không cần LibreOffice
        loader = UnstructuredWordDocumentLoader(file_path)
        documents = loader.load()
    elif file_extension == ".doc":
        # Nếu là Windows, ưu tiên dùng pywin32
        if sys.platform == "win32":
            print("Phát hiện Windows, đang thử đọc file .doc bằng MS Word...")
            documents = _load_doc_with_win32(os.path.abspath(file_path))
        else:
            # Nếu không phải Windows, dùng cách cũ (cần LibreOffice)
            print("Đang thử đọc file .doc bằng Unstructured (yêu cầu LibreOffice)...")
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
    else:
        raise ValueError(f"Loại file không được hỗ trợ: {file_extension}")
    # --- KẾT THÚC CẬP NHẬT ---

    if not documents:
        print(f"Cảnh báo: Không có nội dung nào được trích xuất từ {file_path}")
        return []

    # Khởi tạo công cụ chia nhỏ văn bản
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
    )
    
    # Thực hiện chia nhỏ
    chunks = text_splitter.split_documents(documents)
    
    print(f"Đã tải và chia tài liệu {os.path.basename(file_path)} thành {len(chunks)} chunks.")
    return chunks
