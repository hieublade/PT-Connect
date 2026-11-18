// Danh sách ảnh chân dung Huấn luyện viên thể hình độ phân giải cao chuẩn quốc tế
// Góc chụp chuyên nghiệp, trang phục thể thao/polo đen, khoanh tay cơ bắp đúng phong cách HFI / CITIGYM
const REAL_COACH_PORTRAITS: Record<string, string> = {
  // Lê Hoàng Cường: HLV thể hình khoanh tay áo polo đen (rất giống ảnh mẫu Đào Ngọc Huy)
  'cuong': 'https://images.unsplash.com/photo-1567013127542-490d757e51fc?auto=format&fit=crop&w=800&q=80',
  // Phạm Minh Dũng: Chuyên gia giảm mỡ & thể lực
  'dung': 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?auto=format&fit=crop&w=800&q=80',
  // Trần Quốc Bảo: Boxing, kickfit & thể lực cường độ cao
  'bao': 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&w=800&q=80',
  // Nguyễn Thu Hà: HLV nữ Pilates, Yoga & chỉnh dáng cột sống
  'ha': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
  // Đỗ Tuấn Kiệt: Giảng viên thể hình Hypertrophy & Sức mạnh
  'kiet': 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=800&q=80',
  // Vũ Hoàng: HLV Cardio & thể lực
  'hoang': 'https://images.unsplash.com/photo-1594381898411-846e7d193883?auto=format&fit=crop&w=800&q=80',
};

const DEFAULT_COACH_PORTRAITS = [
  'https://images.unsplash.com/photo-1567013127542-490d757e51fc?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=800&q=80',
  'https://images.unsplash.com/photo-1594381898411-846e7d193883?auto=format&fit=crop&w=800&q=80',
];

// Sinh avatar vector SVG nội bộ (Data URI) không phụ thuộc mạng hay dịch vụ bên ngoài, không bao giờ bị lỗi ảnh vỡ
export function getInitialAvatar(name?: string, role?: string): string {
  const cleanName = (name || (role === 'PT' ? 'HLV' : 'User')).trim();
  // Lấy 1-2 ký tự đầu (nếu là số như "11", hiển thị "11" hoặc chữ hoa)
  const initial = cleanName.length > 2 && !/^\d+$/.test(cleanName)
    ? cleanName.slice(0, 2).toUpperCase()
    : cleanName.slice(0, 2).toUpperCase();

  const isPt = role === 'PT' || cleanName.toLowerCase().includes('hlv');
  const gradStart = isPt ? '#EA580C' : '#3B82F6';
  const gradEnd = isPt ? '#F59E0B' : '#06B6D4';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <defs>
      <linearGradient id="avatarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="${gradStart}" />
        <stop offset="100%" stop-color="${gradEnd}" />
      </linearGradient>
    </defs>
    <circle cx="50" cy="50" r="50" fill="url(#avatarGrad)" />
    <text x="50%" y="54%" font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="36" font-weight="bold" fill="#ffffff" text-anchor="middle" dominant-baseline="middle">${initial}</text>
  </svg>`;
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`;
}

export function getAvatarUrl(name?: string, explicitUrl?: string, role?: string): string {
  // Loại bỏ các URL không an toàn hoặc hết hạn: blob: (chỉ tồn tại tạm trong RAM), dicebear (dễ bị chặn/lỗi)
  if (explicitUrl && 
      !explicitUrl.includes('dicebear') && 
      !explicitUrl.startsWith('blob:') &&
      explicitUrl.trim().length > 0) {
    return explicitUrl;
  }
  if (!name) return getInitialAvatar(name, role);

  const lower = name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  if (lower.includes('cuong')) return REAL_COACH_PORTRAITS['cuong'];
  if (lower.includes('dung')) return REAL_COACH_PORTRAITS['dung'];
  if (lower.includes('bao')) return REAL_COACH_PORTRAITS['bao'];
  if (lower.includes('ha')) return REAL_COACH_PORTRAITS['ha'];
  if (lower.includes('kiet')) return REAL_COACH_PORTRAITS['kiet'];
  if (lower.includes('hoang')) return REAL_COACH_PORTRAITS['hoang'];

  // Nếu tên chỉ toàn số hoặc quá ngắn (ví dụ: "11"), dùng SVG Initials với màu đẹp thay vì lấy ảnh ngẫu nhiên
  if (/^\d+$/.test(name.trim()) || name.trim().length <= 2) {
    return getInitialAvatar(name, role);
  }

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % DEFAULT_COACH_PORTRAITS.length;
  return DEFAULT_COACH_PORTRAITS[index];
}
