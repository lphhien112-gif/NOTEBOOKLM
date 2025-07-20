import React, { useState } from 'react';
import { uploadDocument } from '../api';
import { UploadCloud, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

const FileUploader = ({ onUploadSuccess }) => {
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        setUploading(true);
        setProgress(0);
        const toastId = toast.loading(`Đang tải lên: ${file.name}`);

        try {
            const response = await uploadDocument(file, (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                setProgress(percentCompleted);
            });
            toast.success(`Đã tải lên thành công! Đang xử lý...`, { id: toastId });
            onUploadSuccess(response.data);
        } catch (error) {
            console.error("Lỗi khi tải file:", error);
            toast.error("Tải file thất bại. Vui lòng thử lại.", { id: toastId });
        } finally {
            setUploading(false);
            // Reset input để có thể tải lại cùng một file
            event.target.value = null;
        }
    };

    return (
        <div className="relative border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center">
            <input
                type="file"
                onChange={handleFileChange}
                disabled={uploading}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                accept=".pdf,.doc,.docx,.txt"
            />
            {uploading ? (
                <div className="flex flex-col items-center">
                    <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
                    <p className="mt-2 font-semibold">Đang tải lên... {progress}%</p>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2 dark:bg-gray-700">
                        <div className="bg-indigo-600 h-2.5 rounded-full" style={{ width: `${progress}%` }}></div>
                    </div>
                </div>
            ) : (
                <div className="flex flex-col items-center">
                    <UploadCloud className="w-10 h-10 text-gray-400" />
                    <p className="mt-2 font-semibold">Kéo thả hoặc nhấn để tải file</p>
                    <p className="text-sm text-gray-500">Hỗ trợ: PDF, DOC, DOCX, TXT</p>
                </div>
            )}
        </div>
    );
};

export default FileUploader;
