import React, { useState } from 'react';
import { X } from 'lucide-react';
import api from '../lib/axios';
import { Booking, CreateReviewPayload, Review } from '../types/api';
import { StarRating } from './StarRating';
import { MultiImageUploader, SelectedEvidenceFile, uploadMultipleEvidenceFiles } from '../lib/evidence';

interface Props {
  booking: Booking;
  onClose: () => void;
  onSubmitted: (review: Review) => void;
}

export const ReviewModal: React.FC<Props> = ({ booking, onClose, onSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [studentEvidence, setStudentEvidence] = useState('');
  const [evidenceFiles, setEvidenceFiles] = useState<SelectedEvidenceFile[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isLowRating = rating <= 3;

  const submit = async () => {
    setError(null);
    if (isLowRating && (!comment || comment.trim().length < 5)) {
      setError('Khi đánh giá từ 1 đến 3 sao, bạn vui lòng nhập lý do cụ thể (tối thiểu 5 ký tự) để HLV và Ban Quản Trị có căn cứ xác minh.');
      return;
    }

    setSubmitting(true);
    try {
      let finalEvidence = studentEvidence.trim();
      if (evidenceFiles.length > 0) {
        const uploadedUrls = await uploadMultipleEvidenceFiles(evidenceFiles, (url, data) => api.post(url, data));
        const urlsText = uploadedUrls.join('\n');
        finalEvidence = finalEvidence ? `${urlsText}\n${finalEvidence}` : urlsText;
      }

      const payload: CreateReviewPayload = {
        bookingId: booking.id,
        rating,
        comment: comment.trim() || undefined,
        studentEvidence: isLowRating && finalEvidence ? finalEvidence : undefined,
      };
      const created = (await api.post('/reviews', payload)) as unknown as Review;
      onSubmitted(created);
    } catch (e: any) {
      setError(e.response?.data?.message || e.message || 'Lỗi khi gửi đánh giá');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl my-auto max-h-[92vh] flex flex-col overflow-hidden animate-scale-up border border-slate-100">
        {/* Header */}
        <div className="p-4 sm:p-5 pb-3 border-b border-slate-100 shrink-0 flex items-center justify-between">
          <div>
            <h4 className="text-base font-bold text-slate-900">Đánh giá ca tập #{booking.id}</h4>
            <p className="text-xs text-slate-500 mt-0.5">HLV: {booking.ptName ?? '—'}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="p-4 sm:p-5 overflow-y-auto flex-1 space-y-3.5">
          <div className="my-2 flex flex-col items-center justify-center gap-1">
            <StarRating value={rating} onChange={setRating} size={32} />
            <span className="text-xs font-semibold text-slate-600 mt-1">
              {rating === 5 && 'Tuyệt vời (5 sao)'}
              {rating === 4 && 'Rất tốt (4 sao)'}
              {rating === 3 && 'Trung bình (3 sao)'}
              {rating === 2 && 'Kém (2 sao)'}
              {rating === 1 && 'Rất tệ (1 sao)'}
            </span>
          </div>

          {isLowRating && (
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 space-y-1">
              <div className="font-bold flex items-center gap-1.5 text-amber-900">
                <span>⚠️</span> Lưu ý về quy chế phản biện và kiểm duyệt
              </div>
              <p>
                Đánh giá từ 1 - 3 sao sẽ được chuyển vào quy trình kiểm duyệt công bằng. Huấn luyện viên có quyền phản biện giải trình, và Ban Quản Trị (Admin) sẽ xem xét quyết định xóa bỏ hoặc công khai đánh giá.
              </p>
            </div>
          )}

          <div className="space-y-3">
            <div>
              <label className="text-xs font-semibold text-slate-700 block mb-1">
                Nhận xét / Đóng góp ý kiến {isLowRating && <span className="text-red-500">*</span>}
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                rows={3}
                placeholder={
                  isLowRating
                    ? 'Mô tả cụ thể vấn đề bạn gặp phải (thái độ, giờ giấc, chất lượng bài tập)...'
                    : 'Chia sẻ cảm nhận của bạn về buổi tập...'
                }
                className="w-full p-3 border border-slate-300 rounded-xl text-sm focus:ring-1 focus:ring-[#FF4B4B] outline-none"
              />
            </div>

            {isLowRating && (
              <div className="space-y-2">
                <MultiImageUploader
                  files={evidenceFiles}
                  onChange={setEvidenceFiles}
                  maxFiles={3}
                  label="Bằng chứng ảnh đối chứng ban đầu"
                  subLabel="Hỗ trợ chọn hoặc kéo thả trực tiếp ảnh chụp màn hình, ảnh hóa đơn, biên lai..."
                />
                <div>
                  <label className="text-[11px] font-semibold text-slate-600 block mb-1">
                    Mô tả / Ghi chú thêm về bằng chứng (tùy chọn)
                  </label>
                  <textarea
                    value={studentEvidence}
                    onChange={(e) => setStudentEvidence(e.target.value)}
                    rows={2}
                    placeholder="Mô tả cụ thể sự việc đối chứng hoặc dán link bổ sung nếu có..."
                    className="w-full p-2.5 border border-slate-300 rounded-xl text-xs focus:ring-1 focus:ring-[#FF4B4B] outline-none"
                  />
                </div>
              </div>
            )}
          </div>

          {error && <p className="text-xs text-red-600 mt-2">⚠️ {error}</p>}
        </div>

        {/* Pinned Sticky Footer */}
        <div className="p-3.5 sm:p-4 bg-slate-50 border-t border-slate-100 shrink-0 flex gap-2.5">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-2.5 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-100 transition cursor-pointer"
          >
            Hủy
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="flex-1 py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] disabled:opacity-60 text-white rounded-xl text-xs font-bold shadow-md transition cursor-pointer"
          >
            {submitting ? 'Đang gửi...' : isLowRating ? 'Gửi đánh giá (Kiểm duyệt)' : 'Gửi đánh giá'}
          </button>
        </div>
      </div>
    </div>
  );
};
