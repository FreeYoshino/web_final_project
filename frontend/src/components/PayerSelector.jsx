export default function PayerSelector({ members, isMembersLoading, activePayerId, setActivePayerId }) {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
      <label className="block text-xs font-bold text-gray-400 uppercase mb-2">誰先代墊的？</label>
      {isMembersLoading ? (
        <div className="text-sm text-gray-500 py-2">載入成員中...</div>
      ) : members.length === 0 ? (
        <div className="text-sm text-red-500 py-2">此群組尚無成員，請先至首頁加入成員。</div>
      ) : (
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
          {members.map(m => {
            const mId = m.id || m.user_id;
            const mName = m.name || m.username || m.user_name || "未知";
            return (
              <button
                key={mId}
                type="button" // 避免觸發表單送出
                onClick={() => setActivePayerId(mId)}
                className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
                  activePayerId === mId 
                    ? 'bg-blue-600 text-white shadow-md' 
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                }`}
              >
                {mName}
              </button>
            )
          })}
        </div>
      )}
    </div>
  );
}