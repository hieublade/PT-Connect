import React, { useState } from 'react';
import { Camera, Check } from 'lucide-react';

interface AvatarUploaderProps {
  currentUrl?: string;
  onUpload?: (url: string) => void;
}

export const AvatarUploader: React.FC<AvatarUploaderProps> = ({ currentUrl, onUpload }) => {
  const [url, setUrl] = useState(currentUrl || '');
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    if (url.trim()) {
      onUpload?.(url.trim());
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 max-w-md">
      <h4 className="text-base font-bold text-slate-900 mb-4">Cập Nhật Ảnh Đại Diện</h4>

      <div className="flex items-center gap-4 mb-4">
        <img
          src={url || 'https://api.dicebear.com/7.x/avataaars/svg?seed=Avatar'}
          alt="Preview"
          className="w-20 h-20 rounded-full border-2 border-slate-200 object-cover shadow-sm bg-slate-50"
        />
        <div className="text-xs text-slate-500">
          <p className="font-medium text-slate-700">Ảnh đại diện xem trước</p>
          <p className="mt-0.5">Nhập URL hình ảnh hoặc ảnh công khai từ link web/CDN.</p>
        </div>
      </div>

      <div className="space-y-3">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/my-photo.jpg"
          className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
        />

        <button
          onClick={handleSave}
          className="w-full py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-semibold rounded-lg shadow-sm transition-all flex items-center justify-center gap-2"
        >
          {saved ? (
            <>
              <Check className="w-4 h-4" /> Đã lưu ảnh thành công
            </>
          ) : (
            <>
              <Camera className="w-4 h-4" /> Cập nhật ảnh đại diện
            </>
          )}
        </button>
      </div>
    </div>
  );
};
