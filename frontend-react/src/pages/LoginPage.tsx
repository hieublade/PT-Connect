import React, { useState } from 'react';
import api from '../lib/axios';
import { User } from '../types/api';
import { 
  Dumbbell, 
  ShieldCheck, 
  UserCheck, 
  AlertCircle, 
  Star, 
  Award, 
  Flame, 
  TrendingUp, 
  CheckCircle2, 
  ArrowRight,
  Sparkles,
  Calendar,
  Lock
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

  const fillQuickAccount = (roleEmail: string) => {
    setEmail(roleEmail);
    setPassword('Password123@');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-[#FF4B4B] selection:text-white">
      {/* Top Header / Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-[#FF4B4B] via-red-500 to-rose-400 flex items-center justify-center text-white shadow-lg shadow-red-500/25">
              <Dumbbell className="w-6 h-6 transform -rotate-12" />
            </div>
            <div>
              <span className="text-xl font-black tracking-tight text-white flex items-center gap-1.5">
                PT CONNECT <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/20 text-[#FF4B4B] border border-red-500/30 font-semibold tracking-normal">VIETNAM</span>
              </span>
              <p className="text-[11px] text-slate-400 font-medium">Hệ Sinh Thái Huấn Luyện Viên Cá Nhân Chuyên Nghiệp</p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-6 text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>100% PT Kiểm Duyệt Chứng Chỉ</span>
            </div>
            <div className="flex items-center gap-1 text-amber-400 font-semibold">
              <Star className="w-4 h-4 fill-amber-400" />
              <span>4.9/5 (12,800+ đánh giá)</span>
            </div>
            <a 
              href="#login-section"
              className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium border border-slate-700 transition"
            >
              Vào ứng dụng
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section - California Fitness Vibe */}
      <section className="relative overflow-hidden pt-12 pb-16 lg:pt-16 lg:pb-24">
        {/* Glow Effects */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[350px] bg-red-600/15 blur-[120px] rounded-full pointer-events-none" />
        <div className="absolute -top-10 right-10 w-72 h-72 bg-blue-600/10 blur-[90px] rounded-full pointer-events-none" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* Hero Top Badge */}
          <div className="text-center max-w-3xl mx-auto mb-10">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-red-500/10 border border-red-500/30 text-[#FF4B4B] text-xs font-semibold mb-6 shadow-sm shadow-red-500/10">
              <Sparkles className="w-3.5 h-3.5" />
              <span>TIÊU CHUẨN QUỐC TẾ NASM / ACE & BẢO LÃNH KẾT QUẢ</span>
            </div>

            <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-white tracking-tight uppercase leading-[1.15]">
              Chinh Phục Vóc Dáng Đỉnh Cao <br className="hidden sm:inline" />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#FF4B4B] via-rose-400 to-amber-300">
                Cùng Huấn Luyện Viên Riêng
              </span>
            </h1>

            <p className="mt-5 text-base sm:text-lg text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
              Nền tảng kết nối 1-kèm-1 tiên phong tại Việt Nam: Lộ trình cá nhân hóa khoa học, hợp đồng số bảo vệ quyền lợi học viên và theo dõi tiến độ biến chuyển cơ thể theo thời gian thực.
            </p>
          </div>

          {/* 4 Metric Stats Strip */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl mx-auto mb-14">
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-center backdrop-blur shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-white">50+</div>
              <div className="text-xs text-slate-400 mt-1 font-medium">Đối tác phòng Gym toàn quốc</div>
            </div>
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-center backdrop-blur shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-[#FF4B4B]">100%</div>
              <div className="text-xs text-slate-400 mt-1 font-medium">PT đạt chứng chỉ NASM/ACE</div>
            </div>
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-center backdrop-blur shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-white">18,500+</div>
              <div className="text-xs text-slate-400 mt-1 font-medium">Buổi tập đã hoàn thành an toàn</div>
            </div>
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 text-center backdrop-blur shadow-sm">
              <div className="text-2xl sm:text-3xl font-extrabold text-emerald-400">99.2%</div>
              <div className="text-xs text-slate-400 mt-1 font-medium">Học viên đạt mục tiêu thể hình</div>
            </div>
          </div>

          {/* Split Showcase - Trainerize Inspired Portal & Coach Showcase */}
          <div id="login-section" className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start max-w-6xl mx-auto">
            {/* Left Portal: Login / Register Glass Card */}
            <div className="lg:col-span-6 bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-2xl shadow-black/60 relative">
              <div className="flex border-b border-slate-800 mb-6">
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('LOGIN');
                    setError(null);
                  }}
                  className={`flex-1 pb-3 text-sm font-bold border-b-2 text-center transition-all ${
                    activeTab === 'LOGIN'
                      ? 'border-[#FF4B4B] text-[#FF4B4B]'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Đăng Nhập Cổng Tập
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setActiveTab('REGISTER');
                    setError(null);
                  }}
                  className={`flex-1 pb-3 text-sm font-bold border-b-2 text-center transition-all ${
                    activeTab === 'REGISTER'
                      ? 'border-[#FF4B4B] text-[#FF4B4B]'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Tạo Tài Khoản Mới
                </button>
              </div>

              {error && (
                <div className="mb-5 p-3 rounded-xl bg-red-950/60 border border-red-500/40 text-red-200 text-xs flex items-center gap-2.5">
                  <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                  <span>{error}</span>
                </div>
              )}

              {regSuccess && (
                <div className="mb-5 p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/40 text-emerald-200 text-xs flex items-center gap-2.5">
                  <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400" />
                  <span>{regSuccess}</span>
                </div>
              )}

              {activeTab === 'LOGIN' ? (
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Email đăng nhập
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="vd: student_24@ptconnect.vn"
                      className="mt-1.5 block w-full px-4 py-3 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B] focus:border-[#FF4B4B] transition"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between items-center">
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Mật khẩu
                      </label>
                      <span className="text-[11px] text-slate-400 cursor-default">Mặc định: Password123@</span>
                    </div>
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Nhập mật khẩu"
                      className="mt-1.5 block w-full px-4 py-3 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B] focus:border-[#FF4B4B] transition"
                    />
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full py-3.5 px-4 bg-gradient-to-r from-[#FF4B4B] to-rose-600 hover:from-red-600 hover:to-rose-700 text-white text-sm font-bold rounded-xl shadow-lg shadow-red-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {loading ? 'Đang xác thực thông tin...' : (
                        <>
                          <span>ĐĂNG NHẬP VÀO HỆ THỐNG</span>
                          <ArrowRight className="w-4 h-4" />
                        </>
                      )}
                    </button>
                  </div>

                  {/* Fast Demo Accounts Toolbar */}
                  <div className="mt-6 pt-5 border-t border-slate-800">
                    <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                      <span>Chọn nhanh tài khoản trải nghiệm (1-Click Fill):</span>
                    </div>
                    <div className="grid grid-cols-3 gap-2">
                      <button
                        type="button"
                        onClick={() => fillQuickAccount('student_24@ptconnect.vn')}
                        className="p-2 rounded-lg bg-blue-950/40 border border-blue-500/30 hover:border-blue-400 text-left transition group"
                      >
                        <div className="text-[11px] font-bold text-blue-400 group-hover:text-blue-300">Học Viên Active</div>
                        <div className="text-[10px] text-slate-400 truncate">student_24</div>
                      </button>

                      <button
                        type="button"
                        onClick={() => fillQuickAccount('pt.hoangc@ptconnect.vn')}
                        className="p-2 rounded-lg bg-orange-950/40 border border-orange-500/30 hover:border-orange-400 text-left transition group"
                      >
                        <div className="text-[11px] font-bold text-orange-400 group-hover:text-orange-300">Huấn Luyện Viên</div>
                        <div className="text-[10px] text-slate-400 truncate">pt.hoangc</div>
                      </button>

                      <button
                        type="button"
                        onClick={() => fillQuickAccount('admin@ptconnect.vn')}
                        className="p-2 rounded-lg bg-purple-950/40 border border-purple-500/30 hover:border-purple-400 text-left transition group"
                      >
                        <div className="text-[11px] font-bold text-purple-400 group-hover:text-purple-300">Quản Trị Viên</div>
                        <div className="text-[10px] text-slate-400 truncate">admin</div>
                      </button>
                    </div>
                  </div>
                </form>
              ) : (
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Vai trò đăng ký
                    </label>
                    <div className="grid grid-cols-2 gap-3 mt-1.5">
                      <button
                        type="button"
                        onClick={() => setRegRole('STUDENT')}
                        className={`py-2.5 px-3 text-xs font-bold rounded-xl border text-center flex items-center justify-center gap-1.5 transition-all ${
                          regRole === 'STUDENT'
                            ? 'border-blue-500 bg-blue-950/60 text-blue-300 ring-2 ring-blue-500/30'
                            : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <UserCheck className="w-4 h-4 text-blue-400" /> Học Viên (Student)
                      </button>
                      <button
                        type="button"
                        onClick={() => setRegRole('PT')}
                        className={`py-2.5 px-3 text-xs font-bold rounded-xl border text-center flex items-center justify-center gap-1.5 transition-all ${
                          regRole === 'PT'
                            ? 'border-orange-500 bg-orange-950/60 text-orange-300 ring-2 ring-orange-500/30'
                            : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <Dumbbell className="w-4 h-4 text-orange-400" /> Huấn Luyện Viên (PT)
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Họ và tên
                    </label>
                    <input
                      type="text"
                      required
                      value={regFullName}
                      onChange={(e) => setRegFullName(e.target.value)}
                      placeholder="vd: Trần Đức Thành"
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Địa chỉ Email
                    </label>
                    <input
                      type="email"
                      required
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      placeholder="name@ptconnect.vn"
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Số điện thoại liên hệ
                    </label>
                    <input
                      type="tel"
                      required
                      value={regPhone}
                      onChange={(e) => setRegPhone(e.target.value)}
                      placeholder="0912345678"
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                      Mật khẩu khởi tạo
                    </label>
                    <input
                      type="password"
                      required
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      placeholder="Tối thiểu 6 ký tự"
                      className="mt-1.5 block w-full px-4 py-2.5 bg-slate-950/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                    />
                  </div>

                  <div className="pt-2">
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-full py-3.5 px-4 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-lg shadow-red-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50"
                    >
                      {loading ? 'Đang tạo hồ sơ...' : 'HOÀN TẤT ĐĂNG KÝ HỌC THỬ'}
                    </button>
                  </div>
                </form>
              )}
            </div>

            {/* Right Column: Trainerize-Inspired Interactive Showcase & PT Preview */}
            <div className="lg:col-span-6 space-y-6">
              {/* Feature PT Showcase Spotlight Card */}
              <div className="bg-gradient-to-br from-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xl relative overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" /> HLV Trưởng Tuần Này
                    </span>
                    <span className="px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs font-semibold flex items-center gap-1">
                      <Star className="w-3 h-3 fill-amber-400" /> 5.0 (48 Học viên)
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">NASM Master CPT</span>
                </div>

                <div className="flex items-center gap-4">
                  <img
                    src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=200"
                    alt="HLV Hoàng Minh Cường"
                    className="w-20 h-20 rounded-2xl object-cover border-2 border-red-500/40 shadow-lg"
                  />
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-1.5">
                      HLV Hoàng Minh Cường
                      <Award className="w-4 h-4 text-[#FF4B4B]" />
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">California Centuryon & Elite Fitness Trainer</p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      <span className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md">Giảm mỡ siết cơ</span>
                      <span className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md">Chỉnh vẹo cột sống</span>
                      <span className="text-[10px] px-2 py-0.5 bg-slate-800 text-slate-300 rounded-md">Dinh dưỡng khoa học</span>
                    </div>
                  </div>
                </div>

                {/* Trainerize-style Live Transformation Progress Box */}
                <div className="mt-5 p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80">
                  <div className="flex justify-between items-center text-xs mb-2">
                    <span className="font-semibold text-slate-300 flex items-center gap-1.5">
                      <Flame className="w-3.5 h-3.5 text-[#FF4B4B]" /> Gói Huấn Luyện 1-kèm-1: 30 Buổi Thần Tốc
                    </span>
                    <span className="text-emerald-400 font-bold">Hoàn thành 80%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                    <div className="bg-gradient-to-r from-[#FF4B4B] to-emerald-400 h-full rounded-full" style={{ width: '80%' }} />
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-400 mt-2">
                    <span>Đã tập: 24/30 buổi</span>
                    <span>Chỉ số giảm mỡ: -6.4 kg</span>
                  </div>
                </div>

                {/* Student Review Snippet */}
                <div className="mt-4 pt-4 border-t border-slate-800/80 text-xs text-slate-300 italic flex items-start gap-2">
                  <span className="text-xl text-[#FF4B4B] leading-none">“</span>
                  <div>
                    Sau 2 tháng tập cùng PT Cường qua hệ thống PT Connect, thể lực mình cải thiện rõ rệt. Lịch tập đặt linh hoạt trên app, hợp đồng điện tử minh bạch khiến mình hoàn toàn an tâm!
                    <div className="mt-1 text-[11px] font-semibold text-slate-400 not-italic">— Nguyễn Văn Tuấn (Hội viên Diamond)</div>
                  </div>
                </div>
              </div>

              {/* 3 Core Platform Guarantees */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-center">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center mx-auto mb-2">
                    <Lock className="w-4 h-4" />
                  </div>
                  <div className="text-xs font-bold text-white">Hợp Đồng Số</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">Bảo lãnh hoàn tiền 100% nếu không đạt cam kết</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-center">
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto mb-2">
                    <Calendar className="w-4 h-4" />
                  </div>
                  <div className="text-xs font-bold text-white">Đặt Lịch 24/7</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">Chủ động chọn giờ tập và dời lịch không mất phí</div>
                </div>

                <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800 text-center">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center mx-auto mb-2">
                    <TrendingUp className="w-4 h-4" />
                  </div>
                  <div className="text-xs font-bold text-white">Theo Dõi InBody</div>
                  <div className="text-[11px] text-slate-400 mt-0.5">Biểu đồ cơ mỡ được cập nhật từng tuần</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-8 mt-auto text-xs text-slate-500 text-center">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Dumbbell className="w-4 h-4 text-[#FF4B4B]" />
            <span className="font-semibold text-slate-400">PT Connect Ecosystem</span>
            <span>— Bản quyền © 2026. Chuẩn mực huấn luyện cá nhân Việt Nam.</span>
          </div>
          <div className="flex gap-4 text-slate-400">
            <span>Tiêu chuẩn NASM</span>
            <span>•</span>
            <span>ACE Fitness</span>
            <span>•</span>
            <span>Bảo mật AES-256</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
