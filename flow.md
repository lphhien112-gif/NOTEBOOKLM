/NOTEBOOKLM/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── chat.py         # API cho hỏi-đáp RAG
│   │   │       │   ├── documents.py    # API quản lý tài liệu (tải lên, xóa)
│   │   │       │   └── tasks.py        # API cho các tác vụ chuyên biệt (tóm tắt, v.v.)
│   │   │       └── schemas.py          # Định dạng dữ liệu API
│   │   ├── 📁 core/
│   │   │   ├── __init__.py
│   │   │   └── config.py               # Quản lý cấu hình tập trung
│   │   ├── 📁 services/
│   │   │   ├── __init__.py
│   │   │   ├── rag_pipeline.py         # Logic chính: điều phối RAG và các tác vụ
│   │   │   ├── vector_store.py         # Quản lý tìm kiếm lai (Vector + Keyword)
│   │   │   └── document_parser.py      # Đọc và chia nhỏ nhiều loại file
│   │   └── main.py                     # Điểm khởi động của server backend
│   ├── .env                            # Lưu các biến môi trường
│   ├── Dockerfile                      # <<-- Cấu hình Docker cho backend
│   └── requirements.txt                # Danh sách các thư viện Python
│
├── 📁 data/
│   ├── 📁 vector_store/               # Lưu trữ cơ sở dữ liệu vector (ChromaDB)
│   ├── 📁 uploaded_docs/              # Lưu trữ các file gốc người dùng tải lên
│   ├── keyword_index.json            # Lưu trữ chỉ mục từ khóa cho tìm kiếm lai
│   └── state.json                    # Lưu trạng thái (ví dụ: file cuối cùng được tải lên)
│
├── 📁 frontend/
│   ├── 📁 public/
│   │   └── index.html                  # File HTML gốc
│   ├── 📁 src/
│   │   ├── 📁 api/
│   │   │   └── index.js                # Các hàm gọi API đến backend
│   │   ├── 📁 components/
│   │   │   ├── ChatWindow.jsx          # Giao diện cửa sổ chat và tác vụ
│   │   │   ├── DocumentList.jsx        # Giao diện danh sách tài liệu
│   │   │   └── FileUploader.jsx        # Giao diện tải file
│   │   ├── 📁 pages/
│   │   │   └── MainPage.jsx            # Bố cục chính của trang
│   │   ├── App.jsx                     # Component gốc
│   │   └── index.js                    # Điểm vào của ứng dụng React
│   ├── Dockerfile                      # <<-- Cấu hình Docker cho frontend
│   ├── package.json                    # Quản lý các thư viện JavaScript
│   └── tailwind.config.js              # Cấu hình cho Tailwind CSS
│
├── .gitignore                          # Các file và thư mục bị bỏ qua bởi Git
└── docker-compose.yml                  # <<-- File điều phối chạy cả backend và frontend