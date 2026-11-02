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
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
      <div>
        <div className="flex items-start gap-4">
          <div className="relative">
            <img
              src={pt.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${pt.fullName}`}
              alt={pt.fullName}
              className="w-16 h-16 rounded-full border border-slate-200 bg-slate-50 object-cover"
            />
            <span className="absolute -bottom-2 -right-1 bg-emerald-100 text-emerald-800 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-emerald-300">
              Đã xác thực
            </span>
          </div>

          <div className="flex-1 min-w-0">
            <h4 className="text-lg font-bold text-slate-900 truncate">{pt.fullName}</h4>
            <div className="flex items-center gap-2 text-xs mt-1 text-slate-600">
              <span className="flex items-center text-amber-600 font-bold">
                <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500 mr-0.5" />
                {pt.averageRating.toFixed(1)}/5
              </span>
              <span>({pt.totalReviews} đánh giá)</span>
              <span>•</span>
              <span className="text-blue-700 font-medium flex items-center">
                <Award className="w-3.5 h-3.5 mr-0.5" />
                {pt.experienceYears} năm KN
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2 line-clamp-2">
              {pt.bio || 'Huấn luyện viên chuyên nghiệp tận tâm, đồng hành cùng bạn đạt mục tiêu hình thể.'}
            </p>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 text-xs text-slate-600 flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          <span className="truncate"><b>Khu vực:</b> {pt.availableLocations || 'Chưa cập nhật'}</span>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
        <div>
          <span className="text-xs text-slate-500">Giá chỉ từ:</span>
          <div className="text-base font-extrabold text-red-600">
            {formatVnd(pt.lowestPrice || 3600000)}
          </div>
        </div>

        <button
          onClick={() => onSelect?.(pt)}
          className="px-4 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-sm transition-all"
        >
          Xem Chi Tiết
        </button>
      </div>
    </div>
  );
};
