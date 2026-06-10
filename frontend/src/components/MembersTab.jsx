import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, UserPlus } from 'lucide-react';
import { groupAPI, userAPI } from '../services/api';

export default function MembersTab({ group }) {
  const queryClient = useQueryClient();
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // 防抖邏輯
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput.trim());
    }, 500);
    return () => clearTimeout(timer);
  }, [searchInput]);

  // 搜尋使用者
  const { data: searchData, isFetching: isSearching } = useQuery({
    queryKey: ['usersSearch', debouncedSearch],
    queryFn: () => userAPI.searchUsers(debouncedSearch),
    enabled: debouncedSearch.length > 0
  });
  const searchResults = Array.isArray(searchData) ? searchData : (searchData?.users || []);
  // 取得群組成員
  const { data: membersData, isLoading: isMembersLoading } = useQuery({
    queryKey: ['groupMembers', group.id],
    queryFn: () => groupAPI.getGroupMembers(group.id)
  });
  const members = Array.isArray(membersData) ? membersData : (membersData?.members || []);
  const memberIds = new Set(members.map(m => m.user_id));
  const filteredSearchResults = searchResults.filter(user => !memberIds.has(user.id));
  // 加入群組 Mutation
  const addMemberMutation = useMutation({
    mutationFn: (userId) => groupAPI.addMemberToGroup({
      groupId: group.id,
      memberData: { role: 'member', user_ids: [userId] }
    }),
    onSuccess: () => {
      alert('加入成員成功！');
      queryClient.invalidateQueries({ queryKey: ['groupMembers', group.id] });
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      setSearchInput('');
    },
    onError: (error) => {
      alert('加入失敗：' + (error.response?.data?.detail || error.message));
    }
  });

  const handleSelectUser = (userId) => {
    if (window.confirm('確定要將此使用者加入群組嗎？')) {
      addMemberMutation.mutate(userId);
    }
  };

  return (
    <div className="space-y-4">
      {/* 搜尋輸入框 */}
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

      {/* 搜尋結果選單 */}
      {debouncedSearch && (
        <div className="bg-white rounded-xl border border-gray-200 shadow-lg overflow-hidden relative z-10">
          {isSearching ? (
            <div className="p-4 text-center text-sm text-gray-500">搜尋中...</div>
          ) : filteredSearchResults.length > 0 ? (
            <div className="max-h-48 overflow-y-auto">
              {filteredSearchResults.map(user => (
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
            <div className="p-4 text-center text-sm text-gray-500">
              {searchResults.length > 0
                ? "找到的使用者都已經在群組內囉！"
                : "找不到相符的使用者"}
            </div>
          )}
        </div>
      )}

      {/* 現有成員列表 */}
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
  );
}