import { create } from 'zustand';

export const useGroupStore = create((set, get) => ({
  // 1. 狀態 (State)
  groups: [
    { 
      id: 'g1', 
      name: '板橋租屋處', 
      members: [
        { id: 'u1', name: '我 (CCT)' },
        { id: 'u2', name: '室友小明' },
        { id: 'u3', name: '室友小華' }
      ] 
    },
    { 
      id: 'g2', 
      name: '週五外送團', 
      members: [
        { id: 'u1', name: '我 (CCT)' },
        { id: 'u4', name: '同事阿強' },
        { id: 'u5', name: '同事美美' }
      ] 
    }
  ],
  activeGroupId: 'g1', // 預設選中第一個群組
  activePayerId: 'u1', // 預設支付者是你自己

  // 2. 動作 (Actions)
  // 設定目前要幫哪個群組記帳
  setActiveGroup: (id) => set({ activeGroupId: id }),
  
  // 設定誰是代墊人
  setActivePayer: (id) => set({ activePayerId: id }),

  // 3. 取得器 (Getters / Computed)
  // 獲取目前選中群組的所有資訊 (包括成員)
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