# 📚 NotebookLM - Chat với Tài liệu (RAG)

Ứng dụng Full-stack cho phép người dùng tải lên tài liệu (PDF, Word...) và trò chuyện/hỏi đáp với nội dung tài liệu đó sử dụng công nghệ RAG (Retrieval-Augmented Generation).

## 🚀 Tính năng chính

- **Quản lý tài liệu:** Tải lên và lưu trữ các file tài liệu (.pdf, .docx, .txt).
- **Chat thông minh:** Hỏi đáp ngữ cảnh dựa trên nội dung tài liệu đã tải lên.
- **Xử lý ngôn ngữ tự nhiên:** Sử dụng mô hình LLM để tóm tắt và trích xuất thông tin.
- **Giao diện thân thiện:** Thiết kế hiện đại với React & Tailwind CSS.

## 🛠️ Công nghệ sử dụng

### Frontend
- **React.js**: Thư viện UI chính.
- **Tailwind CSS**: Styling giao diện.
- **Axios**: Gọi API.

### Backend
- **Python & FastAPI**: Xây dựng RESTful API hiệu năng cao.
- **ChromaDB**: Vector Database để lưu trữ và truy vấn ngữ nghĩa.
- **RAG Pipeline**: Xử lý phân tích văn bản (Document Parser) và tìm kiếm (Retrieval).

## ⚙️ Cài đặt và Chạy thử (Local)

Làm theo các bước sau để chạy dự án trên máy của bạn:

### 1. Clone dự án
```bash
git clone https://github.com/lphhien112-gif/NOTEBOOKLM.git
```

### 2. Cài đặt Backend
```bash
cd backend
# Tạo môi trường ảo (Khuyên dùng)
python -m venv venv
# Kích hoạt môi trường:
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Cài đặt thư viện
pip install -r requirements.txt

# Cấu hình biến môi trường
# Tạo file .env và điền API KEY của bạn vào (ví dụ: OPENAI_API_KEY=...)
```
Chạy server backend:
```bash
uvicorn app.main:app --reload
```
*Backend sẽ chạy tại: http://localhost:8000*

### 3. Cài đặt Frontend
Mở một terminal mới:
```bash
cd frontend
# Cài đặt gói phụ thuộc
npm install

# Chạy ứng dụng
npm start
```
*Frontend sẽ chạy tại: http://localhost:3000*

## 📂 Cấu trúc dự án

```text
NOTEBOOKLM/
├── backend/            # Mã nguồn phía Server (Python/FastAPI)
│   ├── app/
│   │   ├── api/        # Các API Endpoint (v1)
│   │   ├── core/       # Cấu hình hệ thống (Config)
│   │   ├── services/   # Logic xử lý (RAG, Vector Store, Parser)
│   │   └── main.py     # File khởi chạy
│   └── requirements.txt
├── frontend/           # Mã nguồn phía Client (ReactJS)
│   ├── src/
│   │   ├── components/ # Các thành phần UI (ChatWindow, FileUploader...)
│   │   ├── pages/      # Các trang chính
│   │   └── api/        # Cấu hình gọi API
│   └── tailwind.config.js
└── data/               # Nơi lưu trữ Database Vector & File tải lên
```

## 🤝 Đóng góp (Contributing)
Mọi đóng góp đều được hoan nghênh. Vui lòng tạo Pull Request hoặc mở Issue để thảo luận.

## 📝 License
Dự án này được phát hành dưới giấy phép MIT.
