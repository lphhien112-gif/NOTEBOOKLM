import React, { useState, useRef, useEffect } from 'react';
import { postChatMessage, summarizeDocument, generateQuestions, extractKeywords } from '../api';
import { Send, User, Bot, Loader2, FileText, Brain, HelpCircle, Mic, Volume2, VolumeX } from 'lucide-react';
import toast from 'react-hot-toast';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.lang = 'vi-VN';
    recognition.interimResults = true;
}

const ChatWindow = ({ document }) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [isVoiceMode, setIsVoiceMode] = useState(false);

    // --- BẮT ĐẦU TÍNH NĂNG MỚI: Quản lý giọng đọc ---
    const [voices, setVoices] = useState([]);
    const [selectedVoiceURI, setSelectedVoiceURI] = useState(localStorage.getItem('selected_voice_uri') || '');
    // --- KẾT THÚC TÍNH NĂNG MỚI ---

    const messagesEndRef = useRef(null);

    // --- BẮT ĐẦU TÍNH NĂNG MỚI: Tải danh sách giọng đọc có sẵn ---
    useEffect(() => {
        const populateVoiceList = () => {
            const availableVoices = window.speechSynthesis.getVoices();
            // Ưu tiên hiển thị các giọng đọc tiếng Việt
            const viVoices = availableVoices.filter(voice => voice.lang.startsWith('vi'));
            setVoices(viVoices.length > 0 ? viVoices : availableVoices);

            // Tự động chọn giọng đọc mặc định nếu chưa có
            if (!localStorage.getItem('selected_voice_uri') && availableVoices.length > 0) {
                const defaultVoice = availableVoices.find(v => v.lang === 'vi-VN') || availableVoices[0];
                if (defaultVoice) {
                    const uri = defaultVoice.voiceURI;
                    setSelectedVoiceURI(uri);
                    localStorage.setItem('selected_voice_uri', uri);
                }
            }
        };

        populateVoiceList();
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = populateVoiceList;
        }
    }, []);
    // --- KẾT THÚC TÍNH NĂNG MỚI ---

    const speak = (text) => {
        if (!isVoiceMode || !('speechSynthesis' in window)) return;

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);

        // --- BẮT ĐẦU CẬP NHẬT: Sử dụng giọng đọc đã được chọn ---
        const selectedVoice = voices.find(v => v.voiceURI === selectedVoiceURI);
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
        // --- KẾT THÚC CẬP NHẬT ---

        utterance.lang = 'vi-VN';
        window.speechSynthesis.speak(utterance);
    };

    useEffect(() => {
        setMessages([{ sender: 'bot', text: `Xin chào! Bây giờ bạn có thể hỏi bất cứ điều gì về tài liệu "${document.filename}".` }]);
        window.speechSynthesis.cancel();
    }, [document]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    useEffect(() => {
        if (!recognition) return;
        recognition.onresult = (event) => {
            const transcript = Array.from(event.results).map(result => result[0]).map(result => result.transcript).join('');
            setInput(transcript);
        };
        recognition.onerror = (event) => {
            console.error("Lỗi Speech Recognition:", event.error);
            toast.error("Lỗi nhận dạng giọng nói. Vui lòng thử lại.");
            stopListening();
        };
        recognition.onend = () => setIsListening(false);
        return () => { if (recognition) recognition.stop(); }
    }, []);

    const startListening = () => {
        if (!recognition) {
            toast.error("Trình duyệt của bạn không hỗ trợ tính năng này.");
            return;
        }
        setInput('');
        setIsListening(true);
        recognition.start();
    };

    const stopListening = () => {
        if (recognition) recognition.stop();
        setIsListening(false);
    };

    const handleMicClick = () => {
        if (isListening) stopListening();
        else startListening();
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (input.trim() === '' || isLoading) return;
        if (isListening) stopListening();

        const userMessage = { sender: 'user', text: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await postChatMessage(input, null);
            const botMessage = { sender: 'bot', text: response.data.answer };
            setMessages((prev) => [...prev, botMessage]);
            speak(response.data.answer);
        } catch (error) {
            const errorMessage = { sender: 'bot', text: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.' };
            setMessages((prev) => [...prev, errorMessage]);
            toast.error("Không thể kết nối đến AI. Vui lòng kiểm tra backend.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleTask = async (taskFunction, taskName) => {
        if (isLoading) return;
        const userMessage = { sender: 'user', text: `Vui lòng ${taskName.toLowerCase()} tài liệu này.` };
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);
        try {
            let response;
            if (taskFunction === generateQuestions) {
                const num = prompt("Bạn muốn tạo bao nhiêu câu hỏi?", "5");
                if (num && parseInt(num) > 0) response = await taskFunction(null, parseInt(num));
                else {
                    setIsLoading(false);
                    setMessages(prev => prev.slice(0, -1));
                    return;
                }
            } else {
                response = await taskFunction(null);
            }
            const botMessage = { sender: 'bot', text: response.data.result };
            setMessages((prev) => [...prev, botMessage]);
            speak(response.data.result);
        } catch (error) {
            const errorMessage = { sender: 'bot', text: `Xin lỗi, không thể ${taskName.toLowerCase()}. Vui lòng thử lại.` };
            setMessages((prev) => [...prev, errorMessage]);
            toast.error(`Tác vụ ${taskName} thất bại.`);
        } finally {
            setIsLoading(false);
        }
    };

    // --- BẮT ĐẦU TÍNH NĂNG MỚI: Hàm xử lý thay đổi giọng đọc ---
    const handleVoiceChange = (e) => {
        const uri = e.target.value;
        setSelectedVoiceURI(uri);
        localStorage.setItem('selected_voice_uri', uri);
    };
    // --- KẾT THÚC TÍNH NĂNG MỚI ---

    return (
        <div className="flex flex-col h-full">
            <header className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h2 className="text-lg font-semibold truncate flex items-center">
                    <FileText className="w-5 h-5 mr-3 text-indigo-400" />
                    Đang trò chuyện về: {document.filename}
                </h2>
                {/* --- BẮT ĐẦU CẬP NHẬT: Thêm dropdown chọn giọng đọc --- */}
                <div className="flex items-center gap-2">
                    {isVoiceMode && voices.length > 0 && (
                        <select
                            value={selectedVoiceURI}
                            onChange={handleVoiceChange}
                            className="bg-gray-200 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md text-sm p-1.5 focus:ring-indigo-500 focus:border-indigo-500"
                        >
                            {voices.map(voice => (
                                <option key={voice.voiceURI} value={voice.voiceURI}>
                                    {voice.name} ({voice.lang})
                                </option>
                            ))}
                        </select>
                    )}
                    <button
                        onClick={() => setIsVoiceMode(!isVoiceMode)}
                        className={`p-2 rounded-full transition-colors ${isVoiceMode
                                ? 'bg-green-500 text-white hover:bg-green-600'
                                : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'
                            }`}
                        title={isVoiceMode ? "Tắt chế độ giọng nói" : "Bật chế độ giọng nói"}
                    >
                        {isVoiceMode ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                    </button>
                </div>
                {/* --- KẾT THÚC CẬP NHẬT --- */}
            </header>

            <div className="flex-grow p-4 overflow-y-auto">
                <div className="space-y-4">
                    {messages.map((msg, index) => (
                        <div key={index} className={`flex items-start gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                            {msg.sender === 'bot' && (<div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center flex-shrink-0"><Bot className="w-5 h-5 text-white" /></div>)}
                            <div className={`max-w-lg p-3 rounded-xl whitespace-pre-wrap ${msg.sender === 'user' ? 'bg-indigo-500 text-white' : 'bg-gray-200 dark:bg-gray-700'}`}>{msg.text}</div>
                            {msg.sender === 'user' && (<div className="w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center flex-shrink-0"><User className="w-5 h-5" /></div>)}
                        </div>
                    ))}
                    {isLoading && (<div className="flex items-start gap-3 justify-start"><div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center flex-shrink-0"><Bot className="w-5 h-5 text-white" /></div><div className="max-w-lg p-3 rounded-xl bg-gray-200 dark:bg-gray-700 flex items-center"><Loader2 className="w-5 h-5 animate-spin mr-2" /><span>AI đang suy nghĩ...</span></div></div>)}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-2 mb-3">
                    <button onClick={() => handleTask(summarizeDocument, "Tóm tắt")} className="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-full flex items-center"><FileText className="w-4 h-4 mr-1.5" /> Tóm tắt</button>
                    <button onClick={() => handleTask(generateQuestions, "Tạo câu hỏi")} className="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-full flex items-center"><HelpCircle className="w-4 h-4 mr-1.5" /> Tạo câu hỏi</button>
                    <button onClick={() => handleTask(extractKeywords, "Trích xuất từ khóa")} className="px-3 py-1.5 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-full flex items-center"><Brain className="w-4 h-4 mr-1.5" /> Trích xuất từ khóa</button>
                </div>
                <form onSubmit={handleSendMessage} className="flex items-center gap-3">
                    <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder={isListening ? "Đang lắng nghe..." : "Nhập câu hỏi của bạn..."} className="flex-grow p-3 bg-gray-200 dark:bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500" disabled={isLoading} />
                    <button type="button" onClick={handleMicClick} className={`p-3 rounded-lg transition-colors ${isListening ? 'bg-red-500 text-white hover:bg-red-600' : 'bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600'}`} disabled={isLoading}><Mic className="w-6 h-6" /></button>
                    <button type="submit" className="p-3 bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 disabled:bg-gray-400" disabled={isLoading || input.trim() === ''}><Send className="w-6 h-6" /></button>
                </form>
            </div>
        </div>
    );
};

export default ChatWindow;
