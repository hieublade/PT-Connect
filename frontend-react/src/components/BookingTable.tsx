import api from '../lib/axios';
import React, { useState } from 'react';
import { Booking } from '../types/api';
import { CheckCircle, XCircle, Key, Calendar, Filter, AlertTriangle, X, ShieldAlert, Send, Upload, CheckCircle2 } from 'lucide-react';
import { compressImageToDataUrl, MultiImageUploader, SelectedEvidenceFile, uploadMultipleEvidenceFiles } from '../lib/evidence';

interface BookingTableProps {
  bookings: Booking[];
  isPtView?: boolean;
  onApprove?: (booking: Booking) => void;
  onReject?: (booking: Booking, reason?: string) => void;
  onCancel?: (booking: Booking, reason?: string) => void;
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

  // Cancel/Reject Modal State
  const [cancelModalBooking, setCancelModalBooking] = useState<Booking | null>(null);
  const [cancelActionType, setCancelActionType] = useState<'REJECT' | 'CANCEL'>('CANCEL');
  const [cancelReason, setCancelReason] = useState<string>('Trùng lịch bận đột xuất');
  const [cancelPreview, setCancelPreview] = useState<any | null>(null);
  const [cancelPreviewLoading, setCancelPreviewLoading] = useState<boolean>(false);

  // Dispute / Khiếu nại Modal State
  const [disputeModalBooking, setDisputeModalBooking] = useState<Booking | null>(null);
  const [disputeType, setDisputeType] = useState<string>('PT_ABSENT');
  const [disputeSeverity, setDisputeSeverity] = useState<'HIGH' | 'MEDIUM' | 'LOW'>('HIGH');
  const [disputeStatement, setDisputeStatement] = useState<string>('');
  const [disputeEvidence, setDisputeEvidence] = useState<string>('');
  const [disputeFiles, setDisputeFiles] = useState<SelectedEvidenceFile[]>([]);
  const [disputeSubmitting, setDisputeSubmitting] = useState<boolean>(false);
  const [disputeError, setDisputeError] = useState<string | null>(null);
  const [disputeSuccessMsg, setDisputeSuccessMsg] = useState<string | null>(null);
  const [disputedBookingIds, setDisputedBookingIds] = useState<Set<number>>(new Set());

  const studentDisputeReasons = [
    { value: 'PT_ABSENT', label: 'HLV vắng mặt không báo trước (No-show)', severity: 'HIGH' as const },
    { value: 'QUALITY_ISSUE', label: 'HLV đến muộn > 15 phút / Cắt bớt giờ tập', severity: 'MEDIUM' as const },
    { value: 'OTP_PREMATURE', label: 'Gian lận điểm danh OTP / Chưa tập đã đòi OTP', severity: 'HIGH' as const },
    { value: 'ATTITUDE_ISSUE', label: 'HLV có thái độ không đúng mực / Thiếu chuyên nghiệp', severity: 'MEDIUM' as const },
    { value: 'OTHER', label: 'Khác (Tranh chấp phí hủy, bảo lưu khóa học...)', severity: 'LOW' as const },
  ];

  const ptDisputeReasons = [
    { value: 'STUDENT_ABSENT', label: 'Học viên bùng lịch không đến (Student No-show)', severity: 'HIGH' as const },
    { value: 'LATE_CANCEL_STUDENT', label: 'Học viên hủy lịch sát giờ nhưng từ chối trừ buổi', severity: 'MEDIUM' as const },
    { value: 'SAFETY_VIOLATION', label: 'Học viên vi phạm quy tắc / Có hành vi thiếu chuẩn mực', severity: 'MEDIUM' as const },
    { value: 'OTHER', label: 'Khác (Tranh chấp thỏa thuận, dụng cụ...)', severity: 'LOW' as const },
  ];

  const currentReasons = isPtView ? ptDisputeReasons : studentDisputeReasons;

  const handleOpenDisputeModal = (b: Booking) => {
    setDisputeModalBooking(b);
    setDisputeType(currentReasons[0].value);
    setDisputeSeverity(currentReasons[0].severity);
    setDisputeStatement('');
    setDisputeEvidence('');
    setDisputeFiles([]);
    setDisputeError(null);
    setDisputeSuccessMsg(null);
  };

  const handleSubmitDispute = async () => {
    if (!disputeModalBooking) return;
    if (!disputeStatement.trim()) {
      setDisputeError('Vui lòng nhập tường trình chi tiết sự việc để Ban Quản Trị xem xét.');
      return;
    }

    setDisputeSubmitting(true);
    setDisputeError(null);
    try {
      let finalEvidence = disputeEvidence.trim();

      if (disputeFiles.length > 0) {
        const urls = await uploadMultipleEvidenceFiles(disputeFiles, api.post);
        if (urls.length > 0) {
          const joinedUrls = urls.join(' | ');
          finalEvidence = finalEvidence ? `${joinedUrls} | ${finalEvidence}` : joinedUrls;
        }
      }

      const selectedOption = currentReasons.find(r => r.value === disputeType);
      await api.post('/disputes', {
        bookingId: disputeModalBooking.id,
        disputeType,
        disputeTypeLabel: selectedOption?.label || 'Khiếu nại ca tập',
        severity: disputeSeverity,
        statement: disputeStatement.trim(),
        evidenceNote: finalEvidence || undefined,
      });

      setDisputedBookingIds(prev => new Set(prev).add(disputeModalBooking.id));
      setDisputeSuccessMsg('✓ Đã gửi hồ sơ khiếu nại thành công! Ban Quản Trị sẽ thẩm tra và ban hành phán quyết trọng tài.');
      setTimeout(() => {
        setDisputeModalBooking(null);
        setDisputeSuccessMsg(null);
      }, 2200);
    } catch (err: any) {
      setDisputeError(err.response?.data?.message || err.message || 'Không thể gửi khiếu nại lúc này.');
    } finally {
      setDisputeSubmitting(false);
    }
  };

  const commonReasons = isPtView
    ? [
        'Trùng lịch bận đột xuất',
        'HLV bị ốm / Sức khỏe không đảm bảo',
        'Có việc gia đình đột xuất',
        'Phòng tập bảo trì thiết bị',
      ]
    : [
        'Bận việc học / công tác đột xuất',
        'Bị ốm / Sức khỏe không tốt',
        'Có việc bận gia đình',
        'Thay đổi lịch trình cá nhân',
      ];

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

  const handleOpenCancelModal = async (booking: Booking, action: 'REJECT' | 'CANCEL') => {
    setCancelModalBooking(booking);
    setCancelActionType(action);
    setCancelReason(commonReasons[0]);
    setCancelPreview(null);
    if (action === 'CANCEL') {
      setCancelPreviewLoading(true);
      try {
        const res: any = await api.get('/bookings/' + booking.id + '/cancel-preview');
        setCancelPreview(res || null);
      } catch (err) {
        console.error('Không thể lấy xem trước chính sách hủy:', err);
      } finally {
        setCancelPreviewLoading(false);
      }
    }
  };

  const handleConfirmCancel = () => {
    if (!cancelModalBooking) return;
    const finalReason = cancelReason.trim() || 'Trùng lịch bận đột xuất';
    if (cancelActionType === 'REJECT') {
      onReject?.(cancelModalBooking, finalReason);
    } else {
      onCancel?.(cancelModalBooking, finalReason);
    }
    setCancelModalBooking(null);
  };

  const filteredBookings = filterStatus === 'ALL'
    ? bookings
    : bookings.filter((b) => b.status === filterStatus);

  return (
    <div className="space-y-4">
      {/* Filter Toolbar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-200">
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
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-8 text-center text-slate-500 dark:text-slate-400">
          <Calendar className="w-10 h-10 mx-auto text-slate-300 mb-2" />
          <p>Không có ca tập nào phù hợp với bộ lọc hiện tại.</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400 font-semibold uppercase">
                <tr>
                  <th className="py-3 px-4">Mã #</th>
                  <th className="py-3 px-4">Thời Gian</th>
                  <th className="py-3 px-4">{isPtView ? 'Học Viên' : 'Huấn Luyện Viên'}</th>
                  <th className="py-3 px-4">Khóa Học / Loại</th>
                  <th className="py-3 px-4">Trạng Thái & Lý Do</th>
                  <th className="py-3 px-4 text-right">Thao Tác</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredBookings.map((b) => {
                  const cfg = statusConfig[b.status] || { bg: 'bg-slate-50 text-slate-700 dark:text-slate-200 border-slate-200', label: b.status };
                  return (
                    <tr key={b.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/50">
                      <td className="py-3 px-4 font-mono font-semibold text-slate-600">#{b.id}</td>
                      <td className="py-3 px-4 text-xs">
                        <div className="font-semibold text-slate-900 dark:text-white">{formatDateTime(b.startTime)}</div>
                        <div className="text-slate-500">Đến: {formatDateTime(b.endTime)}</div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-slate-900 dark:text-white">{isPtView ? b.studentName || 'Học viên' : b.ptName || 'Huấn luyện viên'}</div>
                        <div className="text-xs text-slate-500">{isPtView ? b.studentPhone : ''}</div>
                      </td>
                      <td className="py-3 px-4 text-xs text-slate-700 dark:text-slate-200">
                        {b.courseTitle || (b.bookingType === 'TRIAL' ? 'Ca tập thử (TRIAL)' : 'Gói tập cá nhân')}
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${cfg.bg}`}>
                          {cfg.label}
                        </span>

                        {/* Hiển thị lý do hủy rõ ràng nếu ca bị hủy */}
                        {b.status === 'CANCELLED' && (
                          <div className="mt-1.5 p-2 bg-red-50 rounded-lg border border-red-200/80 text-[11px] text-red-800 max-w-xs leading-normal">
                            <span className="font-bold">
                              [{b.cancelledByRole === 'PT' ? 'HLV HỦY' : b.cancelledByRole === 'STUDENT' ? 'HỌC VIÊN HỦY' : 'HỆ THỐNG HỦY'}]:
                            </span>{' '}
                            <span>{b.cancellationReason || 'Trùng lịch bận việc đột xuất'}</span>
                          </div>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <div className="flex items-center justify-end gap-2 flex-wrap">
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
                                    onClick={() => handleOpenCancelModal(b, 'REJECT')}
                                    className="px-2.5 py-1 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg text-xs font-semibold flex items-center gap-1"
                                  >
                                    <XCircle className="w-3.5 h-3.5" /> Từ chối
                                  </button>
                                </>
                              )}
                              {b.status === 'CONFIRMED' && (
                                <>
                                  <button
                                    onClick={() => onGetOtp?.(b)}
                                    className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                                    title="Tạo mã OTP để cung cấp cho học viên điểm danh"
                                  >
                                    <Key className="w-3.5 h-3.5" /> Tạo mã OTP
                                  </button>
                                  <button
                                    onClick={() => handleOpenCancelModal(b, 'CANCEL')}
                                    className="px-2.5 py-1 border border-red-200 text-red-600 hover:bg-red-50 rounded-lg text-xs font-semibold"
                                  >
                                    Hủy ca
                                  </button>
                                </>
                              )}
                            </>
                          ) : (
                            <>
                              {b.status === 'CONFIRMED' && (
                                <>
                                  <button
                                    onClick={() => onConfirmOtp?.(b)}
                                    className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                                    title="Nhập mã OTP do HLV cung cấp để điểm danh hoàn tất ca tập"
                                  >
                                    <Key className="w-3.5 h-3.5" /> Điểm danh (Nhập OTP)
                                  </button>
                                  <button
                                    onClick={() => handleOpenCancelModal(b, 'CANCEL')}
                                    className="px-2.5 py-1 border border-red-200 text-red-600 hover:bg-red-50 rounded-lg text-xs font-semibold"
                                  >
                                    Hủy ca
                                  </button>
                                </>
                              )}
                              {b.status === 'PENDING' && (
                                <button
                                  onClick={() => handleOpenCancelModal(b, 'CANCEL')}
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

                          {/* Nút Khiếu Nại / Báo Cáo Sự Cố cho các ca không phải PENDING */}
                          {b.status !== 'PENDING' && (
                            disputedBookingIds.has(b.id) ? (
                              <span className="px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 text-[11px] font-semibold flex items-center gap-1 border border-amber-300">
                                ⚖️ Đang khiếu nại
                              </span>
                            ) : (
                              <button
                                type="button"
                                onClick={() => handleOpenDisputeModal(b)}
                                className="px-2 py-1 text-slate-500 hover:text-amber-600 dark:text-slate-400 dark:hover:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950/30 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
                                title="Khiếu nại / Báo cáo sự cố ca tập lên Ban Quản Trị"
                              >
                                <ShieldAlert className="w-3.5 h-3.5 text-amber-500" /> Khiếu nại
                              </button>
                            )
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

      {/* Modal Khiếu Nại & Báo Cáo Sự Cố Ca Tập Lên Ban Quản Trị */}
      {disputeModalBooking && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-scale-up">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <div className="flex items-center gap-2.5 text-amber-600 dark:text-amber-400">
                <ShieldAlert className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  Khiếu Nại & Báo Cáo Sự Cố Ca Tập #{disputeModalBooking.id}
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setDisputeModalBooking(null)}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Thông tin ca tập liên quan */}
            <div className="text-xs text-slate-600 dark:text-slate-300 space-y-1.5 mb-4 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700">
              <div className="flex justify-between">
                <span className="text-slate-400">Thời gian ca tập:</span>
                <b>{formatDateTime(disputeModalBooking.startTime)} - {formatDateTime(disputeModalBooking.endTime)}</b>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">{isPtView ? 'Học viên đối tác:' : 'Huấn luyện viên:'}</span>
                <b>{isPtView ? disputeModalBooking.studentName : disputeModalBooking.ptName}</b>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Khóa học / Gói:</span>
                <span>{disputeModalBooking.courseTitle || 'Ca tập cá nhân'}</span>
              </div>
            </div>

            {disputeSuccessMsg ? (
              <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-xl text-center text-xs text-emerald-800 dark:text-emerald-300 space-y-1">
                <p className="font-bold text-sm">🎉 Gửi khiếu nại thành công!</p>
                <p>{disputeSuccessMsg}</p>
              </div>
            ) : (
              <div className="space-y-3.5">
                {/* Chọn lý do khiếu nại */}
                <div>
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                    Lý do khiếu nại chính:
                  </label>
                  <select
                    value={disputeType}
                    onChange={(e) => {
                      const val = e.target.value;
                      setDisputeType(val);
                      const sel = currentReasons.find(r => r.value === val);
                      if (sel) setDisputeSeverity(sel.severity);
                    }}
                    className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                  >
                    {currentReasons.map((r) => (
                      <option key={r.value} value={r.value}>
                        {r.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Mức độ nghiêm trọng */}
                <div>
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                    Mức độ nghiêm trọng:
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['LOW', 'MEDIUM', 'HIGH'] as const).map((sev) => (
                      <button
                        key={sev}
                        type="button"
                        onClick={() => setDisputeSeverity(sev)}
                        className={`py-1.5 px-2 rounded-lg text-xs font-bold border transition ${
                          disputeSeverity === sev
                            ? sev === 'HIGH'
                              ? 'bg-red-500 text-white border-red-500'
                              : sev === 'MEDIUM'
                              ? 'bg-amber-500 text-white border-amber-500'
                              : 'bg-blue-500 text-white border-blue-500'
                            : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                        }`}
                      >
                        {sev === 'HIGH' ? 'Nghiêm trọng' : sev === 'MEDIUM' ? 'Trung bình' : 'Nhẹ'}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Tường trình chi tiết */}
                <div>
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                    Tường trình chi tiết sự việc <span className="text-red-500">*</span>:
                  </label>
                  <textarea
                    rows={3}
                    value={disputeStatement}
                    onChange={(e) => {
                      setDisputeStatement(e.target.value);
                      if (disputeError) setDisputeError(null);
                    }}
                    placeholder="Mô tả cụ thể: Bạn đã có mặt lúc mấy giờ? Chờ bao lâu? Số lần liên lạc? Yêu cầu hoàn tiền hoặc bồi thường thế nào..."
                    className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                {/* Bằng chứng bằng cách tải ảnh lên */}
                <div>
                  <MultiImageUploader
                    files={disputeFiles}
                    onChange={setDisputeFiles}
                    label="Ảnh chụp bằng chứng xác minh (không bắt buộc)"
                    subLabel="Hỗ trợ chọn nhiều ảnh cùng lúc (Ảnh check-in phòng tập, lịch sử gọi điện, tin nhắn...)"
                  />

                  <input
                    type="text"
                    value={disputeEvidence}
                    onChange={(e) => setDisputeEvidence(e.target.value)}
                    placeholder="Ghi chú thêm về ảnh (VD: Lịch sử 3 cuộc gọi nhỡ lúc 18:05, check-in quầy lễ tân...)"
                    className="w-full mt-2 p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                  />
                </div>

                {disputeError && (
                  <div className="p-2.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl text-xs text-red-700 dark:text-red-300">
                    ⚠️ {disputeError}
                  </div>
                )}

                <div className="p-2.5 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 rounded-xl text-[11px] text-amber-800 dark:text-amber-300 leading-relaxed">
                  ⚖️ <b>Quy trình trọng tài:</b> Sau khi bạn gửi hồ sơ, Ban Quản Trị Hệ Thống sẽ đối soát log hệ thống, liên hệ bên liên quan và ra phán quyết hoàn trả học phí hoặc bồi thường theo đúng chính sách nền tảng.
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setDisputeModalBooking(null)}
                    className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                  >
                    Hủy bỏ
                  </button>
                  <button
                    type="button"
                    disabled={disputeSubmitting}
                    onClick={handleSubmitDispute}
                    className="px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
                  >
                    <Send className="w-3.5 h-3.5" />
                    {disputeSubmitting ? 'Đang gửi hồ sơ...' : 'Gửi hồ sơ khiếu nại'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal Nhập Lý Do Hủy / Từ Chối Ca Tập */}
      {cancelModalBooking && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 animate-scale-up">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2.5 text-red-600">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  {cancelActionType === 'REJECT' ? 'Từ Chối Ca Tập' : 'Hủy Ca Tập'} #{cancelModalBooking.id}
                </h4>
              </div>
              <button
                onClick={() => setCancelModalBooking(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="text-xs text-slate-600 space-y-2 mb-4 bg-slate-50 p-3 rounded-xl border border-slate-100">
              <div>
                <span className="text-slate-400">Thời gian tập:</span>{' '}
                <b>{formatDateTime(cancelModalBooking.startTime)} - {formatDateTime(cancelModalBooking.endTime)}</b>
              </div>
              <div>
                <span className="text-slate-400">{isPtView ? 'Học viên:' : 'HLV:'}</span>{' '}
                <b>{isPtView ? cancelModalBooking.studentName : cancelModalBooking.ptName}</b>
              </div>
            </div>

            {/* Policy Preview Box */}
            {cancelActionType === 'CANCEL' && (
              <div className="mb-4 p-3.5 rounded-xl border border-amber-300 bg-amber-50/80 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 font-bold text-amber-900">
                    <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>Quy Định & Chính Sách Đền Bù Hủy Lịch</span>
                  </div>
                  {cancelModalBooking.status === 'CONFIRMED' && (
                    <span className="text-[10px] font-bold bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full border border-blue-200">
                      Ca tập đã duyệt
                    </span>
                  )}
                </div>

                {cancelPreviewLoading ? (
                  <p className="text-slate-500 italic text-[11px] py-1">
                    Đang tính toán chính sách đền bù và hoàn buổi...
                  </p>
                ) : cancelPreview ? (
                  <div className="space-y-2">
                    <div className="p-2.5 bg-white rounded-lg border border-amber-200 text-slate-800 text-xs leading-relaxed font-medium">
                      {cancelPreview.explanation}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-500 block">Số buổi hợp đồng</span>
                        <span className={cancelPreview.restoreSession ? "text-emerald-600 font-bold" : "text-red-600 font-bold"}>
                          {cancelPreview.restoreSession ? "✓ Hoàn lại 1 buổi" : "✕ Bị trừ mất 1 buổi"}
                        </span>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <span className="text-[10px] text-slate-500 block">
                          {isPtView ? "Tiền phạt trừ ví HLV" : "Tiền đền bù ca tập"}
                        </span>
                        <span className={cancelPreview.penaltyAmount > 0 || cancelPreview.compensationAmount > 0 ? "text-red-600 font-bold" : "text-slate-700 dark:text-slate-200 font-bold"}>
                          {isPtView
                            ? (cancelPreview.penaltyAmount > 0 ? '-' + Number(cancelPreview.penaltyAmount).toLocaleString('vi-VN') + ' ₫' : "0 ₫")
                            : (cancelPreview.penaltyAmount > 0 ? '-' + Number(cancelPreview.penaltyAmount).toLocaleString('vi-VN') + ' ₫' : cancelPreview.compensationAmount > 0 ? 'Đền bù: +' + Number(cancelPreview.compensationAmount).toLocaleString('vi-VN') + ' ₫' : "0 ₫")}
                        </span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-slate-600 text-[11px]">
                    {isPtView
                      ? "• HLV hủy sát giờ (< 24h): Đền bù 100% tiền 1 buổi học vào ví của Học viên và phạt trừ ví HLV."
                      : "• Ca tập đã được PT duyệt nếu hủy sẽ áp dụng đền bù cho Huấn luyện viên."}
                  </p>
                )}
              </div>
            )}

            <div className="space-y-2 mb-4">
              <label className="block text-xs font-bold text-slate-800">
                Lý do {cancelActionType === 'REJECT' ? 'từ chối' : 'hủy ca'} <span className="text-red-500">*</span>:
              </label>

              {/* Gợi ý lý do bấm nhanh */}
              <div className="flex flex-wrap gap-1.5 pb-1">
                {commonReasons.map((r, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setCancelReason(r)}
                    className={`text-[11px] px-2.5 py-1 rounded-lg border transition ${
                      cancelReason === r
                        ? 'bg-red-50 border-red-300 text-red-700 font-bold'
                        : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>

              <textarea
                rows={3}
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="Nhập lý do cụ thể..."
                className="w-full p-2.5 text-xs border border-slate-300 rounded-xl focus:outline-none focus:border-red-500"
              />
              <p className="text-[11px] text-slate-400">
                Lý do này sẽ hiển thị công khai cho {isPtView ? 'học viên' : 'huấn luyện viên'} và lưu vào lịch sử hệ thống.
              </p>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setCancelModalBooking(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
              >
                Đóng
              </button>
              <button
                type="button"
                onClick={handleConfirmCancel}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg shadow-xs transition"
              >
                Xác nhận {cancelActionType === 'REJECT' ? 'từ chối' : 'hủy'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
