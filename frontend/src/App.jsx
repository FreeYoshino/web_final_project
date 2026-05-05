import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './layouts/AppLayout'; 
import NewBillPage from './pages/NewBillPage';
import GroupsPage from './pages/GroupsPage';
const ProfilePage = () => <div className="bg-white p-6 rounded-xl shadow-sm"><h1 className="text-xl font-bold">個人設定</h1></div>;

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 使用新的 AppLayout */}
        <Route path="/" element={<AppLayout />}>
          <Route index element={<GroupsPage />} />
          <Route path="groups" elemen={<GroupsPage/>} />
          <Route path="new-bill" element={<NewBillPage />} />
          <Route path="profile" element={<ProfilePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;