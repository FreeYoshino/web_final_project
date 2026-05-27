import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Phone, Wallet } from 'lucide-react';
import { authAPI } from '../services/api';

const InputField = ({ icon: Icon, name, type = 'text', placeholder, value, onChange }) => (
    <div className="relative">
        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <Icon size={20} />
        </span>
        <input
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            required
            className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-xl focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
        />
    </div>
);

export default function AuthPage() {
    const navigate = useNavigate();
    const [isLoginMode, setIsLoginMode] = useState(true); // 控制目前是登入還是註冊

    // 綁定表單狀態 (包含 API 需要的所有欄位)
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        phone: '',
        name: '',
        password: ''
    });

    // 處理輸入框改變
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    // 註冊的 API 呼叫
    const registerMutation = useMutation({
        mutationFn: authAPI.register,
        onSuccess: () => {
            alert('註冊成功！請登入');
            setIsLoginMode(true); // 註冊成功後自動切換到登入模式
            // 清空密碼，確保安全
            setFormData(prev => ({ ...prev, password: '' }));
        },
        onError: (error) => {
            const detail = error.response?.data?.detail;
            let errMsg = error.message;

            if (typeof detail === 'string') {
                errMsg = detail; // 一般錯誤字串
            } else if (Array.isArray(detail)) {
                errMsg = detail.map(err => err.msg).join('; '); // FastAPI 欄位驗證錯誤
            } else if (detail) {
                errMsg = JSON.stringify(detail); // 其他未知的物件格式
            }

            alert('註冊失敗：' + errMsg);
        }
    });

    // 登入的 API 呼叫 (目前暫定)
    const loginMutation = useMutation({
        mutationFn: authAPI.login,
        onSuccess: (data) => {
            alert('登入成功！');
            // 未來這裡要處理 Token 儲存
            navigate('/');
        },
        onError: (error) => {
            const detail = error.response?.data?.detail;
            let errMsg = error.message;

            if (typeof detail === 'string') {
                errMsg = detail;
            } else if (Array.isArray(detail)) {
                errMsg = detail.map(err => err.msg).join('; ');
            } else if (detail) {
                errMsg = JSON.stringify(detail);
            }

            alert('登入失敗：' + errMsg);
        }
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (isLoginMode) {
            // 登入送出 (通常只需要 email/username 和 password)
            loginMutation.mutate({
                username: formData.username,
                password: formData.password
            });
        } else {
            // 註冊送出 (完整 payload)
            registerMutation.mutate(formData);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-4">
            <div className="w-full max-w-md bg-white rounded-3xl shadow-xl p-8 animate-in fade-in zoom-in-95 duration-300">

                {/* LOGO 區塊 */}
                <div className="flex flex-col items-center mb-8">
                    <div className="w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200 mb-4">
                        <Wallet size={32} />
                    </div>
                    <h1 className="text-2xl font-bold text-gray-800">
                        {isLoginMode ? '歡迎回來' : '建立新帳號'}
                    </h1>
                    <p className="text-gray-500 text-sm mt-2">
                        {isLoginMode ? '請登入以繼續使用記帳服務' : '只需要幾個步驟就能開始記帳'}
                    </p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">

                    {/* 註冊模式才顯示的額外欄位 */}
                    {!isLoginMode && (
                        <>
                            <InputField icon={User} name="name" placeholder="真實姓名 (例如: Alice Chen)" value={formData.name} onChange={handleChange} />
                            <InputField icon={Mail} name="email" type="email" placeholder="電子信箱 (Email)" value={formData.email} onChange={handleChange} />
                            <InputField icon={Phone} name="phone" type="tel" placeholder="手機號碼" value={formData.phone} onChange={handleChange} />
                        </>
                    )}

                    {/* 登入與註冊共用的欄位 */}
                    <InputField icon={User} name="username" placeholder="使用者帳號 (Username)" value={formData.username} onChange={handleChange} />
                    <InputField icon={Lock} name="password" type="password" placeholder="密碼" value={formData.password} onChange={handleChange} />

                    {/* 送出按鈕 */}
                    <button
                        type="submit"
                        disabled={registerMutation.isPending || loginMutation.isPending}
                        className="w-full py-3.5 bg-blue-600 text-white rounded-xl font-bold text-lg hover:bg-blue-700 active:scale-[0.98] transition-all disabled:bg-blue-300 mt-2"
                    >
                        {registerMutation.isPending || loginMutation.isPending
                            ? '處理中...'
                            : (isLoginMode ? '登入' : '註冊')}
                    </button>
                </form>

                {/* 切換模式的按鈕 */}
                <div className="mt-6 text-center">
                    <span className="text-gray-500 text-sm">
                        {isLoginMode ? '還沒有帳號嗎？' : '已經有帳號了？'}
                    </span>
                    <button
                        type="button"
                        onClick={() => {
                            setIsLoginMode(!isLoginMode);
                            setFormData({
                                username: '',
                                email: '',
                                phone: '',
                                name: '',
                                password: ''
                            });
                        }}
                        className="ml-2 text-blue-600 font-bold text-sm hover:underline"
                    >
                        {isLoginMode ? '立即註冊' : '登入現有帳號'}
                    </button>
                </div>

            </div>
        </div>
    );
}