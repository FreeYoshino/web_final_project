import axios from 'axios';
export const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});
// 請求攔截器
api.interceptors.request.use(
  (config) => {
    // 從瀏覽器的 localStorage 拿出 Token
    const token = localStorage.getItem('token');

    if (token) {
      // 如果有 Token，就照著 JWT 標準格式塞入 Authorization header
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
// 回應攔截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      // 如果後端回傳 401 Unauthorized (代表 Token 過期或造假)
      console.warn('Token 無效或已過期，請重新登入');
      localStorage.removeItem('token'); // 清除過期 Token

      // 將使用者強制踢回登入頁
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
export const groupAPI = {
  // 取得使用者的所有群組
  getGroups: async () => {
    const response = await api.get('/groups');
    return response.data;
  },

  getGroupBalances: async (groupId) => {
    const response = await api.get(`/groups/${groupId}/balances`);
    return response.data;
  },
  //   取得群組歷史賬單
  getGroupExpenses: async (groupId) => {
    const response = await api.get(`/groups/${groupId}/expenses`);
    return response.data;
  },

  createSettlement: async (settlementData) => {
    // ⚠️ 請與後端確認這支 API 的正確網址路徑 (例如可能是 /transactions 或 /settlements)
    const response = await api.post('/settlements', settlementData);
    return response.data;
  },

  getSettlements: async (groupId) => {
    const response = await api.get(`/groups/${groupId}/settlements`);
    return response.data;
  },

  createGroup: async (groupData) => {
    // 假設 groupData 是 { name: "我的新群組", description: "..." }
    const response = await api.post('/groups', groupData);
    return response.data;
  },

  // 👉 2. 取得特定群組的成員名單
  getGroupMembers: async (groupId) => {
    const response = await api.get(`/groups/${groupId}/members`);
    return response.data;
  },

  // 👉 3. 新增成員到特定群組
  addMemberToGroup: async ({ groupId, memberData }) => {
    const response = await api.post(`/groups/${groupId}/members`, memberData);
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
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await api.post('login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded' // 告訴後端這是表單
      }
    });
    return response.data;
  }
};

export const userAPI = {
  // 搜尋使用者
  searchUsers: async (keyword) => {
    // 發送 GET /users?q=alice 搜尋請求
    const response = await api.get('/users', {
      params: { q: keyword }
    });
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/users/me');
    return response.data;
  }

};

export const billAPI = {
  createExpense: async (expenseData) => {
    const response = await api.post('/expenses', expenseData);
    return response.data;
  }
};

export default api;