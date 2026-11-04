import React, { useState } from 'react';
import { Booking } from '../types/api';
import { CheckCircle, XCircle, Key, Calendar, Filter } from 'lucide-react';

interface BookingTableProps {
  bookings: Booking[];
  isPtView?: boolean;
  onApprove?: (booking: Booking) => void;
  onReject?: (booking: Booking) => void;
  onCancel?: (booking: Booking) => void;
  onGetOtp?: (booking: Booking) => void;
  onConfirmOtp?: (booking: Booking) => void;
  onReview?: (booking: Booking) => void;
  reviewedBookingIds?: Set<number>;
}

export const BookingTable: React.FC<BookingTableProps> = ({
  bookings,
  isPtView = false,
  onApprove,
  onReject,
  onCancel,
  onGetOtp,
  onConfirmOtp,
  onReview,
  reviewedBookingIds,
}) => {
  const [filterStatus, setFilterStatus] = useState<string>('ALL');

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

  const filteredBookings = filterStatus === 'ALL'
    ? bookings
    : bookings.filter((b) => b.status === filterStatus);

  return (
    <div className="space-y-4">
      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700">
          <Filter className="w-4 h-4 text-slate-400" />
          <span>Lọc ca tập theo trạng thái:</span>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs text-slate-800 bg-slate-50 focus:outline-none focus:ring-1 focus:ring-[#FF4B4B]"
          >
            <option value="ALL">Tất cả ca tập ({bookings.length})</option>
            <option value="PENDING">Chờ HLV duyệt (PENDING)</option>
            <option value="CONFIRMED">Đã xác nhận / Sắp tới (CONFIRMED)</option>
            <option value="COMPLETED">Đã hoàn thành (COMPLETED)</option>
            <option value="CANCELLED">Đã hủy (CANCELLED)</option>
          </select>
        </div>
        <div className="text-xs text-slate-500">
          Hiển thị <b>{filteredBookings.length}</b> ca tập
        </div>
      </div>

      {!filteredBookings.length ? (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-500">
          <Calendar className="w-10 h-10 mx-auto text-slate-300 mb-2" />
          <p>Không có ca tập nào phù hợp với bộ lọc hiện tại.</p>
        </div>
      ) : (
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
                {filteredBookings.map((b) => {
                  const cfg = statusConfig[b.status] || { bg: 'bg-slate-50 text-slate-700 border-slate-200', label: b.status };
                  return (
                    <tr key={b.id} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4 font-mono font-semibold text-slate-600">#{b.id}</td>
                      <td className="py-3 px-4 text-xs">
                        <div className="font-semibold text-slate-900">{formatDateTime(b.startTime)}</div>
                        <div className="text-slate-500">Đến: {formatDateTime(b.endTime)}</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-900">{isPtView ? b.studentName || 'Học viên' : b.ptName || 'Huấn luyện viên'}</div>
                        <div className="text-xs text-slate-500">{isPtView ? b.studentPhone : ''}</div>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-700">
                        {b.courseTitle || (b.bookingType === 'TRIAL' ? 'Ca tập thử (TRIAL)' : 'Gói tập cá nhân')}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${cfg.bg}`}>
                          {cfg.label}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {isPtView ? (
                            <>
                              {b.status === 'PENDING' && (
                                <>
                                  <button
                                    onClick={() => onApprove?.(b)}
                                    className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                                  >
                                    <CheckCircle className="w-3.5 h-3.5" /> Duyệt ca tập
                                  </button>
                                  <button
                                    onClick={() => onReject?.(b)}
                                    className="px-2.5 py-1 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg text-xs font-semibold flex items-center gap-1"
                                  >
                                    <XCircle className="w-3.5 h-3.5" /> Từ chối ca tập
                                  </button>
                                </>
                              )}
                              {b.status === 'CONFIRMED' && (
                                <button
                                  onClick={() => onConfirmOtp?.(b)}
                                  className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
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
                                  className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                                >
                                  <Key className="w-3.5 h-3.5" /> Nhận mã OTP điểm danh
                                </button>
                              )}
                              {b.status === 'PENDING' && (
                                <button
                                  onClick={() => onCancel?.(b)}
                                  className="px-2.5 py-1 border border-slate-300 text-slate-600 hover:bg-slate-100 rounded-lg text-xs font-semibold"
                                >
                                  Hủy ca tập
                                </button>
                              )}
                              {b.status === 'COMPLETED' && onReview && (
                                reviewedBookingIds?.has(b.id) ? (
                                  <span className="text-xs text-emerald-700 font-semibold">✓ Đã đánh giá</span>
                                ) : (
                                  <button
                                    onClick={() => onReview(b)}
                                    className="px-2.5 py-1 bg-amber-500 hover:bg-amber-600 text-white rounded-md text-xs font-semibold cursor-pointer"
                                  >
                                    ★ Đánh giá
                                  </button>
                                )
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
      )}
    </div>
  );
};
