import { useQuery } from '@tanstack/react-query';
import { ArrowRight } from 'lucide-react';
import { groupAPI } from '../services/api';

export default function SettlementTab({ groupId, onInitiateSettlement, currentUserId }) {
  const { data: balanceData, isLoading: isBalancesLoading } = useQuery({
    queryKey: ['groupBalances', groupId],
    queryFn: () => groupAPI.getGroupBalances(groupId)
  });

  if (isBalancesLoading) {
    return <div className="text-center py-10 text-gray-400">計算中，請稍候...</div>;
  }

  const settlements = balanceData?.settlements || [];

  if (settlements.length === 0) {
    return <div className="text-center py-10 text-gray-400">大家都互不相欠，太棒了！</div>;
  }

  const myDebts = settlements.filter(tx => tx.from_user_id === currentUserId);
  const myReceivables = settlements.filter(tx => tx.to_user_id === currentUserId);
  const others = settlements.filter(tx => tx.from_user_id !== currentUserId && tx.to_user_id !== currentUserId);
  const SettlementCard = ({ tx, type }) => (
    <div className="flex items-center justify-between p-4 bg-white rounded-xl border border-gray-100 shadow-sm mb-3">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className={`font-bold ${type === 'debt' ? 'text-gray-800' : 'text-gray-500'}`}>{tx.from_user_name}</span>
          <ArrowRight size={16} className="text-gray-300 mx-1" />
          <span className={`font-bold ${type === 'receivable' ? 'text-gray-800' : 'text-gray-500'}`}>{tx.to_user_name}</span>
        </div>
        {type === 'debt' && <span className="text-red-500 font-bold text-sm">需給付 ${Number(tx.amount).toFixed(0)}</span>}
        {type === 'receivable' && <span className="text-green-500 font-bold text-sm">將收到 ${Number(tx.amount).toFixed(0)}</span>}
        {type === 'other' && <span className="text-gray-400 font-medium text-sm">金額 ${Number(tx.amount).toFixed(0)}</span>}
      </div>

      {/* 只有當身分是「我需要還款」時，才顯示總結算按鈕 */}
      {type === 'debt' && (
        <button
          onClick={() => onInitiateSettlement({ payer_id: tx.from_user_id, receiver_id: tx.to_user_id, amount: tx.amount, expense_id: null })}
          className="bg-blue-50 text-blue-600 hover:bg-blue-100 px-4 py-2 rounded-lg font-bold text-sm transition-colors"
        >
          總結算
        </button>
      )}
    </div>
  );

  return (
    <div className="space-y-6 pb-4">
      {/* 我應付的款項 */}
      {myDebts.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-red-400 uppercase mb-3 px-1">我應付的款項</h4>
          {myDebts.map((tx, idx) => <SettlementCard key={`debt-${idx}`} tx={tx} type="debt" />)}
        </div>
      )}

      {/* 我應收的款項 */}
      {myReceivables.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-green-500 uppercase mb-3 px-1">我應收的款項</h4>
          {myReceivables.map((tx, idx) => <SettlementCard key={`recv-${idx}`} tx={tx} type="receivable" />)}
        </div>
      )}

      {/* 其他成員的帳務 */}
      {others.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-gray-400 uppercase mb-3 px-1">其他成員帳務</h4>
          {others.map((tx, idx) => <SettlementCard key={`other-${idx}`} tx={tx} type="other" />)}
        </div>
      )}
    </div>
  );
}