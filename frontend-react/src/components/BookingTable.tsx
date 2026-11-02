import React from 'react';
import { Booking } from '../types/api';
import { CheckCircle, XCircle, Key, Calendar } from 'lucide-react';

interface BookingTableProps {
  bookings: Booking[];
  isPtView?: boolean;
  onApprove?: (booking: Booking) => void;
  onReject?: (booking: Booking) => void;
  onCancel?: (booking: Booking) => void;
  onGetOtp?: (booking: Booking) => void;
  onConfirmOtp?: (booking: Booking) => void;
}

export const BookingTable: React.FC<BookingTableProps> = ({
  bookings,
  isPtView = false,
  onApprove,
  onReject,
  onCancel,
  onGetOtp,
  onConfirmOtp,
}) => {
  const formatDateTime = (dtStr: string) => {
    try {
      const dt = new Date(dtStr);
      return dt.toLocaleString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dtStr;
    }
  };

  const statusConfig = {
    CONFIRMED: { bg: 'bg-blue-50 text-blue-700 border-blue-200', label: 'Đã xác nhận' },
    COMPLETED: { bg: 'bg-emerald-50 text-emerald-700 border-emerald-200', label: 'Đã hoàn thành' },
    PENDING: { bg: 'bg-amber-50 text-amber-700 border-amber-200', label: 'Chờ duyệt' },
    CANCELLED: { bg: 'bg-red-50 text-red-700 border-red-200', label: 'Đã hủy' },
  };

  if (!bookings.length) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
        <Calendar className="w-10 h-10 mx-auto text-slate-300 mb-2" />
        <p>Hiện chưa có ca tập nào trong danh sách.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-600 font-semibold uppercase">
            <tr>
              <th className="py-3 px-4">Mã #</th>
              <th className="py-3 px-4">Thời Gian</th>
              <th className="py-3 px-4">{isPtView ? 'Học Viên' : 'Huấn Luyện Viên'}</th>
              <th className="py-3 px-4">Khóa Học / Loại</th>
              <th className="py-3 px-4">Trạng Thái</th>
              <th className="py-3 px-4 text-right">Thao Tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {bookings.map((b) => {
              const cfg = statusConfig[b.status] || { bg: 'bg-slate-50 text-slate-700 border-slate-200', label: b.status };
              return (
                <tr key={b.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4 font-mono font-semibold text-slate-600">#{b.id}</td>
                  <td className="py-3 px-4">
                    <div className="font-medium text-slate-800">{formatDateTime(b.startTime)}</div>
                    <div className="text-xs text-slate-500 font-mono">Đến: {formatDateTime(b.endTime)}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900">{isPtView ? b.studentName || `Học viên #${b.studentId}` : b.ptName || `HLV #${b.ptId}`}</div>
                    <div className="text-xs text-slate-500">{isPtView ? b.studentPhone || '' : ''}</div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="font-medium text-slate-700">{b.courseTitle || (b.bookingType === 'TRIAL' ? 'Tập thử miễn phí' : 'Theo gói tập')}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cfg.bg}`}>
                      {cfg.label}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {isPtView ? (
                        <>
                          {b.status === 'PENDING' && (
                            <>
                              <button
                                onClick={() => onApprove?.(b)}
                                className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md text-xs font-medium flex items-center gap-1 shadow-sm"
                              >
                                <CheckCircle className="w-3.5 h-3.5" /> Duyệt ca tập
                              </button>
                              <button
                                onClick={() => onReject?.(b)}
                                className="px-2.5 py-1 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-md text-xs font-medium flex items-center gap-1"
                              >
                                <XCircle className="w-3.5 h-3.5 text-red-500" /> Từ chối ca tập
                              </button>
                            </>
                          )}
                          {b.status === 'CONFIRMED' && (
                            <button
                              onClick={() => onConfirmOtp?.(b)}
                              className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-medium flex items-center gap-1 shadow-sm"
                            >
                              <Key className="w-3.5 h-3.5" /> Xác nhận điểm danh
                            </button>
                          )}
                        </>
                      ) : (
                        <>
                          {b.status === 'CONFIRMED' && (
                            <button
                              onClick={() => onGetOtp?.(b)}
                              className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-md text-xs font-medium flex items-center gap-1 shadow-sm"
                            >
                              <Key className="w-3.5 h-3.5" /> Nhận mã OTP điểm danh
                            </button>
                          )}
                          {(b.status === 'PENDING' || b.status === 'CONFIRMED') && (
                            <button
                              onClick={() => onCancel?.(b)}
                              className="px-2.5 py-1 border border-red-300 hover:bg-red-50 text-red-600 rounded-md text-xs font-medium"
                            >
                              Hủy ca tập
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
