import React, { useState, useEffect } from 'react';
import { User } from './types/api';
import { LoginPage } from './pages/LoginPage';
import { StudentPage } from './pages/StudentPage';
import { PtPage } from './pages/PtPage';
import { AdminPage } from './pages/AdminPage';
import { FloatingChatWidget } from './components/FloatingChatWidget';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('ptconnect_user');
    const token = localStorage.getItem('ptconnect_token');
    if (savedUser && token) {
      try {
        setCurrentUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem('ptconnect_user');
        localStorage.removeItem('ptconnect_token');
      }
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('ptconnect_user');
    localStorage.removeItem('ptconnect_token');
    setCurrentUser(null);
  };

  if (!currentUser) {
    return <LoginPage onLoginSuccess={(u) => setCurrentUser(u)} />;
  }

  if (currentUser.role === 'STUDENT') {
    return (
      <>
        <StudentPage
          user={currentUser}
          onLogout={handleLogout}
          onUserUpdated={(u) => setCurrentUser(u)}
        />
        <FloatingChatWidget currentUser={currentUser} />
      </>
    );
  }

  if (currentUser.role === 'PT') {
    return (
      <>
        <PtPage
          user={currentUser}
          onLogout={handleLogout}
          onUserUpdated={(u) => setCurrentUser(u)}
        />
        <FloatingChatWidget currentUser={currentUser} />
      </>
    );
  }

  if (currentUser.role === 'ADMIN') {
    return <AdminPage user={currentUser} onLogout={handleLogout} />;
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="bg-white p-6 rounded-xl border border-red-200 text-center max-w-sm">
        <h3 className="font-bold text-red-600">Vai trò không xác định: {currentUser.role}</h3>
        <button
          onClick={handleLogout}
          className="mt-4 px-4 py-2 bg-slate-800 text-white text-sm rounded-lg"
        >
          Đăng xuất
        </button>
      </div>
    </div>
  );
};

export default App;
