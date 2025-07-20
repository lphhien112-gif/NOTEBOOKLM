import React from 'react';
import { deleteDocument } from '../api';
import { FileText, Trash2, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const DocumentList = ({ documents, selectedDocument, onDocumentSelect, onDocumentDelete, isProcessing }) => {

    const handleDelete = async (e, doc) => {
        e.stopPropagation(); // Ngăn sự kiện click lan ra thẻ cha
        if (window.confirm(`Bạn có chắc muốn xóa file "${doc.filename}" không?`)) {
            try {
                await deleteDocument(doc.document_id);
                onDocumentDelete(doc.document_id);
                toast.success(`Đã xóa file: ${doc.filename}`);
            } catch (error) {
                console.error("Lỗi khi xóa file:", error);
                toast.error("Xóa file thất bại.");
            }
        }
    };

    if (documents.length === 0) {
        return <p className="text-sm text-gray-500 text-center mt-4">Chưa có tài liệu nào.</p>;
    }

    return (
        <ul className="space-y-2">
            {documents.map((doc) => (
                <li
                    key={doc.document_id}
                    onClick={() => onDocumentSelect(doc)}
                    className={`flex items-center p-3 rounded-lg cursor-pointer transition-colors ${selectedDocument?.document_id === doc.document_id
                            ? 'bg-indigo-100 dark:bg-indigo-900'
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                >
                    <FileText className="w-5 h-5 text-indigo-500" />
                    <span className="ml-3 flex-grow truncate" title={doc.filename}>
                        {doc.filename}
                    </span>
                    {isProcessing && selectedDocument?.document_id === doc.document_id ? (
                        <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
                    ) : (
                        <button
                            onClick={(e) => handleDelete(e, doc)}
                            className="ml-2 p-1 rounded-full hover:bg-red-100 dark:hover:bg-red-900 text-gray-500 hover:text-red-600"
                        >
                            <Trash2 className="w-4 h-4" />
                        </button>
                    )}
                </li>
            ))}
        </ul>
    );
};

export default DocumentList;
