import { NavLink } from 'react-router-dom';
import { Home, Receipt, User } from 'lucide-react';

export default function TopNavbar() {
  // 使用 flex-1 讓每個按鈕自動均分寬度，並稍微調整點擊狀態的樣式
  const navItemClass = ({ isActive }) =>
    `flex flex-1 flex-col items-center justify-center py-3 text-sm gap-1 transition-colors border-b-2 ${
      isActive 
        ? 'text-blue-600 border-blue-600 bg-blue-50/50' 
        : 'text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50'
    }`;

  return (
    // sticky top-0 讓導覽列固定在網頁最上方
    <nav className="sticky top-0 w-full bg-white border-b border-gray-200 z-50 shadow-sm flex">
      <NavLink to="/" className={navItemClass}>
        <Home size={20} />
        <span className="font-medium">群組</span>
      </NavLink>
      
      <NavLink to="/new-bill" className={navItemClass}>
        <Receipt size={20} />
        <span className="font-medium">記帳</span>
      </NavLink>
      
      <NavLink to="/profile" className={navItemClass}>
        <User size={20} />
        <span className="font-medium">設定</span>
      </NavLink>
    </nav>
  );
}