import { useQuery } from '@tanstack/react-query';
import { ArrowRight } from 'lucide-react';
import { groupAPI } from '../services/api';

const METHOD_MAP = { cash: '現金', bank_transfer: '轉帳', credit_card: '信用卡' };
const STATUS_MAP = { pending: '處理中', completed: '已結清' };

export default function RepaymentsTab({ groupId }) {
  const { data: settlementsData, isLoading: isSettlementsLoading } = useQuery({
    queryKey: ['groupSettlements', groupId],
    queryFn: () => groupAPI.getSettlements(groupId)
  });

  return (
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
                  <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-md font-medium">
                    {METHOD_MAP[record.method] || record.method}
                  </span>
                  <span className={`px-2 py-1 rounded-md font-bold ${record.status === 'completed' ? 'bg-green-50 text-green-600' : 'bg-orange-50 text-orange-600'}`}>
                    {STATUS_MAP[record.status] || record.status}
                  </span>
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
  );
}