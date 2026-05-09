import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Plus, ChevronRight, X } from 'lucide-react';
import { useGroupStore } from '../store/groupStore';
import GroupDetailModal from '../components/GroupDetailModal';

export default function GroupsPage() {
    const navigate = useNavigate();
    // 從 Zustand 拿取群組資料與新增功能
    const { groups, addGroup, setActiveGroup, activeGroupId } = useGroupStore();

    // 控制「新增群組」表單是否展開的狀態
    const [isCreating, setIsCreating] = useState(false);
    const [newGroupName, setNewGroupName] = useState('');

    // 紀錄目前點開哪個群組
    const [selectedGroup, setSelectedGroup] = useState(null);
    // 處理表單送出
    const handleCreateSubmit = (e) => {
        e.preventDefault();
        if (!newGroupName.trim()) return;

        addGroup(newGroupName); // 呼叫 Zustand 寫入資料
        setNewGroupName('');    // 清空輸入框
        setIsCreating(false);   // 收起表單
    };

    // 點擊群組卡片時：設定為活躍群組，並跳轉去記帳
    //   const handleGroupClick = (id) => {
    //     setActiveGroup(id);
    //     navigate('/new-bill');
    //   };
    const handleGroupClick = (group) => {
        setSelectedGroup(group); // 儲存點擊的群組物件，開啟視窗
    };

    return (
        <div className="max-w-md mx-auto mt-4 space-y-6">

            {/* --- 頂部標題與新增按鈕 --- */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-gray-800">我的群組</h1>
                {!isCreating && (
                    <button
                        onClick={() => setIsCreating(true)}
                        className="flex items-center gap-1 text-sm font-medium text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full hover:bg-blue-100 transition-colors"
                    >
                        <Plus size={16} /> 建立
                    </button>
                )}
            </div>

            {/* --- 新增群組的展開表單 --- */}
            {isCreating && (
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-blue-100 animate-in fade-in slide-in-from-top-4 duration-200">
                    <div className="flex justify-between items-center mb-3">
                        <h2 className="font-bold text-gray-700">建立新群組</h2>
                        <button onClick={() => setIsCreating(false)} className="text-gray-400 hover:text-gray-600">
                            <X size={20} />
                        </button>
                    </div>

                    <form onSubmit={handleCreateSubmit} className="flex gap-2">
                        <input
                            type="text"
                            autoFocus
                            placeholder="例如：花蓮三天兩夜、週末桌遊團"
                            value={newGroupName}
                            onChange={(e) => setNewGroupName(e.target.value)}
                            className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2 outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                        <button
                            type="submit"
                            disabled={!newGroupName.trim()}
                            className="bg-blue-600 text-white px-4 py-2 rounded-xl font-medium disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
                        >
                            完成
                        </button>
                    </form>
                </div>
            )}

            {/* --- 群組列表 --- */}
            <div className="space-y-3">
                {groups.map((group) => (
                    <button
                        key={group.id}
                        onClick={() => handleGroupClick(group)}
                        className={`w-full flex items-center justify-between p-4 bg-white rounded-2xl shadow-sm border transition-all hover:shadow-md active:scale-[0.98] ${activeGroupId === group.id ? 'border-gray-100' : 'border-gray-100'
                            }`}
                    >
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center shrink-0">
                                <Users size={24} />
                            </div>
                            <div className="text-left">
                                <h3 className="font-bold text-gray-800 text-lg">{group.name}</h3>
                                <p className="text-sm text-gray-500 mt-0.5">
                                    {group.members.length} 位成員
                                </p>
                            </div>
                        </div>
                        <ChevronRight className="text-gray-300" />
                    </button>
                ))}

                {groups.length === 0 && (
                    <div className="text-center py-10 text-gray-400">
                        目前還沒有任何群組喔，趕快建立一個吧！
                    </div>
                )}
                {selectedGroup && (
                    <GroupDetailModal
                        group={selectedGroup}
                        onClose={() => setSelectedGroup(null)} // 點擊關閉時清空 state
                        onNavigateToBill={(groupId) => {
                            setActiveGroup(groupId);
                            navigate('/new-bill');
                        }}
                    />
                )}
            </div>

        </div>
    );
}