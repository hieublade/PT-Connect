export type UserRole = 'STUDENT' | 'PT' | 'ADMIN';
export type UserStatus = 'ACTIVE' | 'PENDING' | 'SUSPENDED';

export interface User {
  id: number;
  fullName: string;
  email: string;
  phone: string;
  role: UserRole;
  status: UserStatus;
  avatarUrl?: string;
}

export interface PtProfile {
  id: number;
  userId: number;
  fullName: string;
  email: string;
  phone: string;
  bio?: string;
  experienceYears: number;
  availableLocations: string;
  locationPricingNote?: string;
  certificateUrl?: string | null;                 // trường chuẩn 1NF
  certificateUrls?: string | string[] | null;     // alias cũ: có thể là chuỗi, '["..."]' hoặc mảng
  averageRating: number;
  totalReviews: number;
  lowestPrice?: number;
  avatarUrl?: string;
  verificationStatus: 'PENDING' | 'VERIFIED' | 'REJECTED';
  userStatus?: UserStatus;
  createdAt?: string;
}

export interface Course {
  id: number;
  ptId: number;
  title: string;
  description: string;
  basePrice: number;
  totalSessions: number;
  validityDays: number;
  status: 'ACTIVE' | 'INACTIVE';
  trainingLocation?: string;
}

export interface AvailabilitySlot {
  id: number;
  ptId: number;
  startTime: string;
  endTime: string;
  status: 'AVAILABLE' | 'BOOKED' | 'LOCKED';
}

export interface Booking {
  id: number;
  bookingType: 'PACKAGE' | 'TRIAL';
  status: 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED';
  startTime: string;
  endTime: string;
  studentId: number;
  studentName?: string;
  studentPhone?: string;
  ptId: number;
  ptName?: string;
  courseTitle?: string;
  totalAmount?: number;
  sessionFee?: number;
  trainingLocation?: string;
  cancellationReason?: string;
  cancelledByRole?: string;
}

export interface Review {
  id: number;
  bookingId: number;
  studentId?: number | null;
  studentName?: string | null;
  studentAvatarUrl?: string | null;
  ptId?: number | null;
  ptName?: string | null;
  rating: number;
  comment?: string | null;
  createdAt?: string | null;
}

export interface CreateReviewPayload {
  bookingId: number;
  rating: number;
  comment?: string;
}

export interface UpdatePtProfilePayload {
  bio?: string;
  experienceYears?: number;
  availableLocations: string;
  locationPricingNote?: string;
  certificateUrl?: string;
}

export interface PaymentTransaction {
  id: number;
  amount: number;
  paymentType: string;
  paymentMethod: string;
  status: string;
  transactionRef?: string;
  description?: string;
  createdAt?: string;
}

export interface Wallet {
  id: number;
  userId: number;
  balance: number;
  lockedBalance: number;
  currency: string;
  status: 'ACTIVE' | 'FROZEN';
  transactions?: PaymentTransaction[];
}

export interface Enrollment {
  id: number;
  studentId?: number;
  studentName?: string;
  studentEmail?: string;
  courseId: number;
  courseTitle?: string;
  ptId?: number;
  ptName?: string;
  trainingLocation?: string;
  finalPrice?: number;
  totalSessions: number;
  remainingSessions: number;
  startDate?: string;
  endDate?: string;
  contractUrl?: string;
  status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  createdAt?: string;
}
