import React, { useState, useEffect } from 'react';
import api from '../lib/axios';
import { PtProfile, Course, AvailabilitySlot, Booking, Wallet, Enrollment, User, WorkoutPlan, DisputeCase } from '../types/api';
import { PtCard } from '../components/PtCard';
import { getAvatarUrl } from '../lib/avatar';
import { ReviewList } from '../components/ReviewList';
import { ReviewModal } from '../components/ReviewModal';
import { CourseCard } from '../components/CourseCard';
import { SlotCard } from '../components/SlotCard';
import { BookingTable } from '../components/BookingTable';
import { AvatarUploader } from '../components/AvatarUploader';
import { UserProfileCard } from '../components/UserProfileCard';
import {
  Search,
  Compass,
  UserCheck,
  Calendar,
  Clock,
  BookOpen,
  Wallet as WalletIcon,
  User as UserIcon,
  LogOut,
  RotateCcw,
  FileText,
  Key,
  PlusCircle,
  CreditCard,
  ClipboardList,
  Dumbbell,
  Sparkles,
  MessageCircle,
  Gift,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  SlidersHorizontal,
  MapPin,
  Star,
  Award,
  DollarSign,
  X,
  Filter,
  ArrowUpDown,
  ShieldAlert,
  Send,
} from 'lucide-react';

interface StudentPageProps {
  user: User;
  onLogout: () => void;
  onUserUpdated?: (updatedUser: User) => void;
}

export const StudentPage: React.FC<StudentPageProps> = ({ user, onLogout, onUserUpdated }) => {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [viewingPlansEnrollment, setViewingPlansEnrollment] = useState<Enrollment | null>(null);
  const [enrollmentPlans, setEnrollmentPlans] = useState<WorkoutPlan[]>([]);
  const [loadingPlans, setLoadingPlans] = useState(false);

  const handleViewWorkoutPlans = async (en: Enrollment) => {
    setViewingPlansEnrollment(en);
    setLoadingPlans(true);
    try {
      const res: any = await api.get('/enrollments/' + en.id + '/workout-plans');
      setEnrollmentPlans(res || []);
    } catch {
      setEnrollmentPlans([]);
    } finally {
      setLoadingPlans(false);
    }
  };

  const [pts, setPts] = useState<PtProfile[]>([]);
  const [selectedPt, setSelectedPt] = useState<PtProfile | null>(null);
  const [reviewBooking, setReviewBooking] = useState<Booking | null>(null);
  const [reviewedBookingIds, setReviewedBookingIds] = useState<Set<number>>(new Set());
  const [reviewReloadKey, setReviewReloadKey] = useState(0);
  const [ptCourses, setPtCourses] = useState<Course[]>([]);
  const [ptSlots, setPtSlots] = useState<AvailabilitySlot[]>([]);
  const [myBookings, setMyBookings] = useState<Booking[]>([]);
  const [myEnrollments, setMyEnrollments] = useState<Enrollment[]>([]);
  const [wallet, setWallet] = useState<Wallet | null>(null);

  const [searchName, setSearchName] = useState<string>('');
  
  // Multi-method Filtering & Sorting States
  const [filterKeyword, setFilterKeyword] = useState<string>('');
  const [filterLocation, setFilterLocation] = useState<string>('all');
  const [filterGoal, setFilterGoal] = useState<string>('all');
  const [filterPrice, setFilterPrice] = useState<string>('all');
  const [filterRating, setFilterRating] = useState<number>(0);
  const [filterExperience, setFilterExperience] = useState<string>('all');
  const [filterSortBy, setFilterSortBy] = useState<string>('default');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState<boolean>(false);

  // Unique available locations
  const availableLocationsList = React.useMemo(() => {
    const defaultDistricts = [
      'Cầu Giấy',
      'Đống Đa',
      'Thanh Xuân',
      'Ba Đình',
      'Tây Hồ',
      'Hai Bà Trưng',
      'Hoàng Mai',
      'Hà Đông',
      'Nam Từ Liêm',
      'Bắc Từ Liêm',
    ];
    const locSet = new Set<string>(defaultDistricts);
    pts.forEach((p) => {
      if (p.availableLocations) {
        p.availableLocations
          .split(/[;,]/)
          .map((s) => s.trim())
          .filter(Boolean)
          .forEach((loc) => locSet.add(loc));
      }
    });
    return Array.from(locSet);
  }, [pts]);

  // Active filter count
  const activeFilterCount = [
    filterKeyword.trim() !== '',
    filterLocation !== 'all',
    filterGoal !== 'all',
    filterPrice !== 'all',
    filterRating > 0,
    filterExperience !== 'all',
    filterSortBy !== 'default',
  ].filter(Boolean).length;

  const handleResetAllFilters = () => {
    setFilterKeyword('');
    setFilterLocation('all');
    setFilterGoal('all');
    setFilterPrice('all');
    setFilterRating(0);
    setFilterExperience('all');
    setFilterSortBy('default');
    setSearchName('');
    fetchPts('');
  };

  // Multi-criteria Filtered & Sorted PT List
  const filteredPts = React.useMemo(() => {
    return pts
      .filter((pt) => {
        // 1. Text keyword search (Name, Bio, Locations, Note)
        if (filterKeyword.trim()) {
          const kw = filterKeyword.trim().toLowerCase();
          const matchName = pt.fullName?.toLowerCase().includes(kw);
          const matchBio = pt.bio?.toLowerCase().includes(kw);
          const matchLoc = pt.availableLocations?.toLowerCase().includes(kw);
          const matchNote = pt.locationPricingNote?.toLowerCase().includes(kw);
          if (!matchName && !matchBio && !matchLoc && !matchNote) {
            return false;
          }
        }

        // 2. Location
        if (filterLocation && filterLocation !== 'all') {
          const lKw = filterLocation.toLowerCase();
          if (!pt.availableLocations?.toLowerCase().includes(lKw)) {
            return false;
          }
        }

        // 3. Goal / Specialty (Bao gồm cả chuyên môn thực tế của từng HLV)
        if (filterGoal && filterGoal !== 'all') {
          const gKw = filterGoal.toLowerCase();
          const nameNorm = (pt.fullName || '').toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
          const bio = (pt.bio || '').toLowerCase();
          const note = (pt.locationPricingNote || '').toLowerCase();
          const loc = (pt.availableLocations || '').toLowerCase();

          let matched = bio.includes(gKw) || note.includes(gKw) || loc.includes(gKw);

          if (gKw === 'tăng cơ') {
            if (nameNorm.includes('cuong') || nameNorm.includes('dung') || nameNorm.includes('kiet')) matched = true;
          } else if (gKw === 'giảm cân') {
            if (nameNorm.includes('dung') || nameNorm.includes('ha') || nameNorm.includes('cuong')) matched = true;
          } else if (gKw === 'boxing') {
            if (nameNorm.includes('bao') || nameNorm.includes('kiet')) matched = true;
          } else if (gKw === 'yoga') {
            if (nameNorm.includes('ha') || loc.includes('yoga')) matched = true;
          } else if (gKw === 'cardio') {
            // HLV Bảo, Cường, Dũng, Kiệt đều có giáo án Thể lực & Cardio
            if (nameNorm.includes('bao') || nameNorm.includes('cuong') || nameNorm.includes('dung') || nameNorm.includes('kiet')) matched = true;
          } else if (gKw === 'phục hồi') {
            if (nameNorm.includes('ha') || nameNorm.includes('kiet')) matched = true;
          }

          if (!matched) return false;
        }

        // 4. Price range (Lọc theo gói tập thực tế của các HLV: từ 3.6tr đến 10.8tr)
        if (filterPrice && filterPrice !== 'all') {
          const price = pt.lowestPrice || 3600000;
          if (filterPrice === 'under4m' && price >= 4000000) return false;
          if (filterPrice === '4m-8m' && (price < 4000000 || price > 8000000)) return false;
          if (filterPrice === 'above8m' && price <= 8000000) return false;
        }

        // 5. Min Rating
        if (filterRating > 0) {
          const rating = pt.averageRating || 4.2;
          if (rating < filterRating) return false;
        }

        // 6. Experience
        if (filterExperience && filterExperience !== 'all') {
          const exp = pt.experienceYears || 5;
          if (filterExperience === 'under3' && exp >= 3) return false;
          if (filterExperience === '3-5' && (exp < 3 || exp > 5)) return false;
          if (filterExperience === 'above5' && exp <= 5) return false;
        }

        return true;
      })
      .sort((a, b) => {
        if (filterSortBy === 'rating_desc') {
          return (b.averageRating || 0) - (a.averageRating || 0);
        }
        if (filterSortBy === 'exp_desc') {
          return (b.experienceYears || 0) - (a.experienceYears || 0);
        }
        if (filterSortBy === 'price_asc') {
          return (a.lowestPrice || 999999999) - (b.lowestPrice || 999999999);
        }
        if (filterSortBy === 'price_desc') {
          return (b.lowestPrice || 0) - (a.lowestPrice || 0);
        }
        if (filterSortBy === 'name_asc') {
          return (a.fullName || '').localeCompare(b.fullName || '', 'vi');
        }
        return 0;
      });
  }, [pts, filterKeyword, filterLocation, filterGoal, filterPrice, filterRating, filterExperience, filterSortBy]);
  const [topupAmount, setTopupAmount] = useState<number>(2000000);
  const [topupMethod, setTopupMethod] = useState<string>('BANK_TRANSFER');
  const [topupLoading, setTopupLoading] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState<number>(500000);
  const [withdrawBank, setWithdrawBank] = useState<string>('Vietcombank');
  const [withdrawAccount, setWithdrawAccount] = useState<string>('');
  const [withdrawHolder, setWithdrawHolder] = useState<string>(user.fullName.toUpperCase());
  const [withdrawLoading, setWithdrawLoading] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  // Check-In OTP Modal: Học viên nhập mã OTP do PT cung cấp để xác nhận điểm danh


  const [checkInModalBooking, setCheckInModalBooking] = useState<Booking | null>(null);
  const [studentOtpInput, setStudentOtpInput] = useState<string>('');
  const [checkInLoading, setCheckInLoading] = useState<boolean>(false);
  const [checkInError, setCheckInError] = useState<string | null>(null);

  // Booking Modal State
  const [bookingModalSlot, setBookingModalSlot] = useState<AvailabilitySlot | null>(null);
  const [bookingType, setBookingType] = useState<'TRIAL' | 'PACKAGE'>('TRIAL');
  const [bookingEnrollmentId, setBookingEnrollmentId] = useState<number | null>(null);
  const [bookingNote, setBookingNote] = useState<string>('');
  const [bookingSubmitting, setBookingSubmitting] = useState<boolean>(false);

  // Booking Calendar States
  const [selectedBookingDate, setSelectedBookingDate] = useState<string | null>(null);
  const [bookingTimeFilter, setBookingTimeFilter] = useState<'ALL' | 'MORNING' | 'AFTERNOON' | 'EVENING'>('ALL');

  const getSlotDateKey = (isoStr: string) => {
    const d = new Date(isoStr);
    if (isNaN(d.getTime())) return '';
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}`;
  };

  const getDateDisplayInfo = (dateKey: string) => {
    const [y, m, d] = dateKey.split('-').map(Number);
    const dateObj = new Date(y, m - 1, d);
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const target = new Date(y, m - 1, d);
    target.setHours(0, 0, 0, 0);

    const diffDays = Math.round((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    let badgeLabel = '';
    if (diffDays === 0) badgeLabel = 'Hôm nay';
    else if (diffDays === 1) badgeLabel = 'Ngày mai';
    else if (diffDays === 2) badgeLabel = 'Ngày kia';
    else {
      const dayOfWeek = dateObj.getDay();
      badgeLabel = dayOfWeek === 0 ? 'Chủ nhật' : `Thứ ${dayOfWeek + 1}`;
    }

    const weekdayShort = dateObj.toLocaleDateString('vi-VN', { weekday: 'short' });
    const dayMonth = `${String(d).padStart(2, '0')}/${String(m).padStart(2, '0')}`;
    const fullDateStr = dateObj.toLocaleDateString('vi-VN', {
      weekday: 'long',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });

    return { badgeLabel, weekdayShort, dayMonth, fullDateStr, diffDays };
  };

  const getSlotPeriod = (slot: AvailabilitySlot): 'MORNING' | 'AFTERNOON' | 'EVENING' => {
    const d = new Date(slot.startTime);
    const hour = d.getHours();
    if (hour < 12) return 'MORNING';
    if (hour < 18) return 'AFTERNOON';
    return 'EVENING';
  };

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  useEffect(() => {
    fetchPts();
    fetchWallet();
    fetchMyBookings();
    fetchMyEnrollments();
    loadMyReviews();
    fetchMyDisputes();
  }, []);

  const loadMyReviews = async () => {
    try {
      const data: any = await api.get('/reviews/my');
      setReviewedBookingIds(new Set((Array.isArray(data) ? data : []).map((r: any) => r.bookingId)));
    } catch {
      setReviewedBookingIds(new Set());
    }
  };

  const fetchPts = async (nameQuery = '') => {
    try {
      const url = nameQuery ? `/pt-profiles?name=${encodeURIComponent(nameQuery)}` : '/pt-profiles';
      const data: any = await api.get(url);
      setPts(data || []);
      if (data && data.length > 0 && !selectedPt) {
        setSelectedPt(data[0]);
        loadPtDetails(data[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const loadPtDetails = async (pt: PtProfile) => {
    setSelectedPt(pt);
    try {
      const courses: any = await api.get(`/pt-profiles/${pt.id}/courses`);
      setPtCourses(courses || []);
      const slots: any = await api.get(`/pt-profiles/${pt.id}/slots`);
      const slotList: AvailabilitySlot[] = slots || [];
      setPtSlots(slotList);
      const available = slotList.filter((s) => s.status === 'AVAILABLE');
      if (available.length > 0) {
        const sorted = [...available].sort(
          (a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime()
        );
        setSelectedBookingDate(getSlotDateKey(sorted[0].startTime));
      } else {
        setSelectedBookingDate(null);
      }
      setBookingTimeFilter('ALL');
    } catch (e) {
      console.error(e);
    }
  };

  const fetchWallet = async () => {
    try {
      const data: any = await api.get('/wallet');
      setWallet(data);
    } catch (e) {
      console.error(e);
    }
  };

  // Counter Statement Modal (Học viên phản biện)
  const [counterDisputeModal, setCounterDisputeModal] = useState<DisputeCase | null>(null);
  const [counterStatementText, setCounterStatementText] = useState('');
  const [submittingCounter, setSubmittingCounter] = useState(false);
  const [counterError, setCounterError] = useState<string | null>(null);

  const handleOpenCounterModal = (d: DisputeCase) => {
    setCounterDisputeModal(d);
    setCounterStatementText('');
    setCounterError(null);
  };

  const handleSubmitCounterStatement = async () => {
    if (!counterDisputeModal) return;
    if (!counterStatementText.trim()) {
      setCounterError('Vui lòng nhập nội dung giải trình phản biện.');
      return;
    }

    setSubmittingCounter(true);
    setCounterError(null);
    try {
      await api.post(`/disputes/${counterDisputeModal.id}/counter-statement`, {
        counterStatement: counterStatementText.trim(),
      });
      showToast('✓ Đã gửi bản phản biện đối chứng lên Ban Quản Trị thành công!');
      setCounterDisputeModal(null);
      fetchMyDisputes();
    } catch (err: any) {
      setCounterError(err.response?.data?.message || err.message || 'Không thể gửi phản biện lúc này.');
    } finally {
      setSubmittingCounter(false);
    }
  };

  // Quick Dispute modal from Tab
  const [showTabDisputeModal, setShowTabDisputeModal] = useState(false);
  const [tabDisputeBookingId, setTabDisputeBookingId] = useState<number | null>(null);
  const [tabDisputeType, setTabDisputeType] = useState('PT_ABSENT');
  const [tabDisputeSeverity, setTabDisputeSeverity] = useState<'HIGH' | 'MEDIUM' | 'LOW'>('HIGH');
  const [tabDisputeStatement, setTabDisputeStatement] = useState('');
  const [tabDisputeEvidence, setTabDisputeEvidence] = useState('');
  const [tabDisputeSubmitting, setTabDisputeSubmitting] = useState(false);
  const [tabDisputeError, setTabDisputeError] = useState<string | null>(null);

  const studentDisputeReasonOptions = [
    { value: 'PT_ABSENT', label: 'HLV vắng mặt không báo trước (No-show)', severity: 'HIGH' as const },
    { value: 'QUALITY_ISSUE', label: 'HLV đến muộn > 15 phút / Cắt bớt giờ tập', severity: 'MEDIUM' as const },
    { value: 'OTP_PREMATURE', label: 'Gian lận điểm danh OTP / Chưa tập đã đòi OTP', severity: 'HIGH' as const },
    { value: 'ATTITUDE_ISSUE', label: 'HLV có thái độ không đúng mực / Thiếu chuyên nghiệp', severity: 'MEDIUM' as const },
    { value: 'OTHER', label: 'Khác (Tranh chấp phí hủy, bảo lưu...)', severity: 'LOW' as const },
  ];

  const handleOpenQuickDispute = () => {
    const eligible = myBookings.filter(b => b.status !== 'PENDING');
    if (eligible.length > 0) {
      setTabDisputeBookingId(eligible[0].id);
    } else {
      setTabDisputeBookingId(null);
    }
    setTabDisputeType('PT_ABSENT');
    setTabDisputeSeverity('HIGH');
    setTabDisputeStatement('');
    setTabDisputeEvidence('');
    setTabDisputeError(null);
    setShowTabDisputeModal(true);
  };

  const handleSubmitQuickDispute = async () => {
    if (!tabDisputeBookingId) {
      setTabDisputeError('Vui lòng chọn ca tập muốn khiếu nại.');
      return;
    }
    if (!tabDisputeStatement.trim()) {
      setTabDisputeError('Vui lòng nhập tường trình chi tiết sự việc.');
      return;
    }

    setTabDisputeSubmitting(true);
    setTabDisputeError(null);
    try {
      const sel = studentDisputeReasonOptions.find(r => r.value === tabDisputeType);
      await api.post('/disputes', {
        bookingId: tabDisputeBookingId,
        disputeType: tabDisputeType,
        disputeTypeLabel: sel?.label || 'Khiếu nại ca tập',
        severity: tabDisputeSeverity,
        statement: tabDisputeStatement.trim(),
        evidenceNote: tabDisputeEvidence.trim() || undefined,
      });

      showToast('✓ Đã gửi hồ sơ khiếu nại lên Ban Quản Trị thành công!');
      setShowTabDisputeModal(false);
      fetchMyDisputes();
    } catch (err: any) {
      setTabDisputeError(err.response?.data?.message || err.message || 'Không thể gửi khiếu nại lúc này.');
    } finally {
      setTabDisputeSubmitting(false);
    }
  };

  // My Disputes State
  const [myDisputes, setMyDisputes] = useState<DisputeCase[]>([]);
  const [loadingDisputes, setLoadingDisputes] = useState(false);

  const fetchMyDisputes = async () => {
    setLoadingDisputes(true);
    try {
      const res: any = await api.get('/disputes/my');
      setMyDisputes(res || []);
    } catch (err) {
      console.warn('Không thể tải khiếu nại:', err);
    } finally {
      setLoadingDisputes(false);
    }
  };

  const fetchMyBookings = async () => {
    try {
      const data: any = await api.get('/bookings/my');
      setMyBookings(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMyEnrollments = async () => {
    try {
      const data: any = await api.get('/enrollments/my');
      setMyEnrollments(data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleEnrollCourse = async (course: Course) => {
    try {
      await api.post('/enrollments', {
        courseId: course.id,
        trainingLocation: course.trainingLocation || selectedPt?.availableLocations || 'Phòng tập cơ sở chính',
        paymentMethod: 'WALLET',
      });
      showToast(`Đăng ký khóa học "${course.title}" thành công!`);
      fetchWallet();
      fetchMyEnrollments();
      setActiveTab(4); // Switch to My Courses
    } catch (err: any) {
      showToast(err.message || 'Lỗi đăng ký khóa học.');
    }
  };

  const ptActiveEnrollments = myEnrollments.filter(
    (en) => en.ptId === selectedPt?.id && en.status === 'ACTIVE' && (en.remainingSessions || 0) > 0
  );

  const openBookingModal = (slot: AvailabilitySlot, preferredType?: 'TRIAL' | 'PACKAGE') => {
    setBookingModalSlot(slot);
    setBookingNote('');
    const activeWithPt = myEnrollments.filter(
      (en) => en.ptId === selectedPt?.id && en.status === 'ACTIVE' && (en.remainingSessions || 0) > 0
    );
    if (preferredType === 'TRIAL') {
      setBookingType('TRIAL');
      setBookingEnrollmentId(null);
    } else if (preferredType === 'PACKAGE') {
      setBookingType('PACKAGE');
      if (activeWithPt.length > 0) {
        setBookingEnrollmentId(activeWithPt[0].id);
      } else {
        setBookingEnrollmentId(null);
      }
    } else if (activeWithPt.length > 0) {
      setBookingEnrollmentId(activeWithPt[0].id);
      setBookingType('PACKAGE');
    } else {
      setBookingEnrollmentId(null);
      setBookingType('TRIAL');
    }
  };

  const handleBookSlot = (slot: AvailabilitySlot) => {
    openBookingModal(slot);
  };

  const confirmSubmitBooking = async () => {
    if (!bookingModalSlot) return;
    if (bookingType === 'PACKAGE' && !bookingEnrollmentId) {
      showToast('Vui lòng chọn hợp đồng khóa học để đặt lịch theo gói.');
      return;
    }
    setBookingSubmitting(true);
    try {
      await api.post('/bookings', {
        slotId: bookingModalSlot.id,
        bookingType,
        enrollmentId: bookingType === 'PACKAGE' ? bookingEnrollmentId : null,
        studentNote: bookingNote.trim() || undefined,
      });
      showToast(
        bookingType === 'TRIAL'
          ? '🎉 Đặt lịch học thử miễn phí (0đ) thành công! Hãy đợi HLV duyệt lịch.'
          : 'Đặt lịch ca tập theo gói thành công! Đã trừ 1 buổi trong hợp đồng.'
      );
      setBookingModalSlot(null);
      fetchMyBookings();
      fetchMyEnrollments();
      if (selectedPt) loadPtDetails(selectedPt);
      setActiveTab(3); // Chuyển sang Lịch Của Tôi
    } catch (err: any) {
      showToast(err.message || 'Lỗi đặt lịch ca tập.');
    } finally {
      setBookingSubmitting(false);
    }
  };

  const formatSlotTime = (dtStr: string) => {
    try {
      const dt = new Date(dtStr);
      return dt.toLocaleString('vi-VN', {
        weekday: 'short',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dtStr;
    }
  };

  const handleOpenCheckInModal = (booking: Booking) => {
    setCheckInModalBooking(booking);
    setStudentOtpInput('');
    setCheckInError(null);
  };

  const handleConfirmStudentAttendance = async () => {
    if (!checkInModalBooking) return;
    const cleanOtp = studentOtpInput.trim();
    if (cleanOtp.length !== 6 || !/^\d{6}$/.test(cleanOtp)) {
      setCheckInError('Vui lòng nhập đúng mã OTP gồm 6 chữ số.');
      return;
    }

    setCheckInLoading(true);
    setCheckInError(null);
    try {
      await api.post(`/attendance/bookings/${checkInModalBooking.id}/otp/verify`, {
        otp: cleanOtp,
        otpCode: cleanOtp,
      });
      showToast('🎉 Điểm danh ca tập thành công! Ca tập đã hoàn thành.');
      setCheckInModalBooking(null);
      setStudentOtpInput('');
      fetchMyBookings();
      fetchWallet();
      fetchMyEnrollments();
    } catch (err: any) {
      setCheckInError(err.response?.data?.message || err.message || 'Mã OTP không chính xác hoặc đã hết thời gian hiệu lực.');
    } finally {
      setCheckInLoading(false);
    }
  };

  const handleTopup = async () => {
    if (topupAmount <= 0) return;
    setTopupLoading(true);
    try {
      await api.post('/wallet/topup', { amount: topupAmount, paymentMethod: topupMethod });
      showToast(`Đã nạp ${topupAmount.toLocaleString('vi-VN')} ₫ vào ví thành công!`);
      fetchWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi nạp tiền.');
    } finally {
      setTopupLoading(false);
    }
  };

  const handleWithdraw = async () => {
    if (withdrawAmount < 50000) {
      showToast('Số tiền rút tối thiểu là 50.000 ₫');
      return;
    }
    if (!withdrawAccount.trim()) {
      showToast('Vui lòng nhập số tài khoản ngân hàng');
      return;
    }
    if (!withdrawHolder.trim()) {
      showToast('Vui lòng nhập tên chủ tài khoản ngân hàng');
      return;
    }
    setWithdrawLoading(true);
    try {
      await api.post('/wallet/withdraw', {
        amount: withdrawAmount,
        bankName: withdrawBank,
        accountNumber: withdrawAccount.trim(),
        accountHolderName: withdrawHolder.trim().toUpperCase(),
      });
      showToast(`Đã tạo lệnh rút ${withdrawAmount.toLocaleString('vi-VN')} ₫ về tài khoản ${withdrawBank} thành công!`);
      setWithdrawAmount(50000);
      fetchWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi khi rút tiền về ngân hàng.');
    } finally {
      setWithdrawLoading(false);
    }
  };

  const totalRemainingSessions = myEnrollments.reduce((acc, curr) => acc + (curr.remainingSessions || 0), 0);

  const availableSlots = ptSlots
    .filter((s) => s.status === 'AVAILABLE')
    .sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime());

  const slotsByDate = availableSlots.reduce<Record<string, AvailabilitySlot[]>>((acc, s) => {
    const key = getSlotDateKey(s.startTime);
    if (!key) return acc;
    if (!acc[key]) acc[key] = [];
    acc[key].push(s);
    return acc;
  }, {});

  // Xác định ngày hôm nay theo giờ địa phương
  const todayKey = (() => {
    const now = new Date();
    const y = now.getFullYear();
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const d = String(now.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  })();

  // Luôn bao gồm ngày Hôm nay trong dải ngày để học viên thấy rõ trạng thái ngày hiện tại
  const dateSet = new Set(Object.keys(slotsByDate));
  dateSet.add(todayKey);
  const uniqueDates = Array.from(dateSet).sort();

  // Ưu tiên chọn ngày có ca rảnh sớm nhất (ví dụ ngày mai nếu hôm nay đã hết ca)
  const earliestDateWithSlots = uniqueDates.find((d) => (slotsByDate[d]?.length || 0) > 0);
  const effectiveBookingDate = selectedBookingDate && uniqueDates.includes(selectedBookingDate)
    ? selectedBookingDate
    : (earliestDateWithSlots || todayKey);

  const currentDaySlots = effectiveBookingDate ? (slotsByDate[effectiveBookingDate] || []) : [];
  const morningSlots = currentDaySlots.filter((s) => getSlotPeriod(s) === 'MORNING');
  const afternoonSlots = currentDaySlots.filter((s) => getSlotPeriod(s) === 'AFTERNOON');
  const eveningSlots = currentDaySlots.filter((s) => getSlotPeriod(s) === 'EVENING');

  const filteredSlots = currentDaySlots.filter((s) => {
    if (bookingTimeFilter === 'ALL') return true;
    return getSlotPeriod(s) === bookingTimeFilter;
  });

  const handleStepDate = (direction: -1 | 1) => {
    if (!effectiveBookingDate || uniqueDates.length === 0) return;
    const currentIndex = uniqueDates.indexOf(effectiveBookingDate);
    const nextIndex = currentIndex + direction;
    if (nextIndex >= 0 && nextIndex < uniqueDates.length) {
      setSelectedBookingDate(uniqueDates[nextIndex]);
    }
  };

  const tabs = [
    { label: 'Khám Phá PT', icon: Compass },
    { label: 'Chi Tiết PT', icon: UserCheck },
    { label: 'Đặt Lịch', icon: Calendar },
    { label: 'Lịch Của Tôi', icon: Clock },
    { label: `Khóa Của Tôi (${myEnrollments.length})`, icon: BookOpen },
    { label: 'Ví Tiền', icon: WalletIcon },
    { label: `Khiếu Nại (${myDisputes.length})`, icon: ShieldAlert },
    { label: 'Hồ Sơ', icon: UserIcon },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Top Navbar */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#FF4B4B] text-white flex items-center justify-center font-bold text-lg shadow-sm">
              PT
            </div>
            <div>
              <span className="font-extrabold text-slate-900 text-lg tracking-tight">PT Connect</span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-blue-100 text-blue-800">
                Học viên
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-bold text-slate-900">{user.fullName}</div>
              <div className="text-xs text-slate-500">{user.email}</div>
            </div>
            <img
              src={getAvatarUrl(user.fullName, user.avatarUrl)}
              alt={user.fullName}
              className="w-9 h-9 rounded-full border border-slate-200 object-cover"
            />
            <button
              onClick={onLogout}
              className="px-3 py-1.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5"
            >
              <LogOut className="w-3.5 h-3.5" /> Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Hero Header Banner - CITIGYM Style */}
      <div className="relative text-white py-8 px-4 sm:px-8 shadow-xl overflow-hidden bg-slate-950 border-b border-slate-800">
        {/* Gym Background Image with Citigym-inspired dark warm overlay */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-30 mix-blend-luminosity scale-105 transition-transform duration-1000"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1920&q=80')",
          }}
        />
        {/* Subtle orange-amber gym lighting gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/85 to-orange-950/40 pointer-events-none" />
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-orange-500/15 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-7xl mx-auto flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 z-10">
          {/* Left Column: Greeting & Citigym Slogan */}
          <div className="flex items-start sm:items-center gap-4">
            <div className="relative shrink-0">
              <img
                src={getAvatarUrl(user.fullName, user.avatarUrl)}
                alt={user.fullName}
                className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl border-2 border-orange-500/80 bg-white/10 shadow-lg object-cover ring-4 ring-orange-500/20"
              />
              <span className="absolute -bottom-1 -right-1 bg-gradient-to-r from-orange-500 to-amber-500 text-white text-[9px] font-black px-1.5 py-0.5 rounded-full shadow-md uppercase">
                Học viên
              </span>
            </div>

            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-gradient-to-r from-orange-500/20 to-amber-500/20 text-orange-400 border border-orange-500/30">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>LUÔN BÊN CẠNH MỖI HÀNH TRÌNH CỦA BẠN</span>
              </div>
              <h2 className="text-xl sm:text-2xl lg:text-3xl font-black text-white tracking-tight">
                Chào mừng bạn, <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-amber-300 to-yellow-200">{user.fullName}</span>!
              </h2>
              <p className="text-slate-300 text-xs sm:text-sm font-medium leading-relaxed max-w-xl">
                Bứt phá giới hạn, kỷ luật luyện tập và đồng hành cùng Huấn luyện viên cá nhân hàng đầu tại PT Connect.
              </p>

              {/* Quick Hero Action Buttons */}
              <div className="flex items-center gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setActiveTab(2)}
                  className="px-3.5 py-1.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white rounded-xl text-xs font-bold shadow-md hover:shadow-lg transition-all flex items-center gap-1.5"
                >
                  <Gift className="w-3.5 h-3.5" /> Đặt Học Thử (0 VNĐ)
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab(0)}
                  className="px-3.5 py-1.5 bg-white/10 hover:bg-white/20 text-slate-200 border border-white/15 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
                >
                  <Search className="w-3.5 h-3.5 text-slate-300" /> Tìm HLV Mới
                </button>
              </div>
            </div>
          </div>

          {/* Right Column: Glassmorphism Quick Stats */}
          <div className="w-full lg:w-auto bg-white/10 backdrop-blur-md rounded-2xl p-4 border border-white/15 flex items-center justify-between sm:justify-start gap-4 sm:gap-6 shadow-2xl">
            <div>
              <span className="text-[10px] sm:text-[11px] text-slate-300 block uppercase font-bold tracking-wider">
                Số dư ví khả dụng
              </span>
              <span className="text-lg sm:text-2xl font-black text-emerald-400 block mt-0.5">
                {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
              </span>
            </div>
            <div className="border-l border-white/15 pl-4 sm:pl-6">
              <span className="text-[10px] sm:text-[11px] text-slate-300 block uppercase font-bold tracking-wider">
                Gói tập đã đăng ký
              </span>
              <span className="text-lg sm:text-2xl font-black text-white block mt-0.5">
                {myEnrollments.length} <span className="text-xs font-medium text-slate-300">khóa</span>
              </span>
            </div>
            <div className="border-l border-white/15 pl-4 sm:pl-6">
              <span className="text-[10px] sm:text-[11px] text-slate-300 block uppercase font-bold tracking-wider">
                Tổng buổi còn lại
              </span>
              <span className="text-lg sm:text-2xl font-black text-orange-400 block mt-0.5">
                {totalRemainingSessions} <span className="text-xs font-medium text-slate-300">buổi</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Toast Alert */}
      {toastMsg && (
        <div className="fixed bottom-5 right-5 z-50 bg-slate-900 text-white px-4 py-3 rounded-xl shadow-2xl text-sm flex items-center gap-2 animate-bounce">
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-slate-200 sticky top-16 z-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 sm:space-x-8 overflow-x-auto py-2">
            {tabs.map((t, idx) => {
              const Icon = t.icon;
              const isCur = activeTab === idx;
              return (
                <button
                  key={t.label}
                  onClick={() => setActiveTab(idx)}
                  className={`flex items-center gap-2 py-2 px-3 text-sm font-semibold rounded-lg whitespace-nowrap transition-all ${
                    isCur
                      ? 'bg-red-50 text-[#FF4B4B]'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isCur ? 'text-[#FF4B4B]' : 'text-slate-400'}`} />
                  {t.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Tab Content Body */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* TAB 0: KHÁM PHÁ PT */}
        {activeTab === 0 && (
          <div className="space-y-6">
            {/* CITIGYM-STYLE PROMO HERO BANNER */}
            <div className="relative rounded-3xl overflow-hidden shadow-xl bg-slate-950 border border-slate-800 text-white p-6 sm:p-8">
              {/* Gym background image with warm athletic glow */}
              <div
                className="absolute inset-0 bg-cover bg-center opacity-35 mix-blend-luminosity scale-100 hover:scale-105 transition-transform duration-700"
                style={{
                  backgroundImage: "url('https://images.unsplash.com/photo-1540497077202-7c8a3999166f?auto=format&fit=crop&w=1600&q=80')",
                }}
              />
              <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/80 to-amber-950/40 pointer-events-none" />
              <div className="absolute top-0 right-0 w-80 h-80 bg-orange-500/20 rounded-full blur-3xl pointer-events-none" />

              <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="max-w-2xl space-y-2.5">
                  <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-black tracking-wider uppercase bg-gradient-to-r from-orange-500 to-amber-500 text-white shadow-sm">
                    <span>🔥</span> ƯU ĐÃI ĐẶC QUYỀN HỌC VIÊN MỚI
                  </div>
                  <h3 className="text-2xl sm:text-3xl font-black text-white tracking-tight leading-tight">
                    Trải Nghiệm 1 Buổi Tập Học Thử Miễn Phí 100% (0 VNĐ)
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
                    Đo lường chỉ số InBody toàn diện, kiểm tra thể lực chuyên sâu và nhận lộ trình rèn luyện cá nhân hóa 1-kèm-1 cùng Huấn luyện viên đạt chuẩn chứng chỉ quốc tế.
                  </p>

                  <div className="flex flex-wrap items-center gap-3 pt-2 text-xs font-semibold text-slate-200">
                    <span className="flex items-center gap-1">
                      <span className="text-emerald-400">✓</span> HLV 1-kèm-1 kèm sát form
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-emerald-400">✓</span> Miễn phí 100% không phát sinh
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-emerald-400">✓</span> Giáo án cá nhân hóa theo mục tiêu
                    </span>
                  </div>
                </div>

                <div className="shrink-0 flex flex-col items-start md:items-end gap-2">
                  <button
                    type="button"
                    onClick={() => setActiveTab(2)}
                    className="px-6 py-3.5 bg-gradient-to-r from-orange-500 via-amber-500 to-yellow-500 hover:from-orange-600 hover:via-amber-600 hover:to-yellow-600 text-slate-950 text-sm font-black rounded-2xl shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
                  >
                    <Gift className="w-5 h-5 text-slate-950" />
                    <span>ĐẶT LỊCH HỌC THỬ (0đ) NGAY ➔</span>
                  </button>
                  <span className="text-[11px] text-slate-400 font-medium">
                    ⚡ Áp dụng cho tất cả các Huấn luyện viên trên hệ thống
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Fitness Goal Category Pills */}
            <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
              <span className="text-xs font-bold text-slate-500 shrink-0">Mục tiêu phổ biến:</span>
              {[
                { label: 'Tất cả PT', q: 'all' },
                { label: '🏋️ Tăng Cơ - Giảm Mỡ', q: 'tăng cơ' },
                { label: '🔥 Giảm Cân - Đốt Mỡ', q: 'giảm cân' },
                { label: '🥊 Boxing & Kickfit', q: 'boxing' },
                { label: '🧘 Yoga & Giãn Cơ', q: 'yoga' },
                { label: '🏃 Thể Lực & Cardio', q: 'cardio' },
                { label: '🩹 Phục Hồi Chấn Thương', q: 'phục hồi' },
              ].map((g) => (
                <button
                  key={g.label}
                  type="button"
                  onClick={() => setFilterGoal(g.q)}
                  className={'px-3 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all border ' + (
                    filterGoal === g.q
                      ? 'bg-slate-900 text-white border-slate-900 shadow-sm'
                      : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                  )}
                >
                  {g.label}
                </button>
              ))}
            </div>

            {/* BỘ LỌC ĐA NĂNG & TÌM KIẾM HUẤN LUYỆN VIÊN */}
            <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm space-y-4">
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-xl bg-[#E52E2E]/10 text-[#E52E2E] flex items-center justify-center font-bold">
                    <Filter className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-lg font-black text-slate-900 tracking-tight">
                      Tìm Kiếm & Bộ Lọc Huấn Luyện Viên
                    </h3>
                    <p className="text-xs text-slate-500">
                      Chọn mục tiêu rèn luyện, khoảng giá, số sao đánh giá và địa điểm tập luyện
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <span className="text-xs font-bold text-slate-700 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200">
                    Tìm thấy <span className="text-[#E52E2E] font-black">{filteredPts.length}</span> / {pts.length} HLV
                  </span>
                  {activeFilterCount > 0 && (
                    <button
                      type="button"
                      onClick={handleResetAllFilters}
                      className="text-xs text-[#E52E2E] hover:text-red-700 font-bold flex items-center gap-1 hover:underline cursor-pointer"
                    >
                      <RotateCcw className="w-3.5 h-3.5" /> Đặt lại tất cả
                    </button>
                  )}
                </div>
              </div>

              {/* Dòng 1: Tìm kiếm từ khóa & Khu vực */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-3">
                <div className="relative md:col-span-8">
                  <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
                  <input
                    type="text"
                    value={filterKeyword}
                    onChange={(e) => setFilterKeyword(e.target.value)}
                    placeholder="Tìm tên Huấn luyện viên, phòng tập, chuyên môn..."
                    className="w-full pl-10 pr-9 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E52E2E] focus:border-[#E52E2E] bg-slate-50/50"
                  />
                  {filterKeyword && (
                    <button
                      type="button"
                      onClick={() => setFilterKeyword('')}
                      className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <div className="relative md:col-span-4">
                  <MapPin className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400 pointer-events-none" />
                  <select
                    value={filterLocation}
                    onChange={(e) => setFilterLocation(e.target.value)}
                    className="w-full pl-10 pr-8 py-2.5 border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[#E52E2E] bg-white appearance-none cursor-pointer text-slate-700 font-medium"
                  >
                    <option value="all">📍 Tất cả khu vực</option>
                    {availableLocationsList.map((loc) => (
                      <option key={loc} value={loc}>
                        {loc}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Dòng 2: Lọc theo Mức Giá (Hiển thị trực tiếp 1 chạm) */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
                <span className="text-xs font-bold text-slate-700 flex items-center gap-1 shrink-0 w-28">
                  <DollarSign className="w-3.5 h-3.5 text-emerald-600" /> Mức học phí:
                </span>
                <div className="flex flex-wrap items-center gap-1.5 flex-1">
                  {[
                    { label: 'Tất cả giá', val: 'all' },
                    { label: '< 4 triệu ₫ (Khởi động)', val: 'under4m' },
                    { label: '4tr - 8 triệu ₫ (Chuẩn)', val: '4m-8m' },
                    { label: '> 8 triệu ₫ (Chuyên sâu)', val: 'above8m' },
                  ].map((p) => (
                    <button
                      key={p.label}
                      type="button"
                      onClick={() => setFilterPrice(p.val)}
                      className={'px-3 py-1.5 rounded-xl text-xs font-bold transition-all border cursor-pointer ' + (
                        filterPrice === p.val
                          ? 'bg-[#E52E2E] text-white border-[#E52E2E] shadow-sm'
                          : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                      )}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dòng 3: Lọc theo Số Ngôi Sao Đánh Giá (Hiển thị trực tiếp 1 chạm) */}
              <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
                <span className="text-xs font-bold text-slate-700 flex items-center gap-1 shrink-0 w-28">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-500" /> Đánh giá sao:
                </span>
                <div className="flex flex-wrap items-center gap-1.5 flex-1">
                  {[
                    { label: '⭐ Tất cả sao', val: 0 },
                    { label: '⭐ 4.5+ (Xuất sắc)', val: 4.5 },
                    { label: '⭐ 4.0+ (Rất tốt)', val: 4.0 },
                    { label: '⭐ 3.5+ (Tốt)', val: 3.5 },
                  ].map((r) => (
                    <button
                      key={r.label}
                      type="button"
                      onClick={() => setFilterRating(r.val)}
                      className={'px-3 py-1.5 rounded-xl text-xs font-bold transition-all border cursor-pointer ' + (
                        filterRating === r.val
                          ? 'bg-amber-500 text-white border-amber-500 shadow-sm'
                          : 'bg-white text-slate-700 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                      )}
                    >
                      {r.label}
                    </button>
                  ))}
                </div>

                {/* Sắp xếp nhanh */}
                <div className="flex items-center gap-2 ml-auto">
                  <span className="text-xs font-semibold text-slate-500">Sắp xếp:</span>
                  <select
                    value={filterSortBy}
                    onChange={(e) => setFilterSortBy(e.target.value)}
                    className="border border-slate-300 rounded-lg px-2.5 py-1 text-xs font-bold text-slate-700 bg-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#E52E2E]"
                  >
                    <option value="default">✨ Đề xuất tốt nhất</option>
                    <option value="rating_desc">⭐ Đánh giá: Cao nhất</option>
                    <option value="exp_desc">🏆 Kinh nghiệm: Nhiều nhất</option>
                    <option value="price_asc">💵 Học phí: Thấp đến cao</option>
                    <option value="price_desc">💎 Học phí: Cao đến thấp</option>
                    <option value="name_asc">🔤 Tên: A đến Z</option>
                  </select>
                </div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-bold text-slate-800">
                  Tìm thấy <span className="text-[#E52E2E] font-extrabold">{filteredPts.length}</span> Huấn luyện viên chuyên nghiệp:
                </p>
                {filterSortBy !== 'default' && (
                  <span className="text-xs text-slate-500 font-medium">
                    (Đang sắp xếp: {filterSortBy === 'rating_desc' ? 'Đánh giá cao nhất' : filterSortBy === 'exp_desc' ? 'Kinh nghiệm nhiều nhất' : filterSortBy === 'price_asc' ? 'Giá thấp đến cao' : filterSortBy === 'price_desc' ? 'Giá cao đến thấp' : 'Tên A - Z'})
                  </span>
                )}
              </div>

              {filteredPts.length === 0 ? (
                <div className="bg-white rounded-3xl border border-slate-200 p-12 text-center shadow-xs">
                  <div className="w-16 h-16 bg-red-50 text-[#E52E2E] rounded-full flex items-center justify-center mx-auto mb-4">
                    <Search className="w-8 h-8" />
                  </div>
                  <h4 className="text-lg font-bold text-slate-900 mb-1">
                    Không tìm thấy Huấn luyện viên nào phù hợp
                  </h4>
                  <p className="text-sm text-slate-500 max-w-md mx-auto mb-6">
                    Không có HLV nào khớp với tất cả các tiêu chí lọc hiện tại. Hãy thử chọn mục tiêu khác hoặc đặt lại bộ lọc.
                  </p>
                  <button
                    type="button"
                    onClick={handleResetAllFilters}
                    className="px-6 py-2.5 bg-gradient-to-r from-[#E52E2E] to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold text-sm rounded-xl shadow-md transition-all inline-flex items-center gap-2 cursor-pointer"
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span>Đặt lại bộ lọc & Xem tất cả ({pts.length}) PT</span>
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredPts.map((pt, idx) => (
                    <PtCard
                      key={pt.id}
                      pt={pt}
                      index={idx}
                      onSelect={(selected) => {
                        loadPtDetails(selected);
                        setActiveTab(1); // Go to Detail
                      }}
                    />
                  ))}
                </div>
              )}\n            </div>
          </div>
        )}

        {/* TAB 1: CHI TIẾT PT */}
        {activeTab === 1 && selectedPt && (
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row gap-6 items-start">
              <img
                src={getAvatarUrl(selectedPt.fullName, selectedPt.avatarUrl)}
                alt={selectedPt.fullName}
                className="w-24 h-24 rounded-2xl border border-slate-200 object-cover"
              />
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <h3 className="text-2xl font-extrabold text-slate-900">{selectedPt.fullName}</h3>
                  <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-0.5 rounded-full border border-emerald-300">
                    Đã xác minh
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-1">{selectedPt.bio}</p>
                <div className="flex items-center gap-4 mt-3 text-xs text-slate-600">
                  <span><b>Kinh nghiệm:</b> {selectedPt.experienceYears} năm</span>
                  <span><b>Khu vực:</b> {selectedPt.availableLocations}</span>
                  <span><b>Đánh giá:</b> {(selectedPt.averageRating ?? 0).toFixed(1)}/5 ⭐ ({selectedPt.totalReviews ?? 0} lượt)</span>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2.5">
                <button
                  type="button"
                  onClick={() => {
                    window.dispatchEvent(new CustomEvent('ptconnect:open_chat', {
                      detail: {
                        partnerId: selectedPt.userId || selectedPt.id,
                        partnerName: selectedPt.fullName,
                        partnerEmail: selectedPt.email,
                        partnerAvatar: getAvatarUrl(selectedPt.fullName, selectedPt.avatarUrl),
                        partnerRole: 'PT'
                      }
                    }));
                  }}
                  className="px-4 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-sm font-bold rounded-xl shadow-md flex items-center justify-center gap-1.5 transition-all cursor-pointer"
                  title="Mở khung chat 1-1 với HLV"
                >
                  <MessageCircle className="w-4 h-4 text-orange-400" /> Nhắn Tin HLV
                </button>
                <button
                  onClick={() => setActiveTab(2)}
                  className="px-5 py-2.5 bg-gradient-to-r from-orange-500 to-amber-500 hover:from-orange-600 hover:to-amber-600 text-white text-sm font-bold rounded-xl shadow-md flex items-center justify-center gap-1.5 transition-all"
                >
                  <Gift className="w-4 h-4" /> Đặt Lịch Học Thử (0đ)
                </button>
                <button
                  onClick={() => setActiveTab(2)}
                  className="px-5 py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-sm font-bold rounded-xl shadow-md flex items-center justify-center gap-1.5 transition-all"
                >
                  <Calendar className="w-4 h-4" /> Xem Khung Giờ Rảnh
                </button>
              </div>
            </div>

            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-4">Các Khóa Học Huấn Luyện Cố Định</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {ptCourses.map((c) => (
                  <CourseCard key={c.id} course={c} isPtView={false} onEnroll={handleEnrollCourse} />
                ))}
              </div>
              {ptCourses.length === 0 && (
                <div className="bg-white p-8 text-center rounded-xl border border-slate-200 text-slate-500 text-sm">
                  HLV này chưa tạo khóa học công khai nào.
                </div>
              )}
            </div>

            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-4">Đánh Giá Từ Học Viên</h4>
              <ReviewList ptProfileId={selectedPt.id} reloadKey={reviewReloadKey} />
            </div>
          </div>
        )}

        {/* TAB 2: ĐẶT LỊCH */}
        {activeTab === 2 && (
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="text-xl font-bold text-slate-900">Đặt Lịch Tập Cùng Huấn Luyện Viên</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Chọn khung giờ trống để đặt lịch học thử miễn phí hoặc tập luyện theo gói khóa học đã đăng ký.
                </p>
              </div>
              {selectedPt && (
                <button
                  onClick={() => loadPtDetails(selectedPt)}
                  className="px-3 py-1.5 border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-semibold text-slate-600 flex items-center gap-1.5 self-start sm:self-auto"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Làm mới khung giờ
                </button>
              )}
            </div>

            {selectedPt ? (
              <>
                {/* PT Switcher & Quick Profile Bar */}
                <div className="p-4 bg-slate-50/80 rounded-2xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <img
                      src={getAvatarUrl(selectedPt.fullName, selectedPt.avatarUrl)}
                      alt={selectedPt.fullName}
                      className="w-12 h-12 rounded-xl object-cover border border-slate-200 shrink-0 bg-white shadow-xs"
                    />
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="text-base font-extrabold text-slate-900">{selectedPt.fullName}</h4>
                        <span className="text-xs font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                          {(selectedPt.averageRating ?? 0).toFixed(1)} ⭐ ({selectedPt.totalReviews ?? 0} lượt)
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">
                        📍 {selectedPt.availableLocations || 'Toàn quốc'} • 💼 {selectedPt.experienceYears} năm kinh nghiệm
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    <label htmlFor="pt-switcher" className="text-xs font-semibold text-slate-600 whitespace-nowrap">
                      Đổi HLV:
                    </label>
                    <select
                      id="pt-switcher"
                      value={selectedPt.id}
                      onChange={(e) => {
                        const found = pts.find((p) => p.id === Number(e.target.value));
                        if (found) loadPtDetails(found);
                      }}
                      className="text-xs font-semibold bg-white border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]/30"
                    >
                      {pts.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.fullName} ({p.availableLocations || 'Toàn quốc'})
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Hướng dẫn & 2 Lựa chọn rõ ràng */}
                <div className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-4">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                    <div>
                      <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-amber-500" />
                        Hai Hình Thức Đặt Lịch Cùng HLV {selectedPt.fullName}
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Hệ thống hỗ trợ 2 hình thức: Bạn có thể bấm nút trực tiếp trên từng khung giờ rảnh bên dưới:
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* Hộp 1: Học Thử */}
                    <div className="p-4 rounded-xl border-2 border-emerald-300 bg-emerald-50/60 flex items-start gap-3.5">
                      <div className="w-10 h-10 rounded-xl bg-emerald-500 text-white flex items-center justify-center font-bold text-lg shadow-xs shrink-0">
                        🎁
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-sm text-emerald-950">1. Học Thử (TRIAL)</span>
                          <span className="text-xs font-extrabold text-emerald-800 bg-emerald-200 px-2.5 py-0.5 rounded-full border border-emerald-300">
                            0 VNĐ (MIỄN PHÍ)
                          </span>
                        </div>
                        <p className="text-xs text-emerald-900 leading-relaxed">
                          Đặt <b>1 buổi tập trải nghiệm miễn phí 100%</b> cùng HLV mà không cần mua trước khóa học.
                        </p>
                      </div>
                    </div>

                    {/* Hộp 2: Theo Khóa Học */}
                    <div className="p-4 rounded-xl border-2 border-blue-300 bg-blue-50/60 flex items-start gap-3.5">
                      <div className="w-10 h-10 rounded-xl bg-blue-500 text-white flex items-center justify-center font-bold text-lg shadow-xs shrink-0">
                        📦
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-bold text-sm text-blue-950">2. Theo Khóa Học (PACKAGE)</span>
                          <span className="text-xs font-bold text-blue-800 bg-blue-200 px-2.5 py-0.5 rounded-full border border-blue-300">
                            Trừ 1 buổi
                          </span>
                        </div>
                        <p className="text-xs text-blue-900 leading-relaxed">
                          {ptActiveEnrollments.length > 0 ? (
                            <>Bạn đang có <b>{ptActiveEnrollments.length} hợp đồng</b> còn buổi với HLV này. Sẽ trừ 1 buổi tập khi đặt.</>
                          ) : (
                            <span className="text-amber-800 font-medium">Bạn chưa đăng ký khóa học nào với HLV này. Hãy đặt Học Thử (0đ) hoặc mua khóa trước.</span>
                          )}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* THANH CHỌN NGÀY VÀ LỌC KHUNG GIỜ */}
                {availableSlots.length > 0 ? (
                  <div className="space-y-4">
                    {/* BƯỚC 1: THANH DẢI NGANG CHỌN NGÀY */}
                    <div className="bg-slate-50/80 p-4 rounded-2xl border border-slate-200 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-[#FF4B4B]" />
                          <span className="text-sm font-bold text-slate-800">1. Chọn ngày tập luyện:</span>
                          <span className="text-xs text-slate-500 font-medium hidden sm:inline">
                            (HLV có lịch rảnh trong {uniqueDates.length} ngày tới)
                          </span>
                        </div>

                        {/* Nút lùi/tiến ngày */}
                        <div className="flex items-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => handleStepDate(-1)}
                            disabled={!effectiveBookingDate || uniqueDates.indexOf(effectiveBookingDate) <= 0}
                            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed text-slate-600 transition shadow-xs"
                            title="Ngày trước đó"
                          >
                            <ChevronLeft className="w-4 h-4" />
                          </button>
                          <span className="text-xs font-bold text-slate-600 px-1">
                            {effectiveBookingDate ? (uniqueDates.indexOf(effectiveBookingDate) + 1) + ' / ' + uniqueDates.length : ''}
                          </span>
                          <button
                            type="button"
                            onClick={() => handleStepDate(1)}
                            disabled={!effectiveBookingDate || uniqueDates.indexOf(effectiveBookingDate) >= uniqueDates.length - 1}
                            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed text-slate-600 transition shadow-xs"
                            title="Ngày kế tiếp"
                          >
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Dải cuộn ngang các ngày */}
                      <div className="flex items-center gap-2.5 overflow-x-auto pb-2 pt-0.5 scrollbar-thin">
                        {uniqueDates.map((dateKey) => {
                          const isSelected = dateKey === effectiveBookingDate;
                          const count = slotsByDate[dateKey]?.length || 0;
                          const info = getDateDisplayInfo(dateKey);

                          return (
                            <button
                              key={dateKey}
                              type="button"
                              onClick={() => {
                                setSelectedBookingDate(dateKey);
                              }}
                              className={'shrink-0 flex flex-col items-center justify-center py-2.5 px-3.5 rounded-xl border-2 transition-all cursor-pointer min-w-[100px] text-center ' + (
                                isSelected
                                  ? 'border-[#FF4B4B] bg-red-50/80 shadow-sm ring-2 ring-[#FF4B4B]/20 text-slate-900'
                                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50 text-slate-700'
                              )}
                            >
                              <span
                                className={'text-[10px] font-bold uppercase tracking-wider ' + (
                                  isSelected ? 'text-[#FF4B4B]' : 'text-slate-500'
                                )}
                              >
                                {info.badgeLabel}
                              </span>
                              <span
                                className={'text-base font-black my-0.5 ' + (
                                  isSelected ? 'text-[#FF4B4B]' : 'text-slate-900'
                                )}
                              >
                                {info.dayMonth}
                              </span>
                              <span
                                className={'text-[10px] font-bold px-2 py-0.5 rounded-full ' + (
                                  isSelected
                                    ? 'bg-[#FF4B4B] text-white'
                                    : count > 0
                                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                    : 'bg-slate-100 text-slate-500 border border-slate-200'
                                )}
                              >
                                {count > 0 ? count + ' ca trống' : (info.diffDays === 0 ? 'Hết ca' : '0 ca')}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>

                    {/* BƯỚC 2: LỌC THEO BUỔI & TỔNG QUAN NGÀY ĐANG CHỌN */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-xs font-bold text-slate-700 flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-slate-500" />
                          2. Lọc theo buổi:
                        </span>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <button
                            type="button"
                            onClick={() => setBookingTimeFilter('ALL')}
                            className={'px-3 py-1 rounded-lg text-xs font-bold transition ' + (
                              bookingTimeFilter === 'ALL'
                                ? 'bg-slate-900 text-white shadow-xs'
                                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                            )}
                          >
                            Tất cả ({currentDaySlots.length})
                          </button>

                          <button
                            type="button"
                            onClick={() => setBookingTimeFilter('MORNING')}
                            className={'px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ' + (
                              bookingTimeFilter === 'MORNING'
                                ? 'bg-amber-500 text-white shadow-xs'
                                : 'bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200'
                            )}
                          >
                            <span>🌅</span> Sáng ({morningSlots.length})
                          </button>

                          <button
                            type="button"
                            onClick={() => setBookingTimeFilter('AFTERNOON')}
                            className={'px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ' + (
                              bookingTimeFilter === 'AFTERNOON'
                                ? 'bg-orange-500 text-white shadow-xs'
                                : 'bg-orange-50 text-orange-700 hover:bg-orange-100 border border-orange-200'
                            )}
                          >
                            <span>☀️</span> Chiều ({afternoonSlots.length})
                          </button>

                          <button
                            type="button"
                            onClick={() => setBookingTimeFilter('EVENING')}
                            className={'px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1 ' + (
                              bookingTimeFilter === 'EVENING'
                                ? 'bg-indigo-600 text-white shadow-xs'
                                : 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200'
                            )}
                          >
                            <span>🌙</span> Tối ({eveningSlots.length})
                          </button>
                        </div>
                      </div>

                      {effectiveBookingDate && (
                        <div className="text-xs text-slate-600 bg-slate-50 px-3 py-1 rounded-lg border border-slate-200 font-medium">
                          Đang chọn: <b className="text-slate-900">{getDateDisplayInfo(effectiveBookingDate).fullDateStr}</b>
                          {' • Còn '}<b className="text-emerald-700">{filteredSlots.length} ca phù hợp</b>
                        </div>
                      )}
                    </div>

                    {/* DANH SÁCH CÁC CA TRỐNG CỦA NGÀY ĐANG CHỌN */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-1">
                      {filteredSlots.map((slot) => {
                        const startDate = new Date(slot.startTime);
                        const endDate = new Date(slot.endTime);
                        const timeStr = startDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) + ' - ' + endDate.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
                        const durationMinutes = Math.round((endDate.getTime() - startDate.getTime()) / 60000);
                        const period = getSlotPeriod(slot);

                        return (
                          <div
                            key={slot.id}
                            className="bg-white rounded-2xl border-2 border-slate-200 hover:border-slate-300 p-4 shadow-xs hover:shadow-md transition-all space-y-3.5 group"
                          >
                            {/* Header ca tập */}
                            <div className="flex items-start justify-between">
                              <div className="flex items-center gap-2.5">
                                <div
                                  className={'w-10 h-10 rounded-xl flex items-center justify-center font-bold text-base ' + (
                                    period === 'MORNING'
                                      ? 'bg-amber-100 text-amber-800'
                                      : period === 'AFTERNOON'
                                      ? 'bg-orange-100 text-orange-800'
                                      : 'bg-indigo-100 text-indigo-800'
                                  )}
                                >
                                  {period === 'MORNING' ? '🌅' : period === 'AFTERNOON' ? '☀️' : '🌙'}
                                </div>
                                <div>
                                  <div className="text-base font-extrabold text-slate-900 tracking-tight">{timeStr}</div>
                                  <div className="text-xs text-slate-500 flex items-center gap-1.5 mt-0.5">
                                    <span>{durationMinutes > 0 ? durationMinutes + ' phút' : '1 ca tập'}</span>
                                    <span>•</span>
                                    <span className="text-slate-600 font-medium">
                                      {period === 'MORNING' ? 'Buổi sáng' : period === 'AFTERNOON' ? 'Buổi chiều' : 'Buổi tối'}
                                    </span>
                                  </div>
                                </div>
                              </div>
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shrink-0">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                                Còn trống
                              </span>
                            </div>

                            {/* 2 NÚT BẤM RIÊNG BIỆT TO RÕ TRÊN TỪNG KHUNG GIỜ */}
                            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-100">
                              <button
                                type="button"
                                onClick={() => openBookingModal(slot, 'TRIAL')}
                                className="w-full py-2.5 px-2 bg-emerald-600 hover:bg-emerald-700 active:scale-[0.98] text-white rounded-xl text-xs font-bold shadow-xs transition-all flex flex-col items-center justify-center gap-0.5"
                                title="Đặt buổi học thử hoàn toàn miễn phí"
                              >
                                <span className="flex items-center gap-1">
                                  <span>🎁</span> Học Thử
                                </span>
                                <span className="text-[10px] font-normal text-emerald-100">0 VNĐ (Miễn phí)</span>
                              </button>

                              <button
                                type="button"
                                onClick={() => openBookingModal(slot, 'PACKAGE')}
                                className="w-full py-2.5 px-2 bg-blue-600 hover:bg-blue-700 active:scale-[0.98] text-white rounded-xl text-xs font-bold shadow-xs transition-all flex flex-col items-center justify-center gap-0.5"
                                title="Đặt buổi tập theo gói khóa học đã mua"
                              >
                                <span className="flex items-center gap-1">
                                  <span>📦</span> Theo Khóa
                                </span>
                                <span className="text-[10px] font-normal text-blue-100">Trừ 1 buổi</span>
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Báo trống khi lọc buổi không có slot */}
                    {filteredSlots.length === 0 && (
                      <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                        <Clock className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                        <p className="text-sm text-slate-700 font-bold">
                          {effectiveBookingDate === todayKey
                            ? 'Các khung giờ rảnh trong ngày hôm nay đã kết thúc.'
                            : 'Không có khung giờ nào trong buổi đã chọn vào ngày này.'}
                        </p>
                        <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                          {effectiveBookingDate === todayKey
                            ? 'Hệ thống hoàn toàn cho phép đặt lịch trong ngày hôm nay nếu HLV có ca rảnh. Tuy nhiên hiện tại đã muộn (qua giờ các ca tập), các ca hôm nay đã trôi qua. Bạn hãy chọn Ngày mai để đặt lịch sớm nhất nhé!'
                            : (bookingTimeFilter !== 'ALL'
                                ? 'Hãy bấm chọn "Tất cả" hoặc chuyển sang buổi khác / ngày khác.'
                                : 'HLV không có khung giờ rảnh nào vào ngày này.')}
                        </p>
                        {effectiveBookingDate === todayKey ? (
                          <button
                            type="button"
                            onClick={() => {
                              const tomorrowKey = uniqueDates.find((d) => d > todayKey);
                              if (tomorrowKey) setSelectedBookingDate(tomorrowKey);
                            }}
                            className="mt-4 px-5 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white rounded-xl text-xs font-bold shadow-md transition inline-flex items-center gap-1.5"
                          >
                            👉 Xem lịch Ngày mai ({(() => { const nextD = uniqueDates.find((d) => d > todayKey); return nextD ? getDateDisplayInfo(nextD).dayMonth : ''; })()}) còn ca trống
                          </button>
                        ) : (
                          bookingTimeFilter !== 'ALL' && (
                            <button
                              type="button"
                              onClick={() => setBookingTimeFilter('ALL')}
                              className="mt-3 px-4 py-1.5 bg-slate-800 text-white rounded-xl text-xs font-bold hover:bg-slate-900 transition"
                            >
                              Xem tất cả {currentDaySlots.length} ca trong ngày
                            </button>
                          )
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-8 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <Calendar className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                    <p className="text-sm text-slate-600 font-bold">Hiện không có khung giờ trống nào trong tương lai của HLV này.</p>
                    <p className="text-xs text-slate-400 mt-1">HLV chưa cập nhật lịch mở mới. Bạn có thể đổi HLV ở trên hoặc quay lại sau.</p>
                  </div>
                )}
              </>
            ) : (
              <div className="space-y-4 text-center py-6">
                <p className="text-sm font-semibold text-slate-700">Vui lòng chọn một Huấn luyện viên để xem khung giờ rảnh và đặt lịch:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-left">
                  {pts.map((p) => (
                    <div
                      key={p.id}
                      onClick={() => loadPtDetails(p)}
                      className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-white hover:border-[#FF4B4B] hover:shadow-md cursor-pointer transition flex items-center gap-3"
                    >
                      <img
                        src={getAvatarUrl(p.fullName, p.avatarUrl)}
                        alt={p.fullName}
                        className="w-12 h-12 rounded-xl object-cover bg-white border border-slate-200 shrink-0"
                      />
                      <div className="min-w-0 flex-1">
                        <div className="font-bold text-sm text-slate-900 truncate">{p.fullName}</div>
                        <div className="text-xs text-slate-500">{p.experienceYears} năm KN • {p.availableLocations || 'Toàn quốc'}</div>
                        <span className="text-[11px] font-bold text-[#FF4B4B] mt-1 inline-block">Chọn đặt lịch ➔</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: LỊCH CỦA TÔI */}
        {activeTab === 3 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Lịch Tập Luyện Của Tôi</h3>
            <BookingTable
              bookings={myBookings}
              reviewedBookingIds={reviewedBookingIds}
              onReview={(b) => setReviewBooking(b)}
              onConfirmOtp={handleOpenCheckInModal}
              onCancel={async (b, reason) => {
                try {
                  const res: any = await api.put('/bookings/' + b.id + '/cancel', {
                    reason: reason || 'Học viên có việc đột xuất',
                  });
                  showToast(res?.message || 'Đã hủy ca tập thành công theo chính sách!');
                  fetchMyBookings();
                  fetchWallet();
                  fetchMyEnrollments();
                } catch (err: any) {
                  showToast(err.message || 'Lỗi khi hủy ca tập.');
                }
              }}
            />
          </div>
        )}

        {/* TAB 4: KHÓA CỦA TÔI & HỢP ĐỒNG */}
        {activeTab === 4 && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-slate-900">Danh Sách Gói Tập Đã Đăng Ký & Hợp Đồng</h3>
                <p className="text-xs text-slate-500 mt-1">
                  Quản lý các hợp đồng huấn luyện viên, theo dõi số buổi tập còn lại và tải hợp đồng pháp lý PDF.
                </p>
              </div>
              <span className="bg-blue-50 text-blue-800 text-xs font-bold px-3 py-1 rounded-full border border-blue-200">
                {myEnrollments.length} gói tập kích hoạt
              </span>
            </div>

            {myEnrollments.length === 0 ? (
              <div className="bg-white p-12 text-center rounded-2xl border border-slate-200">
                <FileText className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                <h4 className="text-base font-bold text-slate-700">Chưa có hợp đồng nào</h4>
                <p className="text-xs text-slate-500 mt-1 mb-4">
                  Bạn chưa đăng ký khóa học nào. Hãy khám phá và chọn Huấn luyện viên phù hợp ở tab Khám Phá PT nhé!
                </p>
                <button
                  onClick={() => setActiveTab(0)}
                  className="px-4 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-xs font-semibold rounded-lg shadow-sm"
                >
                  Khám Phá PT Ngay
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {myEnrollments.map((en) => {
                  const completed = en.totalSessions - en.remainingSessions;
                  const progressPct = en.totalSessions > 0 ? Math.round((completed / en.totalSessions) * 100) : 0;
                  return (
                    <div
                      key={en.id}
                      className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-all flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex justify-between items-start gap-3">
                          <div>
                            <h4 className="text-base font-bold text-slate-900 leading-snug">
                              {en.courseTitle || 'Gói tập cá nhân'}
                            </h4>
                            <span className="text-xs font-mono font-semibold text-slate-400 mt-0.5 block">
                              PTC-HD-{String(en.id).padStart(6, '0')}
                            </span>
                          </div>
                          <span
                            className={`text-xs font-bold px-2.5 py-0.5 rounded-full shrink-0 ${
                              en.status === 'ACTIVE'
                                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {en.status}
                          </span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 my-4 py-3 border-y border-slate-100 text-xs text-slate-600">
                          <div>
                            <span className="text-slate-400 block">Huấn luyện viên:</span>
                            <span className="font-bold text-slate-800">{en.ptName || 'Huấn luyện viên'}</span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Địa điểm tập:</span>
                            <span className="font-bold text-slate-800 truncate block">
                              {en.trainingLocation || 'Phòng tập liên kết'}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Học phí trọn gói:</span>
                            <span className="font-bold text-[#FF4B4B]">
                              {(en.finalPrice || 0).toLocaleString('vi-VN')} ₫
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400 block">Thời hạn hợp đồng:</span>
                            <span className="font-bold text-slate-800">
                              {en.startDate || '2026-09-01'} → {en.endDate || '2026-12-01'}
                            </span>
                          </div>
                        </div>

                        {/* Progress */}
                        <div className="space-y-1.5 mb-4">
                          <div className="flex justify-between text-xs">
                            <span className="text-slate-500 font-medium">Tiến độ buổi tập:</span>
                            <span className="font-bold text-slate-800">
                              {completed}/{en.totalSessions} buổi ({progressPct}%)
                            </span>
                          </div>
                          <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                            <div
                              className="bg-[#FF4B4B] h-full rounded-full transition-all duration-500"
                              style={{ width: `${progressPct}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>

                      <div className="pt-3 border-t border-slate-100 flex items-center justify-between gap-3">
                        <button
                          onClick={() => {
                            if (en.ptId) {
                              const targetPt = pts.find((p) => p.id === en.ptId);
                              if (targetPt) loadPtDetails(targetPt);
                            }
                            setActiveTab(2); // Switch to booking tab
                          }}
                          className="px-3.5 py-2 bg-red-50 text-[#FF4B4B] hover:bg-red-100 rounded-xl text-xs font-bold transition-all"
                        >
                          Đặt lịch
                        </button>

                        <button
                          onClick={() => handleViewWorkoutPlans(en)}
                          className="px-3 py-2 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded-xl text-xs font-bold transition-all flex items-center gap-1"
                        >
                          <ClipboardList className="w-3.5 h-3.5" /> Giáo án
                        </button>

                        <button
                          onClick={async () => {
                            try {
                              const blob = await api.get(`/enrollments/${en.id}/contract`, {
                                responseType: 'blob',
                              });
                              const url = window.URL.createObjectURL(new Blob([blob as any]));
                              const link = document.createElement('a');
                              link.href = url;
                              link.setAttribute('download', `PTC_HD_${String(en.id).padStart(6, '0')}.pdf`);
                              document.body.appendChild(link);
                              link.click();
                              showToast('Đang tải xuống hợp đồng PDF...');
                            } catch (e: any) {
                              showToast('Lỗi tải hợp đồng PDF.');
                            }
                          }}
                          className="px-3.5 py-2 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all shadow-sm"
                        >
                          <FileText className="w-3.5 h-3.5 text-slate-500" /> Tải Hợp Đồng PDF
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: VÍ TIỀN */}
        {activeTab === 5 && wallet && (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold text-slate-900">Quản Lý Ví Điện Tử Nội Bộ (Nạp & Rút Tiền)</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Nạp tiền để thanh toán khóa học, nhận tiền đền bù ca tập và rút tiền thừa về tài khoản ngân hàng cá nhân.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* CỘT TRÁI: Số Dư & Nạp Tiền Vào Ví */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
                    <span className="text-lg">💰</span> Số Dư & Nạp Tiền Vào Ví
                  </h4>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                    {wallet.status}
                  </span>
                </div>

                <div className="text-xs text-slate-500">
                  Chủ tài khoản: <b className="text-slate-800">{wallet.ownerName || user.fullName}</b>
                </div>

                {/* Hộp Số Dư Khả Dụng */}
                <div className="bg-blue-50/80 border border-blue-200 rounded-xl p-4">
                  <div className="text-xs font-semibold text-blue-700">SỐ DƯ KHẢ DỤNG:</div>
                  <div className="text-3xl font-extrabold text-blue-900 mt-1">
                    {wallet.balance.toLocaleString('vi-VN')} ₫
                  </div>
                  {wallet.lockedBalance > 0 && (
                    <div className="text-xs text-blue-600 mt-1">
                      Đang đóng băng: {wallet.lockedBalance.toLocaleString('vi-VN')} ₫
                    </div>
                  )}
                </div>

                {/* Chọn nhanh mệnh giá nạp */}
                <div className="space-y-1.5 pt-2">
                  <span className="text-xs text-slate-600 font-medium">Chọn nhanh mệnh giá nạp:</span>
                  <div className="grid grid-cols-4 gap-2">
                    {[1000000, 2000000, 5000000, 10000000].map((amt) => (
                      <button
                        key={amt}
                        type="button"
                        onClick={() => setTopupAmount(amt)}
                        className={`py-2 text-xs font-semibold rounded-lg border transition-all ${
                          topupAmount === amt
                            ? 'bg-red-50 border-[#FF4B4B] text-[#FF4B4B]'
                            : 'border-slate-200 text-slate-600 hover:bg-slate-50'
                        }`}
                      >
                        {amt / 1000000}Tr
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hoặc nhập số tiền tùy chọn */}
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-600 font-medium block">Hoặc nhập số tiền nạp tùy chọn (VND):</label>
                  <input
                    type="number"
                    min={10000}
                    step={100000}
                    value={topupAmount}
                    onChange={(e) => setTopupAmount(Number(e.target.value))}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-[#FF4B4B]"
                  />
                </div>

                {/* Phương thức nạp mô phỏng */}
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-600 font-medium block">Phương thức nạp mô phỏng:</label>
                  <select
                    value={topupMethod}
                    onChange={(e) => setTopupMethod(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 bg-slate-50 focus:outline-none"
                  >
                    <option value="BANK_TRANSFER">Chuyển khoản ngân hàng (Quét mã VNPAY QR / MoMo / VietQR)</option>
                    <option value="CREDIT_CARD">Thẻ tín dụng / Ghi nợ quốc tế (Visa, Mastercard)</option>
                    <option value="CASH">Nạp tiền mặt tại quầy lễ tân</option>
                  </select>
                </div>

                <button
                  type="button"
                  onClick={handleTopup}
                  disabled={topupLoading || topupAmount <= 0}
                  className="w-full py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow-sm flex items-center justify-center gap-2 transition-all"
                >
                  <PlusCircle className="w-4 h-4" /> {topupLoading ? 'Đang nạp...' : `+ Nạp Tiền Ngay (${topupAmount.toLocaleString('vi-VN')} ₫)`}
                </button>
              </div>

              {/* CỘT PHẢI: Rút Tiền Về Tài Khoản Ngân Hàng */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4 flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="pb-3 border-b border-slate-100">
                    <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
                      <span className="text-lg">🏦</span> Rút Tiền Về Tài Khoản Ngân Hàng
                    </h4>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                      Rút lại số dư chưa sử dụng hoặc tiền hoàn/đền bù trong ví về tài khoản ngân hàng cá nhân.
                    </p>
                  </div>

                  {wallet.balance < 50000 ? (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-800 leading-relaxed">
                      Số dư khả dụng hiện tại là <b>{wallet.balance.toLocaleString('vi-VN')} ₫</b>. Cần tối thiểu <b>50.000 ₫</b> để thực hiện lệnh rút tiền về ngân hàng.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-700">Ngân hàng thụ hưởng (*):</label>
                        <select
                          value={withdrawBank}
                          onChange={(e) => setWithdrawBank(e.target.value)}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs bg-white focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="Vietcombank">Vietcombank (Ngoại Thương)</option>
                          <option value="MB Bank">MB Bank (Quân Đội)</option>
                          <option value="Techcombank">Techcombank (Kỹ Thương)</option>
                          <option value="BIDV">BIDV (Đầu Tư & Phát Triển)</option>
                          <option value="VietinBank">VietinBank (Công Thương)</option>
                          <option value="ACB">ACB (Á Châu)</option>
                          <option value="TPBank">TPBank (Tiên Phong)</option>
                          <option value="VPBank">VPBank (Việt Nam Thịnh Vượng)</option>
                        </select>
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-700">Số tài khoản ngân hàng (*):</label>
                        <input
                          type="text"
                          placeholder="Ví dụ: 0987654321..."
                          value={withdrawAccount}
                          onChange={(e) => setWithdrawAccount(e.target.value)}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-700">Tên chủ tài khoản (*):</label>
                        <input
                          type="text"
                          placeholder="NGUYEN VAN A"
                          value={withdrawHolder}
                          onChange={(e) => setWithdrawHolder(e.target.value.toUpperCase())}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-bold uppercase focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between items-center text-xs">
                          <label className="font-semibold text-slate-700">Số tiền rút (VND) (*):</label>
                          <button
                            type="button"
                            onClick={() => setWithdrawAmount(Math.max(50000, wallet.balance - wallet.lockedBalance))}
                            className="text-[11px] text-blue-600 hover:underline font-semibold"
                          >
                            Rút toàn bộ
                          </button>
                        </div>
                        <input
                          type="number"
                          min={50000}
                          max={wallet.balance - wallet.lockedBalance}
                          step={50000}
                          value={withdrawAmount}
                          onChange={(e) => setWithdrawAmount(Number(e.target.value))}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-bold focus:ring-2 focus:ring-blue-500"
                        />
                        <div className="text-[11px] text-slate-400">
                          Tối thiểu: 50.000 ₫ • Tối đa khả dụng: {(wallet.balance - wallet.lockedBalance).toLocaleString('vi-VN')} ₫
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={handleWithdraw}
                        disabled={withdrawLoading || withdrawAmount < 50000 || !withdrawAccount.trim() || !withdrawHolder.trim()}
                        className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center justify-center gap-1.5"
                      >
                        {withdrawLoading ? 'Đang xử lý rút tiền...' : `Xác Nhận Rút ${withdrawAmount.toLocaleString('vi-VN')} ₫`}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Bảng Lịch Sử Giao Dịch Tài Chính */}
            <div className="space-y-3 pt-4 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-bold text-slate-900">Lịch Sử Giao Dịch Tài Chính</h4>
                <button
                  type="button"
                  onClick={fetchWallet}
                  className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Làm mới lịch sử
                </button>
              </div>

              {!wallet.transactions || wallet.transactions.length === 0 ? (
                <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center text-xs text-slate-500">
                  Chưa có giao dịch tài chính nào phát sinh trong ví.
                </div>
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 font-semibold uppercase">
                      <tr>
                        <th className="py-3 px-4">Mã Giao Dịch</th>
                        <th className="py-3 px-4">Loại GD</th>
                        <th className="py-3 px-4">Số Tiền</th>
                        <th className="py-3 px-4">Phương Thức</th>
                        <th className="py-3 px-4">Trạng Thái</th>
                        <th className="py-3 px-4">Thời Gian</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 text-xs">
                      {wallet.transactions.map((tx: any) => {
                        const isPlus =
                          tx.paymentType === 'TOPUP' ||
                          tx.paymentType === 'COMPENSATION' ||
                          tx.paymentType === 'EARNING';
                        return (
                          <tr key={tx.id} className="hover:bg-slate-50/70">
                            <td className="py-3 px-4 font-mono font-semibold text-slate-700">
                              {tx.transactionRef || `#${tx.id}`}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`font-semibold px-2 py-0.5 rounded-full ${
                                  tx.paymentType === 'TOPUP'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : tx.paymentType === 'PURCHASE_PACKAGE'
                                    ? 'bg-blue-100 text-blue-800'
                                    : tx.paymentType === 'COMPENSATION'
                                    ? 'bg-amber-100 text-amber-800'
                                    : tx.paymentType === 'WITHDRAW'
                                    ? 'bg-purple-100 text-purple-800'
                                    : 'bg-slate-100 text-slate-800'
                                }`}
                              >
                                {tx.paymentType === 'TOPUP'
                                  ? 'NẠP TIỀN'
                                  : tx.paymentType === 'PURCHASE_PACKAGE'
                                  ? 'MUA KHÓA'
                                  : tx.paymentType === 'COMPENSATION'
                                  ? 'ĐỀN BÙ'
                                  : tx.paymentType === 'WITHDRAW'
                                  ? 'RÚT TIỀN'
                                  : tx.paymentType}
                              </span>
                            </td>
                            <td
                              className={`py-3 px-4 font-bold ${
                                isPlus ? 'text-emerald-600' : 'text-red-600'
                              }`}
                            >
                              {isPlus ? '+' : '-'}
                              {tx.amount.toLocaleString('vi-VN')} ₫
                            </td>
                            <td className="py-3 px-4 text-slate-600">{tx.paymentMethod}</td>
                            <td className="py-3 px-4">
                              <span
                                className={`px-2 py-0.5 rounded-full font-bold ${
                                  tx.status === 'SUCCESS'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {tx.status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-slate-500">
                              {tx.createdAt ? tx.createdAt.replace('T', ' ').substring(0, 19) : ''}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 6: KHIẾU NẠI & TRANH CHẤP CỦA HỌC VIÊN */}
        {activeTab === 6 && (
          <div className="space-y-6 animate-fade-in">
            {/* Banner giới thiệu cơ chế Trọng tài */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-xl border border-indigo-500/20">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center shrink-0">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl sm:text-2xl font-black tracking-tight">Hồ Sơ Khiếu Nại & Trọng Tài Nền Tảng</h3>
                    <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                      Bảo vệ 100% quyền lợi học viên: Hoàn tiền, bù buổi tập hoặc bồi thường khi HLV vắng mặt hoặc vi phạm cam kết.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleOpenQuickDispute}
                    className="px-4 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center gap-1.5 shrink-0"
                  >
                    <PlusCircle className="w-4 h-4" /> + Tạo khiếu nại mới
                  </button>
                  <button
                    type="button"
                    onClick={fetchMyDisputes}
                    className="px-3 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shrink-0"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="mt-4 p-3 bg-white/5 rounded-2xl border border-white/10 text-xs text-amber-200/90 leading-relaxed">
                💡 <b>Cách gửi khiếu nại một ca tập:</b> Vào tab <b>Lịch Của Tôi</b>, tìm ca tập gặp sự cố (HLV vắng mặt, gian lận OTP, cắt bớt giờ...) và nhấn nút <b>"⚠️ Khiếu nại"</b>. Ban Quản Trị sẽ xác minh định vị GPS, log liên lạc và ban hành phán quyết trong 24h.
              </div>
            </div>

            {/* Danh sách khiếu nại */}
            <div className="space-y-4">
              <h4 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <span>Danh sách vụ việc của bạn:</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700 font-extrabold">{myDisputes.length} hồ sơ</span>
              </h4>

              {loadingDisputes ? (
                <div className="p-8 text-center text-slate-400 text-xs">Đang kiểm tra hồ sơ khiếu nại...</div>
              ) : myDisputes.length === 0 ? (
                <div className="bg-white rounded-2xl border border-slate-200 p-10 text-center space-y-3">
                  <div className="w-14 h-14 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-7 h-7" />
                  </div>
                  <h5 className="font-bold text-slate-900 text-sm">Bạn chưa có khiếu nại nào</h5>
                  <p className="text-xs text-slate-500 max-w-md mx-auto">
                    Tất cả các ca tập của bạn đều diễn ra thuận lợi. Nếu có bất kỳ sự cố nào xảy ra trong tương lai, bạn luôn có thể báo cáo tại mục Lịch Của Tôi.
                  </p>
                  <button
                    onClick={() => setActiveTab(3)}
                    className="mt-2 px-5 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-xs font-bold rounded-xl transition"
                  >
                    Xem Lịch Của Tôi
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {myDisputes.map((d) => (
                    <div key={d.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3.5 hover:border-slate-300 transition">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg border border-indigo-200">
                            #CASE-{d.id}
                          </span>
                          <span className="font-bold text-slate-900 text-sm">{d.disputeTypeLabel}</span>
                          <span className="text-xs text-slate-400">• Ca tập #{d.bookingId}</span>
                        </div>

                        {d.status.startsWith('RESOLVED') ? (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            ✓ Đã Có Phán Quyết Trọng Tài
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-50 text-amber-700 border border-amber-200 animate-pulse">
                            ⏳ Chờ Ban Quản Trị Xử Lý
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs bg-slate-50 p-3 rounded-xl border border-slate-100">
                        <div>
                          <span className="text-slate-400 block">Huấn luyện viên:</span>
                          <span className="font-bold text-slate-800">{d.ptName}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block">Thời gian ca tập:</span>
                          <span className="font-medium text-slate-700">{d.scheduledTime}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block">Học phí ca tập:</span>
                          <span className="font-bold text-emerald-600">{Number(d.sessionFee || 0).toLocaleString('vi-VN')} ₫</span>
                        </div>
                      </div>

                      <div>
                        <span className="text-xs font-bold text-slate-700 block mb-1">
                          {d.complainant === 'STUDENT' ? 'Tường trình khiếu nại của bạn:' : 'Tường trình khiếu nại từ Huấn Luyện Viên:'}
                        </span>
                        <p className="text-xs text-slate-600 bg-slate-50/70 p-3 rounded-xl border border-slate-100 italic leading-relaxed">
                          "{d.complainant === 'STUDENT' ? (d.studentStatement || d.summary) : (d.ptStatement || d.summary)}"
                        </p>
                      </div>

                      {/* Phản biện đối chứng */}
                      {d.counterStatement ? (
                        <div className="p-3 bg-blue-50/80 rounded-xl border border-blue-200 text-xs space-y-1">
                          <span className="font-bold text-blue-900 block">
                            💬 Phản biện đối chứng {d.complainant === 'STUDENT' ? 'của HLV:' : 'của bạn:'}
                          </span>
                          <p className="italic text-blue-800 leading-relaxed font-medium">"{d.counterStatement}"</p>
                        </div>
                      ) : d.complainant === 'PT' && !d.status.startsWith('RESOLVED') && (
                        <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-300 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 animate-pulse">
                          <div>
                            <span className="font-bold text-amber-900 block">⚠️ HLV đang khiếu nại bạn trong ca tập này!</span>
                            <span className="text-amber-700 text-[11px]">Bạn chưa gửi phản biện. Hãy gửi bản tường trình đối chất để Ban Quản Trị xem xét công bằng trước khi ra phán quyết.</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleOpenCounterModal(d)}
                            className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold text-xs shrink-0 shadow-xs flex items-center gap-1.5 transition"
                          >
                            <MessageCircle className="w-3.5 h-3.5" /> Gửi phản biện ngay
                          </button>
                        </div>
                      )}

                      {d.evidenceNote && (
                        <div className="text-xs text-slate-500 flex items-center gap-1.5">
                          <span>📎 Bằng chứng cung cấp:</span>
                          <span className="font-medium text-slate-700">{d.evidenceNote}</span>
                        </div>
                      )}

                      {/* Phán quyết của Hội Đồng Trọng Tài */}
                      {d.status.startsWith('RESOLVED') && (
                        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl space-y-1">
                          <div className="flex items-center gap-1.5 font-bold text-xs text-emerald-900">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                            <span>PHÁN QUYẾT TỪ BAN QUẢN TRỊ NỀN TẢNG:</span>
                          </div>
                          <p className="text-xs text-emerald-800 font-medium leading-relaxed">
                            {d.resolutionDecision}
                          </p>
                          {d.resolvedAt && (
                            <div className="text-[11px] text-emerald-600 pt-0.5">
                              Thời gian ban hành: {d.resolvedAt}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 7: HỒ SƠ */}
        {activeTab === 7 && (
          <div className="space-y-6">
            <UserProfileCard
              user={user}
              onUserUpdated={(updatedUser) => {
                onUserUpdated?.(updatedUser);
              }}
              showToast={showToast}
            />
          </div>
        )}
      </main>

      {/* Counter Statement Modal for Student */}
      {counterDisputeModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-scale-up border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2 text-indigo-600">
                <MessageCircle className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900">
                  Gửi Bản Phản Biện & Đối Chứng (#CASE-{counterDisputeModal.id})
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setCounterDisputeModal(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3.5">
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-1">
                <span className="font-bold text-amber-900 block">Khiếu nại từ HLV {counterDisputeModal.ptName}:</span>
                <p className="italic text-amber-800">"{counterDisputeModal.ptStatement || counterDisputeModal.summary}"</p>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Bản tường trình phản biện của bạn <span className="text-red-500">*</span>:
                </label>
                <textarea
                  rows={4}
                  value={counterStatementText}
                  onChange={(e) => {
                    setCounterStatementText(e.target.value);
                    if (counterError) setCounterError(null);
                  }}
                  placeholder="Giải trình cụ thể: Lý do bạn không có mặt, sự cố đột xuất hoặc đối chiếu với lời tường trình của HLV..."
                  className="w-full p-2.5 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {counterError && (
                <div className="p-2.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
                  ⚠️ {counterError}
                </div>
              )}

              <p className="text-[11px] text-slate-400 leading-normal">
                💡 Bản phản biện của bạn sẽ được chuyển thẳng đến Hội đồng Trọng tài để đối soát hai chiều trước khi ban hành phán quyết cuối cùng.
              </p>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setCounterDisputeModal(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Hủy bỏ
                </button>
                <button
                  type="button"
                  disabled={submittingCounter}
                  onClick={handleSubmitCounterStatement}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  {submittingCounter ? 'Đang gửi phản biện...' : 'Gửi phản biện lên Admin'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Dispute Modal for Student */}
      {showTabDisputeModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-scale-up border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2.5 text-amber-600">
                <ShieldAlert className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900">Gửi Hồ Sơ Khiếu Nại Lên Ban Quản Trị</h4>
              </div>
              <button
                type="button"
                onClick={() => setShowTabDisputeModal(false)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3.5">
              {/* Chọn ca tập */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Chọn ca tập bạn muốn khiếu nại:
                </label>
                {myBookings.filter(b => b.status !== 'PENDING').length === 0 ? (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800">
                    ⚠️ Bạn chưa có ca tập nào (đã xác nhận, hoàn thành hoặc hủy) để khiếu nại.
                  </div>
                ) : (
                  <select
                    value={tabDisputeBookingId || ''}
                    onChange={(e) => setTabDisputeBookingId(Number(e.target.value))}
                    className="w-full p-2.5 text-xs border border-slate-300 rounded-xl bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-500"
                  >
                    {myBookings
                      .filter(b => b.status !== 'PENDING')
                      .map((b) => (
                        <option key={b.id} value={b.id}>
                          Ca #{b.id} ({b.status}) - HLV: {b.ptName || 'HLV'} ({formatSlotTime(b.startTime)})
                        </option>
                      ))}
                  </select>
                )}
              </div>

              {/* Chọn lý do khiếu nại */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">Lý do khiếu nại:</label>
                <select
                  value={tabDisputeType}
                  onChange={(e) => {
                    const val = e.target.value;
                    setTabDisputeType(val);
                    const sel = studentDisputeReasonOptions.find(r => r.value === val);
                    if (sel) setTabDisputeSeverity(sel.severity);
                  }}
                  className="w-full p-2.5 text-xs border border-slate-300 rounded-xl bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  {studentDisputeReasonOptions.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </div>

              {/* Tường trình chi tiết */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Tường trình chi tiết <span className="text-red-500">*</span>:
                </label>
                <textarea
                  rows={3}
                  value={tabDisputeStatement}
                  onChange={(e) => {
                    setTabDisputeStatement(e.target.value);
                    if (tabDisputeError) setTabDisputeError(null);
                  }}
                  placeholder="Mô tả cụ thể sự việc: bạn đến lúc mấy giờ, gọi HLV bao nhiêu lần, yêu cầu hoàn tiền thế nào..."
                  className="w-full p-2.5 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              {/* Bằng chứng */}
              <div>
                <label className="text-xs font-bold text-slate-700 block mb-1">
                  Bằng chứng đối chứng <span className="text-slate-400 font-normal">(không bắt buộc)</span>:
                </label>
                <input
                  type="text"
                  value={tabDisputeEvidence}
                  onChange={(e) => setTabDisputeEvidence(e.target.value)}
                  placeholder="VD: Lịch sử cuộc gọi nhỡ lúc 18:05, ảnh chụp quầy lễ tân lúc 17:58..."
                  className="w-full p-2 text-xs border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              {tabDisputeError && (
                <div className="p-2.5 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700">
                  ⚠️ {tabDisputeError}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowTabDisputeModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
                >
                  Hủy bỏ
                </button>
                <button
                  type="button"
                  disabled={tabDisputeSubmitting || !tabDisputeBookingId}
                  onClick={handleSubmitQuickDispute}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  {tabDisputeSubmitting ? 'Đang gửi...' : 'Gửi khiếu nại lên Admin'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Check-In OTP Modal Dialog for Student */}
      {checkInModalBooking && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 text-center shadow-2xl animate-scale-up border border-slate-100">
            <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-inner">
              <Key className="w-7 h-7" />
            </div>
            <h4 className="text-xl font-bold text-slate-900">Điểm Danh Ca Tập #{checkInModalBooking.id}</h4>
            <p className="text-xs text-slate-500 mt-1 mb-3">
              Nhập mã OTP 6 chữ số do Huấn luyện viên cung cấp khi bắt đầu buổi tập:
            </p>

            <div className="mb-4 bg-slate-50 p-3 rounded-xl border border-slate-100 text-left text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-slate-400">Huấn luyện viên:</span>
                <span className="font-bold text-slate-800">{checkInModalBooking.ptName || 'HLV'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Khóa học:</span>
                <span className="text-slate-700">{checkInModalBooking.courseTitle || 'Ca tập cá nhân'}</span>
              </div>
            </div>

            <input
              type="text"
              maxLength={6}
              value={studentOtpInput}
              onChange={(e) => {
                setStudentOtpInput(e.target.value.replace(/\D/g, ''));
                if (checkInError) setCheckInError(null);
              }}
              placeholder="123456"
              autoFocus
              className="w-full text-center py-3.5 px-4 border-2 border-emerald-300 focus:border-emerald-500 rounded-2xl font-mono text-3xl font-extrabold tracking-[0.4em] focus:ring-4 focus:ring-emerald-100 outline-none text-emerald-800 bg-emerald-50/40 mb-3 transition"
            />

            {checkInError && (
              <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-xl text-left text-xs text-red-700 flex items-start gap-2">
                <span className="shrink-0 text-sm">⚠️</span>
                <span>{checkInError}</span>
              </div>
            )}

            <div className="p-2.5 bg-blue-50 border border-blue-100 rounded-xl text-left text-[11px] text-blue-700 leading-normal mb-4">
              💡 <b>Lưu ý nghiệp vụ:</b> Huấn luyện viên của bạn sẽ mở phiên điểm danh và cung cấp mã OTP 6 số cho bạn khi ca tập bắt đầu. Nhập mã vào đây để hoàn tất điểm danh.
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  setCheckInModalBooking(null);
                  setCheckInError(null);
                }}
                className="flex-1 py-2.5 border border-slate-300 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 transition"
              >
                Hủy bỏ
              </button>
              <button
                type="button"
                disabled={checkInLoading || studentOtpInput.trim().length !== 6}
                onClick={handleConfirmStudentAttendance}
                className="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-md shadow-emerald-600/20 transition flex items-center justify-center gap-1.5"
              >
                {checkInLoading ? 'Đang xác nhận...' : 'Xác nhận điểm danh'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Workout Plans Modal for Student */}
      {viewingPlansEnrollment && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl max-h-[85vh] flex flex-col">
            <div className="flex justify-between items-center pb-4 border-b border-slate-100">
              <div>
                <h4 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <ClipboardList className="w-5 h-5 text-blue-600" /> Giáo Án Huấn Luyện Cá Nhân Hóa
                </h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  Hợp đồng: {viewingPlansEnrollment.courseTitle} (HLV: {viewingPlansEnrollment.ptName})
                </p>
              </div>
              <button
                onClick={() => setViewingPlansEnrollment(null)}
                className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg text-sm"
              >
                ✕
              </button>
            </div>

            <div className="overflow-y-auto py-4 flex-1 space-y-4">
              {loadingPlans ? (
                <div className="text-center py-8 text-sm text-slate-400">Đang tải giáo án...</div>
              ) : enrollmentPlans.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <Dumbbell className="w-10 h-10 mx-auto text-slate-300 mb-2" />
                  <p className="font-semibold text-slate-700">Huấn luyện viên chưa đăng tải giáo án</p>
                  <p className="text-xs text-slate-400 mt-1">
                    HLV sẽ sớm cập nhật kế hoạch luyện tập và các bài tập chuyên biệt cho bạn.
                  </p>
                </div>
              ) : (
                enrollmentPlans.map((plan) => (
                  <div key={plan.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <h5 className="font-bold text-slate-900 text-sm">{plan.title}</h5>
                        {plan.goal && <p className="text-xs text-slate-600 mt-0.5">🎯 Mục tiêu: {plan.goal}</p>}
                      </div>
                      {plan.startDate && (
                        <span className="text-[11px] text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                          {plan.startDate} ~ {plan.endDate}
                        </span>
                      )}
                    </div>

                    <div className="space-y-2">
                      <div className="text-xs font-semibold text-slate-700">Danh sách bài tập ({plan.workouts?.length || 0}):</div>
                      {(!plan.workouts || plan.workouts.length === 0) ? (
                        <div className="text-xs text-slate-400 italic">Chưa có chi tiết bài tập.</div>
                      ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {plan.workouts.map((w) => (
                            <div key={w.id} className="p-2.5 bg-white rounded-lg border border-slate-200 text-xs">
                              <div className="font-bold text-slate-800 flex items-center gap-1">
                                <Dumbbell className="w-3.5 h-3.5 text-blue-600" /> {w.exerciseName}
                              </div>
                              <div className="text-slate-500 mt-1 space-y-0.5 text-[11px]">
                                <div>Nhóm cơ: <span className="font-medium text-slate-700">{w.targetMuscle || 'Toàn thân'}</span></div>
                                <div>Khối lượng: <span className="font-medium text-slate-700">{w.sets} sets × {w.reps} reps ({w.weightKg || 0}kg)</span></div>
                                <div>Nghỉ: <span className="font-medium text-slate-700">{w.restSeconds}s</span></div>
                              </div>
                              {w.videoDemoUrl && (
                                <a
                                  href={w.videoDemoUrl}
                                  target="_blank"
                                  rel="noreferrer"
                                  className="inline-block mt-1.5 text-[11px] text-blue-600 hover:underline font-semibold"
                                >
                                  Video hướng dẫn ↗
                                </a>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setViewingPlansEnrollment(null)}
                className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Booking Confirmation Modal (Học thử TRIAL vs Khóa học PACKAGE) */}
      {bookingModalSlot && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 space-y-5 shadow-2xl border border-slate-100">
            <div className="flex justify-between items-center pb-3 border-b border-slate-100">
              <h4 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-[#FF4B4B]" /> Xác Nhận Đặt Lịch Tập
              </h4>
              <button
                onClick={() => setBookingModalSlot(null)}
                className="text-slate-400 hover:text-slate-600 text-sm p-1 rounded-lg hover:bg-slate-100"
              >
                ✕
              </button>
            </div>

            {/* Thông tin khung giờ đã chọn */}
            <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 text-xs space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Huấn luyện viên:</span>
                <span className="font-bold text-slate-800">{selectedPt?.fullName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Thời gian bắt đầu:</span>
                <span className="font-semibold text-slate-800">{formatSlotTime(bookingModalSlot.startTime)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Thời gian kết thúc:</span>
                <span className="font-semibold text-slate-800">{formatSlotTime(bookingModalSlot.endTime)}</span>
              </div>
            </div>

            {/* Lựa chọn loại Đặt Lịch: Học thử (TRIAL) vs Gói khóa học (PACKAGE) */}
            <div className="space-y-3">
              <label className="text-xs font-bold text-slate-700 block">Hình thức đặt lịch:</label>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Option TRIAL */}
                <div
                  onClick={() => setBookingType('TRIAL')}
                  className={`p-3.5 rounded-xl border-2 cursor-pointer transition-all ${
                    bookingType === 'TRIAL'
                      ? 'border-emerald-500 bg-emerald-50/50 ring-2 ring-emerald-200'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-xs text-slate-900 flex items-center gap-1.5">
                      <span>🎁</span> Học Thử (TRIAL)
                    </span>
                    <span className="text-xs font-extrabold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full">
                      0 VNĐ
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    Trải nghiệm 1 buổi miễn phí cùng HLV. Không cần hợp đồng gói tập.
                  </p>
                </div>

                {/* Option PACKAGE */}
                <div
                  onClick={() => setBookingType('PACKAGE')}
                  className={`p-3.5 rounded-xl border-2 cursor-pointer transition-all ${
                    bookingType === 'PACKAGE'
                      ? 'border-blue-500 bg-blue-50/50 ring-2 ring-blue-200'
                      : 'border-slate-200 hover:border-slate-300 bg-white'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-xs text-slate-900 flex items-center gap-1.5">
                      <span>📦</span> Theo Gói (PACKAGE)
                    </span>
                    <span className="text-xs font-semibold text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">
                      Trừ buổi
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-tight">
                    Sử dụng buổi tập từ khóa học bạn đã đăng ký với HLV này.
                  </p>
                </div>
              </div>
            </div>

            {/* Nếu chọn PACKAGE: Chọn hợp đồng */}
            {bookingType === 'PACKAGE' && (
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-700 block">Chọn hợp đồng khóa học áp dụng:</label>
                {ptActiveEnrollments.length === 0 ? (
                  <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800">
                    ⚠️ Bạn chưa có hợp đồng khóa học nào còn buổi tập với HLV <b>{selectedPt?.fullName}</b>.
                    Vui lòng chọn <b>"Học Thử (TRIAL)"</b> hoặc đăng ký khóa học trước.
                  </div>
                ) : (
                  <select
                    value={bookingEnrollmentId || ''}
                    onChange={(e) => setBookingEnrollmentId(Number(e.target.value))}
                    className="w-full border border-slate-300 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-blue-500 bg-white"
                  >
                    <option value="">-- Chọn hợp đồng khóa học --</option>
                    {ptActiveEnrollments.map((enr) => (
                      <option key={enr.id} value={enr.id}>
                        #{enr.id} - {enr.courseTitle || 'Khóa tập'} (Còn {enr.remainingSessions}/{enr.totalSessions} buổi - Hạn: {enr.endDate})
                      </option>
                    ))}
                  </select>
                )}
              </div>
            )}

            {/* Ghi chú buổi tập */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-700 block">
                Ghi chú cho Huấn Luyện Viên <span className="font-normal text-slate-400">(không bắt buộc)</span>:
              </label>
              <textarea
                rows={2}
                value={bookingNote}
                onChange={(e) => setBookingNote(e.target.value)}
                placeholder="Mục tiêu tập luyện, tiền sử chấn thương hoặc yêu cầu đặc biệt..."
                className="w-full border border-slate-300 rounded-xl p-2.5 text-xs focus:ring-2 focus:ring-[#FF4B4B] focus:outline-none"
              />
            </div>

            {/* Buttons */}
            <div className="flex gap-2 justify-end pt-3 border-t border-slate-100">
              <button
                onClick={() => setBookingModalSlot(null)}
                className="px-4 py-2 border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-semibold text-slate-600"
              >
                Hủy bỏ
              </button>
              <button
                onClick={confirmSubmitBooking}
                disabled={bookingSubmitting || (bookingType === 'PACKAGE' && !bookingEnrollmentId)}
                className="px-5 py-2 bg-[#FF4B4B] hover:bg-[#E03E3E] disabled:opacity-50 text-white rounded-xl text-xs font-bold shadow-md flex items-center gap-1.5"
              >
                {bookingSubmitting ? 'Đang gửi yêu cầu...' : (bookingType === 'TRIAL' ? 'Xác Nhận Đặt Học Thử (0đ)' : 'Xác Nhận Đặt Ca Tập')}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Review Modal Dialog */}
      {reviewBooking && (
        <ReviewModal
          booking={reviewBooking}
          onClose={() => setReviewBooking(null)}
          onSubmitted={() => {
            setReviewBooking(null);
            setReviewedBookingIds((prev) => new Set(prev).add(reviewBooking.id));
            setReviewReloadKey((k) => k + 1);
            fetchPts();
            showToast('Gửi đánh giá thành công! Cảm ơn bạn đã phản hồi.');
          }}
        />
      )}
    </div>
  );
};
