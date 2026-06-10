import { CheckCircle2, AlertCircle } from 'lucide-react';

export default function SplitSection({ 
  members, 
  splitMode, 
  setSplitMode, 
  exactAmounts, 
  handleExactAmountChange, 
  equalShare, 
  parsedTotal, 
  diff 
}) {
  return (
    <>
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
    </>
  );
}