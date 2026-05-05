import { useState } from 'react';
import { X, UserPlus, Receipt, HandCoins, ArrowRight, Clock } from 'lucide-react';
import { useGroupStore } from '../store/groupStore';

export default function GroupDetailModal({ group, onClose, onNavigateToBill }) {
  const [activeTab, setActiveTab] = useState('members'); // 'members' | 'history' | 'settlement'
  const [newMemberName, setNewMemberName] = useState('');
  const { addMember } = useGroupStore();

  if (!group) return null;

  // --- 1. 新增成員處理 ---
  const handleAddMember = (e) => {
    e.preventDefault();
    if (!newMemberName.trim()) return;
    addMember(group.id, newMemberName);
    setNewMemberName('');
  };

  // --- 2. 結算演算法 (大魔王核心) ---
  const calculateSettlements = () => {
    // a. 計算每個人的淨餘額 (Net Balance)
    // 正數代表「別人欠他錢」，負數代表「他欠別人錢」
    const balances = {};
    group.members.forEach(m => balances[m.id] = 0);

    // 這裡假設未來的 expense 資料結構長這樣：
    // { id: 'e1', title: '午餐', amount: 300, payerId: 'u1', shares: { 'u1': 100, 'u2': 100, 'u3': 100 } }
    (group.expenses || []).forEach(expense => {
      // 代墊者先拿到正數餘額 (因為他付了整筆錢)
      balances[expense.payerId] += expense.amount;
      // 每個人根據應分攤的金額扣除餘額
      Object.entries(expense.shares).forEach(([memberId, shareAmount]) => {
        balances[memberId] -= shareAmount;
      });
    });

    // b. 分出「欠錢的人(Debtors)」和「等收錢的人(Creditors)」
    let debtors = [];
    let creditors = [];
    Object.entries(balances).forEach(([id, balance]) => {
      if (balance < -0.01) debtors.push({ id, amount: Math.abs(balance) }); // 欠錢 (轉為正數方便計算)
      else if (balance > 0.01) creditors.push({ id, amount: balance });     // 收錢
    });

    // c. 互相抵銷 (貪婪配對)
    const transactions = [];
    let dIndex = 0;
    let cIndex = 0;

    while (dIndex < debtors.length && cIndex < creditors.length) {
      let debtor = debtors[dIndex];
      let creditor = creditors[cIndex];
      
      // 找出這筆交易要還多少 (取兩者中較小的金額)
      let settleAmount = Math.min(debtor.amount, creditor.amount);
      
      transactions.push({
        from: group.members.find(m => m.id === debtor.id)?.name || '未知',
        to: group.members.find(m => m.id === creditor.id)?.name || '未知',
        amount: Math.round(settleAmount)
      });

      // 扣除已經配對的金額
      debtor.amount -= settleAmount;
      creditor.amount -= settleAmount;

      if (debtor.amount < 0.01) dIndex++;
      if (creditor.amount < 0.01) cIndex++;
    }

    return transactions;
  };

  const settlements = calculateSettlements();

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
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2 ${
                activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-50'
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
              {group.expenses && group.expenses.length > 0 ? (
                group.expenses.map(exp => (
                  <div key={exp.id} className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm flex justify-between items-center">
                    <div>
                      <h4 className="font-bold text-gray-800">{exp.title}</h4>
                      <p className="text-xs text-gray-500 mt-1">
                        由 {group.members.find(m => m.id === exp.payerId)?.name} 代墊
                      </p>
                    </div>
                    <div className="text-lg font-bold text-blue-600">${exp.amount}</div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">目前還沒有記帳記錄喔！</div>
              )}
            </div>
          )}

          {/* 3. 結算分頁 */}
          {activeTab === 'settlement' && (
            <div className="space-y-3">
              {settlements.length > 0 ? (
                settlements.map((tx, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
                    <div className="flex items-center gap-2 flex-1">
                      <span className="font-bold text-gray-700">{tx.from}</span>
                      <ArrowRight size={16} className="text-gray-300 mx-1" />
                      <span className="font-bold text-gray-700">{tx.to}</span>
                    </div>
                    <div className="bg-red-50 text-red-600 px-3 py-1 rounded-lg font-bold text-sm border border-red-100">
                      給 ${tx.amount}
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
    </div>
  );
}