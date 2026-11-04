import React, { useEffect, useState } from 'react';
import api from '../lib/axios';
import { getAvatarUrl } from '../lib/avatar';
import { Review } from '../types/api';
import { StarRating } from './StarRating';

interface Props {
  ptProfileId: number;
  reloadKey?: number;
}

export const ReviewList: React.FC<Props> = ({ ptProfileId, reloadKey = 0 }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .get(`/reviews/pt/${ptProfileId}`)
      .then((data: any) => { if (!cancelled) setReviews(Array.isArray(data) ? data : []); })
      .catch((e: Error) => { if (!cancelled) setError(e.message); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [ptProfileId, reloadKey]);

  if (loading) return <p className="text-sm text-slate-500">Đang tải đánh giá...</p>;
  if (error) return <p className="text-sm text-red-600">Không tải được đánh giá: {error}</p>;
  if (reviews.length === 0) return <p className="text-sm text-slate-500">Huấn luyện viên chưa có đánh giá nào.</p>;

  return (
    <ul className="space-y-3">
      {reviews.map((r) => (
        <li key={r.id} className="bg-white p-4 rounded-xl border border-slate-200 flex gap-3">
          <img
            src={getAvatarUrl(r.studentName ?? 'Học viên', r.studentAvatarUrl ?? undefined)}
            alt={r.studentName ?? 'Học viên'}
            className="w-10 h-10 rounded-full object-cover border border-slate-200"
          />
          <div className="flex-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900">{r.studentName ?? 'Học viên ẩn danh'}</span>
              <span className="text-xs text-slate-400">{r.createdAt ? r.createdAt.slice(0, 10) : ''}</span>
            </div>
            <StarRating value={r.rating} size={14} />
            {r.comment && <p className="text-sm text-slate-600 mt-1">{r.comment}</p>}
          </div>
        </li>
      ))}
    </ul>
  );
};
