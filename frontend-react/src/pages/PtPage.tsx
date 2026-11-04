import { getAvatarUrl } from "../lib/avatar";
import React, { useState, useEffect } from 'react';
import api from '../lib/axios';
import { User, Course, AvailabilitySlot, Booking } from '../types/api';
import { PtProfileForm } from '../components/PtProfileForm';
import { CourseCard } from '../components/CourseCard';
import { SlotCard } from '../components/SlotCard';
import { BookingTable } from '../components/BookingTable';
import { AvatarUploader } from '../components/AvatarUploader';
import {
  BarChart3,
  CheckCircle2,
  Calendar,
  BookOpen,
  ClipboardList,
  User as UserIcon,
  LogOut,
  Plus,
  Key,
} from 'lucide-react';

interface PtPageProps {
  user: User;
  onLogout: () => void;
}

export const PtPage: React.FC<PtPageProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<number>(0);

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);

  // Slot open form
  const [slotDate, setSlotDate] = useState('2026-11-03');
  const [slotStartTime, setSlotStartTime] = useState('09:00');
  const [slotEndTime, setSlotEndTime] = useState('10:30');

  // Verify OTP modal
  const [verifyOtpModalBooking, setVerifyOtpModalBooking] = useState<Booking | null>(null);
  const [inputOtp, setInputOtp] = useState('');
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  };

  useEffect(() => {
    fetchPtData();
  }, []);

  const fetchPtData = async () => {
    try {
      const bData: any = await api.get('/pt/bookings');
      setBookings(bData || []);
      const sData: any = await api.get('/pt/slots');
      setSlots(sData || []);
      const cData: any = await api.get('/pt/courses');
      setCourses(cData || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenSlot = async () => {
    try {
      const startIso = `${slotDate}T${slotStartTime}:00`;
      const endIso = `${slotDate}T${slotEndTime}:00`;
      await api.post('/pt/slots', {
        startTime: startIso,
        endTime: endIso,
      });
      showToast('Đã mở khung giờ rảnh mới thành công!');
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi mở khung giờ.');
    }
  };

  const handleDeleteSlot = async (slot: AvailabilitySlot) => {
    try {
      await api.delete(`/pt/slots/${slot.id}`);
      showToast('Đã xóa khung giờ rảnh!');
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi xóa slot.');
    }
  };

  const handleApproveBooking = async (b: Booking) => {
    try {
      await api.post(`/pt/bookings/${b.id}/approve`);
      showToast(`Đã duyệt ca tập #${b.id}!`);
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi duyệt ca.');
    }
  };

  const handleRejectBooking = async (b: Booking) => {
    try {
      await api.post(`/pt/bookings/${b.id}/reject`, { reason: 'Trùng lịch bận đột xuất' });
      showToast(`Đã từ chối ca tập #${b.id}!`);
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi từ chối ca.');
    }
  };

  const handleConfirmAttendanceOtp = async () => {
    if (!verifyOtpModalBooking || !inputOtp.trim()) return;
    try {
      await api.post(`/attendance/bookings/${verifyOtpModalBooking.id}/otp/verify`, {
        otp: inputOtp.trim(),
      });
      showToast('Xác nhận điểm danh ca tập thành công!');
      setVerifyOtpModalBooking(null);
      setInputOtp('');
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Mã OTP không chính xác hoặc đã hết hạn.');
    }
  };

  const tabs = [
    { label: 'Tổng Quan', icon: BarChart3 },
    { label: 'Duyệt Lịch', icon: CheckCircle2 },
    { label: 'Khung Giờ', icon: Calendar },
    { label: 'Quản Lý Khóa', icon: BookOpen },
    { label: 'Giáo Án', icon: ClipboardList },
    { label: 'Hồ Sơ', icon: UserIcon },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-orange-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              PT
            </div>
            <div>
              <span className="font-extrabold text-slate-900 text-lg tracking-tight">PT Connect</span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-orange-100 text-orange-800">
                Huấn luyện viên
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-bold text-slate-900">{user.fullName}</div>
              <div className="text-xs text-slate-500">{user.email}</div>
            </div>
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
      <div className="bg-gradient-to-r from-orange-600 to-amber-700 text-white py-6 px-4 sm:px-8 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <img
              src={getAvatarUrl(user.fullName, user.avatarUrl)}
              alt={user.fullName}
              className="w-16 h-16 rounded-full border-2 border-white/80 bg-white/10"
            />
            <div>
              <h2 className="text-2xl font-extrabold">Bảng Điều Khiển Huấn Luyện Viên (PT)</h2>
              <p className="text-orange-100 text-xs sm:text-sm mt-0.5">
                Xin chào, <b>{user.fullName}</b>! Quản lý hồ sơ, lịch rảnh và duyệt các yêu cầu đặt lịch (Booking).
              </p>
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
                      ? 'bg-orange-50 text-orange-600'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isCur ? 'text-orange-600' : 'text-slate-400'}`} />
                  {t.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Body */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* TAB 0: TỔNG QUAN */}
        {activeTab === 0 && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Ca tập chờ duyệt</span>
                <div className="text-2xl font-extrabold text-orange-600 mt-1">
                  {bookings.filter((b) => b.status === 'PENDING').length} ca
                </div>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Khung giờ trống</span>
                <div className="text-2xl font-extrabold text-emerald-600 mt-1">
                  {slots.filter((s) => s.status === 'AVAILABLE').length} slot
                </div>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Khóa học của tôi</span>
                <div className="text-2xl font-extrabold text-blue-600 mt-1">{courses.length} khóa</div>
              </div>

              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Đánh giá trung bình</span>
                <div className="text-2xl font-extrabold text-amber-500 mt-1">5.0 / 5.0 ⭐</div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-4">Đánh Giá Gần Đây Từ Học Viên</h3>
              <div className="space-y-3">
                <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-lg">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">Hạnh Hải Đặng</span>
                    <span className="text-amber-600 font-semibold">(5/5 sao)</span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">PT tận tâm, động viên học viên trong từng set tập.</p>
                </div>
                <div className="p-3.5 bg-slate-50 border border-slate-100 rounded-lg">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-slate-900">Chị Bảo Dương</span>
                    <span className="text-amber-600 font-semibold">(5/5 sao)</span>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">PT đến đúng giờ, bài tập đa dạng không bị nhàm chán.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 1: DUYỆT LỊCH */}
        {activeTab === 1 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Quản Lý & Phê Duyệt Lịch Ca Tập</h3>
            <BookingTable
              bookings={bookings}
              isPtView
              onApprove={handleApproveBooking}
              onReject={handleRejectBooking}
              onConfirmOtp={(b) => setVerifyOtpModalBooking(b)}
            />
          </div>
        )}

        {/* TAB 2: KHUNG GIỜ */}
        {activeTab === 2 && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4 max-w-2xl">
              <h3 className="text-base font-bold text-slate-900">Mở Khung Giờ Rảnh Mới</h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Ngày rảnh</label>
                  <input
                    type="date"
                    value={slotDate}
                    onChange={(e) => setSlotDate(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Giờ bắt đầu</label>
                  <input
                    type="time"
                    value={slotStartTime}
                    onChange={(e) => setSlotStartTime(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 mb-1">Giờ kết thúc</label>
                  <input
                    type="time"
                    value={slotEndTime}
                    onChange={(e) => setSlotEndTime(e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>
              <button
                onClick={handleOpenSlot}
                className="w-full py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-sm flex items-center justify-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Mở Khung Giờ
              </button>
            </div>

            <div>
              <h4 className="text-base font-bold text-slate-900 mb-3">Danh Sách Khung Giờ Đã Thiết Lập ({slots.length})</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {slots.map((s) => (
                  <SlotCard key={s.id} slot={s} onDelete={handleDeleteSlot} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: QUẢN LÝ KHÓA */}
        {activeTab === 3 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Danh Sách Khóa Học Cố Định</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {courses.map((c) => (
                <CourseCard
                  key={c.id}
                  course={c}
                  isPtView
                  onToggleStatus={async (course) => {
                    await api.put(`/pt/courses/${course.id}/toggle-status`);
                    showToast('Đã cập nhật trạng thái khóa học!');
                    fetchPtData();
                  }}
                  onDelete={async (course) => {
                    if (confirm('Bạn có chắc chắn muốn xóa khóa học này?')) {
                      await api.delete(`/pt/courses/${course.id}`);
                      showToast('Đã xóa khóa học!');
                      fetchPtData();
                    }
                  }}
                />
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: GIÁO ÁN */}
        {activeTab === 4 && (
          <div className="bg-white p-6 rounded-xl border border-slate-200 text-slate-600">
            <h3 className="text-lg font-bold text-slate-900 mb-2">Quản Lý Giáo Án & Bài Tập Huấn Luyện</h3>
            <p className="text-sm">Hiện có 10 bài tập tiêu chuẩn mẫu được phân phối theo hợp đồng học viên.</p>
          </div>
        )}

        {/* TAB 5: HỒ SƠ */}
        {activeTab === 5 && (
          <div className="space-y-6">
            <PtProfileForm onSaved={showToast} />
            <AvatarUploader
              currentUrl={user.avatarUrl}
              onUpload={async (url) => {
                await api.put('/users/avatar', { avatarUrl: url });
                showToast('Đã lưu ảnh đại diện!');
              }}
            />
          </div>
        )}
      </main>

      {/* Verify OTP Modal */}
      {verifyOtpModalBooking && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 text-center shadow-2xl">
            <div className="w-12 h-12 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center mx-auto mb-3">
              <Key className="w-6 h-6" />
            </div>
            <h4 className="text-lg font-bold text-slate-900">Nhập Mã OTP Xác Nhận Điểm Danh</h4>
            <p className="text-xs text-slate-500 mt-1">Yêu cầu học viên cung cấp mã 6 số hiển thị trên điện thoại:</p>
            <input
              type="text"
              maxLength={6}
              value={inputOtp}
              onChange={(e) => setInputOtp(e.target.value)}
              placeholder="VD: 849201"
              className="my-5 w-full text-center py-2 px-4 border border-slate-300 rounded-xl font-mono text-2xl font-bold focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <button
                onClick={() => setVerifyOtpModalBooking(null)}
                className="flex-1 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-slate-600"
              >
                Hủy
              </button>
              <button
                onClick={handleConfirmAttendanceOtp}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold"
              >
                Xác nhận điểm danh
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
