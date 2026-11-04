import React, { useState } from 'react';
import api from '../lib/axios';
import { Booking, CreateReviewPayload, Review } from '../types/api';
import { StarRating } from './StarRating';

interface Props {
  booking: Booking;
  onClose: () => void;
  onSubmitted: (review: Review) => void;
}

export const ReviewModal: React.FC<Props> = ({ booking, onClose, onSubmitted }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const payload: CreateReviewPayload = {
        bookingId: booking.id,
        rating,
        comment: comment.trim() || undefined,
      };
      const created = (await api.post('/reviews', payload)) as unknown as Review;
      onSubmitted(created);
    } catch (e: any) {
      setError(e.message || 'Lỗi khi gửi đánh giá');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
        <h4 className="text-lg font-bold text-slate-900">Đánh giá ca tập #{booking.id}</h4>
        <p className="text-xs text-slate-500 mt-1">HLV: {booking.ptName ?? '—'}</p>
        <div className="my-4">
          <StarRating value={rating} onChange={setRating} size={28} />
        </div>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows={4}
          placeholder="Chia sẻ cảm nhận của bạn về buổi tập..."
          className="w-full p-3 border border-slate-300 rounded-xl text-sm focus:ring-1 focus:ring-[#FF4B4B] outline-none"
        />
        {error && <p className="text-xs text-red-600 mt-2">{error}</p>}
        <div className="flex gap-2 mt-4">
          <button onClick={onClose} className="flex-1 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-slate-600">
            Hủy
          </button>
          <button
            onClick={submit}
            disabled={submitting}
            className="flex-1 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] disabled:opacity-60 text-white rounded-lg text-sm font-semibold"
          >
            {submitting ? 'Đang gửi...' : 'Gửi đánh giá'}
          </button>
        </div>
      </div>
    </div>
  );
};
