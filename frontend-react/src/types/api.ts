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
  certificateUrls?: string[];
  averageRating: number;
  totalReviews: number;
  lowestPrice?: number;
  avatarUrl?: string;
  verificationStatus: 'PENDING' | 'VERIFIED' | 'REJECTED';
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
}

export interface Wallet {
  id: number;
  userId: number;
  balance: number;
  lockedBalance: number;
  currency: string;
  status: 'ACTIVE' | 'FROZEN';
}

export interface PaymentTransaction {
  id: number;
  amount: number;
  paymentType: string;
  paymentMethod: string;
  status: string;
  transactionRef?: string;
  description?: string;
  createdAt: string;
}

export interface Enrollment {
  id: number;
  courseId: number;
  courseTitle?: string;
  ptName?: string;
  totalSessions: number;
  remainingSessions: number;
  status: 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
  contractUrl?: string;
  startDate?: string;
  endDate?: string;
}
