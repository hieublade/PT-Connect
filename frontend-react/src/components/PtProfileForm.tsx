import React, { useEffect, useState } from 'react';
import api from '../lib/axios';
import { PtProfile, UpdatePtProfilePayload } from '../types/api';
import { CERT_URL_MAX, isHttpUrl, resolveCertificateUrl } from '../lib/certificate';
import { ReviewList } from './ReviewList';

interface Props {
  onSaved?: (msg: string) => void;
}

export const PtProfileForm: React.FC<Props> = ({ onSaved }) => {
  const [profile, setProfile] = useState<PtProfile | null>(null);
  const [form, setForm] = useState<UpdatePtProfilePayload>({ availableLocations: '' });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

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

  useEffect(() => { load().catch((e) => setError(e.message)); }, []);

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!form.availableLocations.trim()) return setError('Địa điểm nhận dạy không được để trống!');
    if ((form.experienceYears ?? 0) < 0) return setError('Số năm kinh nghiệm phải lớn hơn hoặc bằng 0');
    const cert = (form.certificateUrl ?? '').trim();
    if (cert && !isHttpUrl(cert)) return setError('Đường dẫn chứng chỉ phải bắt đầu bằng http:// hoặc https://');
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
      onSaved?.('Đã cập nhật hồ sơ chuyên môn!');
    } catch (err: any) {
      setError(`Lỗi cập nhật hồ sơ: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  if (!profile) return <p className="text-sm text-slate-500">{error ?? 'Đang tải hồ sơ...'}</p>;

  const input = 'w-full h-10 px-3.5 bg-white border border-slate-300 rounded-lg text-sm outline-none focus:border-[#FF4B4B]';
  const certNow = resolveCertificateUrl(profile);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <form onSubmit={save} className="bg-white p-6 rounded-xl border border-slate-200 space-y-4">
        <h3 className="text-lg font-bold text-slate-900">Hồ Sơ Chuyên Môn</h3>
        <p className="text-xs text-slate-500">
          Trạng thái xét duyệt: <b>{profile.verificationStatus}</b> • Đánh giá: {(profile.averageRating ?? 0).toFixed(1)}/5 ({profile.totalReviews ?? 0} lượt)
        </p>
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Giới thiệu bản thân</label>
          <textarea
            className="w-full p-3 border border-slate-300 rounded-lg text-sm outline-none focus:border-[#FF4B4B]"
            rows={3}
            placeholder="Giới thiệu bản thân"
            value={form.bio ?? ''}
            onChange={(e) => setForm({ ...form, bio: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Số năm kinh nghiệm</label>
          <input
            className={input}
            type="number"
            min={0}
            max={50}
            value={form.experienceYears ?? 0}
            onChange={(e) => setForm({ ...form, experienceYears: Number(e.target.value) })}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Địa điểm nhận dạy</label>
          <input
            className={input}
            placeholder="Địa điểm nhận dạy (phân tách bằng ;)"
            value={form.availableLocations}
            onChange={(e) => setForm({ ...form, availableLocations: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Ghi chú giá theo địa điểm</label>
          <input
            className={input}
            placeholder="Ghi chú giá theo địa điểm"
            value={form.locationPricingNote ?? ''}
            onChange={(e) => setForm({ ...form, locationPricingNote: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Link chứng chỉ hành nghề (1NF)</label>
          <input
            className={input}
            type="url"
            maxLength={CERT_URL_MAX}
            placeholder="https://storage.ptconnect.vn/certs/cert_nasam.jpg"
            value={form.certificateUrl ?? ''}
            onChange={(e) => setForm({ ...form, certificateUrl: e.target.value })}
          />
        </div>
        {certNow && isHttpUrl(certNow) && (
          <a href={certNow} target="_blank" rel="noreferrer" className="text-xs text-blue-600 underline block">
            Xem chứng chỉ hiện tại ↗
          </a>
        )}
        {error && <p className="text-xs text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={saving}
          className="px-5 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white rounded-lg text-sm font-semibold disabled:opacity-60 cursor-pointer"
        >
          {saving ? 'Đang lưu...' : 'Lưu hồ sơ'}
        </button>
      </form>
      <div>
        <h3 className="text-lg font-bold text-slate-900 mb-3">Đánh Giá Từ Học Viên</h3>
        <ReviewList ptProfileId={profile.id} />
      </div>
    </div>
  );
};
