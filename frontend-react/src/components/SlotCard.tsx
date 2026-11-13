import React from 'react';
import { AvailabilitySlot } from '../types/api';
import { Clock, Trash2 } from 'lucide-react';

interface SlotCardProps {
  slot: AvailabilitySlot;
  onDelete?: (slot: AvailabilitySlot) => void;
  onSelect?: (slot: AvailabilitySlot) => void;
  selectable?: boolean;
}

export const SlotCard: React.FC<SlotCardProps> = ({ slot, onDelete, onSelect, selectable = false }) => {
  const formatDateTime = (dtStr: string) => {
    try {
      const dt = new Date(dtStr);
      return dt.toLocaleString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dtStr;
    }
  };

  const statusConfig = {
    AVAILABLE: { bg: 'bg-emerald-50', text: 'text-emerald-800', border: 'border-emerald-200', label: 'Đang trống (AVAILABLE)', canDelete: true },
    BOOKED: { bg: 'bg-blue-50', text: 'text-blue-800', border: 'border-blue-200', label: 'Đã có học viên đặt (BOOKED)', canDelete: false },
    LOCKED: { bg: 'bg-amber-50', text: 'text-amber-800', border: 'border-amber-200', label: 'Đã khóa (LOCKED)', canDelete: false },
  }[slot.status] || { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200', label: slot.status, canDelete: false };

  return (
    <div
      onClick={() => selectable && slot.status === 'AVAILABLE' && onSelect?.(slot)}
      className={`bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 shadow-sm transition-all flex items-center justify-between ${
        selectable && slot.status === 'AVAILABLE' ? 'cursor-pointer hover:border-red-400 hover:ring-2 hover:ring-red-100' : ''
      } border-slate-200`}
    >
      <div className="flex items-center gap-3">
        <div className={`p-2.5 rounded-lg ${statusConfig.bg} ${statusConfig.text}`}>
          <Clock className="w-4 h-4" />
        </div>
        <div>
          <div className="text-xs text-slate-500 font-medium">Bắt đầu: <span className="text-slate-800 dark:text-white font-bold">{formatDateTime(slot.startTime)}</span></div>
          <div className="text-xs text-slate-500 font-medium mt-0.5">Kết thúc: <span className="text-slate-800 dark:text-white font-bold">{formatDateTime(slot.endTime)}</span></div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${statusConfig.bg} ${statusConfig.text} ${statusConfig.border}`}>
          {statusConfig.label}
        </span>

        {onDelete && statusConfig.canDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete(slot);
            }}
            className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-red-200"
            title="Xóa khung giờ"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
