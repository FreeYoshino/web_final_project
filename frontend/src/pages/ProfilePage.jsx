import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { User, LogOut, Settings, Shield, Bell } from 'lucide-react';

export default function ProfilePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // 登出邏輯
  const handleLogout = () => {
    const isConfirmed = window.confirm('確定要登出嗎？');

    if (isConfirmed) {
      // 1. 刪除瀏覽器裡的 Token
      localStorage.removeItem('token');

      // 2. 清空 React Query 的所有快取
      queryClient.clear();

      // 3. 跳轉回登入頁面
      navigate('/login', { replace: true });
    }
  };

  return (
    <div className="max-w-md mx-auto space-y-6 animate-in fade-in duration-300 mt-4">

      {/* 頂部標題 */}
      <h1 className="text-2xl font-bold text-gray-800 px-1">設定</h1>

      {/* 用戶資訊卡片 */}
      <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 flex items-center gap-4">
        <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center shrink-0">
          <User size={32} />
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-800">我的帳號</h2>
          <p className="text-sm text-gray-500 mt-1">管理您的個人資訊與偏好設定</p>
        </div>
      </div>

      {/* 設定選單清單 */}
      <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
        <button className="w-full flex items-center gap-4 p-4 border-b border-gray-50 hover:bg-gray-50 transition-colors text-left">
          <div className="w-10 h-10 bg-gray-50 text-gray-600 rounded-xl flex items-center justify-center shrink-0">
            <Settings size={20} />
          </div>
          <span className="font-bold text-gray-700 flex-1">一般設定</span>
        </button>

        <button className="w-full flex items-center gap-4 p-4 border-b border-gray-50 hover:bg-gray-50 transition-colors text-left">
          <div className="w-10 h-10 bg-gray-50 text-gray-600 rounded-xl flex items-center justify-center shrink-0">
            <Shield size={20} />
          </div>
          <span className="font-bold text-gray-700 flex-1">帳號安全</span>
        </button>

        <button className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors text-left">
          <div className="w-10 h-10 bg-gray-50 text-gray-600 rounded-xl flex items-center justify-center shrink-0">
            <Bell size={20} />
          </div>
          <span className="font-bold text-gray-700 flex-1">通知設定</span>
        </button>
      </div>

      {/* 登出按鈕 */}
      <button
        onClick={handleLogout}
        className="w-full bg-red-50 text-red-600 hover:bg-red-100 py-4 rounded-2xl font-bold flex items-center justify-center gap-2 transition-colors active:scale-[0.98]"
      >
        <LogOut size={20} />
        登出帳號
      </button>

    </div>
  );
}