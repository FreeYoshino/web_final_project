import { useState } from 'react';
import { Calculator, CheckCircle2, AlertCircle } from 'lucide-react';
import { useGroupStore } from '../store/groupStore';
// 假資料：模擬目前群組內的成員
const MOCK_MEMBERS = [
  { id: 1, name: 'A (你自己)' },
  { id: 2, name: '室友 B' },
  { id: 3, name: '室友 C' },
];

export default function NewBillPage() {
  // --- 狀態管理 (State) ---
  const { activeGroupId, setActiveGroup, activePayerId, setActivePayer, groups, getActiveGroup } = useGroupStore();

  const currentGroup = getActiveGroup();
  const members = currentGroup?.members || [];

  const [totalAmount, setTotalAmount] = useState('');
  const [splitMode, setSplitMode] = useState('equal'); // 'equal' | 'exact'
  
  // 紀錄精確模式下，每個人的分攤金額。預設為 0
  const [exactAmounts, setExactAmounts] = useState(
    MOCK_MEMBERS.reduce((acc, member) => ({ ...acc, [member.id]: '' }), {})
  );

  // --- 計算邏輯 ---
  const parsedTotal = parseFloat(totalAmount) || 0;

  // 1. 平分模式計算
  const equalShare = parsedTotal > 0 ? (parsedTotal / MOCK_MEMBERS.length).toFixed(0) : 0;

  // 2. 精確模式防呆計算
  const currentExactSum = Object.values(exactAmounts).reduce(
    (sum, val) => sum + (parseFloat(val) || 0), 
    0
  );
  const diff = parsedTotal - currentExactSum;
  
  // 判斷表單是否可以送出
  const isSubmitDisabled = 
    parsedTotal <= 0 || 
    (splitMode === 'exact' && diff !== 0);

  // --- 處理輸入變更 ---
  const handleExactAmountChange = (memberId, value) => {
    setExactAmounts(prev => ({
      ...prev,
      [memberId]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`送出成功！總額：${parsedTotal}，模式：${splitMode}`);
    // 這裡之後會串接 React Query 和 FastAPI
  };

  return (
    <div className="max-w-md mx-auto space-y-4">
      {/* 選擇群組卡片 */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <label className="block text-xs font-bold text-gray-400 uppercase mb-2">選擇群組</label>
        <select 
          value={activeGroupId}
          onChange={(e) => setActiveGroup(e.target.value)}
          className="w-full p-2 bg-gray-50 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
        >
          {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
        </select>
      </div>

      {/* 選擇代墊人卡片 */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <label className="block text-xs font-bold text-gray-400 uppercase mb-2">誰先代墊的？</label>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {members.map(m => (
            <button
              key={m.id}
              onClick={() => setActivePayer(m.id)}
              className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-all ${
                activePayerId === m.id 
                  ? 'bg-blue-600 text-white shadow-md' 
                  : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              {m.name}
            </button>
          ))}
        </div>
      </div>
    <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 max-w-md mx-auto mt-4">
      <div className="flex items-center gap-2 mb-6 text-gray-800">
        <Calculator className="text-blue-600" />
        <h1 className="text-xl font-bold">新增記帳</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* 1. 總金額輸入 */}
        <div>
          <label className="block text-sm font-medium text-gray-500 mb-1">輸入總金額</label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold">$</span>
            <input
              type="number"
              value={totalAmount}
              onChange={(e) => setTotalAmount(e.target.value)}
              placeholder="0"
              className="w-full text-3xl font-bold pl-10 pr-4 py-3 bg-gray-50 border-transparent rounded-xl focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
            />
          </div>
        </div>

        {/* 2. 模式切換 Toggle */}
        <div className="flex p-1 bg-gray-100 rounded-lg">
          <button
            type="button"
            onClick={() => setSplitMode('equal')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
              splitMode === 'equal' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            平分 (Equal)
          </button>
          <button
            type="button"
            onClick={() => setSplitMode('exact')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${
              splitMode === 'exact' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            精確分攤 (Exact)
          </button>
        </div>

        {/* 3. 動態分攤清單 */}
        <div className="space-y-3">
          {MOCK_MEMBERS.map((member) => (
            <div key={member.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
              <span className="font-medium text-gray-700">{member.name}</span>
              
              {splitMode === 'equal' ? (
                // 平分模式：唯讀顯示
                <span className="text-gray-600 font-medium">${equalShare}</span>
              ) : (
                // 精確模式：輸入框
                <div className="flex items-center gap-1">
                  <span className="text-gray-400">$</span>
                  <input
                    type="number"
                    value={exactAmounts[member.id]}
                    onChange={(e) => handleExactAmountChange(member.id, e.target.value)}
                    className="w-20 text-right font-medium p-1 border-b-2 border-gray-200 focus:border-blue-500 bg-transparent outline-none"
                    placeholder="0"
                  />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* 4. 精確模式的防呆提示 */}
        {splitMode === 'exact' && parsedTotal > 0 && (
          <div className={`flex items-center justify-center gap-2 text-sm p-3 rounded-lg ${
            diff === 0 ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
          }`}>
            {diff === 0 ? (
              <><CheckCircle2 size={18} /> 分攤金額完全吻合！</>
            ) : (
              <><AlertCircle size={18} /> 
                {diff > 0 ? `尚有 $${diff} 未分配` : `超過了 $${Math.abs(diff)}`}
              </>
            )}
          </div>
        )}

        {/* 5. 送出按鈕 */}
        <button
          type="submit"
          disabled={isSubmitDisabled}
          className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
            isSubmitDisabled 
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]'
          }`}
        >
          確認記帳
        </button>
      </form>
    </div>
  </div>
  );
}