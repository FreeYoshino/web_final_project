import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { X, UserPlus, Receipt, HandCoins, ArrowRight, Clock } from 'lucide-react';
import { useGroupStore } from '../store/groupStore';
import { groupAPI } from '../services/api';

export default function GroupDetailModal({ group, onClose, onNavigateToBill }) {
  const [activeTab, setActiveTab] = useState('members'); // 'members' | 'history' | 'settlement'
  const [newMemberName, setNewMemberName] = useState('');
  const [selectedExpense, setSelectedExpense] = useState(null);
  const { addMember } = useGroupStore();

  if (!group) return null;

  const { data: balanceData, isLoading: isBalancesLoading } = useQuery({
    // queryKey 包含 groupId，這樣切換不同群組時，快取才會是獨立的
    queryKey: ['groupBalances', group.id],
    // 呼叫我們在 api.js 寫好的函式，並傳入 groupId
    queryFn: () => groupAPI.getGroupBalances(group.id),
    // 只有在切換到「結算」分頁時才去抓資料，節省資源
    enabled: activeTab === 'settlement'
  });

  const { data: expensesData, isLoading: isExpensesLoading } = useQuery({
    queryKey: ['groupExpenses', group.id],
    queryFn: () => groupAPI.getGroupExpenses(group.id),
    enabled: activeTab === 'history' // 只有切換到歷史記錄才去抓資料
  });
  // --- 1. 新增成員處理 ---
  const handleAddMember = (e) => {
    e.preventDefault();
    if (!newMemberName.trim()) return;
    addMember(group.id, newMemberName);
    setNewMemberName('');
  };

  return (
    // 外層黑色半透明遮罩
    <div className="fixed inset-0 bg-black/40 z-[100] flex justify-center items-end sm:items-center animate-in fade-in duration-200">

      {/* 白底視窗本體 */}
      <div className="bg-white w-full max-w-md h-[85vh] sm:h-[600px] sm:rounded-3xl rounded-t-3xl flex flex-col shadow-2xl animate-in slide-in-from-bottom-10 sm:slide-in-from-bottom-4 duration-300">

        {/* --- Header --- */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-800">{group.name}</h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* --- Tabs 導覽列 --- */}
        <div className="flex border-b border-gray-100 px-2">
          {[
            { id: 'members', label: '成員', icon: UserPlus },
            { id: 'history', label: '記錄', icon: Clock },
            { id: 'settlement', label: '結算', icon: HandCoins }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2 ${activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-50'
                }`}
            >
              <tab.icon size={16} /> {tab.label}
            </button>
          ))}
        </div>

        {/* --- Tab 內容區域 --- */}
        <div className="flex-1 overflow-y-auto p-5 bg-gray-50/50">

          {/* 1. 成員分頁 */}
          {activeTab === 'members' && (
            <div className="space-y-4">
              <form onSubmit={handleAddMember} className="flex gap-2">
                <input
                  type="text"
                  placeholder="輸入新成員名稱..."
                  value={newMemberName}
                  onChange={(e) => setNewMemberName(e.target.value)}
                  className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                />
                <button type="submit" disabled={!newMemberName.trim()} className="bg-gray-900 text-white px-4 py-2 rounded-xl disabled:bg-gray-300">
                  加入
                </button>
              </form>
              <div className="space-y-2">
                {group.members.map(member => (
                  <div key={member.id} className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100 shadow-sm">
                    <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm">
                      {member.name.charAt(0)}
                    </div>
                    <span className="font-medium text-gray-700">{member.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. 歷史記錄分頁 */}
          {activeTab === 'history' && (
            <div className="space-y-3">
              {isExpensesLoading ? (
                <div className="text-center py-10 text-gray-400">載入歷史帳單中...</div>
              ) : expensesData?.items && expensesData.items.length > 0 ? (
                expensesData.items.map(exp => (
                  <button 
                    key={exp.id} 
                    onClick={() => setSelectedExpense(exp)}
                    className="w-full p-4 bg-white rounded-xl border border-gray-100 shadow-sm flex justify-between items-center hover:bg-gray-50 transition-colors active:scale-[0.98] text-left"
                  >
                    <div>
                      <h4 className="font-bold text-gray-800">{exp.description}</h4>
                      <p className="text-xs text-gray-500 mt-1">
                        由 {exp.payer_name || exp.paid_by_id} 代墊
                      </p>
                    </div>
                    <div className="text-lg font-bold text-blue-600">
                      ${Number(exp.amount).toFixed(0)}
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">目前還沒有記帳記錄喔！</div>
              )}
            </div>
          )}

          {/* 3. 結算分頁 */}
          {activeTab === 'settlement' && (
            <div className="space-y-3">
              {isBalancesLoading ? (
                <div className="text-center py-10 text-gray-400">計算中，請稍候...</div>
              ) : balanceData?.settlements?.length > 0 ? (
                // 拿後端回傳的 settlements 陣列來 map
                balanceData.settlements.map((tx, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
                    <div className="flex items-center gap-2 flex-1">
                      {/* 對應 API 回傳的欄位名稱 */}
                      <span className="font-bold text-gray-700">{tx.from_user_name}</span>
                      <ArrowRight size={16} className="text-gray-300 mx-1" />
                      <span className="font-bold text-gray-700">{tx.to_user_name}</span>
                    </div>
                    <div className="bg-red-50 text-red-600 px-3 py-1 rounded-lg font-bold text-sm border border-red-100">
                      {/* 將又臭又長的數字格式化為沒有小數點的整數 */}
                      給 ${Number(tx.amount).toFixed(0)}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">大家都互不相欠，太棒了！</div>
              )}
            </div>
          )}
        </div>

        {/* --- 底部動作區塊 --- */}
        <div className="p-4 bg-white border-t border-gray-100">
          <button
            onClick={() => onNavigateToBill(group.id)}
            className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 hover:bg-blue-700 transition-colors"
          >
            <Receipt size={20} /> 新增這群的帳單
          </button>
        </div>

      </div>
      {/* 👉 4. 單筆帳單詳細視窗 (疊在原本的 Modal 上面) */}
      {selectedExpense && (
        <div className="fixed inset-0 bg-black/60 z-[110] flex justify-center items-center p-4 animate-in fade-in">
          <div className="bg-white w-full max-w-sm rounded-2xl p-6 shadow-xl animate-in zoom-in-95 duration-200">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-800">{selectedExpense.description}</h3>
                <p className="text-sm text-gray-500 mt-1">
                  {new Date(selectedExpense.created_at).toLocaleString()}
                </p>
              </div>
              <button onClick={() => setSelectedExpense(null)} className="text-gray-400 hover:bg-gray-100 p-1 rounded-full">
                <X size={20} />
              </button>
            </div>
            
            <div className="py-4 border-y border-gray-100 my-4 flex justify-between items-center">
              <span className="text-gray-600 font-medium">總金額</span>
              <span className="text-2xl font-bold text-blue-600">${Number(selectedExpense.amount).toFixed(0)}</span>
            </div>

            <div className="mb-6 text-sm text-gray-600">
              <span className="font-bold text-gray-800">
                {selectedExpense.payer_name || selectedExpense.paid_by_id}
              </span> 先行代墊了這筆款項。
            </div>

            {selectedExpense.splits && selectedExpense.splits.length > 0 ? (
              <div className="space-y-2 mb-6 bg-gray-50 p-4 rounded-xl">
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-xs font-bold text-gray-400 uppercase">分攤詳情</h4>
                  <span className="text-xs font-bold text-blue-500 bg-blue-50 px-2 py-1 rounded-md">
                    {selectedExpense.split_type === 'EQUAL' ? '平分' : '精確'}
                  </span>
                </div>
                {selectedExpense.splits.map((split, idx) => {
                  // 👉 利用 group.members 來把 UUID 轉換成真實名字
                  const memberName = group.members.find(m => m.id === split.user_id)?.name || "未知成員";
                  
                  return (
                    <div key={idx} className="flex justify-between text-sm">
                      <span className="text-gray-700">{memberName}</span>
                      <span className="font-medium text-gray-900">${Number(split.split_amount).toFixed(0)}</span>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center text-sm text-gray-400 mb-6 bg-gray-50 p-4 rounded-xl">
                此 API 未包含詳細分攤名單 (Splits)
              </div>
            )}

            <button 
              onClick={() => setSelectedExpense(null)}
              className="w-full bg-gray-900 text-white py-3 rounded-xl font-bold hover:bg-gray-800 transition-colors"
            >
              關閉
            </button>
          </div>
        </div>
      )}
    </div>
  );
}