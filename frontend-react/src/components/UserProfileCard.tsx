import React, { useState, useRef } from 'react';
import {
  User as UserIcon,
  Mail,
  Phone,
  Shield,
  Camera,
  Save,
  Check,
  Sparkles,
  AlertCircle,
  Upload,
  Link as LinkIcon,
  Loader2,
} from 'lucide-react';
import { User } from '../types/api';
import { getAvatarUrl } from '../lib/avatar';
import api from '../lib/axios';

interface UserProfileCardProps {
  user: User;
  onUserUpdated: (updatedUser: User) => void;
  showToast: (msg: string) => void;
}

export const UserProfileCard: React.FC<UserProfileCardProps> = ({ user, onUserUpdated, showToast }) => {
  const [fullName, setFullName] = useState(user.fullName || '');
  const [phone, setPhone] = useState(user.phone || '');
  const [avatarUrl, setAvatarUrl] = useState(user.avatarUrl || '');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUrlInput, setShowUrlInput] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Gợi ý ảnh đại diện thể hình mẫu để kiểm thử 1-click
  const sampleAvatars = [
    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=400&q=80',
    'https://images.unsplash.com/photo-1548690312-e3b507d8c110?auto=format&fit=crop&w=400&q=80',
  ];

  // Xử lý upload tập tin ảnh từ máy tính (File Picker)
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError('Vui lòng chọn một tập tin hình ảnh hợp lệ (PNG, JPG, WEBP)!');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('Dung lượng ảnh tối đa là 5MB.');
      return;
    }

    setError(null);
    setUploading(true);

    // Hiển thị xem trước ảnh ngay lập tức bằng local URL
    const localPreviewUrl = URL.createObjectURL(file);
    setAvatarUrl(localPreviewUrl);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const updatedUser = (await api.post('/users/avatar/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })) as unknown as User;

      if (updatedUser?.avatarUrl) {
        setAvatarUrl(updatedUser.avatarUrl);
      }
      onUserUpdated(updatedUser);
      localStorage.setItem('ptconnect_user', JSON.stringify(updatedUser));
      showToast('✓ Tải ảnh đại diện từ máy tính lên thành công!');
    } catch (err: any) {
      console.error('Lỗi tải ảnh lên:', err);
      setError(err.message || 'Lỗi khi tải ảnh lên máy chủ. Bạn có thể dùng đường dẫn ảnh URL bên dưới.');
    } finally {
      setUploading(false);
      // Reset input value để có thể chọn lại cùng 1 file nếu muốn
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!fullName.trim()) {
      setError('Họ và tên không được để trống.');
      return;
    }

    if (!phone.trim()) {
      setError('Số điện thoại không được để trống.');
      return;
    }

    setSaving(true);
    try {
      const updatedUser = (await api.put('/users/profile', {
        fullName: fullName.trim(),
        phone: phone.trim(),
        avatarUrl: avatarUrl.trim() || undefined,
      })) as unknown as User;

      // Đồng bộ state và bộ nhớ lưu trữ
      onUserUpdated(updatedUser);
      localStorage.setItem('ptconnect_user', JSON.stringify(updatedUser));

      setSaved(true);
      showToast('Cập nhật thông tin hồ sơ thành công!');
      setTimeout(() => setSaved(false), 2500);
    } catch (err: any) {
      setError(err.message || 'Cập nhật hồ sơ thất bại. Vui lòng kiểm tra lại.');
    } finally {
      setSaving(false);
    }
  };

  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'PT':
        return <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-orange-100 text-orange-700">Huấn Luyện Viên (PT)</span>;
      case 'ADMIN':
        return <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-purple-100 text-purple-700">Quản Trị Viên (Admin)</span>;
      default:
        return <span className="px-2.5 py-1 text-xs font-bold rounded-full bg-blue-100 text-blue-700">Học Viên (Student)</span>;
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 max-w-2xl font-sans">
      <div className="flex items-center justify-between pb-4 mb-6 border-b border-slate-100">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <UserIcon className="w-5 h-5 text-red-500" />
            Hồ Sơ Cá Nhân & Định Danh
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Quản lý thông tin tài khoản, họ tên, email, số điện thoại và tải ảnh đại diện
          </p>
        </div>
        <div>{getRoleBadge(user.role)}</div>
      </div>

      {error && (
        <div className="mb-5 p-3 rounded-xl bg-red-50 border border-red-200 flex items-center gap-2 text-xs font-medium text-red-600">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Hidden native file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
        className="hidden"
      />

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Phần ảnh đại diện với hỗ trợ Upload từ máy */}
        <div className="p-4 rounded-2xl bg-slate-50/80 border border-slate-200/90 space-y-3">
          <div className="flex flex-col sm:flex-row items-center gap-5">
            {/* Avatar Preview with Camera Overlay */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="relative cursor-pointer group"
              title="Nhấp để tải ảnh đại diện từ máy tính"
            >
              <img
                src={getAvatarUrl(user.fullName, avatarUrl)}
                alt="Avatar Preview"
                className="w-24 h-24 rounded-full border-2 border-white shadow-md object-cover bg-white group-hover:brightness-90 transition"
              />
              <div className="absolute -bottom-1 -right-1 w-8 h-8 bg-[#FF4B4B] group-hover:bg-[#E03E3E] rounded-full flex items-center justify-center text-white shadow-sm transition">
                {uploading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Camera className="w-4 h-4" />
                )}
              </div>
            </div>

            {/* Upload Buttons & Options */}
            <div className="flex-1 space-y-2 text-center sm:text-left w-full">
              <label className="block text-xs font-bold text-slate-800">
                Ảnh đại diện cá nhân
              </label>

              <div className="flex flex-wrap items-center gap-2 justify-center sm:justify-start">
                <button
                  type="button"
                  disabled={uploading}
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-xs font-bold rounded-xl shadow-xs transition flex items-center gap-2 disabled:opacity-50"
                >
                  {uploading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Đang tải ảnh lên...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" /> Tải ảnh từ máy tính
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => setShowUrlInput(!showUrlInput)}
                  className="px-3 py-2 bg-white hover:bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl border border-slate-200 transition flex items-center gap-1.5"
                >
                  <LinkIcon className="w-3.5 h-3.5 text-slate-400" />
                  {showUrlInput ? 'Thu gọn URL' : 'Dùng link URL'}
                </button>
              </div>

              <p className="text-[11px] text-slate-400">
                Định dạng hỗ trợ: JPG, PNG, WEBP, GIF (Dung lượng tối đa 5MB)
              </p>
            </div>
          </div>

          {/* Collapsible URL Input & Sample Avatars */}
          {showUrlInput && (
            <div className="pt-3 border-t border-slate-200/80 space-y-2 animate-fade-in">
              <label className="block text-[11px] font-semibold text-slate-600">
                Nhập liên kết hình ảnh trực tiếp (URL / CDN):
              </label>
              <input
                type="text"
                value={avatarUrl}
                onChange={(e) => setAvatarUrl(e.target.value)}
                placeholder="https://example.com/my-photo.jpg"
                className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-red-400"
              />

              <div className="flex items-center gap-1.5 flex-wrap pt-1">
                <span className="text-[11px] text-slate-500 flex items-center gap-1">
                  <Sparkles className="w-3 h-3 text-amber-500" /> Ảnh mẫu gym có sẵn:
                </span>
                {sampleAvatars.map((url, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setAvatarUrl(url)}
                    className="text-[11px] px-2 py-0.5 rounded border border-slate-200 bg-white hover:bg-slate-100 text-slate-600 transition"
                  >
                    Mẫu {idx + 1}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Thông tin định danh: Họ tên, Email, SĐT */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <UserIcon className="w-3.5 h-3.5 text-slate-500" />
              Họ và tên <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="Nhập họ và tên đầy đủ"
              className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-red-400 transition"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Mail className="w-3.5 h-3.5 text-slate-500" />
              Địa chỉ Email (Định danh)
            </label>
            <input
              type="email"
              disabled
              value={user.email}
              className="w-full h-10 px-3.5 bg-slate-100 border border-slate-200 rounded-lg text-sm text-slate-500 cursor-not-allowed font-medium"
            />
            <span className="text-[10px] text-slate-400">Email dùng để đăng nhập và bảo mật tài khoản</span>
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Phone className="w-3.5 h-3.5 text-slate-500" />
              Số điện thoại <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              required
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="0987654321"
              className="w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-red-400 transition"
            />
          </div>

          <div className="space-y-1.5">
            <label className="block text-xs font-semibold text-slate-700 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-slate-500" />
              Trạng thái tài khoản
            </label>
            <div className="h-10 px-3.5 bg-slate-50 border border-slate-200 rounded-lg flex items-center">
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Đang hoạt động (ACTIVE)
              </span>
            </div>
          </div>
        </div>

        {/* Nút lưu */}
        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={saving || uploading}
            className="px-6 py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] active:scale-[0.99] text-white text-sm font-semibold rounded-xl shadow-sm transition-all flex items-center gap-2 disabled:opacity-50"
          >
            {saving ? (
              'Đang lưu thông tin...'
            ) : saved ? (
              <>
                <Check className="w-4 h-4" /> Đã lưu thành công!
              </>
            ) : (
              <>
                <Save className="w-4 h-4" /> Lưu Thay Đổi Hồ Sơ
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
