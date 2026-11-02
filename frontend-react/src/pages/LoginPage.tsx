import React, { useState } from 'react';
import api from '../lib/axios';
import { User } from '../types/api';
import { Dumbbell, ShieldCheck, UserCheck, AlertCircle } from 'lucide-react';

interface LoginPageProps {
  onLoginSuccess: (user: User, token: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [activeTab, setActiveTab] = useState<'LOGIN' | 'REGISTER'>('LOGIN');

  // Login form
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Register form
  const [regFullName, setRegFullName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPhone, setRegPhone] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regRole, setRegRole] = useState<'STUDENT' | 'PT'>('STUDENT');
  const [regSuccess, setRegSuccess] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Vui lòng nhập đầy đủ Email và Mật khẩu.');
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const data: any = await api.post('/auth/login', {
        email: email.trim(),
        password,
      });
      const token = data.token;
      const user = data.user;
      localStorage.setItem('ptconnect_token', token);
      localStorage.setItem('ptconnect_user', JSON.stringify(user));
      onLoginSuccess(user, token);
    } catch (err: any) {
      setError(err.message || 'Email hoặc mật khẩu không chính xác.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRegSuccess(null);

    try {
      await api.post('/auth/register', {
        fullName: regFullName.trim(),
        email: regEmail.trim(),
        phone: regPhone.trim(),
        password: regPassword,
        role: regRole,
      });
      setRegSuccess('Đăng ký tài khoản thành công! Bạn có thể chuyển sang tab Đăng nhập để tiếp tục.');
      setActiveTab('LOGIN');
      setEmail(regEmail.trim());
      setPassword(regPassword);
    } catch (err: any) {
      setError(err.message || 'Đăng ký tài khoản không thành công.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-red-50/20 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#FF4B4B] to-rose-400 text-white shadow-lg shadow-red-200 mb-3">
          <Dumbbell className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">PT Connect</h1>
        <p className="mt-1 text-sm text-slate-500">
          Nền tảng kết nối Học viên & Huấn luyện viên cá nhân chuyên nghiệp
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xl shadow-slate-200/50 rounded-2xl border border-slate-200 sm:px-10">
          {/* Tabs */}
          <div className="flex border-b border-slate-200 mb-6">
            <button
              onClick={() => {
                setActiveTab('LOGIN');
                setError(null);
              }}
              className={`flex-1 pb-3 text-sm font-semibold border-b-2 text-center transition-colors ${
                activeTab === 'LOGIN'
                  ? 'border-[#FF4B4B] text-[#FF4B4B]'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              Đăng nhập
            </button>
            <button
              onClick={() => {
                setActiveTab('REGISTER');
                setError(null);
              }}
              className={`flex-1 pb-3 text-sm font-semibold border-b-2 text-center transition-colors ${
                activeTab === 'REGISTER'
                  ? 'border-[#FF4B4B] text-[#FF4B4B]'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              Đăng ký tài khoản
            </button>
          </div>

          {error && (
            <div className="mb-5 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
              <span>{error}</span>
            </div>
          )}

          {regSuccess && (
            <div className="mb-5 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-600" />
              <span>{regSuccess}</span>
            </div>
          )}

          {activeTab === 'LOGIN' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Email đăng nhập
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="example@ptconnect.vn"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B] focus:border-[#FF4B4B]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Mật khẩu
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Nhập mật khẩu của bạn"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B] focus:border-[#FF4B4B]"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 px-4 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-md shadow-red-200 transition-all disabled:opacity-50"
                >
                  {loading ? 'Đang xác thực...' : 'Đăng nhập'}
                </button>
              </div>

              {/* Demo Accounts hint */}
              <div className="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-500 space-y-1">
                <p className="font-semibold text-slate-700">Tài khoản trải nghiệm nhanh (Pass: Password123@):</p>
                <p className="flex justify-between font-mono bg-slate-50 px-2 py-1 rounded">
                  <span>Học viên:</span> <span className="text-blue-600 cursor-pointer" onClick={() => { setEmail('student.a@ptconnect.vn'); setPassword('Password123@'); }}>student.a@ptconnect.vn</span>
                </p>
                <p className="flex justify-between font-mono bg-slate-50 px-2 py-1 rounded">
                  <span>Huấn luyện viên:</span> <span className="text-orange-600 cursor-pointer" onClick={() => { setEmail('pt.hoangc@ptconnect.vn'); setPassword('Password123@'); }}>pt.hoangc@ptconnect.vn</span>
                </p>
                <p className="flex justify-between font-mono bg-slate-50 px-2 py-1 rounded">
                  <span>Quản trị viên:</span> <span className="text-purple-600 cursor-pointer" onClick={() => { setEmail('admin@ptconnect.vn'); setPassword('Password123@'); }}>admin@ptconnect.vn</span>
                </p>
              </div>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Vai trò đăng ký
                </label>
                <div className="grid grid-cols-2 gap-3 mt-1.5">
                  <button
                    type="button"
                    onClick={() => setRegRole('STUDENT')}
                    className={`py-2 px-3 text-xs font-semibold rounded-lg border text-center flex items-center justify-center gap-1.5 transition-all ${
                      regRole === 'STUDENT'
                        ? 'border-blue-600 bg-blue-50 text-blue-700 ring-2 ring-blue-100'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <UserCheck className="w-3.5 h-3.5" /> Học viên (Student)
                  </button>
                  <button
                    type="button"
                    onClick={() => setRegRole('PT')}
                    className={`py-2 px-3 text-xs font-semibold rounded-lg border text-center flex items-center justify-center gap-1.5 transition-all ${
                      regRole === 'PT'
                        ? 'border-orange-600 bg-orange-50 text-orange-700 ring-2 ring-orange-100'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    <Dumbbell className="w-3.5 h-3.5" /> Huấn luyện viên (PT)
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Họ và tên
                </label>
                <input
                  type="text"
                  required
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  placeholder="Nguyễn Văn A"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Địa chỉ Email
                </label>
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  placeholder="name@ptconnect.vn"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Số điện thoại
                </label>
                <input
                  type="tel"
                  required
                  value={regPhone}
                  onChange={(e) => setRegPhone(e.target.value)}
                  placeholder="0912345678"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase">
                  Mật khẩu
                </label>
                <input
                  type="password"
                  required
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="Tối thiểu 6 ký tự"
                  className="mt-1 block w-full px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 px-4 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-md transition-all disabled:opacity-50"
                >
                  {loading ? 'Đang xử lý...' : 'Tạo tài khoản'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
