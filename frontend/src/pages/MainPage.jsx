import React, { useState, useEffect } from 'react';
import { Book, MessageSquare, Trash2, BrainCircuit } from 'lucide-react';
import FileUploader from '../components/FileUploader';
import DocumentList from '../components/DocumentList';
import ChatWindow from '../components/ChatWindow';
import { clearAllData } from '../api';
import toast from 'react-hot-toast';

const MainPage = () => {
    const [documents, setDocuments] = useState([]);
    const [selectedDocument, setSelectedDocument] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);

    // Load documents from localStorage on initial render
    useEffect(() => {
        try {
            const storedDocs = localStorage.getItem('rag_documents');
            if (storedDocs) {
                setDocuments(JSON.parse(storedDocs));
            }
            const storedSelectedDoc = localStorage.getItem('rag_selected_doc');
            if (storedSelectedDoc) {
                setSelectedDocument(JSON.parse(storedSelectedDoc));
            }
        } catch (error) {
            console.error("Lỗi khi tải dữ liệu từ localStorage:", error);
            localStorage.removeItem('rag_documents');
            localStorage.removeItem('rag_selected_doc');
        }
    }, []);

    // Save documents to localStorage whenever they change
    useEffect(() => {
        try {
            localStorage.setItem('rag_documents', JSON.stringify(documents));
        } catch (error) {
            console.error("Lỗi khi lưu tài liệu vào localStorage:", error);
        }
    }, [documents]);

    // Save selected document to localStorage whenever it changes
    useEffect(() => {
        try {
            if (selectedDocument) {
                localStorage.setItem('rag_selected_doc', JSON.stringify(selectedDocument));
            } else {
                localStorage.removeItem('rag_selected_doc');
            }
        } catch (error) {
            console.error("Lỗi khi lưu tài liệu được chọn vào localStorage:", error);
        }
    }, [selectedDocument]);


    const handleUploadSuccess = (newDoc) => {
        const updatedDocs = [...documents, newDoc];
        setDocuments(updatedDocs);
        setSelectedDocument(newDoc); // Tự động chọn file vừa tải lên
        setIsProcessing(true);
        // Giả lập thời gian xử lý của backend
        setTimeout(() => {
            setIsProcessing(false);
            toast.success(`Tài liệu "${newDoc.filename}" đã được xử lý!`);
        }, 5000); // 5 giây
    };

    const handleDocumentSelect = (doc) => {
        setSelectedDocument(doc);
    };

    const handleDocumentDelete = (docId) => {
        const updatedDocs = documents.filter(d => d.document_id !== docId);
        setDocuments(updatedDocs);
        if (selectedDocument && selectedDocument.document_id === docId) {
            setSelectedDocument(updatedDocs.length > 0 ? updatedDocs[0] : null);
        }
    };

    const handleClearAll = async () => {
        if (window.confirm("Bạn có chắc chắn muốn xóa tất cả dữ liệu không? Hành động này không thể hoàn tác.")) {
            try {
                await clearAllData();
                setDocuments([]);
                setSelectedDocument(null);
                toast.success("Đã xóa toàn bộ dữ liệu.");
            } catch (error) {
                console.error("Lỗi khi xóa dữ liệu:", error);
                toast.error("Không thể xóa dữ liệu. Vui lòng thử lại.");
            }
        }
    };

    return (
        <div className="flex h-screen">
            {/* Cột bên trái: Quản lý tài liệu */}
            <aside className="w-1/3 max-w-sm bg-white dark:bg-gray-800 p-6 flex flex-col shadow-lg">
                <div className="flex items-center mb-6">
                    <BrainCircuit className="w-8 h-8 text-indigo-500" />
                    <h1 className="text-2xl font-bold ml-3">Notebook AI</h1>
                </div>

                <FileUploader onUploadSuccess={handleUploadSuccess} />

                <div className="flex-grow mt-6 overflow-y-auto">
                    <h2 className="text-lg font-semibold mb-3 flex items-center">
                        <Book className="w-5 h-5 mr-2" />
                        Tài liệu của bạn
                    </h2>
                    <DocumentList
                        documents={documents}
                        selectedDocument={selectedDocument}
                        onDocumentSelect={handleDocumentSelect}
                        onDocumentDelete={handleDocumentDelete}
                        isProcessing={isProcessing}
                    />
                </div>

                <button
                    onClick={handleClearAll}
                    className="mt-4 w-full flex items-center justify-center px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors disabled:bg-gray-400"
                    disabled={documents.length === 0}
                >
                    <Trash2 className="w-5 h-5 mr-2" />
                    Xóa tất cả dữ liệu
                </button>
            </aside>

            {/* Cột bên phải: Cửa sổ Chat */}
            <main className="w-2/3 flex-grow p-6 flex flex-col">
                <div className="flex-grow bg-white dark:bg-gray-800 rounded-xl shadow-inner h-full">
                    {selectedDocument ? (
                        <ChatWindow document={selectedDocument} key={selectedDocument.document_id} />
                    ) : (
                        <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
                            <MessageSquare className="w-16 h-16 mb-4" />
                            <h2 className="text-2xl font-semibold">Chào mừng bạn!</h2>
                            <p className="mt-2 max-w-md">
                                Vui lòng tải lên một tài liệu hoặc chọn một tài liệu từ danh sách để bắt đầu trò chuyện.
                            </p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default MainPage;
