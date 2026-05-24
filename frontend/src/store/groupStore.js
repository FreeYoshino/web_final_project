import { create } from 'zustand';

export const useGroupStore = create((set, get) => ({
  // 1. 狀態 (State)
  groups: [
    {
      id: 'f69d829f-b9ca-4652-8aad-b5ea403020bf', // Group ID
      name: '測試群組',
      members: [
        { id: '336330aa-4cc1-48bb-81b8-87829fcaa032', name: '測試用戶1' }, // User 1
        { id: 'c677178b-da35-40c1-b844-fc49a3530ba8', name: '測試用戶2' }, // User 2
        { id: '2066a82f-9768-483a-9c72-dde0c9c7eb6c', name: '測試用戶3' }  // User 3
      ]
    }
  ],
  // 👉 2. 預設選中這個真實的群組與用戶
  activeGroupId: 'f69d829f-b9ca-4652-8aad-b5ea403020bf',
  activePayerId: '336330aa-4cc1-48bb-81b8-87829fcaa032',

  setActiveGroup: (id) => set({ activeGroupId: id }),
  setActivePayer: (id) => set({ activePayerId: id }),

  getActiveGroup: () => {
    const { groups, activeGroupId } = get();
    return groups.find(g => g.id === activeGroupId);
  },
  addGroup: (groupName) => set((state) => {
    const newGroup = {
      // 這裡先用時間戳當作簡單的唯一 ID，未來串接後端會改由資料庫產生 UUID
      id: `g_${Date.now()}`,
      name: groupName,
      // 預設將創建者 (自己) 加入群組中
      members: [{ id: 'u1', name: '我 (CCT)' }]
    };
    return {
      groups: [newGroup, ...state.groups], // 將新群組加到陣列最前面
      activeGroupId: newGroup.id // 建立後，自動將它設為當前選中群組
    };
  }),
  // 新增成員
  addMember: (groupId, name) => set((state) => ({
    groups: state.groups.map(g =>
      g.id === groupId
        ? { ...g, members: [...g.members, { id: `u_${Date.now()}`, name }] }
        : g
    )
  })),
  // 新增帳單
  addExpense: (groupId, expense) => set((state) => ({
    groups: state.groups.map(g =>
      g.id === groupId
        ? { ...g, expenses: [expense, ...g.expenses] }
        : g
    )
  }))
}));