# backend/app/services/rag_pipeline.py
import os
import json
from openai import OpenAI
from typing import List, Set, Optional, Dict, Any
from ..core.config import settings
from .vector_store import VectorStoreManager

class RAGPipeline:
    _instance = None # Singleton instance

    def __new__(cls, vector_store_manager: VectorStoreManager):
        if cls._instance is None:
            cls._instance = super(RAGPipeline, cls).__new__(cls)
            cls._instance._init_pipeline(vector_store_manager)
        return cls._instance

    def _init_pipeline(self, vector_store_manager: VectorStoreManager):
        print("Đang khởi tạo RAGPipeline...")
        self.vector_store = vector_store_manager
        
        self.llm_client = OpenAI(
            base_url=settings.OLLAMA_BASE_URL + "/v1",
            api_key='ollama'
        )

        self.conversational_keywords: Set[str] = {
            "xin chào", "chào bạn", "hello", "hi",
            "cảm ơn", "cảm ơn bạn", "thank you", "thanks",
            "bạn là ai", "bạn tên gì",
            "bạn làm được gì", "bạn có thể làm gì"
        }
        
        self.state_file_path = os.path.join(settings.PROJECT_ROOT, "data", "state.json")
        self.last_uploaded_document_id: Optional[str] = self._load_state()
        if self.last_uploaded_document_id:
            print(f"Đã tải trạng thái, tài liệu mặc định là: {self.last_uploaded_document_id}")
        
        print("RAGPipeline đã sẵn sàng.")

    def _load_state(self) -> Optional[str]:
        try:
            if os.path.exists(self.state_file_path):
                with open(self.state_file_path, 'r') as f:
                    state_data = json.load(f)
                    return state_data.get("last_uploaded_document_id")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Lỗi khi tải file trạng thái: {e}")
        return None

    def _save_state(self):
        try:
            with open(self.state_file_path, 'w') as f:
                json.dump({"last_uploaded_document_id": self.last_uploaded_document_id}, f)
        except IOError as e:
            print(f"Lỗi khi lưu file trạng thái: {e}")

    def set_last_uploaded_document_id(self, document_id: str):
        print(f"Thiết lập tài liệu mặc định mới: {document_id}")
        self.last_uploaded_document_id = document_id
        self._save_state()

    def _is_conversational_query(self, query: str) -> bool:
        normalized_query = query.lower().strip().replace('?', '')
        return normalized_query in self.conversational_keywords

    def _generate_conversational_response(self, query: str) -> str:
        print("Đang tạo câu trả lời giao tiếp bằng LLM...")
        system_prompt = "Bạn là một trợ lý AI thân thiện và hữu ích. Hãy trả lời câu hỏi của người dùng một cách ngắn gọn và tự nhiên."
        try:
            response = self.llm_client.chat.completions.create(model=settings.OLLAMA_MODEL, messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}], temperature=0.5)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Lỗi khi tạo câu trả lời giao tiếp: {e}")
            return "Xin chào! Tôi có thể giúp gì cho bạn?"

    # --- BẮT ĐẦU CẢI TIẾN PROMPT ---
    def _format_rag_prompt(self, query: str, context: List[str]) -> str:
        """
        Tạo câu lệnh (prompt) cho quy trình RAG với chỉ thị linh hoạt hơn.
        """
        context_str = "\n\n---\n\n".join(context)
        
        prompt = f"""Bạn là một trợ lý AI chuyên gia. Sử dụng các đoạn văn bản trong phần NGỮ CẢNH dưới đây để trả lời CÂU HỎI của người dùng một cách toàn diện.
Hãy tổng hợp và suy luận thông tin từ các đoạn văn bản để tạo ra một câu trả lời mạch lạc và hữu ích.

NGỮ CẢNH:
{context_str}

CÂU HỎI: {query}

TRẢ LỜI:
"""
        return prompt
    # --- KẾT THÚC CẢI TIẾN PROMPT ---

    def ask(self, query: str, document_id: Optional[str] = None) -> str:
        if self._is_conversational_query(query):
            return self._generate_conversational_response(query)

        target_document_id = document_id or self.last_uploaded_document_id
        if target_document_id:
            print(f"Sử dụng tài liệu mặc định: {target_document_id}")

        print(f"Đang tìm kiếm ngữ cảnh cho câu hỏi: '{query}'")
        found_chunks = self.vector_store.search(query, document_id=target_document_id)
        
        if not found_chunks:
            print("Không tìm thấy ngữ cảnh nào.")
            return "Tôi xin lỗi, tôi không tìm thấy bất kỳ thông tin nào liên quan trong tài liệu của bạn để trả lời câu hỏi này."

        print(f"--- Đã tìm thấy {len(found_chunks)} chunk liên quan ---")
        context_for_prompt = []
        for i, chunk in enumerate(found_chunks):
            print(f"[Chunk {i+1} - Nguồn: {chunk['metadata'].get('source', 'N/A')}, Trang: {chunk['metadata'].get('page', 'N/A')}]")
            print(f"Nội dung: {chunk['content'][:200]}...")
            context_for_prompt.append(chunk['content'])
        print("------------------------------------")
        
        prompt = self._format_rag_prompt(query, context_for_prompt)
        print("Đang gửi yêu cầu RAG đến LLM...")
        try:
            response = self.llm_client.chat.completions.create(model=settings.OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.1)
            answer = response.choices[0].message.content
            print("Đã nhận được câu trả lời RAG từ LLM.")
            return answer
        except Exception as e:
            print(f"Lỗi khi giao tiếp với Ollama (RAG): {e}")
            return "Xin lỗi, đã có lỗi xảy ra khi kết nối với mô hình ngôn ngữ. Vui lòng đảm bảo Ollama đang chạy và thử lại."

    def summarize_document(self, document_id: Optional[str] = None) -> str:
        target_document_id = document_id or self.last_uploaded_document_id
        if not target_document_id:
            return "Vui lòng chỉ định một tài liệu để tóm tắt."

        print(f"Bắt đầu tóm tắt tài liệu: {target_document_id}")
        all_chunks = self.vector_store.get_all_chunks_for_document(target_document_id)

        if not all_chunks:
            return "Không tìm thấy nội dung cho tài liệu này để tóm tắt."

        full_text = "\n".join(all_chunks)
        prompt = f"""Dựa vào toàn bộ văn bản được cung cấp dưới đây, hãy viết một bản tóm tắt chi tiết, nêu bật các ý chính, các số liệu và kết luận quan trọng.

VĂN BẢN:
{full_text}

BẢN TÓM TẮT CHI TIẾT:
"""
        print("Đang gửi yêu cầu tóm tắt đến LLM...")
        try:
            response = self.llm_client.chat.completions.create(model=settings.OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.2)
            return response.choices[0].message.content
        except Exception as e:
            return f"Lỗi khi tóm tắt tài liệu: {e}"

    def generate_questions(self, num_questions: int, document_id: Optional[str] = None) -> str:
        target_document_id = document_id or self.last_uploaded_document_id
        if not target_document_id:
            return "Vui lòng chỉ định một tài liệu để tạo câu hỏi."

        print(f"Bắt đầu tạo câu hỏi cho tài liệu: {target_document_id}")
        all_chunks = self.vector_store.get_all_chunks_for_document(target_document_id)

        if not all_chunks:
            return "Không tìm thấy nội dung cho tài liệu này để tạo câu hỏi."

        full_text = "\n".join(all_chunks)
        prompt = f"""Bạn là một giáo viên nhiều kinh nghiệm. Dựa vào toàn bộ văn bản được cung cấp dưới đây, hãy tạo ra chính xác {num_questions} câu hỏi ôn tập quan trọng để kiểm tra kiến thức.

VĂN BẢN:
{full_text}

{num_questions} CÂU HỎI ÔN TẬP:
"""
        print(f"Đang gửi yêu cầu tạo {num_questions} câu hỏi đến LLM...")
        try:
            response = self.llm_client.chat.completions.create(model=settings.OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}], temperature=0.7)
            return response.choices[0].message.content
        except Exception as e:
            return f"Lỗi khi tạo câu hỏi ôn tập: {e}"

    def extract_keywords_and_topics(self, document_id: Optional[str] = None) -> str:
        target_document_id = document_id or self.last_uploaded_document_id
        if not target_document_id:
            return "Vui lòng chỉ định một tài liệu để trích xuất từ khóa."

        print(f"Bắt đầu trích xuất từ khóa cho tài liệu: {target_document_id}")
        all_chunks = self.vector_store.get_all_chunks_for_document(target_document_id)

        if not all_chunks:
            return "Không tìm thấy nội dung cho tài liệu này để trích xuất từ khóa."

        full_text = "\n".join(all_chunks)
        
        prompt = f"""Bạn là một chuyên gia phân tích dữ liệu. Dựa vào toàn bộ văn bản được cung cấp dưới đây, hãy thực hiện hai việc:
1. Liệt kê 5-10 từ khóa (keywords) hoặc cụm từ quan trọng nhất.
2. Liệt kê 3-5 chủ đề chính (main topics) mà tài liệu này đề cập.

Trình bày kết quả một cách rõ ràng.

VĂN BẢN:
{full_text}

KẾT QUẢ PHÂN TÍCH:
"""
        print("Đang gửi yêu cầu trích xuất từ khóa đến LLM...")
        try:
            response = self.llm_client.chat.completions.create(
                model=settings.OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Lỗi khi trích xuất từ khóa và chủ đề: {e}"
        for chunk in chunks:
            chunk_id = f"{document_id}_{i}"
            self.keyword_corpus[chunk_id] = {
                "tokens": chunk.page_content.split(),
                "content": chunk.page_content,
                "metadata": chunk.metadata
            }
        self._save_keyword_index()
        