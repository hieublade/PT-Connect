import React, { useEffect, useRef, useState } from 'react';
import api from '../lib/axios';
import { PtProfile, UpdatePtProfilePayload } from '../types/api';
import { CERT_URL_MAX, isHttpUrl, resolveCertificateUrl } from '../lib/certificate';
import { ReviewList } from './ReviewList';
import { 
  Upload, 
  FileText, 
  ExternalLink, 
  Trash2, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle,
  Link as LinkIcon,
  Loader2
} from 'lucide-react';

interface Props {
  onSaved?: (msg: string) => void;
}

export const PtProfileForm: React.FC<Props> = ({ onSaved }) => {
  const [profile, setProfile] = useState<PtProfile | null>(null);
  const [form, setForm] = useState<UpdatePtProfilePayload>({ availableLocations: '' });
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [uploadingCert, setUploadingCert] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const load = async () => {
    const p = (await api.get('/pt/profile')) as unknown as PtProfile;
    setProfile(p);
    setForm({
      bio: p.bio ?? '',
      experienceYears: p.experienceYears ?? 0,
      availableLocations: p.availableLocations ?? '',
      locationPricingNote: p.locationPricingNote ?? '',
      certificateUrl: resolveCertificateUrl(p) ?? '',
    });
  };

  useEffect(() => { 
    load().catch((e) => setError(e.message)); 
  }, []);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      setError('Dung lượng tệp chứng chỉ tối đa là 10MB.');
      return;
    }

    setError(null);
    setSuccessMsg(null);
    setUploadingCert(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res: any = await api.post('/pt/profile/certificate/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const updated = res.data?.data || res.data || res;
      const uploadedUrl = updated?.certificateUrl || resolveCertificateUrl(updated);

      if (uploadedUrl) {
        setForm(prev => ({ ...prev, certificateUrl: uploadedUrl }));
        setSuccessMsg('✓ Đã tải tệp chứng chỉ lên máy chủ thành công!');
      }
      await load();
    } catch (err: any) {
      console.error('Lỗi tải tệp chứng chỉ:', err);
      const rawMsg = err.message || '';
      if (rawMsg.includes('No static resource') || err.response?.status === 404) {
        setError('Tính năng tải tệp trực tiếp yêu cầu Restart lại Backend Spring Boot trong IDE (IntelliJ). Hiện tại bạn có thể click nạp link mẫu hoặc dán link online rồi bấm "Lưu hồ sơ" bên dưới!');
      } else {
        setError(rawMsg || 'Lỗi tải tệp lên máy chủ. Bạn có thể dán đường link ảnh chứng chỉ trực tuyến bên dưới.');
      }
    } finally {
      setUploadingCert(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleApplyPresetCert = (url: string) => {
    setForm(prev => ({ ...prev, certificateUrl: url }));
    setError(null);
    setSuccessMsg('✓ Đã nạp đường dẫn chứng chỉ mẫu!');
  };

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccessMsg(null);

    if (!form.availableLocations.trim()) return setError('Địa điểm nhận dạy không được để trống!');
    if ((form.experienceYears ?? 0) < 0) return setError('Số năm kinh nghiệm phải lớn hơn hoặc bằng 0');
    
    const cert = (form.certificateUrl ?? '').trim();
    if (cert && !isHttpUrl(cert)) {
      return setError('Đường dẫn chứng chỉ phải bắt đầu bằng http:// hoặc https:// (hoặc tải trực tiếp từ máy tính)');
    }
    if (cert.length > CERT_URL_MAX) return setError('URL chứng chỉ không được vượt quá 500 ký tự');

    setSaving(true);
    try {
      await api.put('/pt/profile', {
        bio: form.bio?.trim() || undefined,
        experienceYears: Number(form.experienceYears ?? 0),
        availableLocations: form.availableLocations.trim(),
        locationPricingNote: form.locationPricingNote?.trim() || undefined,
        certificateUrl: cert || undefined,
      });
      await load();
      setSuccessMsg('✓ Cập nhật hồ sơ chuyên môn thành công!');
      onSaved?.('Đã cập nhật hồ sơ chuyên môn!');
    } catch (err: any) {
      setError(`Lỗi cập nhật hồ sơ: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!profile) return <p className="text-sm text-slate-500">{error ?? 'Đang tải hồ sơ...'}</p>;

  const inputClass = 'w-full h-10 px-3.5 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-sm outline-none focus:border-[#FF4B4B] transition text-slate-900 dark:text-white';
  const certNow = form.certificateUrl || resolveCertificateUrl(profile);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <form onSubmit={save} className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 space-y-4 shadow-xs">
        <div className="flex items-center justify-between pb-2 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Hồ Sơ Chuyên Môn</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Trạng thái xét duyệt:{' '}
              <span className={`px-2 py-0.5 rounded font-bold text-[11px] ${
                profile.verificationStatus === 'VERIFIED'
                  ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                  : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300'
              }`}>
                {profile.verificationStatus}
              </span>
              {' '}• Đánh giá: {(profile.averageRating ?? 0).toFixed(1)}/5 ({profile.totalReviews ?? 0} lượt)
            </p>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Giới thiệu bản thân (Bio)</label>
          <textarea
            className="w-full p-3 border border-slate-300 dark:border-slate-700 rounded-lg text-sm outline-none focus:border-[#FF4B4B] bg-white dark:bg-slate-900 text-slate-900 dark:text-white transition"
            rows={3}
            placeholder="Chia sẻ về kinh nghiệm huấn luyện, sở trường (tăng cơ, giảm mỡ, pilates, boxing...)"
            value={form.bio ?? ''}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Số năm kinh nghiệm</label>
            <input
              className={inputClass}
              type="number"
              min={0}
              max={50}
              value={form.experienceYears ?? 0}
              onChange={(e) => setForm({ ...form, experienceYears: Number(e.target.value) })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">Ghi chú giá theo địa điểm</label>
            <input
              className={inputClass}
              placeholder="VD: Phụ thu 50k nếu tập tại nhà"
              value={form.locationPricingNote ?? ''}
              onChange={(e) => setForm({ ...form, locationPricingNote: e.target.value })}
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
            Khu vực / Phòng tập nhận dạy (phân tách bằng dấu chấm phẩy ;)
          </label>
          <input
            className={inputClass}
            placeholder="VD: Cầu Giấy; Nam Từ Liêm; Thanh Xuân"
            value={form.availableLocations}
            onChange={(e) => setForm({ ...form, availableLocations: e.target.value })}
          />
          <p className="text-[11px] text-slate-400 mt-1">Học viên sẽ tìm thấy bạn khi tìm kiếm theo các khu vực này.</p>
        </div>

        <div className="pt-3 border-t border-slate-100 dark:border-slate-800">
          <label className="block text-xs font-bold text-slate-800 dark:text-slate-200 mb-1 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-[#FF4B4B]" />
            <span>Chứng chỉ hành nghề & Bằng cấp chuyên môn</span>
          </label>
          <p className="text-[11px] text-slate-500 mb-2.5">
            Bạn có thể tải tệp ảnh từ máy tính lên trực tiếp, hoặc dán đường dẫn ảnh chứng chỉ (Google Drive, Imgur, Cloudinary, v.v.):
          </p>

          <div className="flex flex-wrap items-center gap-2 mb-3">
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*,application/pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <button
              type="button"
              disabled={uploadingCert}
              onClick={() => fileInputRef.current?.click()}
              className="px-3.5 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-bold border border-slate-300 dark:border-slate-700 flex items-center gap-1.5 transition cursor-pointer"
            >
              {uploadingCert ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#FF4B4B]" />
                  <span>Đang tải tệp lên...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 text-[#FF4B4B]" />
                  <span>Chọn tệp ảnh từ máy tính</span>
                </>
              )}
            </button>

            <span className="text-[11px] text-slate-400">hoặc nạp link mẫu:</span>

            <button
              type="button"
              onClick={() => handleApplyPresetCert('https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80')}
              className="px-2 py-1 bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 rounded text-[11px] font-semibold transition cursor-pointer flex items-center gap-1"
              title="Chứng chỉ NASM CPT chuẩn quốc tế"
            >
              <Sparkles className="w-3 h-3 text-amber-600" />
              <span>Chứng chỉ NASM (Mẫu)</span>
            </button>

            <button
              type="button"
              onClick={() => handleApplyPresetCert('https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=1200&q=80')}
              className="px-2 py-1 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded text-[11px] font-semibold transition cursor-pointer flex items-center gap-1"
              title="Chứng chỉ Pilates / Yoga quốc tế"
            >
              <Sparkles className="w-3 h-3 text-blue-600" />
              <span>Pilates / Yoga (Mẫu)</span>
            </button>
          </div>

          <div className="relative">
            <LinkIcon className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              className={`${inputClass} pl-9`}
              type="text"
              maxLength={CERT_URL_MAX}
              placeholder="https://drive.google.com/... hoặc /uploads/certificates/..."
              value={form.certificateUrl ?? ''}
              onChange={(e) => {
                setForm({ ...form, certificateUrl: e.target.value });
                setError(null);
                setSuccessMsg(null);
              }}
            />
          </div>

          {certNow && (
            <div className="mt-2.5 p-3 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 min-w-0">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                <span className="truncate text-slate-700 dark:text-slate-300 font-mono text-[11px]">
                  {certNow}
                </span>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <a
                  href={certNow}
                  target="_blank"
                  rel="noreferrer"
                  className="px-2.5 py-1 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded font-semibold text-xs flex items-center gap-1 transition"
                >
                  <ExternalLink className="w-3 h-3" />
                  <span>Xem</span>
                </a>
                <button
                  type="button"
                  onClick={() => setForm(prev => ({ ...prev, certificateUrl: '' }))}
                  className="px-2 py-1 hover:bg-red-50 text-red-500 rounded font-semibold text-xs flex items-center gap-1 transition cursor-pointer"
                  title="Gỡ bỏ chứng chỉ này"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>Gỡ</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-lg text-xs text-red-600 dark:text-red-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-500 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 rounded-lg text-xs text-emerald-700 dark:text-emerald-300 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={saving || uploadingCert}
          className="w-full sm:w-auto px-6 py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white rounded-lg text-sm font-bold disabled:opacity-60 cursor-pointer shadow-sm active:scale-[0.98] transition flex items-center justify-center gap-1.5"
        >
          {saving ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-white" />
              <span>Đang lưu hồ sơ...</span>
            </>
          ) : (
            <span>Lưu hồ sơ</span>
          )}
        </button>
      </form>

      <div>
        <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-3">Đánh Giá Từ Học Viên</h3>
        <ReviewList ptProfileId={profile.id} />
      </div>
    </div>
  );
};
