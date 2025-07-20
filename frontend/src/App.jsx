import React from 'react';
import MainPage from './pages/MainPage';
import { Toaster } from 'react-hot-toast';

function App() {
    return (
        <div className="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen font-sans">
            <Toaster position="top-center" reverseOrder={false} />
            <MainPage />
        </div>
    );
}

export default App;
export const API_BASE_URL = 'http://localhost:8000/api/v1';