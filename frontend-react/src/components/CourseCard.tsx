import React, { useState } from 'react';
import { Course } from '../types/api';
import { Calendar, Clock, DollarSign, Eye, Sparkles } from 'lucide-react';
import { CoursePreviewModal } from './CoursePreviewModal';

interface CourseCardProps {
  course: Course;
  onEnroll?: (course: Course) => void;
  onEdit?: (course: Course) => void;
  onToggleStatus?: (course: Course) => void;
  onDelete?: (course: Course) => void;
  isPtView?: boolean;
}

export const CourseCard: React.FC<CourseCardProps> = ({
  course,
  onEnroll,
  onEdit,
  onToggleStatus,
  onDelete,
  isPtView = false,
}) => {
  const isActive = course.status === 'ACTIVE';
  const [showPreviewModal, setShowPreviewModal] = useState<boolean>(false);

  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm hover:shadow-md transition-all">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">{course.title}</h3>
          <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">{course.description}</p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${
            isActive
              ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
              : 'bg-slate-100 text-slate-600 dark:text-slate-300 border border-slate-200'
          }`}
        >
          {isActive ? 'Đang bán (ACTIVE)' : 'Đã ngưng bán (INACTIVE)'}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-100">
        <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-red-500" /> Học phí trọn gói
          </span>
          <span className="text-sm font-bold text-red-600 mt-0.5 block">
            {course.basePrice.toLocaleString('vi-VN')} ₫
          </span>
        </div>

        <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <Calendar className="w-3 h-3 text-blue-500" /> Tổng số buổi
          </span>
          <span className="text-sm font-bold text-slate-800 mt-0.5 block">
            {course.totalSessions} buổi
          </span>
        </div>

        <div className="bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-100 dark:border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
            <Clock className="w-3 h-3 text-amber-500" /> Thời hạn khóa
          </span>
          <span className="text-sm font-bold text-slate-800 mt-0.5 block">
            {course.validityDays} ngày
          </span>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
        {isPtView ? (
          <>
            <button
              type="button"
              onClick={() => setShowPreviewModal(true)}
              className="px-3 py-1.5 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg text-xs font-semibold flex items-center gap-1 cursor-pointer transition"
              title="Xem trước lộ trình & nội dung demo như học viên"
            >
              <Eye className="w-3.5 h-3.5 text-blue-500" />
              <span>Xem Demo</span>
            </button>
            {onEdit && (
              <button
                onClick={() => onEdit(course)}
                className="px-3 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-xs font-medium cursor-pointer"
              >
                Chỉnh sửa
              </button>
            )}
            {onToggleStatus && (
              <button
                onClick={() => onToggleStatus(course)}
                className={`px-3 py-1.5 border rounded-lg text-xs font-medium cursor-pointer ${
                  isActive
                    ? 'border-amber-300 text-amber-700 hover:bg-amber-50'
                    : 'border-emerald-300 text-emerald-700 hover:bg-emerald-50'
                }`}
              >
                {isActive ? 'Ngưng bán' : 'Mở bán lại'}
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(course)}
                className="px-3 py-1.5 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg text-xs font-medium cursor-pointer"
              >
                Xóa
              </button>
            )}
          </>
        ) : (
          <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setShowPreviewModal(true)}
              className="w-full py-2.5 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-800 dark:text-slate-100 text-xs font-bold rounded-xl border border-slate-300 dark:border-slate-700 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-2xs hover:border-slate-400"
            >
              <Eye className="w-3.5 h-3.5 text-blue-500" />
              <span>Xem Lộ Trình & Demo</span>
            </button>
            <button
              type="button"
              onClick={() => onEnroll?.(course)}
              className="w-full py-2.5 px-3 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center justify-center gap-1.5 cursor-pointer active:scale-[0.98]"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-200" />
              <span>Đăng ký khóa học</span>
            </button>
          </div>
        )}
      </div>

      <CoursePreviewModal
        course={course}
        isOpen={showPreviewModal}
        onClose={() => setShowPreviewModal(false)}
        onEnroll={onEnroll}
        isPtView={isPtView}
      />
    </div>
  );
};
