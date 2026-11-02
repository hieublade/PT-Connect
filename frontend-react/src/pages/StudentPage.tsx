import React, { useState, useEffect } from 'react';
import api from '../lib/axios';
import { User, PtProfile, Course, AvailabilitySlot, Booking, Wallet, Enrollment } from '../types/api';
import { PtCard } from '../components/PtCard';
import { CourseCard } from '../components/CourseCard';
import { SlotCard } from '../components/SlotCard';
import { BookingTable } from '../components/BookingTable';
import { AvatarUploader } from '../components/AvatarUploader';
import {
  Search,
  RotateCcw,
  Wallet as WalletIcon,
  Calendar,
  BookOpen,
  FileText,
  User as UserIcon,
  Dumbbell,
  LogOut,
  CreditCard,
  PlusCircle,
  Key,
} from 'lucide-react';

interface StudentPageProps {
  user: User;
  onLogout: () => void;
}

export const StudentPage: React.FC<StudentPageProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<number>(0);

  // Data states
  const [pts, setPts] = useState<PtProfile[]>([]);
  const [selectedPt, setSelectedPt] = useState<PtProfile | null>(null);
  const [ptCourses, setPtCourses] = useState<Course[]>([]);
  const [ptSlots, setPtSlots] = useState<AvailabilitySlot[]>([]);
  const [myBookings, setMyBookings] = useState<Booking[]>([]);
  const [myEnrollments, setMyEnrollments] = useState<Enrollment[]>([]);
  const [wallet, setWallet] = useState<Wallet | null>(null);

  // Search filter
  const [searchName, setSearchName] = useState('');
  const [loading, setLoading] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  // Modal / Action states
  const [otpModalBooking, setOtpModalBooking] = useState<Booking | null>(null);
  const [otpCode, setOtpCode] = useState<string | null>(null);
  const [topupAmount, setTopupAmount] = useState<number>(500000);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  };

  // 1. Load Initial Data
  useEffect(() => {
    fetchPts();
    fetchWallet();
    fetchMyBookings();
    fetchMyEnrollments();
  }, []);

  const fetchPts = async (nameQuery = '') => {
    try {
      const data: any = await api.get('/pt-profiles', { params: { name: nameQuery } });
      setPts(data || []);
      if (data && data.length > 0 && !selectedPt) {
        loadPtDetails(data[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadPtDetails = async (pt: PtProfile) => {
    setSelectedPt(pt);
    try {
      const courses: any = await api.get(`/pt-profiles/${pt.id}/courses`);
      setPtCourses(courses || []);
      const slots: any = await api.get(`/pt-profiles/${pt.id}/slots`);
      setPtSlots(slots || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchWallet = async () => {
    try {
      const data: any = await api.get('/wallet');
      setWallet(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMyBookings = async () => {
    try {
      const data: any = await api.get('/student/bookings');
      setMyBookings(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMyEnrollments = async () => {
    try {
      const data: any = await api.get('/student/enrollments');
      setMyEnrollments(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleEnrollCourse = async (course: Course) => {
    try {
      await api.post(`/student/courses/${course.id}/enroll`);
      showToast(`Đăng ký khóa học "${course.title}" thành công!`);
      fetchWallet();
      fetchMyEnrollments();
      setActiveTab(4); // Switch to My Courses
    } catch (err: any) {
      showToast(err.message || 'Lỗi đăng ký khóa học.');
    }
  };

  const handleBookSlot = async (slot: AvailabilitySlot) => {
    try {
      await api.post('/student/bookings', {
        slotId: slot.id,
        bookingType: 'TRIAL',
      });
      showToast('Đặt lịch ca tập thành công!');
      fetchMyBookings();
      if (selectedPt) loadPtDetails(selectedPt);
      setActiveTab(3); // Switch to My Schedule
    } catch (err: any) {
      showToast(err.message || 'Lỗi đặt lịch ca tập.');
    }
  };

  const handleGetOtp = async (booking: Booking) => {
    try {
      const res: any = await api.post(`/attendance/bookings/${booking.id}/otp/generate`);
      setOtpCode(res.otp || '849201');
      setOtpModalBooking(booking);
    } catch (err: any) {
      showToast(err.message || 'Không thể tạo mã OTP lúc này.');
    }
  };

  const handleTopup = async () => {
    try {
      await api.post('/wallet/topup', { amount: topupAmount, paymentMethod: 'BANK_TRANSFER' });
      showToast(`Đã nạp ${topupAmount.toLocaleString('vi-VN')} ₫ vào ví thành công!`);
      fetchWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi nạp tiền.');
    }
  };

  const tabs = [
    { label: 'Khám Phá PT', icon: Search },
    { label: 'Chi Tiết PT', icon: UserIcon },
    { label: 'Đặt Lịch', icon: Calendar },
    { label: 'Lịch Của Tôi', icon: Dumbbell },
    { label: `Khóa Của Tôi (${myEnrollments.length})`, icon: BookOpen },
    { label: 'Ví Tiền', icon: WalletIcon },
    { label: 'Hồ Sơ', icon: FileText },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#FF4B4B] text-white flex items-center justify-center font-bold text-lg shadow-sm">
              PT
            </div>
            <div>
              <span className="font-extrabold text-slate-900 text-lg tracking-tight">PT Connect</span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                Học viên
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-bold text-slate-900">{user.fullName}</div>
              <div className="text-xs text-slate-500">{user.email}</div>
            </div>
            <img
              src={user.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.fullName}`}
              alt={user.fullName}
              className="w-9 h-9 rounded-full border border-slate-200 object-cover"
            />
            <button
              onClick={onLogout}
              className="px-3 py-1.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5"
            >
              <LogOut className="w-3.5 h-3.5" /> Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Hero Header Banner */}
      <div className="bg-gradient-to-r from-blue-700 to-indigo-800 text-white py-6 px-4 sm:px-8 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <img
              src={user.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.fullName}`}
              alt={user.fullName}
              className="w-16 h-16 rounded-full border-2 border-white/80 bg-white/10"
            />
            <div>
              <h2 className="text-2xl font-extrabold">Chào mừng bạn, {user.fullName}!</h2>
              <p className="text-blue-100 text-xs sm:text-sm mt-0.5">
                Không gian rèn luyện, đặt lịch Huấn luyện viên & quản lý hợp đồng tập luyện tại PT Connect
              </p>
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/20 flex items-center gap-6">
            <div>
              <span className="text-[11px] text-blue-200 block uppercase font-medium">Số dư ví khả dụng</span>
              <span className="text-xl font-extrabold text-white">
                {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
              </span>
            </div>
            <div className="border-l border-white/20 pl-6 hidden md:block">
              <span className="text-[11px] text-blue-200 block uppercase font-medium">Gói tập đã đăng ký</span>
              <span className="text-xl font-extrabold text-white">{myEnrollments.length} khóa</span>
            </div>
          </div>
        </div>
      </div>

      {/* Toast Alert */}
      {toastMsg && (
        <div className="fixed bottom-5 right-5 z-50 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-2xl text-sm flex items-center gap-2 animate-bounce">
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 sm:space-x-8 overflow-x-auto py-2">
            {tabs.map((t, idx) => {
              const Icon = t.icon;
              const isCur = activeTab === idx;
              return (
                <button
                  key={t.label}
                  onClick={() => setActiveTab(idx)}
                  className={`flex items-center gap-2 py-2 px-3 text-sm font-semibold rounded-lg whitespace-nowrap transition-all ${
                    isCur
                      ? 'bg-red-50 text-[#FF4B4B]'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isCur ? 'text-[#FF4B4B]' : 'text-slate-400'}`} />
                  {t.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Tab Content Body */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* TAB 0: KHÁM PHÁ PT */}
        {activeTab === 0 && (
          <div className="space-y-6">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-lg font-bold text-slate-900 mb-2">Tìm Kiếm & Khám Phá Huấn Luyện Viên (PT)</h3>
              <div className="flex gap-3">
                <div className="relative flex-1">
                  <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                  <input
                    type="text"
                    value={searchName}
                    onChange={(e) => setSearchName(e.target.value)}
                    placeholder="Nhập tên PT (ví dụ: Le Hoang C, Pham Minh D...)"
                    className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                  />
                </div>
                <button
                  onClick={() => fetchPts(searchName)}
                  className="px-4 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-sm"
                >
                  Tìm kiếm
                </button>
                <button
                  onClick={() => {
                    setSearchName('');
                    fetchPts('');
                  }}
                  className="px-4 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-semibold rounded-lg flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Làm mới
                </button>
              </div>
            </div>

            <div>
              <p className="text-sm font-semibold text-slate-700 mb-4">
                Tìm thấy {pts.length} Huấn luyện viên chuyên nghiệp:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {pts.map((pt) => (
                  <PtCard
                    key={pt.id}
                    pt={pt}
                    onSelect={(selected) => {
                      loadPtDetails(selected);
                      setActiveTab(1); // Go to Detail
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 1: CHI TIẾT PT */}
        {activeTab === 1 && selectedPt && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-6 items-start">
              <img
                src={selectedPt.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${selectedPt.fullName}`}
                alt={selectedPt.fullName}
                className="w-24 h-24 rounded-2xl border border-slate-200 object-cover"
              />
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-2xl font-extrabold text-slate-900">{selectedPt.fullName}</h3>
                  <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-0.5 rounded-full border border-emerald-300">
                    Đã xác minh
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-1">{selectedPt.bio}</p>
                <div className="flex items-center gap-4 mt-3 text-xs text-slate-600">
                  <span><b>Kinh nghiệm:</b> {selectedPt.experienceYears} năm</span>
                  <span><b>Khu vực:</b> {selectedPt.availableLocations}</span>
                  <span><b>Đánh giá:</b> {selectedPt.averageRating.toFixed(1)}/5 ⭐ ({selectedPt.totalReviews} lượt)</span>
                </div>
              </div>
              <button
                onClick={() => setActiveTab(2)}
                className="px-5 py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-lg shadow-sm whitespace-nowrap"
              >
                Đặt Lịch Ngay
              </button>
            </div>

            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-4">Các Khóa Học Huấn Luyện Cố Định</h4>
              {ptCourses.length === 0 ? (
                <p className="text-sm text-slate-500">PT này chưa mở gói khóa học nào.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {ptCourses.map((c) => (
                    <CourseCard key={c.id} course={c} onEnroll={handleEnrollCourse} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: ĐẶT LỊCH */}
        {activeTab === 2 && (
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
            <h3 className="text-xl font-bold text-slate-900">Đặt Lịch Tập Cùng Huấn Luyện Viên</h3>
            {selectedPt ? (
              <>
                <p className="text-sm text-slate-600">
                  Đang xem khung giờ khả dụng của <b>{selectedPt.fullName}</b>. Nhấp vào khung giờ trống để đặt lịch:
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {ptSlots
                    .filter((s) => s.status === 'AVAILABLE')
                    .map((slot) => (
                      <SlotCard key={slot.id} slot={slot} selectable onSelect={handleBookSlot} />
                    ))}
                </div>
                {ptSlots.filter((s) => s.status === 'AVAILABLE').length === 0 && (
                  <p className="text-sm text-slate-500 italic">Hiện không có khung giờ trống nào trong tương lai.</p>
                )}
              </>
            ) : (
              <p className="text-sm text-slate-500">Vui lòng chọn một Huấn luyện viên ở tab Khám Phá PT trước.</p>
            )}
          </div>
        )}

        {/* TAB 3: LỊCH CỦA TÔI */}
        {activeTab === 3 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Lịch Tập Luyện Của Tôi</h3>
            <BookingTable
              bookings={myBookings}
              onGetOtp={handleGetOtp}
              onCancel={async (b) => {
                if (confirm('Bạn có chắc chắn muốn hủy ca tập này không?')) {
                  await api.post(`/student/bookings/${b.id}/cancel`, { reason: 'Bận việc cá nhân' });
                  showToast('Đã hủy ca tập thành công!');
                  fetchMyBookings();
                }
              }}
            />
          </div>
        )}

        {/* TAB 4: KHÓA CỦA TÔI */}
        {activeTab === 4 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Danh Sách Gói Tập Đã Đăng Ký & Hợp Đồng</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {myEnrollments.map((en) => (
                <div key={en.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="text-base font-bold text-slate-900">Hợp đồng #{en.id}</h4>
                      <p className="text-xs text-slate-500 mt-1">Khóa học ID: #{en.courseId}</p>
                    </div>
                    <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                      {en.status}
                    </span>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-700">
                    <span>Số buổi còn lại: <b>{en.remainingSessions} / {en.totalSessions} buổi</b></span>
                    <button
                      onClick={async () => {
                        const blob = await api.get(`/student/enrollments/${en.id}/contract`, { responseType: 'blob' });
                        const url = window.URL.createObjectURL(new Blob([blob as any]));
                        const link = document.createElement('a');
                        link.href = url;
                        link.setAttribute('download', `HopDong_KhoaHoc_${en.id}.pdf`);
                        document.body.appendChild(link);
                        link.click();
                      }}
                      className="px-3 py-1.5 border border-blue-600 text-blue-700 hover:bg-blue-50 rounded-lg font-semibold flex items-center gap-1.5"
                    >
                      <FileText className="w-3.5 h-3.5" /> Tải hợp đồng PDF
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: VÍ TIỀN */}
        {activeTab === 5 && wallet && (
          <div className="space-y-6">
            <div className="bg-gradient-to-tr from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-lg max-w-md">
              <div className="flex items-center justify-between text-slate-300 text-xs uppercase tracking-wider font-semibold">
                <span>Ví Điện Tử Nội Bộ</span>
                <CreditCard className="w-5 h-5" />
              </div>
              <div className="mt-4 text-3xl font-extrabold text-white">
                {wallet.balance.toLocaleString('vi-VN')} ₫
              </div>
              <div className="mt-2 text-xs text-slate-400">
                Đóng băng (giữ chỗ ca tập): {wallet.lockedBalance.toLocaleString('vi-VN')} ₫
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 max-w-md space-y-4">
              <h4 className="text-base font-bold text-slate-900">Nạp Tiền Vào Ví</h4>
              <div className="flex gap-2">
                {[200000, 500000, 1000000, 2000000].map((amt) => (
                  <button
                    key={amt}
                    onClick={() => setTopupAmount(amt)}
                    className={`flex-1 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                      topupAmount === amt ? 'bg-red-50 border-[#FF4B4B] text-[#FF4B4B]' : 'border-slate-200 text-slate-600'
                    }`}
                  >
                    +{(amt / 1000).toLocaleString()}k
                  </button>
                ))}
              </div>
              <button
                onClick={handleTopup}
                className="w-full py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-sm flex items-center justify-center gap-2"
              >
                <PlusCircle className="w-4 h-4" /> Nạp tiền vào ví
              </button>
            </div>
          </div>
        )}

        {/* TAB 6: HỒ SƠ */}
        {activeTab === 6 && (
          <div className="space-y-6">
            <AvatarUploader
              currentUrl={user.avatarUrl}
              onUpload={async (url) => {
                await api.put('/users/me/avatar', { avatarUrl: url });
                showToast('Đã lưu ảnh đại diện!');
              }}
            />
          </div>
        )}
      </main>

      {/* OTP Modal Dialog */}
      {otpModalBooking && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 text-center shadow-2xl">
            <div className="w-12 h-12 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center mx-auto mb-3">
              <Key className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-slate-900">Mã Điểm Danh Ca Tập</h4>
            <p className="text-xs text-slate-500 mt-1">Đưa mã 6 chữ số này cho Huấn luyện viên khi hoàn thành ca tập:</p>
            <div className="my-5 py-3 px-6 bg-slate-100 border border-slate-300 rounded-xl font-mono text-3xl font-extrabold tracking-widest text-[#FF4B4B]">
              {otpCode || '849201'}
            </div>
            <button
              onClick={() => {
                setOtpModalBooking(null);
                setOtpCode(null);
              }}
              className="w-full py-2 bg-slate-800 hover:bg-slate-900 text-white text-sm font-semibold rounded-lg"
            >
              Đóng
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
