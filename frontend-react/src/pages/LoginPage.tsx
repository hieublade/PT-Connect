import React, { useState } from 'react';
import api from '../lib/axios';
import { User } from '../types/api';
import { 
  Dumbbell, 
  ShieldCheck, 
  UserCheck, 
  AlertCircle, 
  Star, 
  Flame, 
  CheckCircle2, 
  ArrowRight,
  Sparkles,
  Trophy,
  Users
} from 'lucide-react';

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

  const fillQuickAccount = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('Password123@');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-rose-50/30 flex items-center justify-center p-4 sm:p-6 lg:p-10">
      <div className="max-w-6xl w-full mx-auto bg-white rounded-3xl shadow-2xl shadow-slate-300/60 border border-slate-200/90 overflow-hidden grid grid-cols-1 lg:grid-cols-12">
        
        {/* Left Column: Real Fitness Imagery & High-Energy Brand Showcase */}
        <div className="lg:col-span-6 relative min-h-[460px] lg:min-h-[640px] flex flex-col justify-between p-8 sm:p-10 overflow-hidden text-white">
          {/* Main Gym Photo Background */}
          <img 
            src="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&q=80&w=1200" 
            alt="Fitness Training Gym" 
            className="absolute inset-0 w-full h-full object-cover"
          />
          
          {/* Contrast Gradients for Maximum Legibility */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/65 to-slate-900/40" />
          <div className="absolute inset-0 bg-red-950/20 mix-blend-multiply" />

          {/* Top Header inside Image */}
          <div className="relative z-10">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-white/15 backdrop-blur-md border border-white/25 text-white text-xs font-semibold shadow-sm">
              <div className="w-6 h-6 rounded-lg bg-[#FF4B4B] flex items-center justify-center text-white">
                <Dumbbell className="w-3.5 h-3.5" />
              </div>
              <span>PT CONNECT VIỆT NAM</span>
            </div>
          </div>

          {/* Center / Bottom Content with Highlights */}
          <div className="relative z-10 space-y-6 my-auto pt-8">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-md bg-red-500/20 border border-red-500/40 text-red-300 text-xs font-bold uppercase tracking-wider">
                <Flame className="w-3.5 h-3.5 text-[#FF4B4B]" />
                Nền tảng Huấn Luyện Viên 1-kèm-1
              </div>
              <h2 className="text-2xl sm:text-4xl font-black text-white leading-tight uppercase tracking-tight">
                Chinh Phục Vóc Dáng <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 via-rose-300 to-amber-200">
                  Cùng Huấn Luyện Viên Riêng
                </span>
              </h2>
              <p className="text-slate-200 text-sm sm:text-base leading-relaxed max-w-md font-normal">
                Lộ trình tập luyện và dinh dưỡng khoa học được cá nhân hóa, hợp đồng số minh bạch bảo lãnh kết quả từng buổi tập.
              </p>
            </div>

            {/* Inset Trainer Card with Real Photo */}
            <div className="p-4 rounded-2xl bg-slate-900/80 backdrop-blur-md border border-white/15 shadow-xl flex items-center gap-4 max-w-md">
              <img
                src="https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&q=80&w=300"
                alt="HLV Thể Hình"
                className="w-14 h-14 rounded-xl object-cover border-2 border-[#FF4B4B] shrink-0"
              />
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-bold text-white truncate flex items-center gap-1">
                    Đội ngũ HLV Quốc Tế
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  </h4>
                  <span className="text-[11px] font-bold text-amber-300 flex items-center gap-0.5">
                    <Star className="w-3 h-3 fill-amber-300" /> 5.0
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-0.5">100% chứng chỉ chuẩn NASM / ACE</p>
                <div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-300">
                  <span className="flex items-center gap-1">
                    <Users className="w-3 h-3 text-red-400" /> 18,500+ Học viên
                  </span>
                  <span className="flex items-center gap-1">
                    <Trophy className="w-3 h-3 text-amber-400" /> 99.2% Thành công
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Security Assurance */}
          <div className="relative z-10 pt-4 flex items-center gap-2 text-xs text-slate-300 border-t border-white/10">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Hợp đồng điện tử bảo lãnh hoàn tiền nếu không đạt mục tiêu hình thể</span>
          </div>
        </div>

        {/* Right Column: Clean, Elegant Light Login / Register Portal */}
        <div className="lg:col-span-6 p-8 sm:p-12 flex flex-col justify-center bg-white">
          <div className="max-w-md w-full mx-auto">
            
            {/* Header / Tabs */}
            <div className="mb-6">
              <div className="flex items-center gap-2.5 mb-2">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#FF4B4B] to-rose-400 flex items-center justify-center text-white shadow-md shadow-red-200">
                  <Dumbbell className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">PT CONNECT</h3>
                  <p className="text-xs text-slate-500">Đăng nhập tài khoản để vào hệ thống</p>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-slate-200 mt-5">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('LOGIN');
                    setError(null);
                  }}
                  className={`flex-1 pb-3 text-sm font-bold border-b-2 text-center transition-colors ${
                    activeTab === 'LOGIN'
                      ? 'border-[#FF4B4B] text-[#FF4B4B]'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Đăng Nhập
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('REGISTER');
                    setError(null);
                  }}
                  className={`flex-1 pb-3 text-sm font-bold border-b-2 text-center transition-colors ${
                    activeTab === 'REGISTER'
                      ? 'border-[#FF4B4B] text-[#FF4B4B]'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Đăng Ký Tài Khoản
                </button>
              </div>
            </div>

            {/* Error & Success Messages */}
            {error && (
              <div className="mb-5 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2.5 shadow-sm">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
                <span>{error}</span>
              </div>
            )}

            {regSuccess && (
              <div className="mb-5 p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2.5 shadow-sm">
                <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-600" />
                <span>{regSuccess}</span>
              </div>
            )}

            {/* Login Form */}
            {activeTab === 'LOGIN' ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Email đăng nhập
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="student_24@ptconnect.vn"
                    className="mt-1.5 block w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B] focus:border-[#FF4B4B] transition shadow-sm"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-center">
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Mật khẩu
                    </label>
                    <span className="text-[11px] text-slate-400">Pass: Password123@</span>
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Nhập mật khẩu của bạn"
                    className="mt-1.5 block w-full px-4 py-3 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B] focus:border-[#FF4B4B] transition shadow-sm"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 px-4 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-lg shadow-red-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {loading ? 'Đang xác thực thông tin...' : (
                      <>
                        <span>ĐĂNG NHẬP VÀO HỆ THỐNG</span>
                        <ArrowRight className="w-4 h-4" />
                      </>
                    )}
                  </button>
                </div>

                {/* Quick 1-Click Demo Accounts */}
                <div className="mt-6 pt-5 border-t border-slate-200">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700 mb-2.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                    <span>Tài khoản trải nghiệm nhanh (1-Click Fill):</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => fillQuickAccount('student_24@ptconnect.vn')}
                      className="p-2.5 rounded-xl bg-blue-50 border border-blue-200 hover:border-blue-400 text-left transition group"
                    >
                      <div className="text-[11px] font-bold text-blue-700 group-hover:text-blue-900">Học Viên Active</div>
                      <div className="text-[10px] text-blue-600 truncate">student_24</div>
                    </button>

                    <button
                      type="button"
                      onClick={() => fillQuickAccount('pt.hoangc@ptconnect.vn')}
                      className="p-2.5 rounded-xl bg-orange-50 border border-orange-200 hover:border-orange-400 text-left transition group"
                    >
                      <div className="text-[11px] font-bold text-orange-700 group-hover:text-orange-900">Huấn Luyện Viên</div>
                      <div className="text-[10px] text-orange-600 truncate">pt.hoangc</div>
                    </button>

                    <button
                      type="button"
                      onClick={() => fillQuickAccount('admin@ptconnect.vn')}
                      className="p-2.5 rounded-xl bg-purple-50 border border-purple-200 hover:border-purple-400 text-left transition group"
                    >
                      <div className="text-[11px] font-bold text-purple-700 group-hover:text-purple-900">Quản Trị Viên</div>
                      <div className="text-[10px] text-purple-600 truncate">admin</div>
                    </button>
                  </div>
                </div>
              </form>
            ) : (
              /* Register Form */
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Vai trò tài khoản
                  </label>
                  <div className="grid grid-cols-2 gap-3 mt-1.5">
                    <button
                      type="button"
                      onClick={() => setRegRole('STUDENT')}
                      className={`py-2.5 px-3 text-xs font-bold rounded-xl border text-center flex items-center justify-center gap-1.5 transition-all ${
                        regRole === 'STUDENT'
                          ? 'border-blue-600 bg-blue-50 text-blue-700 ring-2 ring-blue-100'
                          : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <UserCheck className="w-4 h-4 text-blue-600" /> Học Viên
                    </button>
                    <button
                      type="button"
                      onClick={() => setRegRole('PT')}
                      className={`py-2.5 px-3 text-xs font-bold rounded-xl border text-center flex items-center justify-center gap-1.5 transition-all ${
                        regRole === 'PT'
                          ? 'border-orange-600 bg-orange-50 text-orange-700 ring-2 ring-orange-100'
                          : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      <Dumbbell className="w-4 h-4 text-orange-600" /> Huấn Luyện Viên
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Họ và tên
                  </label>
                  <input
                    type="text"
                    required
                    value={regFullName}
                    onChange={(e) => setRegFullName(e.target.value)}
                    placeholder="Nguyễn Văn A"
                    className="mt-1.5 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Địa chỉ Email
                  </label>
                  <input
                    type="email"
                    required
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="name@ptconnect.vn"
                    className="mt-1.5 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Số điện thoại
                  </label>
                  <input
                    type="tel"
                    required
                    value={regPhone}
                    onChange={(e) => setRegPhone(e.target.value)}
                    placeholder="0912345678"
                    className="mt-1.5 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
                    Mật khẩu
                  </label>
                  <input
                    type="password"
                    required
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Tối thiểu 6 ký tự"
                    className="mt-1.5 block w-full px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                  />
                </div>

                <div className="pt-2">
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3.5 px-4 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-lg shadow-red-200 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {loading ? 'Đang tạo tài khoản...' : 'HOÀN TẤT ĐĂNG KÝ HỌC THỬ'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
