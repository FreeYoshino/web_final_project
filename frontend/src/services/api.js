import axios from 'axios';
export const api = axios.create({
  baseURL: 'http://localhost:8000', 
  timeout: 5000,
});

export const groupAPI = {
  // 取得使用者的所有群組
//   getGroups: async () => {
//     const response = await api.get('/groups'); // 替換成你們後端真實的路由
//     return response.data;
//   },

  getGroupBalances: async (groupId) => {
    const response = await api.get(`/groups/${groupId}/balances`);
    return response.data;
  },
//   取得群組歷史賬單
  getGroupExpenses: async (groupId) => {
    const response = await api.get(`/expenses/${groupId}`);
    return response.data;
  },

  createSettlement: async (settlementData) => {
    // ⚠️ 請與後端確認這支 API 的正確網址路徑 (例如可能是 /transactions 或 /settlements)
    const response = await api.post('/settlements', settlementData);
    return response.data;
  },

  getSettlements: async(groupId) => {
    const response = await api.get(`/settlements/${groupId}`);
    return response.data;
  }
};

export const authAPI = {
  // 1. 註冊 (依照你組員提供的格式)
  register: async (userData) => {
    const response = await api.post('/users', userData); // 請和組員確認正確的 URL 路徑
    return response.data;
  },
  
  // 2. 登入 (先預留位置)
  login: async (credentials) => {
    // 通常登入是 POST /users/login 或是 /token
    const response = await api.post('/users/login', credentials); 
    return response.data;
  }
};

export const billAPI = {
  createExpense: async (expenseData) => {
    const response = await api.post('/expenses', expenseData);
    return response.data;
  }
};