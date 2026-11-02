import React from 'react';
import { PtProfile } from '../types/api';
import { Star, MapPin, Award } from 'lucide-react';

interface PtCardProps {
  pt: PtProfile;
  onSelect?: (pt: PtProfile) => void;
}

export const PtCard: React.FC<PtCardProps> = ({ pt, onSelect }) => {
  const formatVnd = (amount?: number) => {
    if (!amount) return 'Liên hệ';
    return `${amount.toLocaleString('vi-VN')} ₫`;
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 p-5 shadow-sm hover:shadow-lg transition-all duration-200 flex flex-col justify-between group">
      <div>
        {/* Header row: Avatar + Name + Location */}
        <div className="flex items-center gap-3.5 mb-3.5">
          <div className="relative shrink-0">
            <img
              src={pt.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${pt.fullName}`}
              alt={pt.fullName}
              className="w-16 h-16 rounded-2xl border border-slate-200 shadow-sm bg-slate-50 object-cover"
            />
            <span className="absolute -bottom-1 -right-1 bg-emerald-500 text-white text-[9px] font-bold px-1.5 py-0.2 rounded-full shadow-sm flex items-center">
              ✓ Xác thực
            </span>
          </div>

          <div className="min-w-0 flex-1">
            <h4 className="text-base font-bold text-slate-900 group-hover:text-[#FF4B4B] transition-colors leading-snug line-clamp-1">
              {pt.fullName}
            </h4>
            <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
              <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="truncate">{pt.availableLocations || 'Toàn quốc'}</span>
            </div>
          </div>
        </div>

        {/* Badges / Metrics row */}
        <div className="flex flex-wrap items-center gap-2 py-2.5 border-y border-slate-100 my-2">
          <div className="flex items-center gap-1 bg-amber-50 text-amber-900 border border-amber-200/70 px-2.5 py-1 rounded-lg text-xs font-bold">
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" />
            <span>{pt.averageRating ? pt.averageRating.toFixed(1) : '5.0'}/5</span>
            <span className="text-amber-700 font-normal">({pt.totalReviews || 0})</span>
          </div>

          <div className="flex items-center gap-1 bg-blue-50 text-blue-900 border border-blue-200/70 px-2.5 py-1 rounded-lg text-xs font-bold">
            <Award className="w-3.5 h-3.5 text-blue-600" />
            <span>{pt.experienceYears || 1} năm kinh nghiệm</span>
          </div>
        </div>

        {/* Bio summary */}
        <p className="text-xs text-slate-600 leading-relaxed line-clamp-2 mt-2.5 min-h-[32px]">
          {pt.bio || 'Huấn luyện viên chuyên nghiệp tận tâm, thiết kế lộ trình rèn luyện cá nhân hóa theo mục tiêu.'}
        </p>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3.5 border-t border-slate-100 flex items-center justify-between gap-3">
        <div>
          <span className="text-[11px] text-slate-400 font-medium block">Học phí từ</span>
          <div className="text-base font-extrabold text-[#FF4B4B] tracking-tight">
            {formatVnd(pt.lowestPrice || 3600000)}
          </div>
        </div>

        <button
          onClick={() => onSelect?.(pt)}
          className="px-4 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-sm hover:shadow transition-all"
        >
          Xem Chi Tiết
        </button>
      </div>
    </div>
  );
};
