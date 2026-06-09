import { useState } from 'react';

export default function SettlementFormModal({ data, onClose, onSubmit, isPending }) {
  
    const [settleMethod, setSettleMethod] = useState('cash');
  const [settleNotes, setSettleNotes] = useState('');

  if (!data) return null;

  // 點擊確認時，將子組件的表單資料傳回給父組件
  const handleSubmit = () => {
    onSubmit(settleMethod, settleNotes);
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-[120] flex justify-center items-center p-4 animate-in fade-in">
      <div className="bg-white w-full max-w-xs rounded-2xl p-6 shadow-2xl animate-in zoom-in-95">
        <h3 className="text-lg font-bold text-gray-800 mb-4">確認還款資訊</h3>
        
        <div className="mb-4 text-center p-4 bg-gray-50 rounded-xl">
          <p className="text-sm text-gray-500 mb-1">本次結算金額</p>
          <p className="text-3xl font-bold text-red-500">${Number(data.amount).toFixed(0)}</p>
        </div>
        
        <div className="space-y-3 mb-6">
          <div>
            <label className="block text-xs font-bold text-gray-500 mb-1">還款方式</label>
            <select 
              value={settleMethod} 
              onChange={(e) => setSettleMethod(e.target.value)} 
              className="w-full p-2 border border-gray-200 rounded-lg outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            >
              <option value="cash">現金 (Cash)</option>
              <option value="bank_transfer">轉帳 (Bank Transfer)</option>
              <option value="credit_card">信用卡</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-500 mb-1">備註說明 (選填)</label>
            <input 
              type="text" 
              value={settleNotes} 
              onChange={(e) => setSettleNotes(e.target.value)} 
              placeholder={data.expense_id ? "例如：還昨天的午餐錢" : "例如：五月份總結算"} 
              className="w-full p-2 border border-gray-200 rounded-lg outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500" 
            />
          </div>
        </div>
        
        <div className="flex gap-2">
          <button 
            onClick={onClose} 
            className="flex-1 py-2 bg-gray-100 text-gray-600 hover:bg-gray-200 rounded-xl font-bold transition-colors"
          >
            取消
          </button>
          <button 
            onClick={handleSubmit} 
            disabled={isPending} 
            className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold disabled:bg-blue-300 transition-colors"
          >
            {isPending ? '處理中...' : '確認結清'}
          </button>
        </div>
      </div>
    </div>
  );
}