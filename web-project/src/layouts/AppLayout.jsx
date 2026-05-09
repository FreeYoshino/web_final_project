import { Outlet } from 'react-router-dom';
import TopNavbar from '../components/TopNavbar';

export default function AppLayout() {
  return (
    
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans flex flex-col">
      
      <TopNavbar />

      {/* 主要內容區域：我們還是可以加上 max-w-md 或 max-w-lg 讓內容在電腦大螢幕上不會過度展開，但沒有邊框 */}
      <main className="flex-1 w-full max-w-lg mx-auto p-4 sm:p-6">
        <Outlet />
      </main>
      
    </div>
  );
}