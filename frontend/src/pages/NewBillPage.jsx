import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Calculator, CheckCircle2, AlertCircle, FileText, Users } from 'lucide-react';
import { groupAPI, billAPI } from '../services/api';

export default function NewBillPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  // --- 1. 抓取真實群組資料 ---
  const { data: groupsData, isLoading: isGroupsLoading } = useQuery({
    queryKey: ['groups'],
    queryFn: groupAPI.getGroups
  });
  const groups = groupsData?.groups || [];

  // --- 2. 決定目前選擇的群組 ---
  // 優先使用網址列帶過來的 groupId (例如從群組詳細頁點過來)，否則預設選第一個群組
  const urlGroupId = searchParams.get('groupId');
  const [activeGroupId, setActiveGroupId] = useState(urlGroupId || groups[0]?.id || '');

  // 當 groups 載入完成，如果網址沒有指定，就預設選第一個
  useEffect(() => {
    if (groups.length > 0 && !activeGroupId) {
      setActiveGroupId(groups[0].id);
    }
  }, [groups, activeGroupId]);

  // --- 3. 根據選擇的群組，抓取真實成員名單 ---
  const { data: membersData, isLoading: isMembersLoading } = useQuery({
    queryKey: ['groupMembers', activeGroupId],
    queryFn: () => groupAPI.getGroupMembers(activeGroupId),
    enabled: !!activeGroupId // 有 activeGroupId 才去抓
  });
  const members = Array.isArray(membersData) ? membersData : (membersData?.members || []);

  // --- 狀態管理 (State) ---
  const [activePayerId, setActivePayerId] = useState('');
  const [totalAmount, setTotalAmount] = useState('');
  const [splitMode, setSplitMode] = useState('equal'); // 'equal' | 'exact'
  const [description, setDescription] = useState('');
  const [exactAmounts, setExactAmounts] = useState({});

  // 當成員名單載入完成後，初始化分攤金額和預設代墊人
  useEffect(() => {
    if (members.length > 0) {
      // 初始化精確分攤為 0
      const initialAmounts = members.reduce((acc, member) => ({ ...acc, [member.user_id]: '' }), {});
      setExactAmounts(initialAmounts);
      
      // 預設代墊人為第一個成員
      if (!activePayerId) {
        setActivePayerId(members[0].user_id);
      }
    }
  }, [members, activeGroupId]); // activeGroupId 改變時也重新初始化


  // --- 空群組的保護畫面 ---
  if (!isGroupsLoading && groups.length === 0) {
    return (
      <div className="max-w-md mx-auto mt-10">
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

  // --- 計算邏輯 ---
  const parsedTotal = parseFloat(totalAmount) || 0;
  const equalShare = parsedTotal > 0 ? (parsedTotal / (members.length || 1)).toFixed(0) : 0;
  
  const currentExactSum = Object.values(exactAmounts).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);
  const diff = parsedTotal - currentExactSum;
  
  const isSubmitDisabled = parsedTotal <= 0 || !description.trim() || (splitMode === 'exact' && diff !== 0) || !activePayerId;

  // --- 處理輸入變更 ---
  const handleExactAmountChange = (memberId, value) => {
    setExactAmounts(prev => ({ ...prev, [memberId]: value }));
  };

  const createExpenseMutation = useMutation({
    mutationFn: billAPI.createExpense,
    onSuccess: () => {
      alert('記帳成功！');
      queryClient.invalidateQueries({ queryKey: ['groupExpenses'] });
      queryClient.invalidateQueries({ queryKey: ['groupBalances'] });
      queryClient.invalidateQueries({ queryKey: ['groupSettlements'] });
      navigate('/groups'); // 記帳完跳回首頁
    },
    onError: (error) => {
      alert('記帳失敗：' + (error.response?.data?.detail || error.message));
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();

    const payload = {
      description: description.trim(),
      amount: parsedTotal,
      paid_by_id: activePayerId,
      group_id: activeGroupId,
      category: "other", 
      split_type: splitMode === 'equal' ? 'EQUAL' : 'EXACT',
      expense_date: new Date().toISOString(), 
      splits: members.map(member => {
        const mId = member.user_id;
        return {
          user_id: mId,
          // 如果是平分模式，後端要求送 0 還是 equalShare？ 
          // 根據你給的 API 範例，平分模式是送 0。
          split_amount: splitMode === 'exact' ? (parseFloat(exactAmounts[mId]) || 0) : 0
        };
      })
    };

    createExpenseMutation.mutate(payload);
  };

  return (
    <div className="max-w-md mx-auto space-y-4 animate-in fade-in">
      
      {/* 選擇群組卡片 */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <label className="block text-xs font-bold text-gray-400 uppercase mb-2">選擇群組</label>
        {isGroupsLoading ? (
           <div className="text-sm text-gray-500 py-2">載入群組中...</div>
        ) : (
          <select 
            value={activeGroupId}
            onChange={(e) => setActiveGroupId(e.target.value)}
            className="w-full p-2 bg-gray-50 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
          >
            {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
          </select>
        )}
      </div>

      {/* 選擇代墊人卡片 */}
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <label className="block text-xs font-bold text-gray-400 uppercase mb-2">誰先代墊的？</label>
        {isMembersLoading ? (
           <div className="text-sm text-gray-500 py-2">載入成員中...</div>
        ) : members.length === 0 ? (
           <div className="text-sm text-red-500 py-2">此群組尚無成員，請先至首頁加入成員。</div>
        ) : (
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            {members.map(m => {
              const mId = m.id || m.user_id;
              const mName = m.name || m.username || m.user_name || "未知";
              return (
                <button
                  key={mId}
                  onClick={() => setActivePayerId(mId)}
                  className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                    activePayerId === mId 
                      ? 'bg-blue-600 text-white shadow-md' 
                      : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                  }`}
                >
                  {mName}
                </button>
              )
            })}
          </div>
        )}
      </div>

      {/* 記帳表單主體 */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 max-w-md mx-auto mt-4">
        <div className="flex items-center gap-2 mb-6 text-gray-800">
          <Calculator className="text-blue-600" />
          <h1 className="text-xl font-bold">新增記帳</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          
          {/* 項目名稱 */}
          <div>
            <label className="block text-sm font-medium text-gray-500 mb-1">項目名稱</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
                <FileText size={20} />
              </span>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="例如：晚餐、飲料、水電費"
                className="w-full text-lg pl-12 pr-4 py-3 bg-gray-50 border-transparent rounded-xl focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
              />
            </div>
          </div>

          {/* 總金額輸入 */}
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

          {/* 模式切換 Toggle */}
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

          {/* 動態分攤清單 */}
          <div className="space-y-3">
            {members.map((member) => {
               const mId = member.user_id;
               const mName = member.name || member.username || member.user_name || "未知";
               
               return (
                <div key={mId} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                  <span className="font-medium text-gray-700">{mName}</span>
                  
                  {splitMode === 'equal' ? (
                    <span className="text-gray-600 font-medium">${equalShare}</span>
                  ) : (
                    <div className="flex items-center gap-1">
                      <span className="text-gray-400">$</span>
                      <input
                        type="number"
                        value={exactAmounts[mId] ?? ''}
                        onChange={(e) => handleExactAmountChange(mId, e.target.value)}
                        className="w-20 text-right font-medium p-1 border-b-2 border-gray-200 focus:border-blue-500 bg-transparent outline-none"
                        placeholder="0"
                      />
                    </div>
                  )}
                </div>
               )
            })}
          </div>

          {/* 精確模式的防呆提示 */}
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

          {/* 送出按鈕 */}
          <button
            type="submit"
            disabled={isSubmitDisabled || createExpenseMutation.isPending || members.length === 0}
            className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
              (isSubmitDisabled || members.length === 0)
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]'
            }`}
          >
            {createExpenseMutation.isPending ? '處理中...' : '確認記帳'}
          </button>
        </form>
      </div>
    </div>
  );
}