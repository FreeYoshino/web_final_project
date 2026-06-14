import { BrowserRouter, Routes, Route ,Navigate} from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from './layouts/AppLayout';
import NewBillPage from './pages/NewBillPage';
import GroupsPage from './pages/GroupsPage';
import AuthPage from './pages/AuthPage';
import ProfilePage from './pages/ProfilePage';
import { useEffect } from 'react';

const queryClient = new QueryClient();
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');

  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === 'token'){
        window.location.reload();
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };

  }, []);

  if (!token) {
    // replace 屬性可以讓使用者按「上一頁」時不會陷入跳轉迴圈
    return <Navigate to="/login" replace />;
  }

  return children;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AuthPage />} />
          {/* 使用新的 AppLayout */}
          <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route index element={<Navigate to="/groups" replace />} />
            <Route path="groups" element={<GroupsPage />} />
            <Route path="new-bill" element={<NewBillPage />} />
            <Route path="profile" element={<ProfilePage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;