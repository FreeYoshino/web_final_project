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
  }
};

export const billAPI = {
  createExpense: async (expenseData) => {
    const response = await api.post('/expenses', expenseData);
    return response.data;
  }
};