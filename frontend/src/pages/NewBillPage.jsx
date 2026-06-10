import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Calculator, FileText } from 'lucide-react';
import { groupAPI, billAPI } from '../services/api';
import EmptyGroupState from '../components/EmptyGroupState';
import PayerSelector from '../components/PayerSelector';
import SplitSection from '../components/SplitSection';

export default function NewBillPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  // --- 1. 抓取資料 ---
  const { data: groupsData, isLoading: isGroupsLoading } = useQuery({
    queryKey: ['groups'],
    queryFn: groupAPI.getGroups
  });
  const groups = groupsData?.groups || [];

  const urlGroupId = searchParams.get('groupId');
  const [activeGroupId, setActiveGroupId] = useState(urlGroupId || '');

  useEffect(() => {
    if (groups.length > 0 && !activeGroupId) {
      setActiveGroupId(groups[0].id);
    }
  }, [groups, activeGroupId]);

  const { data: membersData, isLoading: isMembersLoading } = useQuery({
    queryKey: ['groupMembers', activeGroupId],
    queryFn: () => groupAPI.getGroupMembers(activeGroupId),
    enabled: !!activeGroupId
  });
  const members = Array.isArray(membersData) ? membersData : (membersData?.members || []);

  // --- 2. 狀態管理 ---
  const [activePayerId, setActivePayerId] = useState('');
  const [totalAmount, setTotalAmount] = useState('');
  const [splitMode, setSplitMode] = useState('equal');
  const [description, setDescription] = useState('');
  const [exactAmounts, setExactAmounts] = useState({});

  useEffect(() => {
    if (members.length > 0) {
      const initialAmounts = members.reduce((acc, member) => ({ ...acc, [member.user_id]: '' }), {});
      setExactAmounts(initialAmounts);
      if (!activePayerId) setActivePayerId(members[0].user_id);
    }
  }, [members, activeGroupId]);

  // --- 3. 計算邏輯 ---
  const parsedTotal = parseFloat(totalAmount) || 0;
  const equalShare = parsedTotal > 0 ? (parsedTotal / (members.length || 1)).toFixed(0) : 0;
  const currentExactSum = Object.values(exactAmounts).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);
  const diff = parsedTotal - currentExactSum;
  
  const isSubmitDisabled = parsedTotal <= 0 || !description.trim() || (splitMode === 'exact' && diff !== 0) || !activePayerId;

  const handleExactAmountChange = (memberId, value) => {
    setExactAmounts(prev => ({ ...prev, [memberId]: value }));
  };

  // --- 4. API 提交 ---
  const createExpenseMutation = useMutation({
    mutationFn: billAPI.createExpense,
    onSuccess: () => {
      alert('記帳成功！');
      queryClient.invalidateQueries({ queryKey: ['groupExpenses'] });
      queryClient.invalidateQueries({ queryKey: ['groupBalances'] });
      queryClient.invalidateQueries({ queryKey: ['groupSettlements'] });
      navigate('/groups');
    },
    onError: (error) => alert('記帳失敗：' + (error.response?.data?.detail || error.message))
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
      splits: members.map(member => ({
        user_id: member.user_id,
        split_amount: splitMode === 'exact' ? (parseFloat(exactAmounts[member.user_id]) || 0) : 0
      }))
    };
    createExpenseMutation.mutate(payload);
  };

  // --- 5. 渲染畫面 ---
  if (!isGroupsLoading && groups.length === 0) return <EmptyGroupState />;

  return (
    <div className="max-w-md mx-auto space-y-4 animate-in fade-in pb-10">
      
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
      <PayerSelector 
        members={members} 
        isMembersLoading={isMembersLoading} 
        activePayerId={activePayerId} 
        setActivePayerId={setActivePayerId} 
      />

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

          {/* 分攤邏輯區塊 */}
          <SplitSection 
            members={members}
            splitMode={splitMode}
            setSplitMode={setSplitMode}
            exactAmounts={exactAmounts}
            handleExactAmountChange={handleExactAmountChange}
            equalShare={equalShare}
            parsedTotal={parsedTotal}
            diff={diff}
          />

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