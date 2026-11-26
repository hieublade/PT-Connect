const REAL_COACH_PORTRAITS: Record<string, string> = {
  'cuong': 'https://images.unsplash.com/photo-1567013127542-490d757e51fc?auto=format&fit=crop&w=800&q=80',
  'dung': 'https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?auto=format&fit=crop&w=800&q=80',
  'bao': 'https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&w=800&q=80',
  'ha': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80',
  'kiet': 'https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?auto=format&fit=crop&w=800&q=80',
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

export function getInitialAvatar(name?: string, role?: string): string {
  const cleanName = (name || (role === 'PT' ? 'HLV' : 'User')).trim();
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
