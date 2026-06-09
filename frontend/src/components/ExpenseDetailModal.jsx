import { X, CheckCircle } from 'lucide-react';

export default function ExpenseDetailModal({ expense, onClose, onSettle, currentUserId }) {
    if (!expense) return null;

    return (
        <div className="fixed inset-0 bg-black/60 z-[110] flex justify-center items-center p-4 animate-in fade-in">
            <div className="bg-white w-full max-w-sm rounded-2xl p-6 shadow-xl animate-in zoom-in-95">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h3 className="text-xl font-bold text-gray-800">{expense.description}</h3>
                        <p className="text-sm text-gray-500 mt-1">
                            {new Date(expense.created_at).toLocaleString()}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:bg-gray-100 p-1 rounded-full transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="py-4 border-y border-gray-100 my-4 flex justify-between items-center">
                    <span className="text-gray-600 font-medium">總金額</span>
                    <span className="text-2xl font-bold text-blue-600">
                        ${Number(expense.amount).toFixed(0)}
                    </span>
                </div>

                {expense.splits && expense.splits.length > 0 && (
                    <div className="space-y-2 mb-6 bg-gray-50 p-4 rounded-xl">
                        <h4 className="text-xs font-bold text-gray-400 uppercase mb-3">分攤詳情</h4>
                        {expense.splits.map((split, idx) => {
                            const memberName = split.user_name || "未知成員";
                            const isPayer = split.user_id === expense.paid_by_id;
                            const isMyDebt = split.user_id === currentUserId;
                            return (
                                <div key={idx} className="flex justify-between items-center text-sm py-1 border-b border-gray-200/50 last:border-0">
                                    <span className="text-gray-700">{memberName} {isPayer && "(代墊)"}</span>
                                    <div className="flex items-center gap-3">
                                        <span className="font-medium text-gray-900">${Number(split.split_amount).toFixed(0)}</span>
                                        {!isPayer && !split.is_settled ? (
                                            isMyDebt ? (
                                                <button
                                                    onClick={() => onSettle(split.user_id, expense.paid_by_id, split.split_amount, expense.id)}
                                                    className="bg-blue-600 text-white text-xs px-2 py-1 rounded hover:bg-blue-700 transition-colors"
                                                >
                                                    還款
                                                </button>
                                            ) : (
                                                <span className="text-orange-500 bg-orange-50 px-2 py-1 rounded text-xs">
                                                    未還款
                                                </span>
                                            )
                                        ) : !isPayer && split.is_settled ? (
                                            <span className="text-green-500 flex items-center gap-1 text-xs">
                                                <CheckCircle size={12} /> 已還清
                                            </span>
                                        ) : null}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
                <button onClick={onClose} className="w-full bg-gray-900 hover:bg-gray-800 text-white py-3 rounded-xl font-bold transition-colors">
                    關閉
                </button>
            </div>
        </div>
    );
}