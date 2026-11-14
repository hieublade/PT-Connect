import React, { useState } from 'react';
import api from '../lib/axios';
import { User } from '../types/api';
import { Dumbbell, ShieldCheck, UserCheck, AlertCircle, Lock } from 'lucide-react';

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
  const [regBio, setRegBio] = useState('');
  const [regExperience, setRegExperience] = useState<number>(0);
  const [regLocations, setRegLocations] = useState('');
  const [regPricingNote, setRegPricingNote] = useState('');
  const [regCertificateUrl, setRegCertificateUrl] = useState('');
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
      const cert = regCertificateUrl.trim();
      if (regRole === 'PT' && cert && !/^https?:\/\//i.test(cert)) {
        setError('Đường dẫn chứng chỉ phải bắt đầu bằng http:// hoặc https://');
        setLoading(false);
        return;
      }
      const payload: Record<string, unknown> = {
        fullName: regFullName.trim(),
        email: regEmail.trim(),
        phone: regPhone.trim(),
        password: regPassword,
        role: regRole,
      };
      if (regRole === 'PT') {
        Object.assign(payload, {
          bio: regBio.trim() || undefined,
          experienceYears: Number(regExperience) || 0,
          availableLocations: regLocations.trim() || undefined,
          locationPricingNote: regPricingNote.trim() || undefined,
          certificateUrl: cert || undefined,
        });
      }
      await api.post('/auth/register', payload);
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

  const fillDemoAccount = (demoEmail: string) => {
    setEmail(demoEmail);
    setPassword('Password123@');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-slate-100/60 to-slate-50 flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative ambient background glows */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-rose-500/10 blur-[100px] pointer-events-none rounded-full" />
      <div className="absolute bottom-0 right-10 w-[400px] h-[300px] bg-orange-500/10 blur-[100px] pointer-events-none rounded-full" />

      {/* Brand Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center mb-6 relative z-10">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-50 border border-rose-200/80 text-rose-600 text-[11px] font-bold tracking-wide uppercase mb-3 shadow-xs">
          <Dumbbell className="w-3.5 h-3.5 text-rose-600" /> PTConnect Elite Platform
        </div>
        <div className="flex items-center justify-center gap-2 mb-2">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-rose-600 via-rose-500 to-orange-500 text-white shadow-md shadow-rose-500/25 flex items-center justify-center font-black text-xl">
            PT
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">PT-Connect</h1>
        </div>
        <p className="mt-1 text-xs sm:text-sm text-slate-500 font-medium">
          Nền tảng kết nối Huấn luyện viên cá nhân &amp; Đảm bảo hợp đồng minh bạch
        </p>
      </div>

      {/* Main Card */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="bg-white/95 backdrop-blur-md py-8 px-6 sm:px-8 rounded-3xl border border-slate-200/90 shadow-xl shadow-slate-200/50">
          
          {/* Linear / iOS Style Segmented Control */}
          <div className="flex bg-slate-100 p-1 rounded-xl mb-6">
            <button
              type="button"
              onClick={() => {
                setActiveTab('LOGIN');
                setError(null);
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'LOGIN'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Đăng nhập
            </button>
            <button
              type="button"
              onClick={() => {
                setActiveTab('REGISTER');
                setError(null);
              }}
              className={`flex-1 py-2 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'REGISTER'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              Đăng ký tài khoản
            </button>
          </div>

          {error && (
            <div
              className={`mb-5 p-4 rounded-xl border flex items-start gap-3 shadow-sm transition-all ${
                error.toLowerCase().includes('khóa')
                  ? 'bg-rose-50 border-rose-300 text-rose-900'
                  : 'bg-red-50 border-red-200 text-red-800'
              }`}
            >
              {error.toLowerCase().includes('khóa') ? (
                <Lock className="w-5 h-5 shrink-0 text-rose-600 mt-0.5" />
              ) : (
                <AlertCircle className="w-5 h-5 shrink-0 text-red-500 mt-0.5" />
              )}
              <div className="flex-1 text-xs">
                <p className="font-bold text-sm">
                  {error.toLowerCase().includes('khóa') ? 'Tài khoản đã bị tạm khóa' : 'Đăng nhập không thành công'}
                </p>
                <p className="mt-1 leading-relaxed text-xs">
                  {error.toLowerCase().includes('khóa')
                    ? 'Tài khoản của bạn đã bị khóa do vi phạm quy định hoặc chính sách hệ thống. Vui lòng liên hệ Quản trị viên (Admin) để được hỗ trợ xử lý.'
                    : error}
                </p>
              </div>
            </div>
          )}

          {regSuccess && (
            <div className="mb-5 p-3 rounded-lg bg-emerald-50 border border-emerald-200/80 text-emerald-800 text-xs flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-600" />
              <span>{regSuccess}</span>
            </div>
          )}

          {activeTab === 'LOGIN' ? (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@ptconnect.vn"
                  className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="block text-xs font-medium text-slate-700">
                    Mật khẩu
                  </label>
                  <span className="text-[11px] text-slate-400 font-mono">Password123@</span>
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Nhập mật khẩu"
                  className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-10 bg-[#FF4B4B] hover:bg-[#e03e3e] active:scale-[0.99] text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50"
                >
                  {loading ? 'Đang xác thực...' : 'Đăng nhập'}
                </button>
              </div>

              {/* Minimalist Demo Accounts Bar */}
              <div className="mt-6 pt-5 border-t border-slate-100">
                <div className="flex items-center justify-between text-[11px] text-slate-500 mb-2.5">
                  <span className="font-bold text-slate-700 flex items-center gap-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-rose-500" /> Tài khoản mẫu kiểm thử:
                  </span>
                  <span className="text-[10px] text-slate-400 font-semibold">1-chạm để điền</span>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => fillDemoAccount('student_24@ptconnect.vn')}
                    className="py-2 px-2 bg-slate-50 hover:bg-rose-50/60 hover:border-rose-300 border border-slate-200/90 rounded-xl text-[11px] font-bold text-slate-700 hover:text-rose-700 text-center transition-all shadow-2xs active:scale-[0.98] cursor-pointer"
                  >
                    <span className="block text-[9px] uppercase font-black text-rose-500">Student</span>
                    Học viên (24)
                  </button>
                  <button
                    type="button"
                    onClick={() => fillDemoAccount('pt.hoangc@ptconnect.vn')}
                    className="py-2 px-2 bg-slate-50 hover:bg-orange-50/60 hover:border-orange-300 border border-slate-200/90 rounded-xl text-[11px] font-bold text-slate-700 hover:text-orange-700 text-center transition-all shadow-2xs active:scale-[0.98] cursor-pointer"
                  >
                    <span className="block text-[9px] uppercase font-black text-orange-500">Trainer</span>
                    Huấn luyện viên
                  </button>
                  <button
                    type="button"
                    onClick={() => fillDemoAccount('admin@ptconnect.vn')}
                    className="py-2 px-2 bg-slate-50 hover:bg-indigo-50/60 hover:border-indigo-300 border border-slate-200/90 rounded-xl text-[11px] font-bold text-slate-700 hover:text-indigo-700 text-center transition-all shadow-2xs active:scale-[0.98] cursor-pointer"
                  >
                    <span className="block text-[9px] uppercase font-black text-indigo-500">Admin</span>
                    Quản trị viên
                  </button>
                </div>
              </div>
            </form>
          ) : (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Vai trò tài khoản
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setRegRole('STUDENT')}
                    className={`py-2 px-3 text-xs font-medium rounded-lg border text-center transition-all ${
                      regRole === 'STUDENT'
                        ? 'border-[#FF4B4B] bg-red-50/50 text-[#FF4B4B] font-semibold'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    Học viên
                  </button>
                  <button
                    type="button"
                    onClick={() => setRegRole('PT')}
                    className={`py-2 px-3 text-xs font-medium rounded-lg border text-center transition-all ${
                      regRole === 'PT'
                        ? 'border-[#FF4B4B] bg-red-50/50 text-[#FF4B4B] font-semibold'
                        : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    Huấn luyện viên
                  </button>
                </div>
              </div>

              {regRole === 'PT' && (
                <div className="space-y-3 p-3 rounded-lg border border-amber-200 bg-amber-50/40">
                  <p className="text-xs font-semibold text-amber-800">
                    Hồ sơ chuyên môn HLV (sẽ được Admin xét duyệt)
                  </p>
                  <textarea
                    rows={2}
                    value={regBio}
                    onChange={(e) => setRegBio(e.target.value)}
                    placeholder="Giới thiệu ngắn bản thân"
                    className="w-full p-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                  />
                  <input
                    type="number"
                    min={0}
                    max={50}
                    value={regExperience}
                    onChange={(e) => setRegExperience(Number(e.target.value))}
                    placeholder="Số năm kinh nghiệm"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                  />
                  <input
                    value={regLocations}
                    onChange={(e) => setRegLocations(e.target.value)}
                    placeholder="Khu vực nhận dạy (VD: Cầu Giấy; Đống Đa)"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                  />
                  <input
                    value={regPricingNote}
                    onChange={(e) => setRegPricingNote(e.target.value)}
                    placeholder="Ghi chú giá theo địa điểm"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                  />
                  <input
                    type="url"
                    maxLength={500}
                    value={regCertificateUrl}
                    onChange={(e) => setRegCertificateUrl(e.target.value)}
                    placeholder="Link chứng chỉ hành nghề (https://...)"
                    className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Họ và tên
                </label>
                <input
                  type="text"
                  required
                  value={regFullName}
                  onChange={(e) => setRegFullName(e.target.value)}
                  placeholder="Nguyễn Văn A"
                  className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Email
                </label>
                <input
                  type="email"
                  required
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  placeholder="name@ptconnect.vn"
                  className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Số điện thoại
                </label>
                <input
                  type="tel"
                  required
                  value={regPhone}
                  onChange={(e) => setRegPhone(e.target.value)}
                  placeholder="0912345678"
                  className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1.5">
                  Mật khẩu
                </label>
                <input
                  type="password"
                  required
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="Tối thiểu 6 ký tự"
                  className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 placeholder:text-slate-400 focus:border-[#FF4B4B] focus:ring-1 focus:ring-[#FF4B4B] outline-none transition"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-10 bg-[#FF4B4B] hover:bg-[#e03e3e] active:scale-[0.99] text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50"
                >
                  {loading ? 'Đang tạo tài khoản...' : 'Tạo tài khoản'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
