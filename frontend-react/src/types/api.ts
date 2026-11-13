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
  ownerName?: string;
  ownerEmail?: string;
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

export interface Workout {
  id: number;
  planId: number;
  exerciseName: string;
  targetMuscle?: string;
  sets: number;
  reps: number;
  weightKg?: number;
  restSeconds: number;
  videoDemoUrl?: string;
}

export interface WorkoutPlan {
  id: number;
  enrollmentId: number;
  ptId?: number;
  ptName?: string;
  studentName?: string;
  courseName?: string;
  title: string;
  goal?: string;
  startDate?: string;
  endDate?: string;
  createdAt?: string;
  workouts?: Workout[];
}


export interface WithdrawPayload {
  amount: number;
  bankName: string;
  accountNumber: string;
  accountHolderName: string;
}


export interface AdminStatistics {
  totalStudents: number;
  totalPts: number;
  totalBookings: number;
  totalRevenue: number;
}

export interface AdminBookingAnalytics {
  id: number;
  studentId: number;
  studentName: string;
  ptId: number;
  ptName: string;
  bookingType: 'PACKAGE' | 'TRIAL';
  status: 'PENDING' | 'CONFIRMED' | 'COMPLETED' | 'CANCELLED';
  startTime: string;
  endTime: string;
  sessionFee?: number;
  createdAt: string;
  cancelledBy?: string;
  cancellationReason?: string;
}

export interface AdminPaymentAnalytics {
  id: number;
  walletId?: number;
  userId?: number;
  userName?: string;
  enrollmentId?: number;
  amount: number;
  paymentType: string;
  paymentMethod: string;
  status: string;
  transactionRef?: string;
  createdAt: string;
}

export interface ChatMessage {
  id: number;
  senderId: number;
  senderName: string;
  senderAvatar?: string;
  recipientId: number;
  recipientName: string;
  recipientAvatar?: string;
  content: string;
  isRead: boolean;
  bookingId?: number;
  createdAt: string;
}

export interface ChatConversation {
  partnerId: number;
  partnerName: string;
  partnerEmail: string;
  partnerAvatar?: string;
  partnerRole: string;
  lastMessage: string;
  lastMessageTime?: string;
  unreadCount: number;
}

export interface DisputeCase {
  id: number;
  bookingId: number;
  studentName: string;
  studentEmail: string;
  studentPhone: string;
  ptName: string;
  ptEmail: string;
  courseTitle: string;
  sessionFee: number;
  scheduledTime: string;
  disputeType: string;
  disputeTypeLabel: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  complainant: 'STUDENT' | 'PT';
  summary: string;
  studentStatement: string;
  ptStatement: string;
  counterStatement?: string;
  evidenceNote: string;
  status: string;
  resolutionDecision?: string;
  resolvedAt?: string;
  createdAt?: string;
}

export interface CreateDisputePayload {
  bookingId: number;
  disputeType: string;
  disputeTypeLabel?: string;
  severity?: 'HIGH' | 'MEDIUM' | 'LOW';
  statement: string;
  evidenceNote?: string;
}


