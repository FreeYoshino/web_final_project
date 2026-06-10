import { Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function EmptyGroupState() {
  const navigate = useNavigate();
  
  return (
    <div className="max-w-md mx-auto mt-10 animate-in fade-in">
      <div className="text-center py-20 bg-white rounded-3xl border border-gray-100 shadow-sm">
        <div className="w-16 h-16 bg-gray-50 text-gray-400 rounded-full flex items-center justify-center mx-auto mb-4">
          <Users size={32} />
        </div>
        <h3 className="text-lg font-bold text-gray-800">還沒有任何群組</h3>
        <p className="text-gray-500 mt-2 mb-6">記帳前，必須先建立一個群組喔！</p>
        <button 
          onClick={() => navigate('/groups')}
          className="bg-blue-600 text-white px-6 py-2.5 rounded-xl font-bold hover:bg-blue-700 transition-colors"
        >
          回首頁建立群組
        </button>
      </div>
    </div>
  );
}