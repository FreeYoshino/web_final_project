import { useQuery } from '@tanstack/react-query';
import { groupAPI } from '../services/api';

export default function HistoryTab({ groupId, onSelectExpense }) {
  const { data: expensesData, isLoading: isExpensesLoading } = useQuery({
    queryKey: ['groupExpenses', groupId],
    queryFn: () => groupAPI.getGroupExpenses(groupId)
  });

  return (
    <div className="space-y-3">
      {isExpensesLoading ? (
        <div className="text-center py-10 text-gray-400">載入歷史帳單中...</div>
      ) : expensesData?.items && expensesData.items.length > 0 ? (
        expensesData.items.map(exp => (
          <button 
            key={exp.id} 
            onClick={() => onSelectExpense(exp)} 
            className="w-full p-4 bg-white rounded-xl border border-gray-100 shadow-sm flex justify-between items-center hover:bg-gray-50 transition-colors active:scale-[0.98] text-left"
          >
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
  );
}