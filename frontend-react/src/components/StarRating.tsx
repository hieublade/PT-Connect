import React from 'react';
import { Star } from 'lucide-react';

interface Props {
  value: number;
  onChange?: (v: number) => void;
  size?: number;
}

export const StarRating: React.FC<Props> = ({ value, onChange, size = 18 }) => (
  <div className="inline-flex items-center gap-0.5" role={onChange ? 'radiogroup' : undefined}>
    {[1, 2, 3, 4, 5].map((n) => (
      <button
        key={n}
        type="button"
        disabled={!onChange}
        onClick={() => onChange?.(n)}
        aria-label={`${n} sao`}
        className={onChange ? 'cursor-pointer' : 'cursor-default'}
      >
        <Star
          width={size}
          height={size}
          className={n <= value ? 'fill-amber-400 text-amber-400' : 'text-slate-300'}
        />
      </button>
    ))}
  </div>
);
