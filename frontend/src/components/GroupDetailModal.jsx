import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, UserPlus, Receipt, HandCoins, ArrowRight, Clock, ListChecks } from 'lucide-react';
import { groupAPI, userAPI } from '../services/api';

import ExpenseDetailModal from './ExpenseDetailModal';
import SettlementFormModal from './SettlementFormModal';
import HistoryTab from './HistoryTab';
import MembersTab from './MembersTab';
import RepaymentsTab from './RepaymentsTab';
import SettlementTab from './SettlementTab';

const methodMap = { cash: '現金', bank_transfer: '轉帳', credit_card: '信用卡' };
const statusMap = { pending: '處理中', completed: '已結清' };

export default function GroupDetailModal({ group, onClose, onNavigateToBill }) {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('members');
  const [selectedExpense, setSelectedExpense] = useState(null);
  const [settlementData, setSettlementData] = useState(null);
  if (!group) return null;
  // 取得當前登入的使用者資料
  const { data: currentUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: userAPI.getMe,
    staleTime: Infinity, // 設定為 Infinity 代表只要網頁沒重整，就不會重複發送請求
  });
  const currentUserId = currentUser?.id;
  const settlementMutation = useMutation({
    mutationFn: groupAPI.createSettlement,
    onSuccess: () => {
      alert('還款成功！');
      queryClient.invalidateQueries({ queryKey: ['groupBalances', group.id] });
      queryClient.invalidateQueries({ queryKey: ['groupExpenses', group.id] });
      queryClient.invalidateQueries({ queryKey: ['groupSettlements', group.id] });
      setSettlementData(null);
    },
    onError: (error) => alert('還款失敗：' + (error.response?.data?.detail || error.message))
  });

  const handleSettleSubmit = (method, notes) => {
    const isSpecificExpense = !!settlementData.expense_id;
    const payload = {
      payer_id: settlementData.payer_id,
      receiver_id: settlementData.receiver_id,
      amount: settlementData.amount,
      method: method,
      group_id: group.id,
      expense_id: settlementData.expense_id,
      status: 'completed',
      notes: notes.trim() || (isSpecificExpense ? '單筆還款' : '總額批次結算'),
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
            { id: 'history', label: '記帳記錄', icon: Clock },
            { id: 'settlement', label: '結算', icon: HandCoins },
            { id: 'repayments', label: '還款紀錄', icon: ListChecks }
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
          {activeTab === 'members' && <MembersTab group={group} />}
          {activeTab === 'history' && <HistoryTab groupId={group.id} onSelectExpense={setSelectedExpense} />}
          {activeTab === 'settlement' && <SettlementTab groupId={group.id} onInitiateSettlement={setSettlementData} currentUserId={currentUserId} />}
          {activeTab === 'repayments' && <RepaymentsTab groupId={group.id} />}
        </div>

        {/* --- 底部動作區塊 --- */}
        <div className="p-4 bg-white border-t border-gray-100 shrink-0">
          <button onClick={() => onNavigateToBill(group.id)} className="w-full bg-blue-600 text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2">
            <Receipt size={20} /> 新增這群的帳單
          </button>
        </div>
      </div>
      {/* --- 單筆帳單詳細視窗 --- */}
      <ExpenseDetailModal
        expense={selectedExpense}
        onClose={() => setSelectedExpense(null)}
        onSettle={(payer_id, receiver_id, amount, expense_id) => {
          setSettlementData({ payer_id, receiver_id, amount, expense_id });
        }}
        currentUserId={currentUserId}
      />
      {/* --- 還款確認表單視窗 --- */}
      <SettlementFormModal
        data={settlementData}
        onClose={() => setSettlementData(null)}
        onSubmit={handleSettleSubmit}
        isPending={settlementMutation.isPending}
      />
    </div>
  );
}