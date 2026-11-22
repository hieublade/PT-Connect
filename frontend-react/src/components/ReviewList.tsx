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
        <li key={r.id} className="bg-white p-4 rounded-xl border border-slate-200 flex gap-3 shadow-xs">
          <img
            src={getAvatarUrl(r.studentName ?? 'Học viên', r.studentAvatarUrl ?? undefined)}
            alt={r.studentName ?? 'Học viên'}
            className="w-10 h-10 rounded-full object-cover border border-slate-200 shrink-0"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-slate-900">{r.studentName ?? 'Học viên ẩn danh'}</span>
              <span className="text-xs text-slate-400">{r.createdAt ? r.createdAt.slice(0, 10) : ''}</span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              <StarRating value={r.rating} size={14} />
              <span className="text-xs font-bold text-amber-500">{r.rating}/5 sao</span>
            </div>
            {r.comment && <p className="text-sm text-slate-600 mt-1.5 break-words">{r.comment}</p>}

            {/* Khung phản hồi/giải trình của Huấn luyện viên (nếu có) */}
            {r.ptAppeal && (
              <div className="mt-3 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700">
                <div className="font-bold text-slate-800 flex items-center gap-1.5 mb-1">
                  <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                  Phản hồi từ Huấn luyện viên:
                  {r.ptAppealedAt && (
                    <span className="font-normal text-slate-400 text-[10px] ml-auto">
                      {r.ptAppealedAt.slice(0, 10)}
                    </span>
                  )}
                </div>
                <p className="text-slate-600 italic">"{r.ptAppeal}"</p>
              </div>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
};
