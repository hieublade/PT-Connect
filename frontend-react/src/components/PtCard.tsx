import React from 'react';
import { PtProfile } from '../types/api';
import { Star, MapPin, Award, CheckCircle2, ChevronRight, Sparkles, MessageCircle } from 'lucide-react';
import { getAvatarUrl } from '../lib/avatar';

interface PtCardProps {
  pt: PtProfile;
  index?: number;
  onSelect?: (pt: PtProfile) => void;
  onBook?: (pt: PtProfile) => void;
}

// Chuyên môn và vai trò thực tế tương ứng với từng Huấn luyện viên
const PT_EXTRA_INFO: Record<string, { role: string; highlights: string[] }> = {
  'cuong': {
    role: 'Giảng viên Huấn luyện Thể hình & Trưởng bộ môn Tăng cơ - HFI',
    highlights: [
      'Chứng chỉ Chuyên gia Huấn luyện Cá nhân NASM & HFI',
      'Kèm sát 1-kèm-1 form tạ chuẩn, tối ưu phát triển sợi cơ',
      'Thiết kế giáo án Hypertrophy & dinh dưỡng tăng cơ',
    ],
  },
  'dung': {
    role: 'Chuyên gia Dinh dưỡng Thể thao & Giảm mỡ chuyên sâu 12 tuần',
    highlights: [
      'Lộ trình siết mỡ cắt nét khoa học, không nhịn ăn tiêu cực',
      'Đo lường và bám sát chỉ số mỡ nội tạng InBody mỗi tuần',
      'Cam kết giảm 4 - 8kg mỡ thừa và cải thiện sức bền toàn diện',
    ],
  },
  'bao': {
    role: 'HLV Boxing, Kickfit & Huấn luyện Thể lực Cardio cường độ cao',
    highlights: [
      'Cựu Vận động viên Võ thuật & Boxing thực chiến',
      'Tập luyện phản xạ, cardio đốt mỡ cấp tốc 800+ kcal/buổi',
      'Giải tỏa stress hiệu quả và rèn luyện thể lực bền bỉ',
    ],
  },
  'ha': {
    role: 'Chuyên gia Nắn chỉnh Dáng, Giãn cơ & HLV Yoga Pilates Trị liệu',
    highlights: [
      'Khắc phục tật gù lưng, cổ rùa, đau mỏi vai gáy văn phòng',
      'Chỉnh dáng thon gọn eo, hông quả táo và cơ bụng săn chắc',
      'Chứng chỉ Quốc tế Yoga Alliance 500h & Pilates Reformer',
    ],
  },
  'kiet': {
    role: 'Huấn luyện viên Thể hình Chuyên nghiệp & Phục hồi Thể lực',
    highlights: [
      'Hơn 7 năm kinh nghiệm huấn luyện học viên thi đấu & cá nhân',
      'Tăng sức mạnh nền tảng, Squat / Bench / Deadlift an toàn',
      'Tư vấn thực đơn dinh dưỡng macro phù hợp ngân sách',
    ],
  },
};

const DEFAULT_EXTRA_INFO = {
  role: 'Huấn luyện viên Thể hình Chuyên nghiệp & Thể lực Cá nhân',
  highlights: [
    'Giảng viên đào tạo Fitness đạt chuẩn chứng chỉ quốc tế',
    'Kèm sát kỹ thuật 1-kèm-1, phòng tránh chấn thương khớp',
    'Cam kết đạt mục tiêu vóc dáng theo chỉ số InBody',
  ],
};

function getPtExtraInfo(name?: string) {
  if (!name) return DEFAULT_EXTRA_INFO;
  const lower = name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  if (lower.includes('cuong')) return PT_EXTRA_INFO['cuong'];
  if (lower.includes('dung')) return PT_EXTRA_INFO['dung'];
  if (lower.includes('bao')) return PT_EXTRA_INFO['bao'];
  if (lower.includes('ha')) return PT_EXTRA_INFO['ha'];
  if (lower.includes('kiet')) return PT_EXTRA_INFO['kiet'];
  return DEFAULT_EXTRA_INFO;
}

export const PtCard: React.FC<PtCardProps> = ({ pt, index = 0, onSelect, onBook }) => {
  const formatVnd = (amount?: number) => {
    if (!amount) return '3.600.000 ₫';
    return `${amount.toLocaleString('vi-VN')} ₫`;
  };

  const extra = getPtExtraInfo(pt.fullName);
  const trainerNumber = index + 1;

  return (
    <div
      onClick={() => onSelect?.(pt)}
      className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm hover:shadow-2xl hover:-translate-y-1.5 transition-all duration-300 flex flex-col justify-between group cursor-pointer"
    >
      <div>
        {/* 1. KHUNG ẢNH CHÂN DUNG LỚN CHUẨN GYM (PHONG CÁCH VIỆN ĐÀO TẠO FITNESS) */}
        <div className="relative w-full aspect-[4/4.6] bg-slate-100 overflow-hidden">
          <img
            src={getAvatarUrl(pt.fullName, pt.avatarUrl)}
            alt={pt.fullName}
            className="w-full h-full object-cover object-top transition-transform duration-700 ease-out group-hover:scale-108"
          />

          {/* Huy hiệu số thứ tự đỏ chuẩn thể thao (góc trên bên trái - giống ảnh mẫu) */}
          <div className="absolute top-0 left-0 bg-[#E52E2E] text-white font-black text-base px-3.5 py-1.5 rounded-br-2xl shadow-lg flex items-center justify-center">
            {trainerNumber}
          </div>

          {/* Huy hiệu xác thực (góc trên bên phải) */}
          <div className="absolute top-3 right-3 bg-emerald-600/95 text-white text-[11px] font-bold px-2.5 py-1 rounded-full shadow-md backdrop-blur-xs flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5 text-white" />
            <span>Xác thực</span>
          </div>

          {/* Lớp phủ gradient mờ dưới chân ảnh kèm kinh nghiệm */}
          <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/80 via-slate-950/30 to-transparent p-3 flex items-end justify-between text-white">
            <div className="flex items-center gap-1.5 text-xs font-semibold">
              <Award className="w-4 h-4 text-amber-400" />
              <span>{pt.experienceYears || 5} năm kinh nghiệm</span>
            </div>

            <div className="flex items-center gap-1 text-xs font-black bg-amber-500 text-slate-950 px-2 py-0.5 rounded-md shadow-sm">
              <Star className="w-3 h-3 fill-slate-950" />
              <span>{pt.totalReviews ? (pt.averageRating ?? 5.0).toFixed(1) : '5.0'}</span>
            </div>
          </div>
        </div>

        {/* 2. NỘI DUNG THÔNG TIN HUẤN LUYỆN VIÊN */}
        <div className="p-5 space-y-3">
          {/* Tên HLV phong cách Athletic Red + Bold */}
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded bg-[#E52E2E] text-white font-black text-xs flex items-center justify-center shrink-0">
              {trainerNumber}
            </span>
            <h4 className="text-xl font-black text-slate-900 group-hover:text-[#E52E2E] transition-colors uppercase italic tracking-tight font-sans truncate">
              {pt.fullName}
            </h4>
          </div>

          {/* Chức danh / Vai trò nổi bật */}
          <p className="text-xs font-bold text-slate-800 leading-snug line-clamp-2">
            {extra.role}
          </p>

          {/* Gạch đầu dòng thế mạnh / chứng chỉ chuẩn như ảnh mẫu */}
          <ul className="space-y-1.5 text-xs text-slate-600 pt-1 border-t border-slate-100">
            {extra.highlights.map((h, i) => (
              <li key={i} className="flex items-start gap-1.5 leading-relaxed">
                <span className="text-[#E52E2E] font-bold shrink-0 mt-0.5">•</span>
                <span className="line-clamp-1">{h}</span>
              </li>
            ))}
          </ul>

          {/* Địa điểm tập luyện */}
          <div className="flex items-center gap-1.5 text-xs text-slate-500 pt-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0" />
            <span className="truncate">{pt.availableLocations || 'Khu vực Đống Đa, Cầu Giấy'}</span>
          </div>
        </div>
      </div>

      {/* 3. FOOTER: HỌC PHÍ & NÚT HÀNH ĐỘNG */}
      <div className="p-5 pt-3 border-t border-slate-100 bg-slate-50/60 flex items-center justify-between gap-3">
        <div>
          <span className="text-[10px] text-slate-500 uppercase font-bold block">
            Học phí từ
          </span>
          <div className="text-lg font-black text-[#E52E2E] tracking-tight">
            {formatVnd(pt.lowestPrice)}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              window.dispatchEvent(new CustomEvent('ptconnect:open_chat', {
                detail: {
                  partnerId: pt.userId || pt.id,
                  partnerName: pt.fullName,
                  partnerEmail: pt.email,
                  partnerAvatar: getAvatarUrl(pt.fullName, pt.avatarUrl),
                  partnerRole: 'PT'
                }
              }));
            }}
            className="p-2.5 bg-white hover:bg-orange-50 border border-slate-200 hover:border-orange-400 text-slate-700 hover:text-orange-600 rounded-xl transition-all shadow-xs cursor-pointer flex items-center justify-center"
            title={`Nhắn tin trực tiếp với HLV ${pt.fullName}`}
          >
            <MessageCircle className="w-4 h-4 text-orange-500" />
          </button>

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onSelect?.(pt);
            }}
            className="px-4 py-2.5 bg-gradient-to-r from-[#E52E2E] to-red-600 hover:from-red-600 hover:to-red-700 text-white text-xs font-black rounded-xl shadow-md hover:shadow-lg transition-all flex items-center gap-1.5 cursor-pointer uppercase"
          >
            <span>Xem Chi Tiết</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
