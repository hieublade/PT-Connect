import React, { useState, useEffect } from 'react';
import api from '../lib/axios';
import { PtProfile, Course, AvailabilitySlot, Booking, Wallet, Enrollment, User } from '../types/api';
import { PtCard } from '../components/PtCard';
import { CourseCard } from '../components/CourseCard';
import { SlotCard } from '../components/SlotCard';
import { BookingTable } from '../components/BookingTable';
import { AvatarUploader } from '../components/AvatarUploader';
import {
  Search,
  Compass,
  UserCheck,
  Calendar,
  Clock,
  BookOpen,
  Wallet as WalletIcon,
  User as UserIcon,
  LogOut,
  RotateCcw,
  FileText,
  Key,
  PlusCircle,
  CreditCard,
} from 'lucide-react';

interface StudentPageProps {
  user: User;
  onLogout: () => void;
}

export const StudentPage: React.FC<StudentPageProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [pts, setPts] = useState<PtProfile[]>([]);
  const [selectedPt, setSelectedPt] = useState<PtProfile | null>(null);
  const [ptCourses, setPtCourses] = useState<Course[]>([]);
  const [ptSlots, setPtSlots] = useState<AvailabilitySlot[]>([]);
  const [myBookings, setMyBookings] = useState<Booking[]>([]);
  const [myEnrollments, setMyEnrollments] = useState<Enrollment[]>([]);
  const [wallet, setWallet] = useState<Wallet | null>(null);

  const [searchName, setSearchName] = useState<string>('');
  const [topupAmount, setTopupAmount] = useState<number>(2000000);
  const [topupMethod, setTopupMethod] = useState<string>('BANK_TRANSFER');
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  // OTP Modal
  const [otpModalBooking, setOtpModalBooking] = useState<Booking | null>(null);
  const [otpCode, setOtpCode] = useState<string>('');

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  useEffect(() => {
    fetchPts();
    fetchWallet();
    fetchMyBookings();
    fetchMyEnrollments();
  }, []);

  const fetchPts = async (nameQuery = '') => {
    try {
      const url = nameQuery ? `/pt-profiles?name=${encodeURIComponent(nameQuery)}` : '/pt-profiles';
      const data: any = await api.get(url);
      setPts(data || []);
      if (data && data.length > 0 && !selectedPt) {
        setSelectedPt(data[0]);
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
      const data: any = await api.get('/bookings/my');
      setMyBookings(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMyEnrollments = async () => {
    try {
      const data: any = await api.get('/enrollments/my');
      setMyEnrollments(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleEnrollCourse = async (course: Course) => {
    try {
      await api.post('/enrollments', {
        courseId: course.id,
        trainingLocation: course.trainingLocation || selectedPt?.availableLocations || 'Phòng tập cơ sở chính',
        paymentMethod: 'WALLET',
      });
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
      await api.post('/bookings', {
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
      await api.post('/wallet/topup', { amount: topupAmount, paymentMethod: topupMethod });
      showToast(`Đã nạp ${topupAmount.toLocaleString('vi-VN')} ₫ vào ví thành công!`);
      fetchWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi nạp tiền.');
    }
  };

  const totalRemainingSessions = myEnrollments.reduce((acc, curr) => acc + (curr.remainingSessions || 0), 0);

  const tabs = [
    { label: 'Khám Phá PT', icon: Compass },
    { label: 'Chi Tiết PT', icon: UserCheck },
    { label: 'Đặt Lịch', icon: Calendar },
    { label: 'Lịch Của Tôi', icon: Clock },
    { label: `Khóa Của Tôi (${myEnrollments.length})`, icon: BookOpen },
    { label: 'Ví Tiền', icon: WalletIcon },
    { label: 'Hồ Sơ', icon: UserIcon },
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
            <div className="border-l border-white/20 pl-6 hidden md:block">
              <span className="text-[11px] text-blue-200 block uppercase font-medium">Tổng buổi còn lại</span>
              <span className="text-xl font-extrabold text-white">{totalRemainingSessions} buổi</span>
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
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
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
                  className="px-5 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-sm"
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
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
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
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-6 items-start">
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
                className="px-5 py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-md"
              >
                Đặt Lịch Ngay
              </button>
            </div>

            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-4">Các Khóa Học Huấn Luyện Cố Định</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {ptCourses.map((c) => (
                  <CourseCard key={c.id} course={c} isStudentView onEnroll={handleEnrollCourse} />
                ))}
              </div>
              {ptCourses.length === 0 && (
                <div className="bg-white p-8 text-center rounded-xl border border-slate-200 text-slate-500 text-sm">
                  HLV này chưa tạo khóa học công khai nào.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: ĐẶT LỊCH */}
        {activeTab === 2 && (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
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
                  await api.put(`/bookings/${b.id}/cancel`, { reason: 'Bận việc cá nhân' });
                  showToast('Đã hủy ca tập thành công!');
                  fetchMyBookings();
                }
              }}
            />
          </div>
        )}

        {/* TAB 4: KHÓA CỦA TÔI & HỢP ĐỒNG */}
        {activeTab === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-slate-900">Danh Sách Gói Tập Đã Đăng Ký & Hợp Đồng</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Quản lý các hợp đồng huấn luyện viên, theo dõi số buổi tập còn lại và tải hợp đồng pháp lý PDF.
                </p>
              </div>
              <span className="bg-blue-50 text-blue-800 text-xs font-bold px-3 py-1 rounded-full border border-blue-200">
                {myEnrollments.length} gói tập kích hoạt
              </span>
            </div>

            {myEnrollments.length === 0 ? (
              <div className="bg-white p-12 text-center rounded-2xl border border-slate-200">
                <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <h4 className="text-base font-bold text-slate-700">Chưa có hợp đồng nào</h4>
                <p className="text-xs text-slate-500 mt-1 mb-4">
                  Bạn chưa đăng ký khóa học nào. Hãy khám phá và chọn Huấn luyện viên phù hợp ở tab Khám Phá PT nhé!
                </p>
                <button
                  onClick={() => setActiveTab(0)}
                  className="px-4 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-xs font-semibold rounded-lg shadow-sm"
                >
                  Khám Phá PT Ngay
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {myEnrollments.map((en) => {
                  const completed = en.totalSessions - en.remainingSessions;
                  const progressPct = en.totalSessions > 0 ? Math.round((completed / en.totalSessions) * 100) : 0;
                  return (
                    <div
                      key={en.id}
                      className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex justify-between items-start gap-3">
                          <div>
                            <h4 className="text-base font-bold text-slate-900 leading-snug">
                              {en.courseTitle || 'Gói tập cá nhân'}
                            </h4>
                            <span className="text-xs font-mono font-semibold text-slate-400 mt-0.5 block">
                              PTC-HD-{String(en.id).padStart(6, '0')}
                            </span>
                          </div>
                          <span
                            className={`text-xs font-bold px-2.5 py-0.5 rounded-full shrink-0 ${
                              en.status === 'ACTIVE'
                                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {en.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 my-4 py-3 border-y border-slate-100 text-xs text-slate-600">
                          <div>
                            <span className="text-slate-400 block">Huấn luyện viên:</span>
                            <span className="font-bold text-slate-800">{en.ptName || 'Huấn luyện viên'}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Địa điểm tập:</span>
                            <span className="font-bold text-slate-800 truncate block">
                              {en.trainingLocation || 'Phòng tập liên kết'}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Học phí trọn gói:</span>
                            <span className="font-bold text-[#FF4B4B]">
                              {(en.finalPrice || 0).toLocaleString('vi-VN')} ₫
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Thời hạn hợp đồng:</span>
                            <span className="font-bold text-slate-800">
                              {en.startDate || '2026-09-01'} → {en.endDate || '2026-12-01'}
                            </span>
                          </div>
                        </div>

                        {/* Progress */}
                        <div className="space-y-1.5 mb-4">
                          <div className="flex justify-between text-xs">
                            <span className="text-slate-500 font-medium">Tiến độ buổi tập:</span>
                            <span className="font-bold text-slate-800">
                              {completed}/{en.totalSessions} buổi ({progressPct}%)
                            </span>
                          </div>
                          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                            <div
                              className="bg-[#FF4B4B] h-full rounded-full transition-all duration-500"
                              style={{ width: `${progressPct}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
                        <button
                          onClick={() => {
                            if (en.ptId) {
                              const targetPt = pts.find((p) => p.id === en.ptId);
                              if (targetPt) loadPtDetails(targetPt);
                            }
                            setActiveTab(2); // Switch to booking tab
                          }}
                          className="px-3.5 py-2 bg-red-50 text-[#FF4B4B] hover:bg-red-100 rounded-xl text-xs font-bold transition-all"
                        >
                          Đặt lịch tập cho gói này
                        </button>

                        <button
                          onClick={async () => {
                            try {
                              const blob = await api.get(`/enrollments/${en.id}/contract`, {
                                responseType: 'blob',
                              });
                              const url = window.URL.createObjectURL(new Blob([blob as any]));
                              const link = document.createElement('a');
                              link.href = url;
                              link.setAttribute('download', `PTC_HD_${String(en.id).padStart(6, '0')}.pdf`);
                              document.body.appendChild(link);
                              link.click();
                              showToast('Đang tải xuống hợp đồng PDF...');
                            } catch (e: any) {
                              showToast('Lỗi tải hợp đồng PDF.');
                            }
                          }}
                          className="px-3.5 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-sm"
                        >
                          <FileText className="w-3.5 h-3.5 text-slate-500" /> Tải Hợp Đồng PDF
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: VÍ TIỀN */}
        {activeTab === 5 && wallet && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Wallet Info Card */}
              <div className="bg-gradient-to-tr from-slate-900 to-slate-800 text-white p-6 rounded-2xl shadow-lg flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-slate-300 text-xs uppercase tracking-wider font-semibold">
                    <span>Ví Điện Tử Nội Bộ</span>
                    <CreditCard className="w-5 h-5 text-slate-300" />
                  </div>
                  <div className="mt-4 text-3xl font-extrabold text-white">
                    {wallet.balance.toLocaleString('vi-VN')} ₫
                  </div>
                  <div className="mt-2 text-xs text-slate-400">
                    Đóng băng (giữ chỗ ca tập): {wallet.lockedBalance.toLocaleString('vi-VN')} ₫
                  </div>
                </div>
                <div className="pt-4 border-t border-slate-700/60 mt-4 text-[11px] text-slate-400">
                  Chủ tài khoản: <b>{user.fullName}</b> • Trạng thái: <b>{wallet.status}</b>
                </div>
              </div>

              {/* Top-up Form */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <h4 className="text-base font-bold text-slate-900">Nạp Tiền Vào Ví</h4>

                <div className="space-y-1.5">
                  <span className="text-xs text-slate-500 font-medium">Chọn nhanh mệnh giá:</span>
                  <div className="grid grid-cols-4 gap-2">
                    {[1000000, 2000000, 5000000, 10000000].map((amt) => (
                      <button
                        key={amt}
                        onClick={() => setTopupAmount(amt)}
                        className={`py-2 text-xs font-semibold rounded-lg border transition-all ${
                          topupAmount === amt
                            ? 'bg-red-50 border-[#FF4B4B] text-[#FF4B4B]'
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {amt / 1000000}Tr
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <span className="text-xs text-slate-500 font-medium">Phương thức nạp mô phỏng:</span>
                  <select
                    value={topupMethod}
                    onChange={(e) => setTopupMethod(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 bg-slate-50"
                  >
                    <option value="BANK_TRANSFER">Chuyển khoản ngân hàng (Quét mã QR / VietQR)</option>
                    <option value="CREDIT_CARD">Thẻ tín dụng / Ghi nợ quốc tế (Visa, Mastercard)</option>
                    <option value="CASH">Nạp tiền mặt tại quầy lễ tân</option>
                  </select>
                </div>

                <button
                  onClick={handleTopup}
                  className="w-full py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-sm flex items-center justify-center gap-2 transition-all"
                >
                  <PlusCircle className="w-4 h-4" /> Nạp Tiền Ngay ({topupAmount.toLocaleString('vi-VN')} ₫)
                </button>
              </div>
            </div>

            {/* Transaction History Table */}
            <div className="space-y-3 pt-4 border-t border-slate-200">
              <h4 className="text-lg font-bold text-slate-900">Lịch Sử Giao Dịch Tài Chính</h4>
              {!wallet.transactions || wallet.transactions.length === 0 ? (
                <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
                  Chưa có giao dịch tài chính nào phát sinh.
                </div>
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 font-semibold uppercase">
                      <tr>
                        <th className="py-3 px-4">Mã Giao Dịch</th>
                        <th className="py-3 px-4">Loại GD</th>
                        <th className="py-3 px-4">Số Tiền</th>
                        <th className="py-3 px-4">Phương Thức</th>
                        <th className="py-3 px-4">Trạng Thái</th>
                        <th className="py-3 px-4">Thời Gian</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-xs">
                      {wallet.transactions.map((tx: any) => {
                        const isPlus =
                          tx.paymentType === 'TOPUP' ||
                          tx.paymentType === 'REFUND' ||
                          tx.paymentType === 'COMPENSATION';
                        return (
                          <tr key={tx.id} className="hover:bg-slate-50/70">
                            <td className="py-3 px-4 font-mono font-semibold text-slate-700">
                              {tx.transactionRef || `#${tx.id}`}
                            </td>
                            <td className="py-3 px-4">
                              <span className="font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-800">
                                {tx.paymentType === 'TOPUP'
                                  ? 'NẠP TIỀN'
                                  : tx.paymentType === 'PURCHASE_PACKAGE'
                                  ? 'MUA KHÓA'
                                  : tx.paymentType}
                              </span>
                            </td>
                            <td
                              className={`py-3 px-4 font-bold ${
                                isPlus ? 'text-emerald-600' : 'text-red-600'
                              }`}
                            >
                              {isPlus ? '+' : '-'}
                              {tx.amount.toLocaleString('vi-VN')} ₫
                            </td>
                            <td className="py-3 px-4 text-slate-600">{tx.paymentMethod}</td>
                            <td className="py-3 px-4">
                              <span
                                className={`px-2 py-0.5 rounded-full font-bold ${
                                  tx.status === 'SUCCESS'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {tx.status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-slate-500">
                              {tx.createdAt ? tx.createdAt.replace('T', ' ').slice(0, 19) : 'Vừa xong'}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
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
            <p className="text-xs text-slate-500 mt-1 mb-4">
              Cung cấp mã số 6 chữ số này cho Huấn luyện viên khi đến phòng tập để hoàn tất điểm danh:
            </p>
            <div className="text-4xl font-mono font-extrabold tracking-widest text-emerald-600 bg-emerald-50 py-3 rounded-xl border border-emerald-200 mb-6">
              {otpCode}
            </div>
            <button
              onClick={() => setOtpModalBooking(null)}
              className="w-full py-2.5 bg-slate-900 text-white text-sm font-semibold rounded-xl hover:bg-slate-800"
            >
              Đóng hộp thoại
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
