import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, UserPlus, Receipt, HandCoins, ArrowRight, Clock, CheckCircle, ListChecks, Search } from 'lucide-react';
import { groupAPI, userAPI } from '../services/api'; // 👉 記得引入 userAPI

export default function GroupDetailModal({ group, onClose, onNavigateToBill }) {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('members');

  // 👉 1. 防抖搜尋的 State 準備
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  const [selectedExpense, setSelectedExpense] = useState(null);
  const [settlementData, setSettlementData] = useState(null);
  const [settleMethod, setSettleMethod] = useState('cash');
  const [settleNotes, setSettleNotes] = useState('');

  if (!group) return null;

  // 👉 2. 防抖邏輯 (Debounce)：使用者停下手 500 毫秒後，才更新 debouncedSearch
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // 👉 3. 只有當 debouncedSearch 有字時，才去呼叫搜尋 API
  const { data: searchData, isFetching: isSearching } = useQuery({
    queryKey: ['usersSearch', debouncedSearch],
    queryFn: () => userAPI.searchUsers(debouncedSearch),
    enabled: debouncedSearch.length > 0 // 輸入框有字才發送請求
  });
  const searchResults = searchData?.users || [];

  // 原本的 Query...
  const { data: membersData, isLoading: isMembersLoading } = useQuery({
    queryKey: ['groupMembers', group.id],
    queryFn: () => groupAPI.getGroupMembers(group.id)
  });
  const members = Array.isArray(membersData) ? membersData : (membersData?.members || []);

  const { data: balanceData, isLoading: isBalancesLoading } = useQuery({
    queryKey: ['groupBalances', group.id],
    queryFn: () => groupAPI.getGroupBalances(group.id),
    enabled: activeTab === 'settlement'
  });

  const { data: expensesData, isLoading: isExpensesLoading } = useQuery({
    queryKey: ['groupExpenses', group.id],
    queryFn: () => groupAPI.getGroupExpenses(group.id),
    enabled: activeTab === 'history'
  });

  const { data: settlementsData, isLoading: isSettlementsLoading } = useQuery({
    queryKey: ['groupSettlements', group.id],
    queryFn: () => groupAPI.getSettlements(group.id),
    enabled: activeTab === 'repayments'
  });

  // 加入群組的 Mutation
  const addMemberMutation = useMutation({
    mutationFn: (userId) => groupAPI.addMemberToGroup({
      groupId: group.id,
      memberData: { role: 'member', user_ids: [userId] }
    }),
    onSuccess: () => {
      alert('加入成員成功！');
      queryClient.invalidateQueries({ queryKey: ['groupMembers', group.id] });
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      setSearchInput(''); // 清空搜尋框
    },
    onError: (error) => {
      alert('加入失敗：' + (error.response?.data?.detail || error.message));
    }
  });

  // 點擊搜尋結果時，直接把對方加入群組
  const handleSelectUser = (userId) => {
    if (window.confirm('確定要將此使用者加入群組嗎？')) {
      addMemberMutation.mutate(userId);
    }
  };

  const methodMap = { cash: '現金', bank_transfer: '轉帳', credit_card: '信用卡' };
  const statusMap = { pending: '處理中', completed: '已結清' };

  const settlementMutation = useMutation({
    mutationFn: groupAPI.createSettlement,
    onSuccess: () => {
      alert('還款成功！');
      queryClient.invalidateQueries({ queryKey: ['groupBalances', group.id] });
      queryClient.invalidateQueries({ queryKey: ['groupExpenses', group.id] });
      queryClient.invalidateQueries({ queryKey: ['groupSettlements', group.id] });
      setSettlementData(null);
      setSettleNotes('');
    },
    onError: (error) => alert('還款失敗：' + (error.response?.data?.detail || error.message))
  });

  const handleSettleSubmit = () => {
    const isSpecificExpense = !!settlementData.expense_id;
    const payload = {
      payer_id: settlementData.payer_id,
      receiver_id: settlementData.receiver_id,
      amount: settlementData.amount,
      method: settleMethod,
      group_id: group.id,
      expense_id: settlementData.expense_id,
      status: 'completed',
      notes: settleNotes.trim() || (isSpecificExpense ? '單筆還款' : '總額批次結算'),
      transaction_date: new Date().toISOString()
    };
    settlementMutation.mutate(payload);
  };

  return (
    <div className="fixed inset-0 bg-black/40 z-[100] flex justify-center items-end sm:items-center animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-md h-[85vh] sm:h-[600px] sm:rounded-3xl rounded-t-3xl flex flex-col shadow-2xl animate-in slide-in-from-bottom-10 sm:slide-in-from-bottom-4 duration-300">

        {/* --- Header --- */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100 shrink-0">
          <h2 className="text-xl font-bold text-gray-800">{group.name}</h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* --- Tabs --- */}
        <div className="flex border-b border-gray-100 px-2 overflow-x-auto shrink-0">
          {[
            { id: 'members', label: '成員', icon: UserPlus },
            { id: 'history', label: '記錄', icon: Clock },
            { id: 'settlement', label: '結算', icon: HandCoins },
            { id: 'repayments', label: '紀錄', icon: ListChecks }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap px-4 ${activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-50'
                }`}
            >
              <tab.icon size={16} /> {tab.label}
            </button>
          ))}
        </div>

        {/* --- 內容區域 --- */}
        <div className="flex-1 overflow-y-auto p-5 bg-gray-50/50">

          {/* 1. 成員分頁 */}
          {activeTab === 'members' && (
            <div className="space-y-4">

              {/* 👉 全新的搜尋輸入框 */}
              <div className="relative">
                <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                  <Search size={18} className="text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="搜尋使用者名稱來加入群組..."
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white border border-gray-200 rounded-xl outline-none text-sm transition-all focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              {/* 👉 搜尋結果選單 */}
              {debouncedSearch && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-lg overflow-hidden relative z-10">
                  {isSearching ? (
                    <div className="p-4 text-center text-sm text-gray-500">搜尋中...</div>
                  ) : searchResults.length > 0 ? (
                    <div className="max-h-48 overflow-y-auto">
                      {searchResults.map(user => (
                        <button
                          key={user.id}
                          onClick={() => handleSelectUser(user.id)}
                          disabled={addMemberMutation.isPending}
                          className="w-full flex items-center gap-3 p-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-0 transition-colors disabled:opacity-50"
                        >
                          <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm shrink-0">
                            {(user.name || user.username || "?").charAt(0).toUpperCase()}
                          </div>
                          <div className="flex-1 overflow-hidden">
                            <span className="font-bold text-gray-800 block truncate">{user.name || user.username}</span>
                            <span className="text-xs text-gray-400 block truncate">@{user.username}</span>
                          </div>
                          <UserPlus size={16} className="text-blue-500 shrink-0" />
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 text-center text-sm text-gray-500">找不到相符的使用者</div>
                  )}
                </div>
              )}

              {/* 原本的群組成員列表 */}
              <div className="pt-2">
                <h3 className="text-xs font-bold text-gray-400 uppercase mb-3 px-1">現有成員</h3>
                {isMembersLoading ? (
                  <div className="text-center py-4 text-gray-400">載入名單中...</div>
                ) : (
                  <div className="space-y-2">
                    {members.map(member => {
                      const memberId = member.id || member.user_id;
                      const memberName = member.name || member.username || member.user_name || "未知成員";
                      const username = member.username || member.user_name || "未知帳號";
                      const realName = member.name ? `(${member.name})` : "";
                      return (
                        <div key={memberId} className="flex justify-between items-center p-3 bg-white rounded-xl border border-gray-100 shadow-sm">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm">
                              {memberName.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <span className="font-medium text-gray-700 block">{username} <span className="text-gray-400 text-sm">{realName}</span></span>
                            </div>
                          </div>
                          {member.role === 'admin' && (
                            <span className="text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-md font-bold">管理員</span>
                          )}
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ... (2. 歷史記錄, 3. 結算, 4. 還款紀錄 分頁維持原樣，請參考上一版的代碼) ... */}

          {/* 2. 歷史記錄分頁 */}
          {activeTab === 'history' && (
            <div className="space-y-3">
              {isExpensesLoading ? (
                <div className="text-center py-10 text-gray-400">載入歷史帳單中...</div>
              ) : expensesData?.items && expensesData.items.length > 0 ? (
                expensesData.items.map(exp => (
                  console.log(exp),
                  <button key={exp.id} onClick={() => setSelectedExpense(exp)} className="w-full p-4 bg-white rounded-xl border border-gray-100 shadow-sm flex justify-between items-center hover:bg-gray-50 transition-colors active:scale-[0.98] text-left">
                    <div>
                      <h4 className="font-bold text-gray-800">{exp.description}</h4>
                      <p className="text-xs text-gray-500 mt-1">由 {exp.payer_name || exp.paid_by_id} 代墊</p>
                    </div>
                    <div className="text-lg font-bold text-blue-600">${Number(exp.amount).toFixed(0)}</div>
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
                balanceData.settlements.map((tx, idx) => (
                  <div key={idx} className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-100 shadow-sm">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-gray-700">{tx.from_user_name}</span>
                        <ArrowRight size={16} className="text-gray-300 mx-1" />
                        <span className="font-bold text-gray-700">{tx.to_user_name}</span>
                      </div>
                      <span className="text-red-500 font-bold text-sm">需給付 ${Number(tx.amount).toFixed(0)}</span>
                    </div>
                    <button onClick={() => setSettlementData({ payer_id: tx.from_user_id, receiver_id: tx.to_user_id, amount: tx.amount, expense_id: null })} className="bg-blue-50 text-blue-600 hover:bg-blue-100 px-4 py-2 rounded-lg font-bold text-sm transition-colors">
                      總結算
                    </button>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">大家都互不相欠，太棒了！</div>
              )}
            </div>
          )}

          {/* 4. 還款紀錄分頁 */}
          {activeTab === 'repayments' && (
            <div className="space-y-3">
              {isSettlementsLoading ? (
                <div className="text-center py-10 text-gray-400">載入還款紀錄中...</div>
              ) : settlementsData?.settlements && settlementsData.settlements.length > 0 ? (
                settlementsData.settlements.map((record) => (
                  <div key={record.id} className="p-4 bg-white rounded-xl border border-gray-100 shadow-sm flex flex-col gap-3">
                    <div className="flex justify-between items-center border-b border-gray-50 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-gray-700">{record.payer_name}</span>
                        <ArrowRight size={16} className="text-gray-300" />
                        <span className="font-bold text-gray-700">{record.receiver_name}</span>
                      </div>
                      <div className="text-lg font-bold text-green-600">+${Number(record.amount).toFixed(0)}</div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between items-center text-xs">
                        <div className="flex gap-2">
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-md font-medium">{methodMap[record.method] || record.method}</span>
                          <span className={`px-2 py-1 rounded-md font-bold ${record.status === 'completed' ? 'bg-green-50 text-green-600' : 'bg-orange-50 text-orange-600'}`}>{statusMap[record.status] || record.status}</span>
                        </div>
                        <span className="text-gray-400">{new Date(record.transaction_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">目前還沒有任何還款紀錄喔！</div>
              )}
            </div>
          )}

        </div>

        {/* --- 底部動作區塊 --- */}
        <div className="p-4 bg-white border-t border-gray-100 shrink-0">
          <button onClick={() => onNavigateToBill(group.id)} className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2">
            <Receipt size={20} /> 新增這群的帳單
          </button>
        </div>

      </div>

      {/* --- 單筆帳單詳細視窗 --- */}
      {selectedExpense && (
        <div className="fixed inset-0 bg-black/60 z-[110] flex justify-center items-center p-4 animate-in fade-in">
          <div className="bg-white w-full max-w-sm rounded-2xl p-6 shadow-xl animate-in zoom-in-95">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-800">{selectedExpense.description}</h3>
                <p className="text-sm text-gray-500 mt-1">{new Date(selectedExpense.created_at).toLocaleString()}</p>
              </div>
              <button onClick={() => setSelectedExpense(null)} className="text-gray-400 hover:bg-gray-100 p-1 rounded-full"><X size={20} /></button>
            </div>
            <div className="py-4 border-y border-gray-100 my-4 flex justify-between items-center">
              <span className="text-gray-600 font-medium">總金額</span>
              <span className="text-2xl font-bold text-blue-600">${Number(selectedExpense.amount).toFixed(0)}</span>
            </div>
            {selectedExpense.splits && selectedExpense.splits.length > 0 && (
              <div className="space-y-2 mb-6 bg-gray-50 p-4 rounded-xl">
                <h4 className="text-xs font-bold text-gray-400 uppercase mb-3">分攤詳情</h4>
                {selectedExpense.splits.map((split, idx) => {
                  const memberData = members.find(m => (m.id || m.user_id) === split.user_id);
                  const memberName = memberData ? (memberData.username) : "未知成員";
                  const isPayer = split.user_id === selectedExpense.paid_by_id;

                  return (
                    <div key={idx} className="flex justify-between items-center text-sm py-1 border-b border-gray-200/50 last:border-0">
                      <span className="text-gray-700">{memberName} {isPayer && "(代墊)"}</span>
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-gray-900">${Number(split.split_amount).toFixed(0)}</span>
                        {!isPayer && !split.is_settled ? (
                          <button onClick={() => setSettlementData({ payer_id: split.user_id, receiver_id: selectedExpense.paid_by_id, amount: split.split_amount, expense_id: selectedExpense.id })} className="bg-blue-600 text-white text-xs px-2 py-1 rounded">
                            還款
                          </button>
                        ) : !isPayer && split.is_settled ? (
                          <span className="text-green-500 flex items-center gap-1 text-xs"><CheckCircle size={12} /> 已還清</span>
                        ) : null}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            <button onClick={() => setSelectedExpense(null)} className="w-full bg-gray-900 text-white py-3 rounded-xl font-bold">關閉</button>
          </div>
        </div>
      )}

      {/* --- 還款確認表單視窗 --- */}
      {settlementData && (
        <div className="fixed inset-0 bg-black/70 z-[120] flex justify-center items-center p-4">
          <div className="bg-white w-full max-w-xs rounded-2xl p-6 shadow-2xl">
            <h3 className="text-lg font-bold text-gray-800 mb-4">確認還款資訊</h3>
            <div className="mb-4 text-center p-4 bg-gray-50 rounded-xl">
              <p className="text-sm text-gray-500 mb-1">本次結算金額</p>
              <p className="text-3xl font-bold text-red-500">${Number(settlementData.amount).toFixed(0)}</p>
            </div>
            <div className="space-y-3 mb-6">
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">還款方式</label>
                <select value={settleMethod} onChange={(e) => setSettleMethod(e.target.value)} className="w-full p-2 border border-gray-200 rounded-lg outline-none">
                  <option value="cash">現金 (Cash)</option>
                  <option value="bank_transfer">轉帳 (Bank Transfer)</option>
                  <option value="credit_card">信用卡</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-bold text-gray-500 mb-1">備註說明 (選填)</label>
                <input type="text" value={settleNotes} onChange={(e) => setSettleNotes(e.target.value)} placeholder={settlementData.expense_id ? "例如：還昨天的午餐錢" : "例如：五月份總結算"} className="w-full p-2 border border-gray-200 rounded-lg outline-none" />
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setSettlementData(null)} className="flex-1 py-2 bg-gray-100 text-gray-600 rounded-xl font-bold">取消</button>
              <button onClick={handleSettleSubmit} disabled={settlementMutation.isPending} className="flex-1 py-2 bg-blue-600 text-white rounded-xl font-bold disabled:bg-blue-300">
                {settlementMutation.isPending ? '處理中...' : '確認結清'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}