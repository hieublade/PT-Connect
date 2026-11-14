type CertSource = { certificateUrl?: string | null; certificateUrls?: string | string[] | null };

const cleanOne = (raw: unknown): string | null => {
  if (raw == null) return null;
  if (Array.isArray(raw)) {
    for (const item of raw) {
      const c = cleanOne(item);
      if (c) return c;
    }
    return null;
  }
  let s = String(raw).trim();
  if (!s) return null;
  if (s.startsWith('[') && s.endsWith(']')) {
    try {
      return cleanOne(JSON.parse(s));
    } catch {
      s = s.slice(1, -1).trim().replace(/^["']|["']$/g, '').trim();
      return s || null;
    }
  }
  return s.replace(/^"|"$/g, '').trim() || null;
};

/** Ưu tiên certificateUrl, fallback certificateUrls (chuỗi / chuỗi JSON / mảng). */
export const resolveCertificateUrl = (src?: CertSource | null): string | null =>
  src ? cleanOne(src.certificateUrl) ?? cleanOne(src.certificateUrls) : null;

export const isHttpUrl = (s?: string | null): boolean =>
  !!s && (/^https?:\/\//i.test(s.trim()) || s.trim().startsWith('/') || s.trim().startsWith('data:image/') || s.trim().startsWith('blob:'));

export const CERT_URL_MAX = 500;
