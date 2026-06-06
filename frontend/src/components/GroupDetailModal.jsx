import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, UserPlus, Receipt, HandCoins, ArrowRight, Clock, CheckCircle, ListChecks } from 'lucide-react';
import { useGroupStore } from '../store/groupStore';
import { groupAPI } from '../services/api';

export default function GroupDetailModal({ group, onClose, onNavigateToBill }) {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('members');
  const [newMemberName, setNewMemberName] = useState('');
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [settlementData, setSettlementData] = useState(null); 
  const [settleMethod, setSettleMethod] = useState('cash');
  const [settleNotes, setSettleNotes] = useState('');
  const { addMember } = useGroupStore();

  if (!group) return null;

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

  const methodMap = {
    cash: '現金',
    bank_transfer: '轉帳',
    credit_card: '信用卡'
  };

  const statusMap = {
    pending: '處理中',
    completed: '已結清'
  };

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
    onError: (error) => {
      alert('還款失敗：' + (error.response?.data?.detail || error.message));
    }
  });

  const handleAddMember = (e) => {
    e.preventDefault();
    if (!newMemberName.trim()) return;
    addMember(group.id, newMemberName);
    setNewMemberName('');
  };

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

    console.log('準備送出的還款資料:', payload);
    settlementMutation.mutate(payload);
  };

  return (
    // 外層黑色半透明遮罩
    <div className="fixed inset-0 bg-black/40 z-[100] flex justify-center items-end sm:items-center animate-in fade-in duration-200">

      {/* 白底視窗本體 */}
      <div className="bg-white w-full max-w-md h-[85vh] sm:h-[600px] sm:rounded-3xl rounded-t-3xl flex flex-col shadow-2xl animate-in slide-in-from-bottom-10 sm:slide-in-from-bottom-4 duration-300">

        {/* --- Header --- */}
        <div className="flex items-center justify-between p-5 border-b border-gray-100 shrink-0">
          <h2 className="text-xl font-bold text-gray-800">{group.name}</h2>
          <button onClick={onClose} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* --- Tabs 導覽列 --- */}
        <div className="flex border-b border-gray-100 px-2 overflow-x-auto shrink-0">
          {[
            { id: 'members', label: '成員', icon: UserPlus },
            { id: 'history', label: '記錄', icon: Clock },
            { id: 'settlement', label: '結算', icon: HandCoins },
            { id: 'repayments', label: '還款紀錄', icon: ListChecks }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap px-4 ${
                activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:bg-gray-50'
              }`}
            >
              <tab.icon size={16} /> {tab.label}
            </button>
          ))}
        </div>

        {/* --- Tab 內容區域 (有捲軸的區域) --- */}
        <div className="flex-1 overflow-y-auto p-5 bg-gray-50/50">

          {/* 1. 成員分頁 */}
          {activeTab === 'members' && (
            <div className="space-y-4">
              <form onSubmit={handleAddMember} className="flex gap-2">
                <input type="text" placeholder="輸入新成員名稱..." value={newMemberName} onChange={(e) => setNewMemberName(e.target.value)} className="flex-1 px-4 py-2 bg-white border border-gray-200 rounded-xl outline-none" />
                <button type="submit" disabled={!newMemberName.trim()} className="bg-gray-900 text-white px-4 py-2 rounded-xl">加入</button>
              </form>
              <div className="space-y-2">
                {group.members.map(member => (
                  <div key={member.id} className="flex items-center gap-3 p-3 bg-white rounded-xl border border-gray-100">
                    <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-bold text-sm">{member.name.charAt(0)}</div>
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
                    <button
                      onClick={() => setSettlementData({
                        payer_id: tx.from_user_id,
                        receiver_id: tx.to_user_id,
                        amount: tx.amount,
                        expense_id: null
                      })}
                      className="bg-blue-50 text-blue-600 hover:bg-blue-100 px-4 py-2 rounded-lg font-bold text-sm transition-colors"
                    >
                      總結算
                    </button>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">大家都互不相欠，太棒了！</div>
              )}
            </div>
          )}

          {/* 4. 還款紀錄分頁 (👉 搬進來這裡了！) */}
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
                      <div className="text-lg font-bold text-green-600">
                        +${Number(record.amount).toFixed(0)}
                      </div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between items-center text-xs">
                        <div className="flex gap-2">
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-md font-medium">
                            {methodMap[record.method] || record.method}
                          </span>
                          <span className={`px-2 py-1 rounded-md font-bold ${record.status === 'completed' ? 'bg-green-50 text-green-600' : 'bg-orange-50 text-orange-600'}`}>
                            {statusMap[record.status] || record.status}
                          </span>
                        </div>
                        <span className="text-gray-400">
                          {new Date(record.transaction_date).toLocaleDateString()}
                        </span>
                      </div>
                      {(record.notes || record.expense_description) && (
                        <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded-lg mt-1">
                          {record.expense_description && (
                            <span className="font-bold text-gray-700 mr-1">[{record.expense_description}]</span>
                          )}
                          {record.notes}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-gray-400">目前還沒有任何還款紀錄喔！</div>
              )}
            </div>
          )}

        </div> {/* 👈 內容區域在這裡完美結束 */}

        {/* --- 底部動作區塊 --- */}
        <div className="p-4 bg-white border-t border-gray-100 shrink-0">
          <button onClick={() => onNavigateToBill(group.id)} className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2">
            <Receipt size={20} /> 新增這群的帳單
          </button>
        </div>

      </div> {/* 👈 白底視窗本體在這裡完美結束 */}

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
                  const memberName = group.members.find(m => m.id === split.user_id)?.name || "未知成員";
                  const isPayer = split.user_id === selectedExpense.paid_by_id;

                  return (
                    <div key={idx} className="flex justify-between items-center text-sm py-1 border-b border-gray-200/50 last:border-0">
                      <span className="text-gray-700">{memberName} {isPayer && "(代墊)"}</span>
                      <div className="flex items-center gap-3">
                        <span className="font-medium text-gray-900">${Number(split.split_amount).toFixed(0)}</span>
                        {!isPayer && !split.is_settled ? (
                          <button
                            onClick={() => setSettlementData({
                              payer_id: split.user_id,
                              receiver_id: selectedExpense.paid_by_id,
                              amount: split.split_amount,
                              expense_id: selectedExpense.id
                            })}
                            className="bg-blue-600 text-white text-xs px-2 py-1 rounded"
                          >
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
                <select
                  value={settleMethod}
                  onChange={(e) => setSettleMethod(e.target.value)}
                  className="w-full p-2 border border-gray-200 rounded-lg outline-none"
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
                  placeholder={settlementData.expense_id ? "例如：還昨天的午餐錢" : "例如：五月份總結算"}
                  className="w-full p-2 border border-gray-200 rounded-lg outline-none"
                />
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setSettlementData(null)}
                className="flex-1 py-2 bg-gray-100 text-gray-600 rounded-xl font-bold"
              >
                取消
              </button>
              <button
                onClick={handleSettleSubmit}
                disabled={settlementMutation.isPending}
                className="flex-1 py-2 bg-blue-600 text-white rounded-xl font-bold disabled:bg-blue-300"
              >
                {settlementMutation.isPending ? '處理中...' : '確認結清'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div> // 👈 黑色遮罩完美結束
  );
}