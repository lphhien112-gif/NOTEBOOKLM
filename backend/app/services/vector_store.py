# backend/app/services/vector_store.py
import chromadb
import os
import shutil
import json
from chromadb.utils import embedding_functions
from rank_bm25 import BM25Okapi # Import thư viện BM25 cho tìm kiếm từ khóa
from typing import List, Optional, Dict, Any
from ..core.config import settings
from .document_parser import load_and_split_document

class VectorStoreManager:
    """
    Quản lý tất cả các tương tác với cơ sở dữ liệu.
    Bao gồm cả Vector Store (ChromaDB) và Keyword Store (BM25).
    Sử dụng mẫu Singleton để đảm bảo chỉ có một instance được tạo ra.
    """
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """Khởi tạo các client và tải các chỉ mục cần thiết khi ứng dụng khởi động."""
        print("Đang khởi tạo VectorStoreManager...")
        # --- Khởi tạo Vector Store (ChromaDB) cho tìm kiếm ngữ nghĩa ---
        self.client = chromadb.PersistentClient(path=settings.VECTOR_STORE_PATH)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=settings.EMBEDDING_MODEL_NAME)
        self.collection = self.client.get_or_create_collection(name="rag_document_collection", embedding_function=self.embedding_function)

        # --- Khởi tạo Keyword Store (BM25) cho tìm kiếm từ khóa ---
        self.keyword_index_path = os.path.join(settings.PROJECT_ROOT, "data", "keyword_index.json")
        self._load_keyword_index()

        print("VectorStoreManager đã sẵn sàng.")

    def _load_keyword_index(self):
        """Tải chỉ mục từ khóa từ file JSON vào bộ nhớ."""
        self.keyword_corpus = {} # Lưu trữ {chunk_id: {"tokens": [...], "content": "...", "metadata": {...}}}
        try:
            if os.path.exists(self.keyword_index_path):
                with open(self.keyword_index_path, 'r', encoding='utf-8') as f:
                    self.keyword_corpus = json.load(f)
                print(f"Đã tải {len(self.keyword_corpus)} chunks vào chỉ mục từ khóa.")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Lỗi khi tải chỉ mục từ khóa, sẽ tạo mới: {e}")
            self.keyword_corpus = {}

    def _save_keyword_index(self):
        """Lưu chỉ mục từ khóa từ bộ nhớ vào file JSON."""
        try:
            with open(self.keyword_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.keyword_corpus, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Lỗi khi lưu chỉ mục từ khóa: {e}")

    def add_document(self, file_path: str, document_id: str):
        """Thêm một tài liệu mới vào cả hai hệ thống lưu trữ."""
        chunks = load_and_split_document(file_path)
        if not chunks: return
        
        ids = [f"{document_id}_{i}" for i in range(len(chunks))]
        contents = [chunk.page_content for chunk in chunks]
        metadatas = [{"document_id": document_id, "source": os.path.basename(chunk.metadata.get("source", file_path)), "page": chunk.metadata.get("page", 0)} for chunk in chunks]
        
        # 1. Thêm vào Vector Store
        self.collection.add(ids=ids, documents=contents, metadatas=metadatas)
        print(f"Đã thêm {len(contents)} chunks vào vector store.")
        
        # 2. Thêm vào Keyword Store
        for i, content in enumerate(contents):
            chunk_id = ids[i]
            # Tokenize (tách từ) đơn giản bằng cách tách khoảng trắng
            tokenized_text = content.lower().split()
            self.keyword_corpus[chunk_id] = {
                "tokens": tokenized_text,
                "content": content,
                "metadata": metadatas[i]
            }
        self._save_keyword_index()
        print(f"Đã thêm {len(contents)} chunks vào keyword index.")

    def delete_document(self, document_id: str):
        """Xóa một tài liệu khỏi cả hai hệ thống lưu trữ."""
        # 1. Xóa khỏi Vector Store
        self.collection.delete(where={"document_id": document_id})
        
        # 2. Xóa khỏi Keyword Store
        ids_to_delete = [chunk_id for chunk_id in self.keyword_corpus if chunk_id.startswith(document_id)]
        for chunk_id in ids_to_delete:
            del self.keyword_corpus[chunk_id]
        self._save_keyword_index()
        print(f"Đã xóa các chunks của document_id: {document_id} khỏi cả hai store.")

    def search(self, query: str, k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Thực hiện tìm kiếm lai (Hybrid Search): kết hợp Semantic và Keyword search.
        """
        # 1. TÌM KIẾM NGỮ NGHĨA (SEMANTIC SEARCH)
        print("Bắt đầu Semantic Search...")
        where_filter = {"document_id": document_id} if document_id else {}
        # SỬA LỖI: Bỏ "ids" khỏi danh sách include vì nó không được hỗ trợ trong một số phiên bản
        vector_results = self.collection.query(
            query_texts=[query], n_results=k*2, where=where_filter, include=["metadatas", "documents"]
        )
        vector_chunks = []
        if vector_results and vector_results['ids']:
            for i, chunk_id in enumerate(vector_results['ids'][0]):
                vector_chunks.append({
                    "id": chunk_id,
                    "content": vector_results['documents'][0][i],
                    "metadata": vector_results['metadatas'][0][i]
                })

        # 2. TÌM KIẾM TỪ KHÓA (KEYWORD SEARCH)
        print("Bắt đầu Keyword Search...")
        corpus_to_search = {chunk_id: data['tokens'] for chunk_id, data in self.keyword_corpus.items() 
                            if not document_id or data['metadata'].get('document_id') == document_id}
        
        keyword_chunks = []
        if corpus_to_search:
            tokenized_corpus = list(corpus_to_search.values())
            chunk_ids = list(corpus_to_search.keys())
            
            bm25 = BM25Okapi(tokenized_corpus)
            tokenized_query = query.lower().split()
            
            top_n_indices = bm25.get_top_n(tokenized_query, range(len(tokenized_corpus)), n=k*2)
            
            for i in top_n_indices:
                chunk_id = chunk_ids[i]
                original_chunk = self.keyword_corpus[chunk_id]
                keyword_chunks.append({
                    "id": chunk_id,
                    "content": original_chunk['content'],
                    "metadata": original_chunk['metadata']
                })

        # 3. TÁI XẾP HẠNG (RE-RANKING)
        print("Bắt đầu Re-ranking...")
        ranked_results = {}
        
        for i, chunk in enumerate(vector_chunks):
            ranked_results[chunk['id']] = 1 / (i + 60)
        
        for i, chunk in enumerate(keyword_chunks):
            chunk_id = chunk['id']
            score = 1 / (i + 60)
            if chunk_id in ranked_results:
                ranked_results[chunk_id] += score
            else:
                ranked_results[chunk_id] = score
        
        sorted_ids = sorted(ranked_results.keys(), key=lambda x: ranked_results[x], reverse=True)
        
        final_chunks = []
        all_found_chunks = {c['id']: c for c in vector_chunks + keyword_chunks}
        for chunk_id in sorted_ids:
            if len(final_chunks) >= k:
                break
            if chunk_id in all_found_chunks:
                final_chunks.append(all_found_chunks[chunk_id])
        
        return final_chunks

    def get_all_chunks_for_document(self, document_id: str) -> List[str]:
        results = self.collection.get(where={"document_id": document_id})
        return results.get('documents', [])

    def clear_all_data(self) -> dict:
        try:
            self.client.delete_collection(name="rag_document_collection")
            self.collection = self.client.get_or_create_collection(name="rag_document_collection", embedding_function=self.embedding_function)
            deleted_collections = 1
        except Exception: deleted_collections = 0
        
        deleted_files = 0
        for filename in os.listdir(settings.UPLOAD_PATH):
            file_path = os.path.join(settings.UPLOAD_PATH, filename)
            try:
                if os.path.isfile(file_path): os.unlink(file_path)
                deleted_files += 1
            except Exception as e: print(f'Lỗi khi xóa {file_path}. Lý do: {e}')
        
        for file_to_delete in [self.keyword_index_path, os.path.join(settings.PROJECT_ROOT, "data", "state.json")]:
            if os.path.exists(file_to_delete):
                try:
                    os.remove(file_to_delete)
                    print(f"Đã xóa file: {os.path.basename(file_to_delete)}")
                except OSError as e:
                    print(f"Lỗi khi xóa file {os.path.basename(file_to_delete)}: {e}")
        
        self.keyword_corpus = {}
        return {"deleted_collections": deleted_collections, "deleted_files": deleted_files}
