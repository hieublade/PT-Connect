import React from 'react';
import { FileText, ExternalLink, Image as ImageIcon, Upload, X, CheckCircle2 } from 'lucide-react';

export interface EvidenceItem {
  url?: string;
  name: string;
  isRealUrl: boolean;
}

export interface ParsedEvidence {
  cleanText: string;
  items: EvidenceItem[];
}

/**
 * Nén và chuyển đổi tệp ảnh của người dùng thành Base64 Data URL (kích thước tối ưu 30-50KB)
 * Đảm bảo mọi ảnh người dùng tải lên từ máy tính luôn hiển thị chính xác ảnh đó
 */
export async function compressImageToDataUrl(file: File, maxWidth = 900, quality = 0.72): Promise<string> {
  return new Promise((resolve) => {
    try {
      const reader = new FileReader();
      reader.onload = (e) => {
        const rawResult = e.target?.result as string;
        if (!rawResult) {
          resolve('');
          return;
        }
        const img = new Image();
        img.onload = () => {
          let width = img.width;
          let height = img.height;
          if (width > maxWidth || height > maxWidth) {
            if (width > height) {
              height = Math.round((height * maxWidth) / width);
              width = maxWidth;
            } else {
              width = Math.round((width * maxWidth) / height);
              height = maxWidth;
            }
          }
          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          if (ctx) {
            ctx.drawImage(img, 0, 0, width, height);
            const dataUrl = canvas.toDataURL('image/jpeg', quality);
            try {
              localStorage.setItem('evidence_img_' + file.name, dataUrl);
            } catch {
              // Ignore if quota exceeded
            }
            resolve(dataUrl);
          } else {
            resolve(rawResult);
          }
        };
        img.onerror = () => resolve(rawResult);
        img.src = rawResult;
      };
      reader.onerror = () => resolve('');
      reader.readAsDataURL(file);
    } catch {
      resolve('');
    }
  });
}

/**
 * Trích xuất các liên kết hình ảnh, tên tệp đính kèm và làm sạch văn bản tường trình
 */
export function parseEvidence(rawText?: string | null): ParsedEvidence {
  if (!rawText) return { cleanText: '', items: [] };

  const items: EvidenceItem[] = [];
  let text = rawText;

  // 1. Tìm các cấu trúc [Ảnh đối chứng: <url_hoặc_tên_file>] hoặc [Ảnh: ...] hoặc [Tệp: ...]
  const bracketRegex = /\[(?:Ảnh đối chứng|Ảnh|Tệp):\s*([^\]]+)\]/gi;
  let match;
  while ((match = bracketRegex.exec(rawText)) !== null) {
    const rawVal = match[1].trim();
    const isUrl = rawVal.startsWith('/uploads/') || rawVal.startsWith('http://') || rawVal.startsWith('https://') || rawVal.startsWith('data:image/');
    
    // Kiểm tra xem trong localStorage có ảnh thực tế người dùng vừa upload không
    let cachedDataUrl: string | null = null;
    if (!isUrl) {
      try {
        cachedDataUrl = localStorage.getItem('evidence_img_' + rawVal);
      } catch {}
    }

    // Tự động map tên tệp sang URL thực tế hoặc /uploads/disputes/<tên_tệp>
    const resolvedUrl = isUrl
      ? rawVal
      : (cachedDataUrl || (rawVal ? `/uploads/disputes/${encodeURI(rawVal)}` : undefined));

    items.push({
      url: resolvedUrl,
      name: isUrl ? (rawVal.startsWith('data:image/') ? 'Ảnh chụp đối chứng' : (rawVal.split('/').pop() || 'Ảnh bằng chứng')) : rawVal,
      isRealUrl: Boolean(resolvedUrl),
    });
  }
  text = text.replace(bracketRegex, '').replace(/\|\s*$/, '').trim();

  // 2. Tìm các URL hoặc tên file ảnh cách nhau bằng dấu ' | '
  const parts = text.split(' | ');
  const remainingParts: string[] = [];
  for (const part of parts) {
    const trimmed = part.trim();
    const isUrl = trimmed.startsWith('/uploads/') || trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.startsWith('data:image/');
    const isImageFile = /\.(png|jpe?g|webp|gif|bmp|svg)$/i.test(trimmed);

    let cachedDataUrl: string | null = null;
    if (!isUrl && isImageFile) {
      try {
        cachedDataUrl = localStorage.getItem('evidence_img_' + trimmed);
      } catch {}
    }

    if (isUrl || isImageFile || cachedDataUrl) {
      const resolvedUrl = isUrl ? trimmed : (cachedDataUrl || `/uploads/disputes/${encodeURI(trimmed)}`);
      if (!items.some(it => it.url === resolvedUrl || it.name === trimmed)) {
        items.push({
          url: resolvedUrl,
          name: trimmed.startsWith('data:image/') ? 'Ảnh đối chứng' : (trimmed.split('/').pop() || 'Ảnh bằng chứng'),
          isRealUrl: true,
        });
      }
    } else {
      remainingParts.push(trimmed);
    }
  }

  text = remainingParts.join(' | ').trim();
  text = text.replace(/^["“”']+|["“”']+$/g, '').trim();

  return { cleanText: text, items };
}

export const DEFAULT_FALLBACK_SVG = 'data:image/svg+xml;utf8,' + encodeURIComponent(`
<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200" viewBox="0 0 300 200" fill="#0f172a">
  <rect width="300" height="200" fill="#1e293b"/>
  <rect x="20" y="20" width="260" height="160" rx="12" fill="#334155" stroke="#475569" stroke-width="2"/>
  <circle cx="150" cy="85" r="28" fill="#3b82f6" fill-opacity="0.2"/>
  <path d="M141 85 L147 91 L160 76" stroke="#60a5fa" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="150" y="132" fill="#f8fafc" font-size="13" font-family="sans-serif" font-weight="bold" text-anchor="middle">Tài Liệu Đối Soát Vụ Việc</text>
  <text x="150" y="152" fill="#94a3b8" font-size="10" font-family="sans-serif" text-anchor="middle">✓ Đã xác minh đính kèm</text>
</svg>
`);

/**
 * Thẻ hiển thị một bằng chứng (ảnh thumbnail hoặc badge tệp đối chứng)
 */
export const EvidenceImageCard: React.FC<{
  item: EvidenceItem;
  onPreviewImage?: (url: string, name: string) => void;
}> = ({ item, onPreviewImage }) => {
  const [imgSrc, setImgSrc] = React.useState<string>(item.url || '');
  const [hasError, setHasError] = React.useState(false);

  React.useEffect(() => {
    setImgSrc(item.url || '');
    setHasError(false);
  }, [item.url]);

  const handleOpenPreview = () => {
    const targetUrl = imgSrc || item.url || DEFAULT_FALLBACK_SVG;
    if (onPreviewImage) {
      onPreviewImage(targetUrl, item.name);
    } else {
      window.open(targetUrl, '_blank');
    }
  };

  // Nếu hoàn toàn không có url và đã báo lỗi
  if (!imgSrc && hasError) {
    return (
      <div
        onClick={handleOpenPreview}
        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-50/80 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-xs text-indigo-800 dark:text-indigo-300 shadow-xs cursor-pointer hover:bg-indigo-100/80 transition"
        title="Bấm để xem tệp đối chứng"
      >
        <ImageIcon className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400 shrink-0" />
        <span>Tệp ảnh đối chứng: <b>{item.name}</b></span>
        <span className="text-[10px] font-semibold text-emerald-700 dark:text-emerald-400 bg-emerald-100/80 dark:bg-emerald-950 px-1.5 py-0.5 rounded border border-emerald-300/60 ml-1">
          ✓ Đã nộp
        </span>
      </div>
    );
  }

  return (
    <div
      className="group relative rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-900 shadow-xs hover:shadow-md transition cursor-pointer"
      onClick={handleOpenPreview}
      title={`Bấm để phóng to xem ảnh đối chứng: ${item.name}`}
    >
      <img
        src={imgSrc || item.url}
        alt={item.name}
        onError={() => {
          // Tự động fallback sang placeholder chuẩn nếu tệp ảnh riêng lẻ chưa tải được
          if (imgSrc !== DEFAULT_FALLBACK_SVG) {
            setImgSrc(DEFAULT_FALLBACK_SVG);
          } else {
            setHasError(true);
          }
        }}
        className="h-20 w-32 object-cover group-hover:scale-105 transition duration-200"
      />
      <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition flex items-center justify-center">
        <span className="text-[11px] font-bold text-white bg-black/70 px-2 py-0.5 rounded-md flex items-center gap-1 shadow-xs">
          <ExternalLink className="w-3 h-3" /> Xem ảnh
        </span>
      </div>
      <div className="p-1 bg-white dark:bg-slate-900 text-[10px] text-slate-600 dark:text-slate-300 truncate max-w-[128px] text-center border-t border-slate-100 dark:border-slate-800 font-medium">
        {item.name}
      </div>
    </div>
  );
};

/**
 * Component hiển thị danh sách bằng chứng & ảnh đính kèm
 */
export const EvidenceAttachmentList: React.FC<{
  items: EvidenceItem[];
  onPreviewImage?: (url: string, name: string) => void;
}> = ({ items, onPreviewImage }) => {
  if (!items || items.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2 pt-2">
      {items.map((item, idx) => (
        <EvidenceImageCard key={idx} item={item} onPreviewImage={onPreviewImage} />
      ))}
    </div>
  );
};

export interface SelectedEvidenceFile {
  file: File;
  preview: string;
}

/**
 * Component hỗ trợ chọn và xem trước nhiều ảnh bằng chứng cùng lúc
 */
export const MultiImageUploader: React.FC<{
  files: SelectedEvidenceFile[];
  onChange: (files: SelectedEvidenceFile[]) => void;
  maxFiles?: number;
  label?: string;
  subLabel?: string;
}> = ({
  files,
  onChange,
  maxFiles = 6,
  label = 'Ảnh chụp bằng chứng đối chứng',
  subLabel = 'Hỗ trợ chọn nhiều ảnh cùng lúc (PNG, JPG, WEBP tối đa 5MB mỗi ảnh)',
}) => {
  const fileInputRef = React.useRef<HTMLInputElement | null>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files;
    if (!selected || selected.length === 0) return;

    const remainingSlots = maxFiles - files.length;
    if (remainingSlots <= 0) {
      alert(`Bạn chỉ có thể tải lên tối đa ${maxFiles} ảnh.`);
      return;
    }

    const filesToProcess = Array.from(selected).slice(0, remainingSlots);
    let loadedCount = 0;
    const addedItems: SelectedEvidenceFile[] = [];

    filesToProcess.forEach((file) => {
      if (!file.type.startsWith('image/')) {
        alert(`Tệp "${file.name}" không phải là ảnh hợp lệ!`);
        loadedCount++;
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        alert(`Tệp "${file.name}" vượt quá giới hạn 5MB!`);
        loadedCount++;
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        addedItems.push({ file, preview: reader.result as string });
        loadedCount++;
        if (loadedCount === filesToProcess.length) {
          onChange([...files, ...addedItems]);
        }
      };
      reader.onerror = () => {
        loadedCount++;
        if (loadedCount === filesToProcess.length && addedItems.length > 0) {
          onChange([...files, ...addedItems]);
        }
      };
      reader.readAsDataURL(file);
    });

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleRemove = (index: number) => {
    onChange(files.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="text-xs font-bold text-slate-700 dark:text-slate-200">
          {label} <span className="text-slate-400 font-normal">({files.length}/{maxFiles} ảnh)</span>:
        </label>
        {files.length > 0 && files.length < maxFiles && (
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="text-[11px] font-bold text-amber-600 dark:text-amber-400 hover:underline flex items-center gap-1 cursor-pointer"
          >
            + Chọn thêm ảnh
          </button>
        )}
      </div>

      {/* Grid danh sách ảnh đã chọn */}
      {files.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
          {files.map((item, idx) => (
            <div
              key={idx}
              className="relative group rounded-xl overflow-hidden border border-slate-300 dark:border-slate-700 bg-slate-900 shadow-2xs"
            >
              <img
                src={item.preview}
                alt={item.file.name}
                className="h-24 w-full object-cover group-hover:scale-105 transition duration-200"
              />
              <button
                type="button"
                onClick={() => handleRemove(idx)}
                className="absolute top-1.5 right-1.5 bg-red-600 hover:bg-red-700 text-white p-1 rounded-full shadow-md transition cursor-pointer"
                title="Xóa ảnh này"
              >
                <X className="w-3.5 h-3.5" />
              </button>
              <div className="p-1 bg-white/95 dark:bg-slate-900/95 text-[10px] text-slate-700 dark:text-slate-300 truncate text-center border-t border-slate-200 dark:border-slate-800 font-medium">
                {item.file.name} ({(item.file.size / 1024).toFixed(0)} KB)
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Nút/Vùng chọn ảnh */}
      {files.length < maxFiles && (
        <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-amber-500 rounded-xl p-3.5 cursor-pointer hover:bg-amber-50/50 dark:hover:bg-amber-950/20 transition bg-slate-50/50 dark:bg-slate-800/40 text-center">
          <Upload className="w-5 h-5 text-slate-400 mb-1" />
          <span className="text-xs font-bold text-slate-700 dark:text-slate-200">
            {files.length === 0
              ? 'Nhấn vào đây để tải ảnh chụp bằng chứng (Chọn được nhiều ảnh cùng lúc)'
              : 'Nhấn để chọn thêm ảnh đối chứng'}
          </span>
          <span className="text-[11px] text-slate-400 mt-0.5">{subLabel}</span>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileSelect}
            className="hidden"
          />
        </label>
      )}
    </div>
  );
};

/**
 * Xử lý tải lên danh sách nhiều ảnh: nén Base64 Data URL và gửi lên máy chủ
 */
export async function uploadMultipleEvidenceFiles(
  files: SelectedEvidenceFile[],
  apiPost: (url: string, data: any) => Promise<any>
): Promise<string[]> {
  if (!files || files.length === 0) return [];

  const urls: string[] = [];
  for (const item of files) {
    let fileDataUrl = '';
    try {
      fileDataUrl = await compressImageToDataUrl(item.file);
    } catch {}

    try {
      const formData = new FormData();
      formData.append('file', item.file);
      const res: any = await apiPost('/disputes/upload-evidence', formData);
      const serverUrl = res?.url || (res && typeof res === 'object' && res.url);
      if (serverUrl) {
        urls.push(serverUrl);
      } else if (fileDataUrl) {
        urls.push(fileDataUrl);
      } else {
        urls.push(item.file.name);
      }
    } catch (err) {
      console.warn('Lỗi tải ảnh lên máy chủ, sử dụng dữ liệu ảnh trực tiếp:', item.file.name, err);
      if (fileDataUrl) {
        urls.push(fileDataUrl);
      } else {
        urls.push(item.file.name);
      }
    }
  }
  return urls;
}

/**
 * Kiểm tra xem bên liên quan (Học viên hoặc HLV) đã nộp bằng chứng cho yêu cầu hiện tại hay chưa
 * Hỗ trợ đồng bộ trạng thái giữa máy chủ và localStorage để đảm bảo reset về ĐANG CHỜ ngay khi Admin gửi yêu cầu
 */
export function isEvidenceSubmitted(
  dispute: {
    id: number;
    evidenceRequested?: boolean;
    evidenceRequestTarget?: 'BOTH' | 'PT' | 'STUDENT';
    studentEvidenceSubmitted?: boolean;
    ptEvidenceSubmitted?: boolean;
    additionalEvidenceStudent?: string;
    additionalEvidencePt?: string;
  },
  role: 'STUDENT' | 'PT'
): boolean {
  if (!dispute) return false;

  const target = dispute.evidenceRequestTarget;
  const isTargeted =
    target === 'BOTH' ||
    target === role ||
    (!target && role === 'STUDENT');

  if (!isTargeted) return false;

  const localKey = `dispute_${dispute.id}_${role.toLowerCase()}_submitted`;
  let localVal: string | null = null;
  try {
    localVal = localStorage.getItem(localKey);
  } catch {}

  if (role === 'STUDENT') {
    if (localVal === 'false') return false;
    if (dispute.studentEvidenceSubmitted !== undefined && dispute.studentEvidenceSubmitted !== null) {
      return Boolean(dispute.studentEvidenceSubmitted);
    }
    if (localVal !== null) return localVal === 'true';
    return false;
  } else {
    if (localVal === 'false') return false;
    if (dispute.ptEvidenceSubmitted !== undefined && dispute.ptEvidenceSubmitted !== null) {
      return Boolean(dispute.ptEvidenceSubmitted);
    }
    if (localVal !== null) return localVal === 'true';
    return false;
  }
}
