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

export function getAvatarUrl(name?: string, explicitUrl?: string): string {
  if (explicitUrl && !explicitUrl.includes('dicebear')) {
    return explicitUrl;
  }
  if (!name) return DEFAULT_COACH_PORTRAITS[0];

  const lower = name.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  if (lower.includes('cuong')) return REAL_COACH_PORTRAITS['cuong'];
  if (lower.includes('dung')) return REAL_COACH_PORTRAITS['dung'];
  if (lower.includes('bao')) return REAL_COACH_PORTRAITS['bao'];
  if (lower.includes('ha')) return REAL_COACH_PORTRAITS['ha'];
  if (lower.includes('kiet')) return REAL_COACH_PORTRAITS['kiet'];
  if (lower.includes('hoang')) return REAL_COACH_PORTRAITS['hoang'];

  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % DEFAULT_COACH_PORTRAITS.length;
  return DEFAULT_COACH_PORTRAITS[index];
}
