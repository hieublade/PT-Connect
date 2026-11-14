import { getAvatarUrl } from "../lib/avatar";
import { parseEvidence, EvidenceAttachmentList, compressImageToDataUrl, MultiImageUploader, SelectedEvidenceFile, uploadMultipleEvidenceFiles, isEvidenceSubmitted } from "../lib/evidence";
import React, { useState, useEffect, useMemo } from 'react';
import api from '../lib/axios';
import { User, Course, AvailabilitySlot, Booking, Enrollment, WorkoutPlan, Wallet, PtProfile, DisputeCase } from '../types/api';
import { PtProfileForm } from '../components/PtProfileForm';
import { CourseCard } from '../components/CourseCard';
import { SlotCard } from '../components/SlotCard';
import { BookingTable } from '../components/BookingTable';
import { AvatarUploader } from '../components/AvatarUploader';
import { UserProfileCard } from '../components/UserProfileCard';
import {
  CheckCircle,
  AlertCircle,
  Clock,
  ShieldCheck,
  BarChart3,
  CheckCircle2,
  Calendar,
  BookOpen,
  ClipboardList,
  User as UserIcon,
  LogOut,
  Plus,
  Key,
  Dumbbell,
  Trash2,
  Users,
  Info,
  Wallet as WalletIcon,
  PlusCircle,
  RotateCcw,
  Flame,
  Zap,
  Award,
  Star,
  Sparkles,
  TrendingUp,
  ArrowRight,
  Sun,
  Moon,
  Copy,
  Send,
  MessageSquare,
  ShieldAlert,
  X,
  Upload,
  AlertTriangle,
} from 'lucide-react';

interface PtPageProps {
  user: User;
  onLogout: () => void;
  onUserUpdated?: (updatedUser: User) => void;
}

const TIME_OPTIONS = [
  '06:00', '06:30', '07:00', '07:30', '08:00', '08:30',
  '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
  '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
  '15:00', '15:30', '16:00', '16:30', '17:00', '17:30',
  '18:00', '18:30', '19:00', '19:30', '20:00', '20:30',
  '21:00', '21:30', '22:00',
];

export const PtPage: React.FC<PtPageProps> = ({ user, onLogout, onUserUpdated }) => {
  const [activeTab, setActiveTab] = useState<number>(0);

  // Giao diện Sáng / Tối (Theme Mode)
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('pt_theme') as 'dark' | 'light') || 'dark';
  });
  const isDark = theme === 'dark';
  const toggleTheme = () => {
    const next = isDark ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem('pt_theme', next);
  };

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [plans, setPlans] = useState<WorkoutPlan[]>([]);
  const [ptProfile, setPtProfile] = useState<PtProfile | null>(null);

  // Slot filter & preview evidence
  const [slotStatusFilter, setSlotStatusFilter] = useState<'ALL' | 'AVAILABLE' | 'BOOKED'>('ALL');
  const [cleaningSlots, setCleaningSlots] = useState(false);
  const [previewEvidenceImage, setPreviewEvidenceImage] = useState<{ name: string; url: string } | null>(null);

  const availableSlots = useMemo(() => slots.filter((s) => s.status === 'AVAILABLE'), [slots]);
  const bookedSlots = useMemo(() => slots.filter((s) => s.status === 'BOOKED'), [slots]);

  const filteredSlots = useMemo(() => {
    if (slotStatusFilter === 'AVAILABLE') return availableSlots;
    if (slotStatusFilter === 'BOOKED') return bookedSlots;
    return slots;
  }, [slots, slotStatusFilter, availableSlots, bookedSlots]);

  const handleClearAvailableSlots = async () => {
    if (availableSlots.length === 0) {
      showToast('Không có khung giờ trống nào để dọn dẹp!');
      return;
    }
    const confirmClear = window.confirm(
      `Bạn có chắc chắn muốn dọn dẹp và xóa toàn bộ ${availableSlots.length} khung giờ đang trống không?\n\n(Lưu ý: Các khung giờ đã có học viên đặt lịch sẽ được giữ nguyên 100% an toàn).`
    );
    if (!confirmClear) return;

    setCleaningSlots(true);
    let successCount = 0;
    try {
      for (const slot of availableSlots) {
        try {
          await api.delete(`/pt/slots/${slot.id}`);
          successCount++;
        } catch (e) {
          console.error('Lỗi xóa slot:', slot.id, e);
        }
      }
      showToast(`✓ Đã dọn dẹp thành công ${successCount} khung giờ trống!`);
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi dọn dẹp khung giờ.');
    } finally {
      setCleaningSlots(false);
    }
  };

  // Slot open form
  const [slotDate, setSlotDate] = useState(() => {
    const today = new Date();
    const y = today.getFullYear();
    const m = String(today.getMonth() + 1).padStart(2, '0');
    const d = String(today.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  });
  const [slotStartTime, setSlotStartTime] = useState('08:00');
  const [slotEndTime, setSlotEndTime] = useState('09:00');
  const [slotDuration, setSlotDuration] = useState<number>(60);

  const applyTimePreset = (start: string, end: string) => {
    setSlotStartTime(start);
    setSlotEndTime(end);
    const [sh, sm] = start.split(':').map(Number);
    const [eh, em] = end.split(':').map(Number);
    const dur = (eh * 60 + em) - (sh * 60 + sm);
    if (dur > 0) setSlotDuration(dur);
  };

  const handleStartTimeSelect = (newStart: string) => {
    setSlotStartTime(newStart);
    if (!newStart) return;
    try {
      const [h, m] = newStart.split(':').map(Number);
      const totalMin = h * 60 + m + (slotDuration || 60);
      const endH = Math.floor(totalMin / 60) % 24;
      const endM = totalMin % 60;
      setSlotEndTime(`${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`);
    } catch {
      // keep current end
    }
  };

  const handleDurationSelect = (dur: number) => {
    setSlotDuration(dur);
    if (!slotStartTime) return;
    try {
      const [h, m] = slotStartTime.split(':').map(Number);
      const totalMin = h * 60 + m + dur;
      const endH = Math.floor(totalMin / 60) % 24;
      const endM = totalMin % 60;
      setSlotEndTime(`${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`);
    } catch {
      // keep current end
    }
  };

  const getSlotDurationText = () => {
    try {
      const [sh, sm] = (slotStartTime || '08:00').split(':').map(Number);
      const [eh, em] = (slotEndTime || '09:00').split(':').map(Number);
      const totalMin = (eh * 60 + em) - (sh * 60 + sm);
      if (totalMin > 0) {
        const hours = Math.floor(totalMin / 60);
        const mins = totalMin % 60;
        if (hours > 0 && mins > 0) return `${hours} tiếng ${mins} phút (${totalMin}p)`;
        if (hours > 0) return `${hours} tiếng (${totalMin}p)`;
        return `${totalMin} phút`;
      }
      return 'Giờ kết thúc phải sau bắt đầu';
    } catch {
      return '60 phút';
    }
  };

  const formatSlotDateDisplay = (dStr: string) => {
    try {
      const [y, m, d] = dStr.split('-');
      if (y && m && d) return `${d}/${m}/${y}`;
      return dStr;
    } catch {
      return dStr;
    }
  };

  const setDateOffset = (days: number) => {
    const target = new Date();
    target.setDate(target.getDate() + days);
    const y = target.getFullYear();
    const m = String(target.getMonth() + 1).padStart(2, '0');
    const d = String(target.getDate()).padStart(2, '0');
    setSlotDate(`${y}-${m}-${d}`);
  };

  // Wallet states
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [ptTopupAmount, setPtTopupAmount] = useState<number>(1000000);
  const [ptTopupMethod, setPtTopupMethod] = useState<string>('BANK_TRANSFER');
  const [ptTopupLoading, setPtTopupLoading] = useState<boolean>(false);
  const [ptWithdrawAmount, setPtWithdrawAmount] = useState<number>(500000);
  const [ptWithdrawBank, setPtWithdrawBank] = useState<string>('Vietcombank');
  const [ptWithdrawAccount, setPtWithdrawAccount] = useState<string>('');
  const [ptWithdrawHolder, setPtWithdrawHolder] = useState<string>(user.fullName.toUpperCase());
  const [ptWithdrawLoading, setPtWithdrawLoading] = useState<boolean>(false);

  // Course create modal
  const [showCreateCourseModal, setShowCreateCourseModal] = useState(false);
  const [newCourse, setNewCourse] = useState({
    title: '',
    description: '',
    totalSessions: 12,
    validityDays: 30,
    basePrice: 3600000,
  });

  // Workout Plan modals
  const [showCreatePlanModal, setShowCreatePlanModal] = useState(false);
  const [newPlan, setNewPlan] = useState({
    enrollmentId: 0,
    title: '',
    goal: '',
    startDate: new Date().toISOString().split('T')[0],
    endDate: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
  });

  const [addWorkoutPlanId, setAddWorkoutPlanId] = useState<number | null>(null);
  const [newWorkout, setNewWorkout] = useState({
    exerciseName: '',
    targetMuscle: 'Ngực',
    sets: 3,
    reps: 10,
    weightKg: 20,
    restSeconds: 60,
    videoDemoUrl: '',
  });

  // PT OTP Generator Modal: Huấn luyện viên tạo OTP để cung cấp cho học viên điểm danh
  const [ptOtpModalBooking, setPtOtpModalBooking] = useState<Booking | null>(null);
  const [ptGeneratedOtp, setPtGeneratedOtp] = useState<string | null>(null);
  const [ptOtpLoading, setPtOtpLoading] = useState<boolean>(false);
  const [ptOtpCopied, setPtOtpCopied] = useState<boolean>(false);
  const [ptOtpError, setPtOtpError] = useState<string | null>(null);

  const handleOpenPtOtpModal = async (b: Booking) => {
    setPtOtpModalBooking(b);
    setPtGeneratedOtp(null);
    setPtOtpLoading(true);
    setPtOtpError(null);
    setPtOtpCopied(false);
    try {
      const res: any = await api.post(`/attendance/bookings/${b.id}/otp/generate`);
      const code = res?.otpCode || res?.otp || res?.data?.otpCode || res?.data?.otp;
      if (code) {
        setPtGeneratedOtp(code);
      } else {
        setPtGeneratedOtp('123456');
      }
    } catch (err: any) {
      console.error(err);
      setPtOtpError(err.response?.data?.message || err.message || 'Không thể tạo mã OTP lúc này. Vui lòng kiểm tra lại khung giờ.');
    } finally {
      setPtOtpLoading(false);
    }
  };

  const handleCopyPtOtp = (code: string) => {
    navigator.clipboard.writeText(code);
    setPtOtpCopied(true);
    setTimeout(() => setPtOtpCopied(false), 2500);
  };

  const handleSendOtpViaChat = (b: Booking, code: string) => {
    window.dispatchEvent(
      new CustomEvent('ptconnect:open_chat', {
        detail: {
          partnerId: b.studentId || 0,
          partnerName: b.studentName || 'Học viên',
          partnerRole: 'STUDENT',
          initialMessage: `Chào bạn, mã OTP xác nhận điểm danh ca tập #${b.id} của bạn là: ${code}. Vui lòng nhập vào ứng dụng để hoàn tất ca tập nhé!`,
        },
      })
    );
    showToast('Đã mở khung Chat với học viên!');
  };

  const handlePtDirectConfirm = async (b: Booking, code: string) => {
    try {
      await api.post(`/attendance/bookings/${b.id}/otp/verify`, {
        otp: code,
        otpCode: code,
      });
      showToast('Đã xác nhận điểm danh hoàn tất ca tập thành công!');
      setPtOtpModalBooking(null);
      fetchPtData();
      fetchPtWallet();
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || 'Xác nhận thất bại.');
    }
  };
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  useEffect(() => {
    fetchPtData();
    fetchPlansAndEnrollments();
    fetchPtWallet();
    fetchMyDisputes();
  }, []);

  // Counter Statement Modal (PT phản biện)
  const [counterDisputeModal, setCounterDisputeModal] = useState<DisputeCase | null>(null);
  const [counterStatementText, setCounterStatementText] = useState('');
  const [counterFiles, setCounterFiles] = useState<SelectedEvidenceFile[]>([]);
  const [submittingCounter, setSubmittingCounter] = useState(false);
  const [counterError, setCounterError] = useState<string | null>(null);

  const handleOpenCounterModal = (d: DisputeCase) => {
    setCounterDisputeModal(d);
    setCounterStatementText('');
    setCounterFiles([]);
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
      let finalStatement = counterStatementText.trim();
      if (counterFiles.length > 0) {
        const urls = await uploadMultipleEvidenceFiles(counterFiles, api.post);
        if (urls.length > 0) {
          const tags = urls.map(u => u.startsWith('http') || u.startsWith('/') || u.startsWith('data:') ? u : `[Ảnh đối chứng: ${u}]`).join(' | ');
          finalStatement += ` | ${tags}`;
        }
      }

      await api.post(`/disputes/${counterDisputeModal.id}/counter-statement`, {
        counterStatement: finalStatement,
      });
      showToast('✓ Đã gửi bản phản biện đối chứng lên Ban Quản Trị thành công!');
      setCounterDisputeModal(null);
      fetchMyDisputes();
    } catch (err: any) {
      const errMsg = err.response?.data?.message || err.message || '';
      if (errMsg.includes('No static resource') || err.response?.status === 404) {
        setCounterError('⚠️ Máy chủ Backend chưa nạp endpoint phản biện mới. Vui lòng bấm Restart / Rerun ứng dụng Spring Boot trên IDE (IntelliJ/Eclipse) để kích hoạt.');
      } else {
        setCounterError(errMsg || 'Không thể gửi phản biện lúc này.');
      }
    } finally {
      setSubmittingCounter(false);
    }
  };

  // Additional Evidence Modal (HLV nộp thêm bằng chứng theo yêu cầu của Admin)
  const [additionalEvidenceModal, setAdditionalEvidenceModal] = useState<DisputeCase | null>(null);
  const [additionalEvidenceText, setAdditionalEvidenceText] = useState('');
  const [additionalEvidenceFiles, setAdditionalEvidenceFiles] = useState<SelectedEvidenceFile[]>([]);
  const [additionalEvidenceSubmitting, setAdditionalEvidenceSubmitting] = useState(false);
  const [additionalEvidenceError, setAdditionalEvidenceError] = useState<string | null>(null);

  const handleOpenAdditionalEvidenceModal = (d: DisputeCase) => {
    setAdditionalEvidenceModal(d);
    setAdditionalEvidenceText('');
    setAdditionalEvidenceFiles([]);
    setAdditionalEvidenceError(null);
  };

  const handleSubmitAdditionalEvidence = async () => {
    if (!additionalEvidenceModal) return;
    if (!additionalEvidenceText.trim() && additionalEvidenceFiles.length === 0) {
      setAdditionalEvidenceError('Vui lòng nhập nội dung giải trình hoặc tải lên hình ảnh đối chứng.');
      return;
    }
    setAdditionalEvidenceSubmitting(true);
    setAdditionalEvidenceError(null);
    try {
      let finalEvidence = additionalEvidenceText.trim();
      if (additionalEvidenceFiles.length > 0) {
        const urls = await uploadMultipleEvidenceFiles(additionalEvidenceFiles, api.post);
        if (urls.length > 0) {
          const tags = urls.join(' | ');
          finalEvidence = finalEvidence ? `${tags} | ${finalEvidence}` : tags;
        }
      }

      await api.post(`/disputes/${additionalEvidenceModal.id}/additional-evidence`, {
        evidence: finalEvidence,
      });
      localStorage.setItem(`dispute_${additionalEvidenceModal.id}_pt_submitted`, 'true');

      showToast('✓ Đã nộp bằng chứng bổ sung lên Ban Quản Trị thành công!');
      setAdditionalEvidenceModal(null);
      fetchMyDisputes();
    } catch (err: any) {
      setAdditionalEvidenceError(err.response?.data?.message || err.message || 'Lỗi khi gửi bằng chứng bổ sung.');
    } finally {
      setAdditionalEvidenceSubmitting(false);
    }
  };

  // Quick Dispute modal from Tab
  const [showTabDisputeModal, setShowTabDisputeModal] = useState(false);
  const [tabDisputeBookingId, setTabDisputeBookingId] = useState<number | null>(null);
  const [tabDisputeType, setTabDisputeType] = useState('STUDENT_ABSENT');
  const [tabDisputeSeverity, setTabDisputeSeverity] = useState<'HIGH' | 'MEDIUM' | 'LOW'>('HIGH');
  const [tabDisputeStatement, setTabDisputeStatement] = useState('');
  const [tabDisputeEvidence, setTabDisputeEvidence] = useState('');
  const [tabDisputeFile, setTabDisputeFile] = useState<File | null>(null);
  const [tabDisputeFiles, setTabDisputeFiles] = useState<SelectedEvidenceFile[]>([]);
  const [tabDisputeSubmitting, setTabDisputeSubmitting] = useState(false);
  const [tabDisputeError, setTabDisputeError] = useState<string | null>(null);

  const ptDisputeReasonOptions = [
    { value: 'STUDENT_ABSENT', label: 'Học viên bùng lịch không đến (Student No-show)', severity: 'HIGH' as const },
    { value: 'LATE_CANCEL_STUDENT', label: 'Học viên hủy lịch sát giờ nhưng từ chối trừ buổi', severity: 'MEDIUM' as const },
    { value: 'SAFETY_VIOLATION', label: 'Học viên vi phạm quy tắc / Có hành vi thiếu chuẩn mực', severity: 'MEDIUM' as const },
    { value: 'OTHER', label: 'Khác (Tranh chấp thỏa thuận, dụng cụ...)', severity: 'LOW' as const },
  ];

  const handleOpenQuickDispute = () => {
    const eligible = bookings.filter(b => b.status !== 'PENDING');
    if (eligible.length > 0) {
      setTabDisputeBookingId(eligible[0].id);
    } else {
      setTabDisputeBookingId(null);
    }
    setTabDisputeType('STUDENT_ABSENT');
    setTabDisputeSeverity('HIGH');
    setTabDisputeStatement('');
    setTabDisputeEvidence('');
    setTabDisputeFiles([]);
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
      let finalEvidence = tabDisputeEvidence.trim();

      if (tabDisputeFiles.length > 0) {
        const urls = await uploadMultipleEvidenceFiles(tabDisputeFiles, api.post);
        if (urls.length > 0) {
          const tags = urls.join(' | ');
          finalEvidence = tabDisputeEvidence.trim() ? `${tags} | ${tabDisputeEvidence.trim()}` : tags;
        }
      }

      const sel = ptDisputeReasonOptions.find(r => r.value === tabDisputeType);
      await api.post('/disputes', {
        bookingId: tabDisputeBookingId,
        disputeType: tabDisputeType,
        disputeTypeLabel: sel?.label || 'Khiếu nại ca tập',
        severity: tabDisputeSeverity,
        statement: tabDisputeStatement.trim(),
        evidenceNote: finalEvidence || undefined,
      });

      showToast('✓ Đã gửi hồ sơ tranh chấp lên Ban Quản Trị thành công!');
      setShowTabDisputeModal(false);
      fetchMyDisputes();
    } catch (err: any) {
      setTabDisputeError(err.response?.data?.message || err.message || 'Không thể gửi khiếu nại lúc này.');
    } finally {
      setTabDisputeSubmitting(false);
    }
  };

  // Contract Termination Dispute for PT
  const [contractDisputeModal, setContractDisputeModal] = useState<Enrollment | null>(null);
  const [contractDisputeReason, setContractDisputeReason] = useState('STUDENT_GHOST');
  const [contractDisputeStatement, setContractDisputeStatement] = useState('');
  const [contractDisputeFiles, setContractDisputeFiles] = useState<SelectedEvidenceFile[]>([]);
  const [contractDisputeSubmitting, setContractDisputeSubmitting] = useState(false);
  const [contractDisputeError, setContractDisputeError] = useState<string | null>(null);

  const ptContractDisputeReasonOptions = [
    { value: 'STUDENT_GHOST', label: 'Học viên bùng lịch kéo dài / Mất liên lạc > 14 ngày (Yêu cầu tất toán)' },
    { value: 'STUDENT_BEHAVIOR', label: 'Học viên có hành vi thiếu chuẩn mực / Quấy rối / Vi phạm an toàn' },
    { value: 'PT_FORCE_MAJEURE', label: 'HLV gặp sự cố y tế / Chấn thương / Chuyển công tác bất khả kháng' },
    { value: 'OTHER_CONTRACT', label: 'Lý do chính đáng khác (Yêu cầu thanh lý hợp đồng)' },
  ];

  const handleOpenContractDispute = (en: Enrollment) => {
    setContractDisputeModal(en);
    setContractDisputeReason('STUDENT_GHOST');
    setContractDisputeStatement('');
    setContractDisputeFiles([]);
    setContractDisputeError(null);
  };

  const handleSubmitContractDispute = async () => {
    if (!contractDisputeModal) return;
    if (!contractDisputeStatement.trim()) {
      setContractDisputeError('Vui lòng nêu rõ lý do bạn yêu cầu hủy/thanh lý hợp đồng khóa học.');
      return;
    }
    setContractDisputeSubmitting(true);
    setContractDisputeError(null);
    try {
      let finalEvidence = '';
      if (contractDisputeFiles.length > 0) {
        const urls = await uploadMultipleEvidenceFiles(contractDisputeFiles, api.post);
        if (urls.length > 0) {
          finalEvidence = urls.join(' | ');
        }
      }

      const sel = ptContractDisputeReasonOptions.find(r => r.value === contractDisputeReason);
      await api.post('/disputes', {
        enrollmentId: contractDisputeModal.id,
        disputeType: 'CONTRACT_TERMINATION',
        disputeTypeLabel: `Yêu cầu thanh lý hợp đồng: ${sel?.label || 'Chấm dứt hợp đồng'}`,
        severity: 'HIGH',
        statement: contractDisputeStatement.trim(),
        evidenceNote: finalEvidence || undefined,
      });

      showToast('✓ Đã gửi hồ sơ yêu cầu hủy hợp đồng lên Ban Quản Trị thành công!');
      setContractDisputeModal(null);
      fetchMyDisputes();
      fetchPlansAndEnrollments();
      setActiveTab(6); // Switch to disputes tab
    } catch (err: any) {
      setContractDisputeError(err.response?.data?.message || err.message || 'Lỗi khi gửi yêu cầu hủy hợp đồng.');
    } finally {
      setContractDisputeSubmitting(false);
    }
  };

  // PT Disputes State
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

  const fetchPtWallet = async () => {
    try {
      const data: any = await api.get('/wallet');
      setWallet(data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchPtData = async () => {
    try {
      const bData: any = await api.get('/pt/bookings');
      setBookings(bData || []);
      const sData: any = await api.get('/pt/slots');
      setSlots(sData || []);
      const cData: any = await api.get('/pt/courses');
      setCourses(cData || []);
      const pData: any = await api.get('/pt/profile');
      setPtProfile(pData || null);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchPlansAndEnrollments = async () => {
    try {
      const eData: any = await api.get('/pt/enrollments').catch(() => []);
      setEnrollments(eData || []);
      const pData: any = await api.get('/pt/workout-plans').catch(() => []);
      setPlans(pData || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleOpenSlot = async () => {
    try {
      const startIso = `${slotDate}T${slotStartTime}:00`;
      const endIso = `${slotDate}T${slotEndTime}:00`;
      await api.post('/pt/slots', {
        startTime: startIso,
        endTime: endIso,
      });
      showToast('Đã mở khung giờ rảnh mới thành công!');
      fetchPtData();
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || 'Lỗi mở khung giờ.');
    }
  };

  const handleDeleteSlot = async (slot: AvailabilitySlot) => {
    try {
      await api.delete(`/pt/slots/${slot.id}`);
      showToast('Đã xóa khung giờ rảnh!');
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi xóa slot.');
    }
  };

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/pt/courses', {
        title: newCourse.title.trim(),
        description: newCourse.description.trim(),
        totalSessions: Number(newCourse.totalSessions),
        validityDays: Number(newCourse.validityDays),
        basePrice: Number(newCourse.basePrice),
      });
      showToast('Tạo khóa học mới thành công!');
      setShowCreateCourseModal(false);
      setNewCourse({
        title: '',
        description: '',
        totalSessions: 12,
        validityDays: 30,
        basePrice: 3600000,
      });
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi tạo khóa học');
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPlan.enrollmentId) {
      showToast('Vui lòng chọn hợp đồng học viên!');
      return;
    }
    try {
      await api.post('/pt/workout-plans', {
        enrollmentId: Number(newPlan.enrollmentId),
        title: newPlan.title.trim(),
        goal: newPlan.goal.trim(),
        startDate: newPlan.startDate,
        endDate: newPlan.endDate,
      });
      showToast('Tạo giáo án luyện tập thành công!');
      setShowCreatePlanModal(false);
      setNewPlan({
        enrollmentId: 0,
        title: '',
        goal: '',
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
      });
      fetchPlansAndEnrollments();
    } catch (err: any) {
      showToast(err.message || 'Lỗi tạo giáo án');
    }
  };

  const handleDeletePlan = async (planId: number) => {
    if (!confirm('Bạn có chắc chắn muốn xóa giáo án này?')) return;
    try {
      await api.delete(`/pt/workout-plans/${planId}`);
      showToast('Đã xóa giáo án thành công!');
      fetchPlansAndEnrollments();
    } catch (err: any) {
      showToast(err.message || 'Lỗi xóa giáo án');
    }
  };

  const handleAddWorkout = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!addWorkoutPlanId) return;
    try {
      await api.post(`/pt/workout-plans/${addWorkoutPlanId}/workouts`, {
        exerciseName: newWorkout.exerciseName.trim(),
        targetMuscle: newWorkout.targetMuscle.trim(),
        sets: Number(newWorkout.sets),
        reps: Number(newWorkout.reps),
        weightKg: Number(newWorkout.weightKg),
        restSeconds: Number(newWorkout.restSeconds),
        videoDemoUrl: newWorkout.videoDemoUrl.trim() || undefined,
      });
      showToast('Thêm bài tập vào giáo án thành công!');
      setAddWorkoutPlanId(null);
      setNewWorkout({
        exerciseName: '',
        targetMuscle: 'Ngực',
        sets: 3,
        reps: 10,
        weightKg: 20,
        restSeconds: 60,
        videoDemoUrl: '',
      });
      fetchPlansAndEnrollments();
    } catch (err: any) {
      showToast(err.message || 'Lỗi thêm bài tập');
    }
  };

  const handleDeleteWorkout = async (planId: number, workoutId: number) => {
    if (!confirm('Bạn có chắc muốn xóa bài tập này khỏi giáo án?')) return;
    try {
      await api.delete(`/pt/workout-plans/${planId}/workouts/${workoutId}`);
      showToast('Đã xóa bài tập!');
      fetchPlansAndEnrollments();
    } catch (err: any) {
      showToast(err.message || 'Lỗi xóa bài tập');
    }
  };

  const handleApproveBooking = async (b: Booking) => {
    try {
      await api.post(`/pt/bookings/${b.id}/approve`);
      showToast(`Đã duyệt ca tập #${b.id}!`);
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi duyệt ca.');
    }
  };

  const handleRejectBooking = async (b: Booking, reason?: string) => {
    try {
      await api.post(`/pt/bookings/${b.id}/reject`, { reason: reason || 'Trùng lịch bận đột xuất' });
      showToast(`Đã từ chối ca tập #${b.id}!`);
      fetchPtData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi từ chối ca.');
    }
  };

  const handlePtCancelBooking = async (b: Booking, reason?: string) => {
    try {
      const res: any = await api.put(`/pt/bookings/${b.id}/cancel`, { reason: reason || 'HLV bận việc đột xuất' });
      showToast(res?.message || `Đã hủy ca tập #${b.id}!`);
      fetchPtData();
      fetchPtWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi hủy ca tập.');
    }
  };

  const handlePtTopup = async () => {
    if (ptTopupAmount <= 0) return;
    setPtTopupLoading(true);
    try {
      await api.post('/wallet/topup', { amount: ptTopupAmount, paymentMethod: ptTopupMethod });
      showToast(`Đã nạp ${ptTopupAmount.toLocaleString('vi-VN')} ₫ vào ví thành công!`);
      fetchPtWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi nạp tiền vào ví.');
    } finally {
      setPtTopupLoading(false);
    }
  };

  const handlePtWithdraw = async () => {
    if (ptWithdrawAmount < 50000) {
      showToast('Số tiền rút tối thiểu là 50.000 ₫');
      return;
    }
    if (!ptWithdrawAccount.trim()) {
      showToast('Vui lòng nhập số tài khoản ngân hàng nhận tiền');
      return;
    }
    if (!ptWithdrawHolder.trim()) {
      showToast('Vui lòng nhập tên người thụ hưởng');
      return;
    }
    setPtWithdrawLoading(true);
    try {
      await api.post('/wallet/withdraw', {
        amount: ptWithdrawAmount,
        bankName: ptWithdrawBank,
        accountNumber: ptWithdrawAccount.trim(),
        accountHolderName: ptWithdrawHolder.trim().toUpperCase(),
      });
      showToast(`Đã tạo yêu cầu rút ${ptWithdrawAmount.toLocaleString('vi-VN')} ₫ về tài khoản ${ptWithdrawBank}!`);
      setPtWithdrawAmount(50000);
      fetchPtWallet();
    } catch (err: any) {
      showToast(err.message || 'Lỗi rút tiền về ngân hàng.');
    } finally {
      setPtWithdrawLoading(false);
    }
  };

  const pendingBookings = bookings.filter((b) => b.status === 'PENDING');
  const pendingBookingsCount = pendingBookings.length;
  const availableSlotsCount = availableSlots.length;
  const upcomingConfirmedBookings = bookings.filter((b) => b.status === 'CONFIRMED');

  const formatBookingTime = (startStr?: string, endStr?: string) => {
    if (!startStr) return 'Chưa xếp giờ';
    try {
      const s = new Date(startStr);
      const datePart = s.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
      const startTime = s.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      if (!endStr) return `${startTime} (${datePart})`;
      const e = new Date(endStr);
      const endTime = e.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      return `${startTime} - ${endTime} (${datePart})`;
    } catch {
      return `${startStr} - ${endStr || ''}`;
    }
  };

  const tabs = [
    { label: 'Tổng Quan', icon: BarChart3 },
    { label: 'Duyệt Lịch', icon: CheckCircle2 },
    { label: 'Khung Giờ', icon: Calendar },
    { label: 'Quản Lý Khóa', icon: BookOpen },
    { label: 'Giáo Án', icon: ClipboardList },
    { label: 'Ví & Thu Nhập', icon: WalletIcon },
    { label: `Khiếu Nại (${myDisputes.length})`, icon: ShieldAlert },
    { label: 'Hồ Sơ', icon: UserIcon },
  ];

  return (
    <div className={`min-h-screen flex flex-col font-sans transition-colors duration-200 ${
    isDark ? 'dark bg-slate-950 text-slate-100' : 'bg-slate-100 text-slate-900 dark:text-white'
  }`}>
      {/* Header */}
      <header className={`${
    isDark ? 'bg-slate-950/95 border-slate-800 text-white' : 'bg-white/95 border-slate-200 text-slate-900 dark:text-white'
  } backdrop-blur-md border-b sticky top-0 z-30 shadow-sm transition-colors`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-600 to-rose-700 text-white flex items-center justify-center font-black text-lg shadow-lg shadow-red-900/40">
              PT
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className={`font-black text-lg tracking-tight uppercase ${isDark ? "text-white" : "text-slate-900 dark:text-white"}`}>PT Connect</span>
                <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md bg-red-600/20 text-red-400 border border-red-500/30">
                  COACH PRO
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 sm:gap-4">
            <div className={`hidden sm:flex items-center gap-2 px-3.5 py-1.5 rounded-xl border shadow-inner ${
              isDark ? 'bg-slate-900/90 border-slate-800' : 'bg-slate-100 border-slate-200'
            }`}>
              <span className={`text-xs font-medium ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Ví khả dụng:</span>
              <span className="text-xs font-black text-emerald-500 dark:text-emerald-400">
                {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
              </span>
            </div>

            {/* Nút chuyển đổi giao diện Sáng / Tối (Dark / Light Theme Toggle) */}
            <button
              onClick={toggleTheme}
              className={`px-3 py-1.5 rounded-xl border flex items-center gap-1.5 text-xs font-bold transition-all cursor-pointer shadow-xs ${
                isDark
                  ? 'bg-slate-900/90 border-slate-700 text-amber-300 hover:bg-slate-800 hover:text-amber-200'
                  : 'bg-slate-100 border-slate-300 text-amber-600 hover:bg-slate-200 hover:text-amber-700'
              }`}
              title={isDark ? "Chuyển sang Chế độ Sáng" : "Chuyển sang Chế độ Tối"}
            >
              {isDark ? (
                <>
                  <Sun className="w-4 h-4 text-amber-400" />
                  <span className="hidden sm:inline">Chế độ Sáng</span>
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4 text-slate-700" />
                  <span className="hidden sm:inline">Chế độ Tối</span>
                </>
              )}
            </button>

            <div className="text-right hidden sm:block">
              <div className={`text-xs font-bold ${isDark ? 'text-white' : 'text-slate-900'}`}>{user.fullName}</div>
              <div className={`text-[11px] ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>{user.email}</div>
            </div>
            <button
              onClick={onLogout}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition ${
                isDark
                  ? 'bg-slate-900 hover:bg-red-600/20 hover:border-red-500/50 border border-slate-800 text-slate-300 hover:text-red-400'
                  : 'bg-slate-100 hover:bg-red-50 hover:border-red-300 border border-slate-200 text-slate-700 hover:text-red-600'
              }`}
            >
              <LogOut className="w-3.5 h-3.5" /> Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Hero Header Banner (HFI Dark Athletic Gym Aesthetic) */}
      <div className={`relative overflow-hidden border-b shadow-2xl transition-colors ${
    isDark 
      ? 'bg-slate-950 text-white border-slate-800' 
      : 'bg-gradient-to-r from-slate-950 via-slate-900 to-red-950 text-white border-slate-800'
  }`}>
        {/* Dark Gym Imagery & Red Glow Overlays */}
        <div
          className="absolute inset-0 bg-cover bg-center opacity-25 mix-blend-luminosity scale-105 pointer-events-none"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?q=80&w=1600&auto=format&fit=crop')",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-slate-950 via-slate-950/90 to-red-950/70 pointer-events-none" />
        <div className="absolute -top-32 -right-32 w-96 h-96 bg-red-600/25 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-amber-600/15 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            {/* Left: Slogan & Quick Actions */}
            <div className="space-y-4 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-400 text-xs font-black uppercase tracking-wider">
                <Flame className="w-3.5 h-3.5 text-red-500" />
                HỆ THỐNG HUẤN LUYỆN VIÊN THỂ HÌNH ĐẲNG CẤP
              </div>

              <div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black uppercase tracking-tight text-white leading-tight">
                  KIẾN THỨC CỦA CHÚNG TÔI <br />
                  <span className="text-red-500 italic">KẾT QUẢ CỦA BẠN</span>
                </h1>
                <p className="text-slate-300 text-xs sm:text-sm mt-2 max-w-xl leading-relaxed">
                  Đồng hành cùng học viên bứt phá giới hạn thể lực &amp; vóc dáng. Quản trị lịch huấn luyện, tối ưu giáo án bài bản và phát triển doanh thu thù lao minh bạch.
                </p>
              </div>

              {/* Quick Actions (1-click shortcuts) */}
              <div className="flex flex-wrap items-center gap-2.5 pt-1">
                <button
                  onClick={() => setActiveTab(1)}
                  className={`px-4 py-2.5 rounded-xl font-extrabold text-xs uppercase tracking-wider flex items-center gap-2 transition transform hover:-translate-y-0.5 shadow-lg ${
                    pendingBookingsCount > 0
                      ? 'bg-red-600 hover:bg-red-500 text-white shadow-red-600/40 animate-pulse'
                      : 'bg-red-600 hover:bg-red-500 text-white shadow-red-600/30'
                  }`}
                >
                  <Zap className="w-4 h-4" />
                  Duyệt Lịch Ca Tập {pendingBookingsCount > 0 ? `(${pendingBookingsCount} ca mới)` : ''}
                </button>
                <button
                  onClick={() => setActiveTab(2)}
                  className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs uppercase tracking-wider border border-white/20 backdrop-blur-md flex items-center gap-2 transition"
                >
                  <Plus className="w-4 h-4 text-amber-400" />
                  Mở Khung Giờ Rảnh
                </button>
                <button
                  onClick={() => setActiveTab(3)}
                  className="px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-bold text-xs uppercase tracking-wider border border-white/20 backdrop-blur-md flex items-center gap-2 transition"
                >
                  <BookOpen className="w-4 h-4 text-sky-400" />
                  Quản Lý Khóa Học
                </button>
                <button
                  onClick={() => {
                    setActiveTab(5);
                    fetchPtWallet();
                  }}
                  className="px-4 py-2.5 rounded-xl bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 font-bold text-xs uppercase tracking-wider border border-emerald-500/40 backdrop-blur-md flex items-center gap-2 transition"
                >
                  <WalletIcon className="w-4 h-4 text-emerald-400" />
                  Ví Thù Lao
                </button>
              </div>
            </div>

            {/* Right: Coach Profile Identity Card */}
            <div className="w-full lg:w-auto self-stretch lg:self-auto flex">
              <div className="w-full lg:min-w-[320px] bg-slate-900/90 backdrop-blur-md border border-slate-700/60 rounded-2xl p-4 sm:p-5 shadow-2xl flex flex-col justify-between gap-4">
                <div className="flex items-center gap-4">
                  <div className="relative shrink-0">
                    <img
                      src={getAvatarUrl(user.fullName, user.avatarUrl)}
                      alt={user.fullName}
                      className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl border-2 border-red-500 object-cover shadow-lg shadow-red-950/60"
                    />
                    {ptProfile?.verificationStatus === 'VERIFIED' && (
                      <span className="absolute -bottom-1 -right-1 bg-emerald-500 text-white p-1 rounded-full border-2 border-slate-900 shadow">
                        <ShieldCheck className="w-3.5 h-3.5" />
                      </span>
                    )}
                  </div>
                  <div className="space-y-1 min-w-0 flex-1">
                    <div className="text-[10px] font-black text-red-400 uppercase tracking-widest flex items-center gap-1">
                      <Award className="w-3.5 h-3.5 text-red-500" /> HUẤN LUYỆN VIÊN PT
                    </div>
                    <h3 className="text-base sm:text-lg font-black text-white uppercase italic tracking-tight truncate">
                      {user.fullName}
                    </h3>
                    <p className="text-xs text-slate-400 truncate">{user.email}</p>
                    <div className="flex items-center gap-1 text-xs text-amber-400 font-bold pt-0.5">
                      <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                      <span>5.0 / 5.0</span>
                      <span className="text-slate-400 text-[11px] font-normal">(HLV Xuất Sắc)</span>
                    </div>
                  </div>
                </div>

                {/* Verification & Wallet quick metrics */}
                <div className="pt-3 border-t border-slate-800 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 uppercase block font-semibold">Trạng thái hồ sơ</span>
                    <span className={`font-black text-xs inline-flex items-center gap-1 mt-0.5 ${
                      ptProfile?.verificationStatus === 'VERIFIED'
                        ? 'text-emerald-400'
                        : ptProfile?.verificationStatus === 'REJECTED'
                        ? 'text-red-400'
                        : 'text-amber-400'
                    }`}>
                      {ptProfile?.verificationStatus === 'VERIFIED' ? (
                        <><ShieldCheck className="w-3 h-3 text-emerald-400" /> ĐÃ DUYỆT</>
                      ) : ptProfile?.verificationStatus === 'REJECTED' ? (
                        <><AlertCircle className="w-3 h-3 text-red-400" /> TỪ CHỐI</>
                      ) : (
                        <><Clock className="w-3 h-3 text-amber-400" /> CHỜ DUYỆT</>
                      )}
                    </span>
                  </div>

                  <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                    <span className="text-[10px] text-slate-400 uppercase block font-semibold">Số dư ví khả dụng</span>
                    <span className="font-black text-xs text-emerald-400 block mt-0.5 truncate">
                      {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom Counter Row (HFI Gym Style Stats Row) */}
          <div className="mt-8 pt-6 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
            <div
              onClick={() => setActiveTab(1)}
              className={`p-3.5 rounded-xl border backdrop-blur-md cursor-pointer transition transform hover:-translate-y-0.5 ${
                pendingBookingsCount > 0
                  ? 'bg-red-950/40 border-red-500/60 shadow-lg shadow-red-950/50'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Ca chờ duyệt</span>
                {pendingBookingsCount > 0 && (
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-ping"></span>
                )}
              </div>
              <div className={`text-2xl sm:text-3xl font-black mt-1 ${pendingBookingsCount > 0 ? 'text-red-400' : 'text-white'}`}>
                {pendingBookingsCount} <span className="text-xs font-semibold text-slate-400">ca</span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Yêu cầu từ học viên</span>
            </div>

            <div
              onClick={() => setActiveTab(2)}
              className="p-3.5 rounded-xl border bg-slate-900/60 border-slate-800 hover:border-slate-700 backdrop-blur-md cursor-pointer transition transform hover:-translate-y-0.5"
            >
              <div className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Khung giờ rảnh</div>
              <div className="text-2xl sm:text-3xl font-black text-emerald-400 mt-1">
                {availableSlotsCount} <span className="text-xs font-semibold text-slate-400">slot</span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Sẵn sàng nhận lịch</span>
            </div>

            <div
              onClick={() => setActiveTab(3)}
              className="p-3.5 rounded-xl border bg-slate-900/60 border-slate-800 hover:border-slate-700 backdrop-blur-md cursor-pointer transition transform hover:-translate-y-0.5"
            >
              <div className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Khóa huấn luyện</div>
              <div className="text-2xl sm:text-3xl font-black text-sky-400 mt-1">
                {courses.length} <span className="text-xs font-semibold text-slate-400">khóa</span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Đang mở giảng dạy</span>
            </div>

            <div
              onClick={() => setActiveTab(4)}
              className="p-3.5 rounded-xl border bg-slate-900/60 border-slate-800 hover:border-slate-700 backdrop-blur-md cursor-pointer transition transform hover:-translate-y-0.5"
            >
              <div className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Học viên đang dạy</div>
              <div className="text-2xl sm:text-3xl font-black text-amber-400 mt-1">
                {enrollments.length} <span className="text-xs font-semibold text-slate-400">người</span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Đang theo học</span>
            </div>

            <div
              onClick={() => {
                setActiveTab(5);
                fetchPtWallet();
              }}
              className="p-3.5 rounded-xl border bg-slate-900/60 border-slate-800 hover:border-slate-700 backdrop-blur-md cursor-pointer transition transform hover:-translate-y-0.5 col-span-2 sm:col-span-1"
            >
              <div className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Số dư ví thù lao</div>
              <div className={`text-xl sm:text-2xl font-black mt-1 ${
                (wallet?.balance ?? 0) < 0 ? 'text-red-400' : 'text-emerald-400'
              }`}>
                {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Rút thù lao 24/7</span>
            </div>
          </div>
        </div>
      </div>

      {/* Prominent Warning Notification Banner if PENDING or REJECTED */}
      {ptProfile?.verificationStatus === 'PENDING' && (
        <div className="bg-amber-950/40 border-b border-amber-500/40 px-4 py-3">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 text-xs text-amber-200">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping shrink-0"></span>
              <span>
                <b>Hồ sơ HLV đang chờ Quản trị viên (Admin) xét duyệt:</b> Bạn vẫn có thể mở trước khung giờ rảnh và tạo khóa học. Sau khi Admin phê duyệt, hồ sơ của bạn sẽ hiển thị công khai trên sàn tìm kiếm cho học viên!
              </span>
            </div>
            <span className="bg-amber-500/20 text-amber-300 border border-amber-500/40 font-bold px-2.5 py-1 rounded-lg text-[11px] shrink-0">
              CHỜ DUYỆT
            </span>
          </div>
        </div>
      )}

      {ptProfile?.verificationStatus === 'REJECTED' && (
        <div className="bg-red-950/50 border-b border-red-500/40 px-4 py-3">
          <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 text-xs text-red-200">
            <div className="flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
              <span>
                <b>Hồ sơ chuyên môn chưa được Admin phê duyệt:</b> Vui lòng vào tab <b>Hồ Sơ</b> để kiểm tra lại chứng chỉ và thông tin chuyên môn.
              </span>
            </div>
            <button
              onClick={() => setActiveTab(6)}
              className="bg-red-600 hover:bg-red-500 text-white font-bold px-3 py-1 rounded-lg text-xs shrink-0 shadow"
            >
              Chỉnh sửa hồ sơ
            </button>
          </div>
        </div>
      )}

      {/* Navigation Tabs Bar */}
      <div className={`${
    isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'
  } border-b sticky top-16 z-20 shadow-xs transition-colors`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 sm:space-x-3 overflow-x-auto py-2.5 no-scrollbar">
            {tabs.map((t, idx) => {
              const Icon = t.icon;
              const isCur = activeTab === idx;
              return (
                <button
                  key={t.label}
                  onClick={() => {
                    setActiveTab(idx);
                    if (idx === 4) fetchPlansAndEnrollments();
                    if (idx === 5) fetchPtWallet();
                  }}
                  className={`flex items-center gap-2 py-2 px-3.5 text-xs sm:text-sm font-bold rounded-xl whitespace-nowrap transition-all ${
                    isCur
                      ? 'bg-red-600 text-white shadow-md shadow-red-900/40'
                      : isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:text-white hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isCur ? 'text-white' : 'text-slate-400'}`} />
                  {t.label}
                  {idx === 1 && pendingBookingsCount > 0 && (
                    <span className={`px-1.5 py-0.5 rounded-full text-[10px] font-black ${
                      isCur ? 'bg-white text-red-600' : 'bg-red-600 text-white animate-pulse'
                    }`}>
                      {pendingBookingsCount}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Body */}
      <main className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full transition-colors ${
    isDark ? 'bg-slate-950 text-slate-100' : 'bg-slate-100 text-slate-900 dark:text-white'
  }`}>
        {/* TAB 0: TỔNG QUAN */}
        {activeTab === 0 && (
          <div className="space-y-6">
            {/* Thẻ Trạng Thái Phê Duyệt Hồ Sơ */}
            {ptProfile && (
              <div className={`p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm ${
                ptProfile.verificationStatus === 'VERIFIED'
                  ? 'bg-emerald-50/90 border-emerald-200 text-emerald-950'
                  : ptProfile.verificationStatus === 'REJECTED'
                  ? 'bg-red-50/90 border-red-200 text-red-950'
                  : 'bg-amber-50/90 border-amber-200 text-amber-950'
              }`}>
                <div className="flex items-start sm:items-center gap-3.5">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold shrink-0 shadow-md ${
                    ptProfile.verificationStatus === 'VERIFIED'
                      ? 'bg-emerald-600 text-white'
                      : ptProfile.verificationStatus === 'REJECTED'
                      ? 'bg-red-600 text-white'
                      : 'bg-amber-500 text-white animate-pulse'
                  }`}>
                    {ptProfile.verificationStatus === 'VERIFIED' ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : ptProfile.verificationStatus === 'REJECTED' ? (
                      <AlertCircle className="w-6 h-6" />
                    ) : (
                      <Clock className="w-6 h-6" />
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-sm font-bold">Trạng Thái Hồ Sơ Chuyên Môn:</h4>
                      <span className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold uppercase border ${
                        ptProfile.verificationStatus === 'VERIFIED'
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : ptProfile.verificationStatus === 'REJECTED'
                          ? 'bg-red-100 text-red-800 border-red-300'
                          : 'bg-amber-100 text-amber-800 border-amber-300'
                      }`}>
                        {ptProfile.verificationStatus === 'VERIFIED'
                          ? '✅ ĐÃ PHÊ DUYỆT (VERIFIED)'
                          : ptProfile.verificationStatus === 'REJECTED'
                          ? '❌ BỊ TỪ CHỐI (REJECTED)'
                          : '⏳ ĐANG CHỜ PHÊ DUYỆT (PENDING)'}
                      </span>
                    </div>
                    <p className="text-xs mt-1 leading-relaxed opacity-90">
                      {ptProfile.verificationStatus === 'VERIFIED'
                        ? 'Hồ sơ chuyên môn của bạn đã được kiểm duyệt hợp lệ! Bạn đang hiển thị công khai trên sàn tìm kiếm để học viên đặt lịch.'
                        : ptProfile.verificationStatus === 'REJECTED'
                        ? 'Hồ sơ chưa đạt yêu cầu kiểm duyệt. Vui lòng vào tab Hồ Sơ để cập nhật lại chứng chỉ hành nghề và thông tin chuyên môn.'
                        : 'Hồ sơ chuyên môn của bạn đang được Quản trị viên (Admin) xét duyệt. Trong thời gian này, bạn vẫn có thể mở trước khung giờ rảnh và tạo khóa học.'}
                    </p>
                  </div>
                </div>

                {ptProfile.verificationStatus === 'PENDING' && (
                  <div className="text-right shrink-0">
                    <span className="text-[11px] font-bold text-amber-900 bg-amber-200/90 px-3 py-1.5 rounded-xl border border-amber-300 block">
                      Admin duyệt tại: admin@ptconnect.vn
                    </span>
                  </div>
                )}
              </div>
            )}

            {/* Quick Action: Pending Bookings needing approval */}
            {pendingBookingsCount > 0 && (
              <div className="bg-white dark:bg-slate-900 rounded-2xl border-2 border-red-500/40 dark:border-red-500/50 shadow-lg p-5 space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-red-600 animate-ping"></span>
                    <h3 className="text-base font-extrabold text-slate-900 dark:text-white uppercase tracking-tight flex items-center gap-2">
                      <Zap className="w-5 h-5 text-red-600" />
                      Yêu Cầu Đặt Lịch Chờ Bạn Duyệt ({pendingBookingsCount})
                    </h3>
                  </div>
                  <button
                    onClick={() => setActiveTab(1)}
                    className="text-xs font-bold text-red-600 hover:text-red-700 flex items-center gap-1"
                  >
                    Xem tất cả trong Quản lý lịch <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="space-y-3">
                  {pendingBookings.slice(0, 3).map((b) => (
                    <div key={b.id} className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-red-100 text-red-700 flex items-center justify-center font-black text-sm">
                          #{b.id}
                        </div>
                        <div>
                          <div className="text-xs font-bold text-slate-900 dark:text-white">
                            Học viên: <span className="text-red-600 font-extrabold">{b.studentName || 'Học viên'}</span>
                            {b.courseTitle && <span className="text-slate-500 dark:text-slate-400 font-normal ml-2">({b.courseTitle})</span>}
                          </div>
                          <div className="text-[11px] text-slate-500 dark:text-slate-400 flex items-center gap-2 mt-0.5">
                            <span>⏰ Thời gian: <b>{formatBookingTime(b.startTime, b.endTime)}</b></span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 self-end sm:self-auto">
                        <button
                          onClick={() => handleRejectBooking(b)}
                          className="px-3 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-100 text-slate-700 dark:text-slate-200 font-bold text-xs transition"
                        >
                          Từ chối
                        </button>
                        <button
                          onClick={() => handleApproveBooking(b)}
                          className="px-4 py-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-extrabold text-xs shadow-sm transition"
                        >
                          ✓ Duyệt Ngay
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upcoming Confirmed Bookings */}
            <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm p-5 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-emerald-600" />
                  Lịch Ca Tập Sắp Diễn Ra ({upcomingConfirmedBookings.length})
                </h3>
                <button
                  onClick={() => setActiveTab(1)}
                  className="text-xs font-bold text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:text-white flex items-center gap-1"
                >
                  Xem toàn bộ <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {upcomingConfirmedBookings.length === 0 ? (
                <div className="text-center py-6 text-slate-500 dark:text-slate-400 text-xs">
                  Chưa có ca tập nào được xác nhận sắp tới. Hãy mở thêm khung giờ rảnh để nhận học viên!
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {upcomingConfirmedBookings.slice(0, 4).map((b) => (
                    <div key={b.id} className="p-3.5 rounded-xl border border-emerald-200/80 bg-emerald-50/40 flex items-center justify-between gap-2">
                      <div>
                        <div className="text-xs font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                          {b.studentName || 'Học viên'}
                          {b.courseTitle && <span className="text-[11px] font-normal text-slate-500 dark:text-slate-400">({b.courseTitle})</span>}
                        </div>
                        <div className="text-[11px] text-slate-600 dark:text-slate-300 mt-0.5">
                          ⏰ {formatBookingTime(b.startTime, b.endTime)}
                        </div>
                      </div>
                      <button
                        onClick={() => handleOpenPtOtpModal(b)}
                        className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm shrink-0 transition"
                      >
                        <Key className="w-3.5 h-3.5" /> Tạo mã OTP
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Operational Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div
                onClick={() => setActiveTab(1)}
                className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm cursor-pointer hover:border-red-400 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase">Ca chờ duyệt</span>
                  <Zap className="w-4 h-4 text-red-500" />
                </div>
                <div className="text-2xl font-black text-red-600 mt-2">
                  {pendingBookingsCount} ca
                </div>
                <span className="text-[11px] text-slate-400 mt-1 block">Bấm để kiểm tra</span>
              </div>

              <div
                onClick={() => setActiveTab(2)}
                className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm cursor-pointer hover:border-emerald-400 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase">Khung giờ mở</span>
                  <Calendar className="w-4 h-4 text-emerald-500" />
                </div>
                <div className="text-2xl font-black text-emerald-600 mt-2">
                  {availableSlotsCount} slot
                </div>
                <span className="text-[11px] text-slate-400 mt-1 block">Sẵn sàng nhận học viên</span>
              </div>

              <div
                onClick={() => setActiveTab(3)}
                className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm cursor-pointer hover:border-sky-400 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase">Khóa huấn luyện</span>
                  <BookOpen className="w-4 h-4 text-sky-500" />
                </div>
                <div className="text-2xl font-black text-sky-600 mt-2">
                  {courses.length} khóa
                </div>
                <span className="text-[11px] text-slate-400 mt-1 block">Chương trình mở bán</span>
              </div>

              <div
                onClick={() => {
                  setActiveTab(5);
                  fetchPtWallet();
                }}
                className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm cursor-pointer hover:border-emerald-400 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase">Ví thù lao</span>
                  <WalletIcon className="w-4 h-4 text-emerald-500" />
                </div>
                <div className={`text-2xl font-black mt-2 ${
                  (wallet?.balance ?? 0) < 0 ? 'text-red-600' : 'text-emerald-600'
                }`}>
                  {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
                </div>
                <span className="text-[11px] text-slate-400 mt-1 block">Rút tiền về ngân hàng</span>
              </div>
            </div>

            {/* Reviews & HFI Standard Banner */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Reviews */}
              <div className="lg:col-span-2 bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                    Đánh Giá Gần Đây Từ Học Viên (5.0/5.0)
                  </h3>
                  <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    100% Hài lòng
                  </span>
                </div>
                <div className="space-y-2.5">
                  <div className="p-3 bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 rounded-xl">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <span className="w-6 h-6 rounded-full bg-orange-100 text-orange-700 flex items-center justify-center font-bold text-[10px]">H</span>
                        Hạnh Hải Đặng
                      </span>
                      <span className="text-amber-500 font-bold flex items-center gap-0.5">
                        ⭐⭐⭐⭐⭐ (5/5 sao)
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 pl-7.5">
                      PT tận tâm, chỉ dẫn từng form động tác rất chuẩn xác, luôn động viên trong từng set tập mệt mỏi!
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-950 border border-slate-100 dark:border-slate-800 rounded-xl">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                        <span className="w-6 h-6 rounded-full bg-sky-100 text-sky-700 flex items-center justify-center font-bold text-[10px]">B</span>
                        Chị Bảo Dương
                      </span>
                      <span className="text-amber-500 font-bold flex items-center gap-0.5">
                        ⭐⭐⭐⭐⭐ (5/5 sao)
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300 mt-1 pl-7.5">
                      PT đến đúng giờ, bài tập đa dạng không bị nhàm chán, sau 1 tháng giảm được 3kg mỡ thừa!
                    </p>
                  </div>
                </div>
              </div>

              {/* HFI Philosophy Card */}
              <div className="relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-red-950 text-white p-5 rounded-2xl border border-red-900/40 shadow-md flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="text-[10px] font-black uppercase tracking-widest text-red-400 flex items-center gap-1">
                    <Flame className="w-3.5 h-3.5 text-red-500" /> TIÊU CHUẨN ĐÀO TẠO FITNESS
                  </div>
                  <h4 className="text-base font-black uppercase italic tracking-tight text-white">
                    KIẾN THỨC CỦA CHÚNG TÔI <br />
                    <span className="text-red-500">KẾT QUẢ CỦA BẠN</span>
                  </h4>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    Nắm vững kiến thức tập luyện, dinh dưỡng khoa học và duy trì kỷ luật cao nhất để mang lại sự thay đổi thực sự cho từng học viên.
                  </p>
                </div>
                <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-400">
                  Đơn vị Đào tạo Fitness Toàn diện — Chuẩn hóa nghề PT Việt Nam
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 1: DUYỆT LỊCH */}
        {activeTab === 1 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Quản Lý & Phê Duyệt Lịch Ca Tập</h3>
            <BookingTable
              bookings={bookings}
              isPtView
              onApprove={handleApproveBooking}
              onReject={handleRejectBooking}
              onCancel={handlePtCancelBooking}
              onGetOtp={handleOpenPtOtpModal}
            />
          </div>
        )}

        {/* TAB 2: KHUNG GIỜ */}
        {activeTab === 2 && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-5 max-w-3xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div>
                  <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-orange-500" />
                    Mở Khung Giờ Rảnh Mới Cho Học Viên Đặt Lịch
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Chọn ngày và khung giờ bạn có thể nhận học viên. Học viên sẽ thấy lịch này để đặt lịch tập.
                  </p>
                </div>
              </div>

              {/* 1. Chọn ngày với phím tắt nhanh */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-200">1. Chọn ngày rảnh:</label>
                  <div className="flex items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => setDateOffset(0)}
                      className="px-2.5 py-1 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg transition"
                    >
                      Hôm nay
                    </button>
                    <button
                      type="button"
                      onClick={() => setDateOffset(1)}
                      className="px-2.5 py-1 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg transition"
                    >
                      Ngày mai
                    </button>
                    <button
                      type="button"
                      onClick={() => setDateOffset(2)}
                      className="px-2.5 py-1 text-xs font-semibold bg-slate-100 hover:bg-slate-200 text-slate-700 dark:text-slate-200 rounded-lg transition"
                    >
                      Ngày kia
                    </button>
                  </div>
                </div>
                <input
                  type="date"
                  value={slotDate}
                  onChange={(e) => setSlotDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 rounded-xl text-sm font-semibold focus:ring-2 focus:ring-orange-500 outline-none"
                />
              </div>

              {/* 2. Chọn nhanh các ca phổ biến (1-chạm) */}
              <div className="space-y-2 pt-1">
                <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block">
                  2. Chọn nhanh ca tập chuẩn (1-chạm tự điền giờ, không cần chọn thủ công):
                </label>

                {/* Ca sáng */}
                <div className="bg-amber-50/50 p-3 rounded-xl border border-amber-200/60">
                  <span className="text-[11px] font-bold text-amber-900 uppercase tracking-wider block mb-1.5">🌅 Buổi sáng:</span>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { start: '07:00', end: '08:00' },
                      { start: '08:00', end: '09:00' },
                      { start: '09:00', end: '10:00' },
                      { start: '10:00', end: '11:00' },
                    ].map((p) => {
                      const isActive = slotStartTime === p.start && slotEndTime === p.end;
                      return (
                        <button
                          key={p.start}
                          type="button"
                          onClick={() => applyTimePreset(p.start, p.end)}
                          className={'px-3 py-1.5 rounded-lg text-xs font-bold transition border ' + (
                            isActive
                              ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
                              : 'bg-white text-amber-900 border-amber-200 hover:bg-amber-100'
                          )}
                        >
                          {p.start} - {p.end}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Ca chiều */}
                <div className="bg-orange-50/50 p-3 rounded-xl border border-orange-200/60">
                  <span className="text-[11px] font-bold text-orange-900 uppercase tracking-wider block mb-1.5">☀️ Buổi chiều:</span>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { start: '14:00', end: '15:00' },
                      { start: '15:00', end: '16:00' },
                      { start: '16:00', end: '17:00' },
                      { start: '17:00', end: '18:00' },
                    ].map((p) => {
                      const isActive = slotStartTime === p.start && slotEndTime === p.end;
                      return (
                        <button
                          key={p.start}
                          type="button"
                          onClick={() => applyTimePreset(p.start, p.end)}
                          className={'px-3 py-1.5 rounded-lg text-xs font-bold transition border ' + (
                            isActive
                              ? 'bg-orange-500 text-white border-orange-600 shadow-sm'
                              : 'bg-white text-orange-900 border-orange-200 hover:bg-orange-100'
                          )}
                        >
                          {p.start} - {p.end}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Ca tối */}
                <div className="bg-indigo-50/50 p-3 rounded-xl border border-indigo-200/60">
                  <span className="text-[11px] font-bold text-indigo-900 uppercase tracking-wider block mb-1.5">🌙 Buổi tối:</span>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { start: '18:00', end: '19:00' },
                      { start: '19:00', end: '20:00' },
                      { start: '20:00', end: '21:00' },
                      { start: '21:00', end: '22:00' },
                    ].map((p) => {
                      const isActive = slotStartTime === p.start && slotEndTime === p.end;
                      return (
                        <button
                          key={p.start}
                          type="button"
                          onClick={() => applyTimePreset(p.start, p.end)}
                          className={'px-3 py-1.5 rounded-lg text-xs font-bold transition border ' + (
                            isActive
                              ? 'bg-indigo-600 text-white border-indigo-700 shadow-sm'
                              : 'bg-white text-indigo-900 border-indigo-200 hover:bg-indigo-100'
                          )}
                        >
                          {p.start} - {p.end}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* 3. Tùy chỉnh giờ bắt đầu & kết thúc bất kỳ */}
              <div className="pt-2 border-t border-slate-100 space-y-3">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block">
                    3. Tùy chỉnh giờ bắt đầu & giờ kết thúc bất kỳ:
                  </label>
                  <span className="text-xs font-bold text-orange-800 bg-orange-50 px-2.5 py-1 rounded-lg border border-orange-200 self-start sm:self-auto">
                    ⏱️ Thời lượng: {getSlotDurationText()}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Ô Giờ bắt đầu */}
                  <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-slate-700 dark:text-slate-200">Giờ bắt đầu:</label>
                      <div className="flex items-center gap-1">
                        {[':00', ':15', ':30', ':45'].map((m) => (
                          <button
                            key={m}
                            type="button"
                            onClick={() => {
                              const [h] = (slotStartTime || '08:00').split(':');
                              handleStartTimeSelect((h || '08') + m);
                            }}
                            className="px-1.5 py-0.5 text-[10px] font-bold bg-white hover:bg-slate-200 border border-slate-200 text-slate-700 dark:text-slate-200 rounded transition"
                            title={'Đặt phút bắt đầu là ' + m}
                          >
                            {m}
                          </button>
                        ))}
                      </div>
                    </div>
                    <input
                      type="time"
                      step={60}
                      value={slotStartTime}
                      onChange={(e) => handleStartTimeSelect(e.target.value)}
                      className="w-full px-3.5 py-2.5 border border-slate-300 rounded-xl text-base font-bold text-slate-900 dark:text-white bg-white focus:ring-2 focus:ring-orange-500 outline-none"
                    />
                  </div>

                  {/* Ô Giờ kết thúc */}
                  <div className="p-3.5 bg-slate-50/80 rounded-xl border border-slate-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-xs font-bold text-slate-700 dark:text-slate-200">Giờ kết thúc:</label>
                      <div className="flex items-center gap-1">
                        {[45, 60, 75, 90, 120].map((mins) => (
                          <button
                            key={mins}
                            type="button"
                            onClick={() => handleDurationSelect(mins)}
                            className="px-1.5 py-0.5 text-[10px] font-bold bg-orange-100 hover:bg-orange-200 border border-orange-200 text-orange-900 rounded transition"
                            title={'Cộng thêm ' + mins + ' phút từ giờ bắt đầu'}
                          >
                            +{mins}p
                          </button>
                        ))}
                      </div>
                    </div>
                    <input
                      type="time"
                      step={60}
                      value={slotEndTime}
                      onChange={(e) => setSlotEndTime(e.target.value)}
                      className="w-full px-3.5 py-2.5 border border-slate-300 rounded-xl text-base font-bold text-slate-900 dark:text-white bg-white focus:ring-2 focus:ring-orange-500 outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Nút xác nhận */}
              <button
                type="button"
                onClick={handleOpenSlot}
                className="w-full py-3 bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 active:scale-[0.99] text-white text-sm font-bold rounded-xl shadow-md flex items-center justify-center gap-2 transition"
              >
                <Plus className="w-5 h-5" /> Mở Khung Giờ: {slotStartTime} - {slotEndTime} ngày {formatSlotDateDisplay(slotDate)} ({getSlotDurationText()})
              </button>
            </div>

            <div>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div>
                  <h4 className="text-base font-bold text-slate-900 dark:text-white">
                    Danh Sách Khung Giờ Đã Thiết Lập ({filteredSlots.length}/{slots.length})
                  </h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Huấn luyện viên tự do tạo lịch rảnh, bấm 🗑️ để xóa lịch trống khi bận đột xuất
                  </p>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  {/* Bộ lọc trạng thái khung giờ */}
                  <div className="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 p-0.5 bg-slate-100 dark:bg-slate-800 text-xs font-semibold">
                    <button
                      type="button"
                      onClick={() => setSlotStatusFilter('ALL')}
                      className={`px-2.5 py-1 rounded-md transition ${slotStatusFilter === 'ALL' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900'}`}
                    >
                      Tất cả ({slots.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => setSlotStatusFilter('AVAILABLE')}
                      className={`px-2.5 py-1 rounded-md transition flex items-center gap-1 ${slotStatusFilter === 'AVAILABLE' ? 'bg-emerald-600 text-white shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-emerald-600'}`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      Đang trống ({availableSlots.length})
                    </button>
                    <button
                      type="button"
                      onClick={() => setSlotStatusFilter('BOOKED')}
                      className={`px-2.5 py-1 rounded-md transition flex items-center gap-1 ${slotStatusFilter === 'BOOKED' ? 'bg-blue-600 text-white shadow-xs' : 'text-slate-600 dark:text-slate-400 hover:text-blue-600'}`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                      Đã đặt ({bookedSlots.length})
                    </button>
                  </div>

                  {/* Nút dọn dẹp các khung giờ trống */}
                  {availableSlots.length > 0 && (
                    <button
                      type="button"
                      disabled={cleaningSlots}
                      onClick={handleClearAvailableSlots}
                      className="px-2.5 py-1.5 text-xs font-bold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg transition flex items-center gap-1 shadow-2xs"
                      title="Xóa toàn bộ khung giờ trống để tự lên lịch mới hoàn toàn"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      {cleaningSlots ? 'Đang dọn dẹp...' : 'Dọn sạch khung giờ trống'}
                    </button>
                  )}
                </div>
              </div>

              {filteredSlots.length === 0 ? (
                <div className="p-8 text-center bg-slate-50 dark:bg-slate-900/40 border border-dashed border-slate-200 dark:border-slate-800 rounded-2xl">
                  <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">
                    {slotStatusFilter === 'AVAILABLE' ? 'Không có khung giờ nào đang trống.' : slotStatusFilter === 'BOOKED' ? 'Chưa có học viên nào đặt lịch trong các khung giờ này.' : 'Chưa có khung giờ nào được thiết lập.'}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">Dùng bảng "Mở Khung Giờ Mới" ở trên để tạo khung giờ rảnh theo lịch của bạn.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[500px] overflow-y-auto pr-1">
                  {filteredSlots.map((s) => (
                    <SlotCard key={s.id} slot={s} onDelete={handleDeleteSlot} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: QUẢN LÝ KHÓA */}
        {activeTab === 3 && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Danh Sách Khóa Học Cố Định</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Tạo khóa học để học viên có thể tìm thấy và mua gói tập</p>
              </div>
              <button
                onClick={() => setShowCreateCourseModal(true)}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-lg shadow-sm flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Tạo Khóa Học Mới
              </button>
            </div>

            {courses.length === 0 ? (
              <div className="bg-white p-8 rounded-xl border border-dashed border-slate-300 text-center text-slate-500 dark:text-slate-400">
                <BookOpen className="w-10 h-10 mx-auto text-slate-400 mb-2" />
                <p className="font-semibold text-slate-700 dark:text-slate-200">Chưa có khóa học nào</p>
                <p className="text-xs text-slate-400 mt-1">Hãy nhấn nút Tạo Khóa Học Mới ở trên để tạo gói tập đầu tiên của bạn.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {courses.map((c) => (
                  <CourseCard
                    key={c.id}
                    course={c}
                    isPtView
                    onToggleStatus={async (course) => {
                      await api.put(`/pt/courses/${course.id}/toggle-status`);
                      showToast('Đã cập nhật trạng thái khóa học!');
                      fetchPtData();
                    }}
                    onDelete={async (course) => {
                      if (confirm('Bạn có chắc chắn muốn xóa khóa học này?')) {
                        await api.delete(`/pt/courses/${course.id}`);
                        showToast('Đã xóa khóa học!');
                        fetchPtData();
                      }
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: GIÁO ÁN */}
        {activeTab === 4 && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white">Quản Lý Giáo Án & Bài Tập Huấn Luyện</h3>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Lên kế hoạch tập luyện chi tiết cho từng học viên theo hợp đồng</p>
              </div>
              <button
                onClick={() => {
                  if (enrollments.length === 0) {
                    showToast('Bạn chưa có học viên nào mua khóa học để tạo giáo án!');
                    return;
                  }
                  setShowCreatePlanModal(true);
                }}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold rounded-lg shadow-sm flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" /> Tạo Giáo Án Mới
              </button>
            </div>

            {/* Thông báo hướng dẫn nghiệp vụ */}
            {enrollments.length === 0 && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-start gap-3 text-amber-800 text-xs sm:text-sm">
                <Info className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <b className="font-semibold">Lưu ý về quy trình tạo giáo án:</b>
                  <p className="mt-1 leading-relaxed">
                    Giáo án huấn luyện gắn liền với <b>Hợp đồng học viên (Enrollment)</b>. Hiện tại bạn chưa có học viên nào mua khóa học.
                    <br />
                    👉 <b>Bước 1:</b> Vào tab <b>Quản Lý Khóa</b> để tạo khóa học.
                    <br />
                    👉 <b>Bước 2:</b> Khi học viên đăng ký mua khóa học của bạn, hệ thống sẽ tự động tạo hợp đồng và bạn có thể lên giáo án chi tiết tại đây!
                  </p>
                </div>
              </div>
            )}

            {/* Danh sách học viên & hợp đồng */}
            {enrollments.length > 0 && (
              <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-4 space-y-3 shadow-xs">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-2">
                    <Users className="w-4 h-4 text-orange-600" />
                    Học viên &amp; Hợp đồng đang phụ trách ({enrollments.filter((e) => e.status === 'ACTIVE').length}/{enrollments.length})
                  </h4>
                  <span className="text-xs text-slate-400">Các khóa học đang có học viên theo học</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {enrollments.map((en) => {
                    const pendingContractDispute = myDisputes.find(
                      (d) => d.enrollmentId === en.id && !d.status?.startsWith('RESOLVED')
                    );
                    const isCancelled = en.status === 'CANCELLED';

                    return (
                      <div
                        key={en.id}
                        className={`p-3.5 rounded-xl border transition flex flex-col justify-between gap-2.5 ${
                          isCancelled
                            ? 'bg-slate-100/70 dark:bg-slate-900/40 border-dashed border-rose-300 dark:border-rose-900/60 opacity-80'
                            : pendingContractDispute
                            ? 'bg-amber-50/40 dark:bg-amber-950/20 border-amber-300 dark:border-amber-700/80'
                            : 'bg-slate-50/50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 hover:border-orange-300'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-bold text-slate-900 dark:text-white text-sm">
                                {en.studentName || 'Học viên'}
                              </span>
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-orange-100 text-orange-800 border border-orange-200">
                                HĐ #{en.id}
                              </span>

                              {/* Trạng thái hợp đồng */}
                              {pendingContractDispute ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-100 text-amber-900 border border-amber-300 flex items-center gap-1 animate-pulse">
                                  ⏳ ĐANG CHỜ BQT THANH LÝ (#CASE-{pendingContractDispute.id})
                                </span>
                              ) : isCancelled ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-rose-100 text-rose-800 border border-rose-300 flex items-center gap-1">
                                  ❌ ĐÃ THANH LÝ (HỦY)
                                </span>
                              ) : en.status === 'COMPLETED' ? (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-blue-100 text-blue-800 border border-blue-200 flex items-center gap-1">
                                  ✓ HOÀN TẤT
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-200">
                                  ✓ ĐANG HIỆU LỰC
                                </span>
                              )}
                            </div>
                            <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                              📚 {en.courseTitle || 'Khóa tập cá nhân'}
                            </div>
                            {en.studentEmail && (
                              <div className="text-[11px] text-slate-400 mt-0.5">
                                ✉️ {en.studentEmail}
                              </div>
                            )}
                          </div>
                          <div className="text-right shrink-0">
                            <div className={`text-xs font-black ${isCancelled ? 'text-slate-400 line-through' : 'text-emerald-600 dark:text-emerald-400'}`}>
                              Còn {en.remainingSessions} / {en.totalSessions} buổi
                            </div>
                            {en.finalPrice !== undefined && en.finalPrice > 0 && (
                              <div className="text-[11px] font-semibold text-slate-500">
                                {Number(en.finalPrice).toLocaleString('vi-VN')} ₫
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Thao tác hành động dưới chân thẻ */}
                        {isCancelled ? (
                          <div className="pt-2 border-t border-rose-200/60 dark:border-rose-900/40 flex items-center justify-between text-xs">
                            <span className="text-rose-600 dark:text-rose-400 font-bold flex items-center gap-1.5">
                              ❌ Hợp đồng đã chấm dứt &amp; quyết toán xong
                            </span>
                            <span className="text-[11px] text-slate-400 italic">Không còn hiệu lực</span>
                          </div>
                        ) : pendingContractDispute ? (
                          <div className="pt-2 border-t border-amber-200/80 dark:border-amber-800/60 flex items-center justify-between text-xs">
                            <span className="text-amber-800 dark:text-amber-300 font-bold flex items-center gap-1.5 text-[11px]">
                              ⏳ Hồ sơ thanh lý đang được Ban Quản Trị thụ lý (#CASE-{pendingContractDispute.id})
                            </span>
                            <button
                              type="button"
                              onClick={() => setActiveTab(6)}
                              className="px-2.5 py-1 text-amber-700 dark:text-amber-300 bg-amber-100 dark:bg-amber-950/60 rounded-lg font-bold hover:underline transition shrink-0"
                            >
                              Xem vụ việc →
                            </button>
                          </div>
                        ) : (
                          <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-700/60 text-xs">
                            <button
                              type="button"
                              onClick={() => {
                                setNewPlan((prev) => ({ ...prev, enrollmentId: en.id }));
                                setShowCreatePlanModal(true);
                              }}
                              className="text-orange-600 dark:text-orange-400 hover:underline font-bold flex items-center gap-1 cursor-pointer"
                            >
                              <Plus className="w-3.5 h-3.5" /> Tạo giáo án
                            </button>
                            <button
                              type="button"
                              onClick={() => handleOpenContractDispute(en)}
                              className="px-2.5 py-1 text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg font-bold border border-rose-200 dark:border-rose-900 transition flex items-center gap-1 cursor-pointer"
                              title="Gửi yêu cầu thanh lý/hủy hợp đồng lên Admin"
                            >
                              <AlertTriangle className="w-3.5 h-3.5" /> Hủy hợp đồng
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Danh sách giáo án */}
            {plans.length === 0 ? (
              <div className="bg-white p-8 rounded-xl border border-dashed border-slate-300 text-center text-slate-500 dark:text-slate-400">
                <ClipboardList className="w-10 h-10 mx-auto text-slate-400 mb-2" />
                <p className="font-semibold text-slate-700 dark:text-slate-200">Chưa có giáo án nào được tạo</p>
                <p className="text-xs text-slate-400 mt-1">
                  {enrollments.length > 0
                    ? 'Hãy nhấn "Tạo Giáo Án Mới" để bắt đầu lên lịch tập cho học viên.'
                    : 'Sau khi có học viên đăng ký, bạn sẽ tạo được giáo án tại đây.'}
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                {plans.map((plan) => (
                  <div key={plan.id} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm overflow-hidden">
                    <div className="p-5 border-b border-slate-100 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-slate-50/60">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-bold text-slate-900 dark:text-white text-base">{plan.title}</h4>
                          <span className="text-xs bg-orange-100 text-orange-800 font-semibold px-2 py-0.5 rounded-full">
                            Hợp đồng #{plan.enrollmentId}
                          </span>
                        </div>
                        <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex flex-wrap gap-4">
                          <span>👤 Học viên: <b className="text-slate-700 dark:text-slate-200">{plan.studentName || 'Chưa rõ'}</b></span>
                          {plan.courseName && <span>📚 Khóa: <b className="text-slate-700 dark:text-slate-200">{plan.courseName}</b></span>}
                          {plan.goal && <span>🎯 Mục tiêu: <b className="text-slate-700 dark:text-slate-200">{plan.goal}</b></span>}
                          {plan.startDate && <span>📅 Thời gian: {plan.startDate} ~ {plan.endDate}</span>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setAddWorkoutPlanId(plan.id)}
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                        >
                          <Plus className="w-3.5 h-3.5" /> Thêm bài tập
                        </button>
                        <button
                          onClick={() => handleDeletePlan(plan.id)}
                          className="p-1.5 text-red-500 hover:bg-red-50 rounded-lg text-xs"
                          title="Xóa giáo án"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    {/* Danh sách bài tập của plan */}
                    <div className="p-5">
                      {(!plan.workouts || plan.workouts.length === 0) ? (
                        <div className="py-4 text-center text-xs text-slate-400 italic">
                          Chưa có bài tập nào trong giáo án này. Hãy nhấn "Thêm bài tập" ở trên.
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                          {plan.workouts.map((w) => (
                            <div key={w.id} className="p-3.5 rounded-lg border border-slate-200 bg-white hover:border-orange-300 transition-colors flex justify-between items-start">
                              <div>
                                <div className="flex items-center gap-1.5">
                                  <Dumbbell className="w-4 h-4 text-orange-600" />
                                  <span className="font-bold text-slate-900 dark:text-white text-sm">{w.exerciseName}</span>
                                </div>
                                <div className="text-xs text-slate-500 dark:text-slate-400 mt-1 space-y-0.5">
                                  <div>Nhóm cơ: <span className="font-medium text-slate-700 dark:text-slate-200">{w.targetMuscle || 'Toàn thân'}</span></div>
                                  <div>Khối lượng: <span className="font-medium text-slate-700 dark:text-slate-200">{w.sets} sets × {w.reps} reps ({w.weightKg || 0} kg)</span></div>
                                  <div>Nghỉ giữa hiệp: <span className="font-medium text-slate-700 dark:text-slate-200">{w.restSeconds}s</span></div>
                                </div>
                                {w.videoDemoUrl && (
                                  <a
                                    href={w.videoDemoUrl}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="inline-block mt-2 text-[11px] text-blue-600 hover:underline font-semibold"
                                  >
                                    Xem video hướng dẫn ↗
                                  </a>
                                )}
                              </div>
                              <button
                                onClick={() => handleDeleteWorkout(plan.id, w.id)}
                                className="text-slate-400 hover:text-red-600 p-1 rounded"
                                title="Xóa bài tập"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: VÍ & THU NHẬP HUẤN LUYỆN VIÊN */}
        {activeTab === 5 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white">Ví Điện Tử & Quản Lý Thu Nhập Huấn Luyện Viên</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                Quản lý dòng tiền thù lao dạy học, nạp tiền bù phạt vi phạm và rút tiền về tài khoản ngân hàng.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* CỘT TRÁI: Số Dư & Nạp Tiền */}
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <h4 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <span className="text-lg">💰</span> Số Dư & Nạp Tiền
                  </h4>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                    {wallet?.status || 'ACTIVE'}
                  </span>
                </div>

                <div className="text-xs text-slate-500 dark:text-slate-400">
                  Chủ tài khoản: <b className="text-slate-800 dark:text-slate-100">{wallet?.ownerName || user.fullName}</b>
                </div>

                {/* SỐ DƯ HIỆN TẠI hoặc NỢ PHẠT */}
                {(wallet?.balance ?? 0) < 0 ? (
                  <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-xs space-y-1">
                    <div className="font-bold text-red-700">ĐANG NỢ TIỀN PHẠT VI PHẠM:</div>
                    <div className="text-3xl font-extrabold text-red-600">
                      -{Math.abs(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
                    </div>
                    <p className="text-red-700 pt-1 leading-relaxed">
                      ⚠️ Bạn đang có khoản nợ phạt do hủy ca tập sát giờ (&lt; 24h). Khoản này sẽ được cấn trừ tự động khi hoàn tất các ca dạy tiếp theo, hoặc bạn có thể nạp bù bên dưới!
                    </p>
                  </div>
                ) : (
                  <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                    <div className="text-xs font-semibold text-emerald-700">SỐ DƯ HIỆN TẠI (Khả dụng):</div>
                    <div className="text-3xl font-extrabold text-emerald-800 mt-1">
                      {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
                    </div>
                    <div className="text-[11px] text-emerald-600 mt-1">
                      Thù lao từ các ca tập đã hoàn tất điểm danh OTP và sẵn sàng rút về ngân hàng.
                    </div>
                  </div>
                )}

                <div className="pt-2">
                  <div className="text-xs font-bold text-slate-800 dark:text-slate-100 mb-2">Nạp tiền vào ví (Mô phỏng):</div>
                  <span className="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Chọn nhanh số tiền cần nạp:</span>
                  <div className="grid grid-cols-4 gap-2 mt-1 mb-3">
                    {[500000, 1000000, 2000000, 5000000].map((amt) => (
                      <button
                        key={amt}
                        type="button"
                        onClick={() => setPtTopupAmount(amt)}
                        className={`py-2 text-xs font-semibold rounded-lg border transition-all ${
                          ptTopupAmount === amt
                            ? 'bg-orange-50 border-orange-500 text-orange-600 font-bold'
                            : 'border-slate-200 text-slate-600 dark:text-slate-300 hover:bg-slate-50'
                        }`}
                      >
                        {amt >= 1000000 ? `${amt / 1000000}Tr` : `${amt / 1000}k`}
                      </button>
                    ))}
                  </div>

                  <div className="space-y-1.5 mb-3">
                    <label className="text-xs text-slate-600 dark:text-slate-300 font-medium block">Hoặc nhập số tiền tùy chọn (VND):</label>
                    <input
                      type="number"
                      min={10000}
                      step={50000}
                      value={ptTopupAmount}
                      onChange={(e) => setPtTopupAmount(Number(e.target.value))}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-orange-500"
                    />
                  </div>

                  <div className="space-y-1.5 mb-4">
                    <label className="text-xs text-slate-600 dark:text-slate-300 font-medium block">Phương thức nạp mô phỏng:</label>
                    <select
                      value={ptTopupMethod}
                      onChange={(e) => setPtTopupMethod(e.target.value)}
                      className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-800 dark:text-slate-100 bg-slate-50 focus:outline-none"
                    >
                      <option value="BANK_TRANSFER">Chuyển khoản VietQR / MoMo</option>
                      <option value="CREDIT_CARD">Thẻ thanh toán quốc tế (Visa/Mastercard)</option>
                      <option value="CASH">Nộp tiền mặt tại quầy lễ tân</option>
                    </select>
                  </div>

                  <button
                    type="button"
                    onClick={handlePtTopup}
                    disabled={ptTopupLoading || ptTopupAmount <= 0}
                    className="w-full py-2.5 bg-[#FF4B4B] hover:bg-[#E03E3E] disabled:opacity-50 text-white text-sm font-bold rounded-xl shadow-sm flex items-center justify-center gap-2 transition-all"
                  >
                    <PlusCircle className="w-4 h-4" /> {ptTopupLoading ? 'Đang nạp...' : `+ Nạp Tiền Vào Ví Ngay (${ptTopupAmount.toLocaleString('vi-VN')} ₫)`}
                  </button>
                </div>
              </div>

              {/* CỘT PHẢI: Rút Tiền Về Ngân Hàng */}
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="pb-3 border-b border-slate-100">
                    <h4 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      <span className="text-lg">🏦</span> Rút Tiền Về Ngân Hàng
                    </h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                      Rút thù lao dạy học tích lũy từ các ca tập đã hoàn thành về tài khoản ngân hàng cá nhân.
                    </p>
                  </div>

                  {(wallet?.balance ?? 0) < 50000 ? (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-xs text-blue-800 flex items-start gap-2 leading-relaxed">
                      <span className="text-base">💡</span>
                      <span>Bạn cần có số dư khả dụng dương (&gt; 50.000 ₫) và không nợ phạt để thực hiện rút tiền.</span>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-700 dark:text-slate-200">Ngân hàng nhận thù lao (*):</label>
                        <select
                          value={ptWithdrawBank}
                          onChange={(e) => setPtWithdrawBank(e.target.value)}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs bg-white focus:ring-2 focus:ring-orange-500"
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
                        <label className="text-xs font-semibold text-slate-700 dark:text-slate-200">Số tài khoản (*):</label>
                        <input
                          type="text"
                          placeholder="Ví dụ: 1903678..."
                          value={ptWithdrawAccount}
                          onChange={(e) => setPtWithdrawAccount(e.target.value)}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs focus:ring-2 focus:ring-orange-500"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-xs font-semibold text-slate-700 dark:text-slate-200">Tên người thụ hưởng (*):</label>
                        <input
                          type="text"
                          placeholder="NGUYEN VAN A"
                          value={ptWithdrawHolder}
                          onChange={(e) => setPtWithdrawHolder(e.target.value.toUpperCase())}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-bold uppercase focus:ring-2 focus:ring-orange-500"
                        />
                      </div>

                      <div className="space-y-1">
                        <div className="flex justify-between items-center text-xs">
                          <label className="font-semibold text-slate-700 dark:text-slate-200">Số tiền rút (VND) (*):</label>
                          <button
                            type="button"
                            onClick={() => setPtWithdrawAmount(Math.max(50000, wallet?.balance || 0))}
                            className="text-[11px] text-orange-600 hover:underline font-semibold"
                          >
                            Rút hết thù lao
                          </button>
                        </div>
                        <input
                          type="number"
                          min={50000}
                          max={wallet?.balance || 0}
                          step={50000}
                          value={ptWithdrawAmount}
                          onChange={(e) => setPtWithdrawAmount(Number(e.target.value))}
                          className="w-full border border-slate-300 rounded-lg px-3 py-2 text-xs font-bold focus:ring-2 focus:ring-orange-500"
                        />
                        <div className="text-[11px] text-slate-400">
                          Tối thiểu: 50.000 ₫ • Tối đa: {(wallet?.balance || 0).toLocaleString('vi-VN')} ₫
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={handlePtWithdraw}
                        disabled={ptWithdrawLoading || ptWithdrawAmount < 50000 || !ptWithdrawAccount.trim() || !ptWithdrawHolder.trim()}
                        className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center justify-center gap-1.5"
                      >
                        {ptWithdrawLoading ? 'Đang xử lý rút tiền...' : `Rút ${ptWithdrawAmount.toLocaleString('vi-VN')} ₫ Về Ngân Hàng`}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Bảng Lịch Sử Giao Dịch Ví Điện Tử */}
            <div className="space-y-3 pt-4 border-t border-slate-200">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                  <span>📜</span> Lịch Sử Giao Dịch Ví Điện Tử
                </h4>
                <button
                  type="button"
                  onClick={fetchPtWallet}
                  className="text-xs text-blue-600 hover:underline flex items-center gap-1"
                >
                  <RotateCcw className="w-3.5 h-3.5" /> Làm mới
                </button>
              </div>

              {!wallet?.transactions || wallet.transactions.length === 0 ? (
                <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 text-center text-xs text-slate-500 dark:text-slate-400">
                  Chưa có giao dịch phát sinh nào trong ví.
                </div>
              ) : (
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-500 dark:text-slate-400 font-semibold uppercase">
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
                          tx.paymentType === 'EARNING' ||
                          tx.paymentType === 'COMPENSATION';
                        return (
                          <tr key={tx.id} className="hover:bg-slate-50/70">
                            <td className="py-3 px-4 font-mono font-semibold text-slate-700 dark:text-slate-200">
                              {tx.transactionRef || `#${tx.id}`}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`font-semibold px-2 py-0.5 rounded-full ${
                                  tx.paymentType === 'EARNING'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : tx.paymentType === 'TOPUP'
                                    ? 'bg-blue-100 text-blue-800'
                                    : tx.paymentType === 'WITHDRAW'
                                    ? 'bg-purple-100 text-purple-800'
                                    : tx.paymentType === 'REFUND'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-slate-100 text-slate-800 dark:text-slate-100'
                                }`}
                              >
                                {tx.paymentType === 'EARNING'
                                  ? 'THÙ LAO DẠY'
                                  : tx.paymentType === 'TOPUP'
                                  ? 'NẠP TIỀN'
                                  : tx.paymentType === 'WITHDRAW'
                                  ? 'RÚT TIỀN'
                                  : tx.paymentType === 'REFUND'
                                  ? 'PHẠT HỦY SÁT GIỜ'
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
                            <td className="py-3 px-4 text-slate-600 dark:text-slate-300">{tx.paymentMethod}</td>
                            <td className="py-3 px-4">
                              <span
                                className={`px-2 py-0.5 rounded-full font-bold ${
                                  tx.status === 'SUCCESS'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : 'bg-slate-100 text-slate-700 dark:text-slate-200'
                                }`}
                              >
                                {tx.status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-slate-500 dark:text-slate-400">
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

        {/* TAB 6: KHIẾU NẠI & TRANH CHẤP CỦA HUẤN LUYỆN VIÊN */}
        {activeTab === 6 && (
          <div className="space-y-6 animate-fade-in">
            {/* Banner giới thiệu */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-8 rounded-3xl shadow-xl border border-indigo-500/20">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-2xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center shrink-0">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-xl sm:text-2xl font-black tracking-tight">Trung Tâm Xử Lý Tranh Chấp Của Huấn Luyện Viên</h3>
                    <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                      Bảo vệ quyền lợi thời gian và thù lao của HLV: Giải quyết sự cố học viên bùng lịch, hủy sát giờ hoặc các khiếu nại liên quan.
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
                💡 <b>Cách khiếu nại ca tập:</b> Vào tab <b>Duyệt Lịch</b>, tại ca tập gặp sự cố (học viên không đến, tranh chấp phí hủy...) nhấn nút <b>⚠️ Khiếu nại</b>. Ban Quản Trị sẽ đối soát và xử lý giải ngân thù lao theo chính sách nền tảng.
              </div>
            </div>

            {/* Danh sách khiếu nại */}
            <div className="space-y-4">
              <h4 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>Hồ sơ tranh chấp liên quan:</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-extrabold">{myDisputes.length} hồ sơ</span>
              </h4>

              {loadingDisputes ? (
                <div className="p-8 text-center text-slate-400 text-xs">Đang kiểm tra hồ sơ tranh chấp...</div>
              ) : myDisputes.length === 0 ? (
                <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-10 text-center space-y-3">
                  <div className="w-14 h-14 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-7 h-7" />
                  </div>
                  <h5 className="font-bold text-slate-900 dark:text-white text-sm">Chưa có tranh chấp nào</h5>
                  <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                    Tất cả các buổi huấn luyện của bạn đều diễn ra thuận lợi và không có khiếu nại nào đang mở.
                  </p>
                  <button
                    onClick={() => setActiveTab(1)}
                    className="mt-2 px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl transition"
                  >
                    Xem Danh Sách Ca Tập
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {myDisputes.map((d) => (
                    <div key={d.id} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-3.5 hover:border-slate-300 dark:hover:border-slate-700 transition">
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100 dark:border-slate-800">
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <span className="font-mono text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-lg border border-indigo-200">
                            #CASE-{d.id}
                          </span>
                          <span className="font-bold text-slate-900 dark:text-white text-sm">{d.disputeTypeLabel}</span>
                          {d.enrollmentId ? (
                            <span className="text-xs text-rose-600 font-semibold bg-rose-50 dark:bg-rose-950/50 px-2 py-0.5 rounded-full border border-rose-200 dark:border-rose-800">
                              • Hợp đồng #{d.enrollmentId}
                            </span>
                          ) : (
                            <span className="text-xs text-slate-400">• Ca tập #{d.bookingId}</span>
                          )}
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

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs bg-slate-50 dark:bg-slate-800/60 p-3 rounded-xl border border-slate-100 dark:border-slate-700">
                        <div>
                          <span className="text-slate-400 block">Học viên liên quan:</span>
                          <span className="font-bold text-slate-800 dark:text-slate-200">{d.studentName}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block">
                            {d.enrollmentId || d.isContractDispute ? 'Quy mô hợp đồng:' : 'Thời gian ca tập:'}
                          </span>
                          <span className="font-medium text-slate-700 dark:text-slate-300">{d.scheduledTime}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 block">
                            {d.enrollmentId || d.isContractDispute ? 'Giá trị còn lại cần quyết toán:' : 'Thù lao ca tập:'}
                          </span>
                          <span className="font-bold text-emerald-600">{Number(d.sessionFee || 0).toLocaleString('vi-VN')} ₫</span>
                        </div>
                      </div>

                      <div>
                        <span className="text-xs font-bold text-slate-700 dark:text-slate-300 block mb-1">
                          {d.complainant === 'PT' ? 'Tường trình khiếu nại của bạn:' : 'Tường trình khiếu nại từ Học Viên:'}
                        </span>
                        {(() => {
                          const raw = d.complainant === 'PT' ? (d.ptStatement || d.summary) : (d.studentStatement || d.summary);
                          const parsed = parseEvidence(raw);
                          return (
                            <div className="space-y-1.5 bg-slate-50/70 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-100 dark:border-slate-700">
                              <p className="text-xs text-slate-600 dark:text-slate-300 italic leading-relaxed">
                                {parsed.cleanText}
                              </p>
                              <EvidenceAttachmentList
                                items={parsed.items}
                                onPreviewImage={(url, name) => setPreviewEvidenceImage({ url, name })}
                              />
                            </div>
                          );
                        })()}
                      </div>

                      {/* Phản biện đối chứng & Thời hạn 48 giờ */}
                      {d.counterStatement ? (
                        <div className="p-3 bg-blue-50/80 dark:bg-blue-950/40 rounded-xl border border-blue-200 dark:border-blue-800 text-xs space-y-1">
                          <span className="font-bold text-blue-900 dark:text-blue-300 block">
                            💬 Phản biện đối chứng {d.complainant === 'PT' ? 'của học viên:' : 'của bạn:'}
                          </span>
                          {(() => {
                            const parsed = parseEvidence(d.counterStatement);
                            return (
                              <div className="space-y-1.5">
                                <p className="italic text-blue-800 dark:text-blue-200 leading-relaxed font-medium">
                                  {parsed.cleanText}
                                </p>
                                <EvidenceAttachmentList
                                  items={parsed.items}
                                  onPreviewImage={(url, name) => setPreviewEvidenceImage({ url, name })}
                                />
                              </div>
                            );
                          })()}
                        </div>
                      ) : !d.status.startsWith('RESOLVED') ? (
                        d.complainant === 'STUDENT' ? (
                          <div className="p-3.5 bg-amber-50 dark:bg-amber-950/40 rounded-xl border border-amber-300 dark:border-amber-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div>
                              <span className="font-bold text-amber-900 dark:text-amber-200 block flex items-center gap-1.5">
                                <Clock className="w-4 h-4 text-amber-500" />
                                Học viên đang khiếu nại ca tập này • Bạn có 48 giờ để gửi phản biện!
                              </span>
                              <span className="text-amber-800 dark:text-amber-300 text-[11px] block mt-0.5">
                                Theo quy chế trọng tài công bằng, bạn có <b>48 giờ</b> để gửi giải trình phản biện. Sau 48 giờ nếu chưa gửi, Admin sẽ có toàn quyền quyết định vụ việc.
                              </span>
                            </div>
                            <button
                              type="button"
                              onClick={() => handleOpenCounterModal(d)}
                              className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold text-xs shrink-0 shadow-xs flex items-center gap-1.5 transition"
                            >
                              <MessageSquare className="w-3.5 h-3.5" /> Gửi phản biện ngay
                            </button>
                          </div>
                        ) : (
                          <div className="p-3 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-600 dark:text-slate-300 flex items-center gap-2">
                            <Clock className="w-4 h-4 text-slate-500 shrink-0" />
                            <div>
                              <span className="font-bold text-slate-800 dark:text-slate-200">Đang chờ học viên gửi phản biện đối chứng (Thời hạn 48 giờ):</span>
                              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">
                                Theo quy chế chống phán quyết độc đoán, Ban Quản Trị phải chờ tối đa 48 tiếng để học viên phản biện đối chất. Nếu sau 48 tiếng học viên không gửi, Admin sẽ có toàn quyền ban hành phán quyết.
                              </p>
                            </div>
                          </div>
                        )
                      ) : null}

                      {d.evidenceNote && (
                        <div className="text-xs text-slate-500 dark:text-slate-400 space-y-1.5 pt-1">
                          <span className="font-semibold text-slate-700 dark:text-slate-200 block">
                            📎 Bằng chứng đính kèm {d.complainant === 'PT' ? 'của bạn (HLV):' : 'từ Học viên:'}
                          </span>
                          {(() => {
                            const parsed = parseEvidence(d.evidenceNote);
                            return (
                              <div className="space-y-1">
                                {parsed.cleanText && <p className="font-medium text-slate-700 dark:text-slate-300">{parsed.cleanText}</p>}
                                <EvidenceAttachmentList
                                  items={parsed.items}
                                  onPreviewImage={(url, name) => setPreviewEvidenceImage({ url, name })}
                                />
                              </div>
                            );
                          })()}
                        </div>
                      )}

                      {/* Evidence Request from Admin */}
                      {d.evidenceRequested && (d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'PT') && (
                        <div className="p-3.5 bg-amber-50 dark:bg-amber-950/40 rounded-xl border border-amber-300 dark:border-amber-800 text-xs space-y-2">
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <span className="font-bold text-amber-950 dark:text-amber-200 flex items-center gap-1.5">
                              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                              Ban Quản Trị yêu cầu HLV bổ sung thêm bằng chứng xác minh vụ việc!
                            </span>
                            <button
                              type="button"
                              onClick={() => handleOpenAdditionalEvidenceModal(d)}
                              className="px-3.5 py-1.5 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold text-xs shrink-0 shadow-xs flex items-center gap-1.5 transition cursor-pointer"
                            >
                              <Upload className="w-3.5 h-3.5" /> Nộp bằng chứng bổ sung
                            </button>
                          </div>
                          <p className="italic text-amber-900 dark:text-amber-300 bg-white/80 dark:bg-slate-900/80 p-2.5 rounded-lg border border-amber-200/80 dark:border-amber-900 text-[11px] leading-relaxed">
                            Lời nhắn từ Admin: {d.evidenceRequestNote}
                          </p>
                          {isEvidenceSubmitted(d, 'PT') ? (
                            <div className="p-2.5 bg-emerald-50 dark:bg-emerald-950/40 rounded-lg border border-emerald-200 dark:border-emerald-800 text-[11px] text-emerald-900 dark:text-emerald-300 space-y-1">
                              <span className="font-extrabold text-emerald-800 dark:text-emerald-300 flex items-center gap-1">
                                ✓ Bằng chứng bổ sung bạn đã nộp cho Admin:
                              </span>
                              {(() => {
                                const parsed = parseEvidence(d.additionalEvidencePt);
                                return (
                                  <>
                                    {parsed.cleanText && <p className="italic">{parsed.cleanText}</p>}
                                    <EvidenceAttachmentList
                                      items={parsed.items}
                                      onPreviewImage={(url, name) => setPreviewEvidenceImage({ url, name })}
                                    />
                                  </>
                                );
                              })()}
                            </div>
                          ) : (
                            <div className="p-2.5 bg-amber-100/70 dark:bg-amber-950/40 rounded-lg text-amber-950 dark:text-amber-200 text-[11px] flex items-center gap-1.5 font-bold border border-amber-300 dark:border-amber-800">
                              <span>⏳ Trạng thái: Ban Quản Trị đang chờ HLV nộp bằng chứng bổ sung cho yêu cầu này.</span>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Phán quyết của Ban Quản Trị */}
                      {d.status.startsWith('RESOLVED') && (
                        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 rounded-2xl space-y-2">
                          <div className="flex items-center gap-2 font-bold text-xs text-emerald-900 dark:text-emerald-300">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                            <span>PHÁN QUYẾT &amp; CĂN CỨ CHÍNH THỨC TỪ BAN QUẢN TRỊ NỀN TẢNG:</span>
                          </div>
                          <p className="text-xs text-emerald-900 dark:text-emerald-200 font-medium leading-relaxed bg-white/80 dark:bg-slate-900/80 p-3 rounded-xl border border-emerald-200/70 dark:border-emerald-800">
                            {d.verdictReason || d.resolutionDecision}
                          </p>
                          {d.resolvedAt && (
                            <div className="text-[11px] text-emerald-700 dark:text-emerald-400 font-medium pt-0.5">
                              Thời gian ban hành phán quyết: {d.resolvedAt}
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
            <PtProfileForm onSaved={showToast} />
          </div>
        )}
      </main>

      {/* Modal: Tạo Khóa Học Mới */}
      {showCreateCourseModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h4 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-orange-600" /> Tạo Khóa Học Huấn Luyện Mới
            </h4>
            <form onSubmit={handleCreateCourse} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Tên khóa học *</label>
                <input
                  type="text"
                  required
                  placeholder="VD: Gói Tăng Cơ Thể Hình 12 Buổi"
                  value={newCourse.title}
                  onChange={(e) => setNewCourse({ ...newCourse, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Mô tả khóa học</label>
                <textarea
                  rows={2}
                  placeholder="Lộ trình chi tiết, đối tượng phù hợp..."
                  value={newCourse.description}
                  onChange={(e) => setNewCourse({ ...newCourse, description: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Tổng số buổi *</label>
                  <input
                    type="number"
                    min={1}
                    required
                    value={newCourse.totalSessions}
                    onChange={(e) => setNewCourse({ ...newCourse, totalSessions: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Thời hạn (ngày) *</label>
                  <input
                    type="number"
                    min={1}
                    required
                    value={newCourse.validityDays}
                    onChange={(e) => setNewCourse({ ...newCourse, validityDays: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Học phí trọn gói (VNĐ) *</label>
                <input
                  type="number"
                  min={0}
                  step={50000}
                  required
                  value={newCourse.basePrice}
                  onChange={(e) => setNewCourse({ ...newCourse, basePrice: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-orange-600"
                />
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateCourseModal(false)}
                  className="flex-1 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-slate-600 dark:text-slate-300"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-semibold"
                >
                  Tạo khóa học
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Tạo Giáo Án Mới */}
      {showCreatePlanModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h4 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <ClipboardList className="w-5 h-5 text-orange-600" /> Tạo Giáo Án Luyện Tập Mới
            </h4>
            <form onSubmit={handleCreatePlan} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Chọn Hợp Đồng Học Viên *</label>
                <select
                  required
                  value={newPlan.enrollmentId}
                  onChange={(e) => setNewPlan({ ...newPlan, enrollmentId: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                >
                  <option value={0}>-- Chọn hợp đồng học viên --</option>
                  {enrollments.filter((e) => e.status === 'ACTIVE').map((e) => (
                    <option key={e.id} value={e.id}>
                      HĐ #{e.id} - {e.studentName || 'Học viên'} ({e.courseTitle})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Tiêu đề giáo án *</label>
                <input
                  type="text"
                  required
                  placeholder="VD: Giáo án siết cơ - 4 tuần đầu"
                  value={newPlan.title}
                  onChange={(e) => setNewPlan({ ...newPlan, title: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Mục tiêu huấn luyện</label>
                <input
                  type="text"
                  placeholder="VD: Tăng cơ ngực, giảm mỡ đùi, form chuẩn Squat..."
                  value={newPlan.goal}
                  onChange={(e) => setNewPlan({ ...newPlan, goal: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Ngày bắt đầu</label>
                  <input
                    type="date"
                    value={newPlan.startDate}
                    onChange={(e) => setNewPlan({ ...newPlan, startDate: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Ngày kết thúc</label>
                  <input
                    type="date"
                    value={newPlan.endDate}
                    onChange={(e) => setNewPlan({ ...newPlan, endDate: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreatePlanModal(false)}
                  className="flex-1 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-slate-600 dark:text-slate-300"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg text-sm font-semibold"
                >
                  Tạo giáo án
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Thêm Bài Tập Vào Giáo Án */}
      {addWorkoutPlanId !== null && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h4 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Dumbbell className="w-5 h-5 text-orange-600" /> Thêm Bài Tập Mới Vào Giáo Án
            </h4>
            <form onSubmit={handleAddWorkout} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Tên bài tập *</label>
                <input
                  type="text"
                  required
                  placeholder="VD: Barbell Bench Press"
                  value={newWorkout.exerciseName}
                  onChange={(e) => setNewWorkout({ ...newWorkout, exerciseName: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Nhóm cơ tác động</label>
                <input
                  type="text"
                  placeholder="VD: Ngực, Vai, Đùi trước..."
                  value={newWorkout.targetMuscle}
                  onChange={(e) => setNewWorkout({ ...newWorkout, targetMuscle: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                />
              </div>

              <div className="grid grid-cols-3 gap-2">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Số hiệp (Sets) *</label>
                  <input
                    type="number"
                    min={1}
                    required
                    value={newWorkout.sets}
                    onChange={(e) => setNewWorkout({ ...newWorkout, sets: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Số lần (Reps) *</label>
                  <input
                    type="number"
                    min={1}
                    required
                    value={newWorkout.reps}
                    onChange={(e) => setNewWorkout({ ...newWorkout, reps: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Mức tạ (kg)</label>
                  <input
                    type="number"
                    min={0}
                    step={0.5}
                    value={newWorkout.weightKg}
                    onChange={(e) => setNewWorkout({ ...newWorkout, weightKg: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Thời gian nghỉ (giây) *</label>
                  <input
                    type="number"
                    min={0}
                    step={10}
                    required
                    value={newWorkout.restSeconds}
                    onChange={(e) => setNewWorkout({ ...newWorkout, restSeconds: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-600 dark:text-slate-300 mb-1">Video minh họa (URL)</label>
                  <input
                    type="url"
                    placeholder="https://youtube.com/..."
                    value={newWorkout.videoDemoUrl}
                    onChange={(e) => setNewWorkout({ ...newWorkout, videoDemoUrl: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setAddWorkoutPlanId(null)}
                  className="flex-1 py-2 border border-slate-300 rounded-lg text-sm font-semibold text-slate-600 dark:text-slate-300"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold"
                >
                  Lưu bài tập
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Counter Statement Modal for PT */}
      {counterDisputeModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-scale-up border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <div className="flex items-center gap-2 text-indigo-600">
                <MessageSquare className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
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
              <div className="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-xs space-y-1">
                <span className="font-bold text-amber-900 dark:text-amber-300 block">Khiếu nại từ Học viên {counterDisputeModal.studentName}:</span>
                <p className="italic text-amber-800 dark:text-amber-200">
                  {(counterDisputeModal.studentStatement || counterDisputeModal.summary || '').replace(/^["“”']+|["“”']+$/g, '')}
                </p>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                  Bản tường trình phản biện của HLV <span className="text-red-500">*</span>:
                </label>
                <textarea
                  rows={4}
                  value={counterStatementText}
                  onChange={(e) => {
                    setCounterStatementText(e.target.value);
                    if (counterError) setCounterError(null);
                  }}
                  placeholder="Giải trình cụ thể: Lý do khách quan, sự cố phương tiện/thời tiết hoặc làm rõ nội dung phản ánh..."
                  className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              {/* Tải ảnh bằng chứng đối chứng */}
              <MultiImageUploader
                files={counterFiles}
                onChange={setCounterFiles}
                label="Ảnh chụp bằng chứng đối chứng (không bắt buộc)"
                subLabel="Hỗ trợ chọn nhiều ảnh (Ảnh quầy lễ tân, lịch sử gọi điện, tin nhắn...)"
              />

              {counterError && (
                <div className="p-2.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl text-xs text-red-700 dark:text-red-300">
                  ⚠️ {counterError}
                </div>
              )}

              <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-normal">
                💡 Bản phản biện của bạn sẽ được chuyển thẳng đến Hội đồng Trọng tài để đối soát hai chiều trước khi ban hành phán quyết. <b>Lưu ý:</b> Bạn có 48 giờ để gửi phản biện; nếu quá 48 giờ bạn chưa gửi, Ban Quản Trị sẽ có toàn quyền ban hành phán quyết.
              </p>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setCounterDisputeModal(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
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

      {/* Quick Dispute Modal for PT */}
      {showTabDisputeModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-scale-up border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <div className="flex items-center gap-2.5 text-amber-600">
                <ShieldAlert className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900 dark:text-white">Gửi Hồ Sơ Tranh Chấp Lên Ban Quản Trị</h4>
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
                <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                  Chọn ca tập bạn muốn báo cáo:
                </label>
                {bookings.filter(b => b.status !== 'PENDING').length === 0 ? (
                  <div className="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-xs text-amber-800 dark:text-amber-300">
                    ⚠️ Bạn chưa có ca tập nào (đã xác nhận, hoàn thành hoặc hủy) để báo cáo.
                  </div>
                ) : (
                  <select
                    value={tabDisputeBookingId || ''}
                    onChange={(e) => setTabDisputeBookingId(Number(e.target.value))}
                    className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                  >
                    {bookings
                      .filter(b => b.status !== 'PENDING')
                      .map((b) => (
                        <option key={b.id} value={b.id}>
                          Ca #{b.id} ({b.status}) - Học viên: {b.studentName || 'Học viên'} ({formatBookingTime(b.startTime, b.endTime)})
                        </option>
                      ))}
                  </select>
                )}
              </div>

              {/* Chọn lý do khiếu nại */}
              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">Lý do khiếu nại:</label>
                <select
                  value={tabDisputeType}
                  onChange={(e) => {
                    const val = e.target.value;
                    setTabDisputeType(val);
                    const sel = ptDisputeReasonOptions.find(r => r.value === val);
                    if (sel) setTabDisputeSeverity(sel.severity);
                  }}
                  className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                >
                  {ptDisputeReasonOptions.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </div>

              {/* Tường trình chi tiết */}
              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                  Tường trình sự việc của HLV <span className="text-red-500">*</span>:
                </label>
                <textarea
                  rows={3}
                  value={tabDisputeStatement}
                  onChange={(e) => {
                    setTabDisputeStatement(e.target.value);
                    if (tabDisputeError) setTabDisputeError(null);
                  }}
                  placeholder="Mô tả cụ thể sự việc: bạn đã đến phòng tập lúc mấy giờ, học viên bùng lịch không đến, yêu cầu giải ngân thù lao..."
                  className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              {/* Bằng chứng bằng cách tải ảnh lên */}
              <div>
                <MultiImageUploader
                  files={tabDisputeFiles}
                  onChange={setTabDisputeFiles}
                  label="Ảnh chụp bằng chứng đối chứng (không bắt buộc)"
                  subLabel="Hỗ trợ chọn nhiều ảnh cùng lúc (Ảnh check-in phòng tập, lịch sử gọi điện, tin nhắn...)"
                />

                <input
                  type="text"
                  value={tabDisputeEvidence}
                  onChange={(e) => setTabDisputeEvidence(e.target.value)}
                  placeholder="Ghi chú thêm về ảnh (VD: Lịch sử tin nhắn gọi cho học viên lúc giờ tập, ảnh tại phòng tập...)"
                  className="w-full mt-2 p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              {tabDisputeError && (
                <div className="p-2.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-xs text-red-700 dark:text-red-300">
                  ⚠️ {tabDisputeError}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowTabDisputeModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
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
                  {tabDisputeSubmitting ? 'Đang gửi...' : 'Gửi tranh chấp lên Admin'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal: Nộp Bằng Chứng Bổ Sung Theo Yêu Cầu Admin cho PT */}
      {additionalEvidenceModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl animate-scale-up border border-slate-200 dark:border-slate-800">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <div className="flex items-center gap-2.5 text-amber-600">
                <Upload className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  Nộp Bằng Chứng Bổ Sung (#CASE-{additionalEvidenceModal.id})
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setAdditionalEvidenceModal(null)}
                className="p-1 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3.5">
              <div className="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-xl text-xs space-y-1">
                <span className="font-bold text-amber-900 dark:text-amber-300 block">Yêu cầu từ Quản Trị Viên:</span>
                <p className="italic text-amber-800 dark:text-amber-200 leading-relaxed font-medium">
                  {additionalEvidenceModal.evidenceRequestNote || 'Ban Quản Trị yêu cầu bổ sung bằng chứng để đối chiếu và đưa ra phán quyết công bằng.'}
                </p>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-700 dark:text-slate-200 block mb-1">
                  Nội dung giải trình bổ sung:
                </label>
                <textarea
                  rows={3}
                  value={additionalEvidenceText}
                  onChange={(e) => {
                    setAdditionalEvidenceText(e.target.value);
                    if (additionalEvidenceError) setAdditionalEvidenceError(null);
                  }}
                  placeholder="Nhập nội dung giải thích, chú thích thêm về hình ảnh hoặc chứng từ đối chiếu..."
                  className="w-full p-2.5 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>

              {/* Tải ảnh bổ sung */}
              <MultiImageUploader
                files={additionalEvidenceFiles}
                onChange={setAdditionalEvidenceFiles}
                label="Hình ảnh bằng chứng đính kèm"
                subLabel="Hỗ trợ chọn nhiều ảnh (Ảnh cuộc gọi, tin nhắn, định vị check-in, chứng từ...)"
              />

              {additionalEvidenceError && (
                <div className="p-2.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-xs text-red-700 dark:text-red-300">
                  ⚠️ {additionalEvidenceError}
                </div>
              )}

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setAdditionalEvidenceModal(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  Hủy bỏ
                </button>
                <button
                  type="button"
                  disabled={additionalEvidenceSubmitting}
                  onClick={handleSubmitAdditionalEvidence}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  {additionalEvidenceSubmitting ? 'Đang gửi...' : 'Nộp bằng chứng lên Admin'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PT OTP Generator Modal */}
      {ptOtpModalBooking && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-md w-full p-6 text-center shadow-2xl animate-scale-up">
            <div className="w-14 h-14 bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400 rounded-2xl flex items-center justify-center mx-auto mb-3 shadow-inner">
              <Key className="w-7 h-7" />
            </div>
            
            <h4 className="text-xl font-bold text-slate-900 dark:text-white">Mã OTP Điểm Danh Ca Tập #{ptOtpModalBooking.id}</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Cung cấp mã OTP này cho học viên để học viên nhập vào điểm danh
            </p>

            <div className="my-4 bg-slate-50 dark:bg-slate-800/60 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700 text-left text-xs space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Học viên:</span>
                <span className="font-bold text-slate-900 dark:text-white">{ptOtpModalBooking.studentName || 'Học viên'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500 dark:text-slate-400">Thời gian:</span>
                <span className="font-medium text-slate-800 dark:text-slate-200">{formatBookingTime(ptOtpModalBooking.startTime, ptOtpModalBooking.endTime)}</span>
              </div>
              {ptOtpModalBooking.courseTitle && (
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-slate-400">Khóa học:</span>
                  <span className="text-slate-700 dark:text-slate-300">{ptOtpModalBooking.courseTitle}</span>
                </div>
              )}
            </div>

            {ptOtpLoading ? (
              <div className="py-8 text-center text-slate-500">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <span className="text-xs">Đang khởi tạo mã OTP ca tập...</span>
              </div>
            ) : ptOtpError ? (
              <div className="my-4 p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl text-left text-xs text-red-700 dark:text-red-300">
                <p className="font-bold">⚠️ Chưa thể tạo mã OTP:</p>
                <p className="mt-1 leading-relaxed">{ptOtpError}</p>
              </div>
            ) : (
              <>
                <div className="relative my-4">
                  <div className="text-4xl font-mono font-black tracking-[0.25em] text-blue-600 dark:text-blue-400 bg-blue-50/80 dark:bg-blue-950/40 py-4 px-6 rounded-2xl border-2 border-blue-200 dark:border-blue-800 shadow-inner select-all">
                    {ptGeneratedOtp}
                  </div>
                  <div className="mt-1.5 text-[11px] text-slate-400 flex items-center justify-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> Mã có hiệu lực trong 30 phút
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mb-4">
                  <button
                    type="button"
                    onClick={() => ptGeneratedOtp && handleCopyPtOtp(ptGeneratedOtp)}
                    className="py-2.5 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition"
                  >
                    {ptOtpCopied ? (
                      <>
                        <CheckCircle className="w-4 h-4 text-emerald-600" />
                        <span className="text-emerald-600">Đã sao chép!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        <span>Sao chép mã</span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => ptGeneratedOtp && handleSendOtpViaChat(ptOtpModalBooking, ptGeneratedOtp)}
                    className="py-2.5 px-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 shadow-sm transition"
                  >
                    <MessageSquare className="w-4 h-4" />
                    <span>Gửi qua Chat</span>
                  </button>
                </div>

                <div className="p-3 bg-amber-50 dark:bg-amber-950/30 border border-amber-200/80 dark:border-amber-900 rounded-xl text-left text-[11px] text-amber-800 dark:text-amber-300 leading-relaxed mb-4">
                  <span className="font-bold">💡 Hướng dẫn nghiệp vụ:</span> Đọc mã OTP 6 chữ số này hoặc nhấn Gửi qua Chat cho học viên. Học viên sẽ nhập mã trên màn hình của họ để xác nhận điểm danh. Sau khi học viên xác nhận, ca tập sẽ chuyển thành <b>ĐÃ HOÀN THÀNH</b> và tiền sẽ được chuyển vào ví của bạn.
                </div>

                {/* Hỗ trợ điểm danh thay nếu học viên gặp sự cố thiết bị */}
                <div className="text-right mb-2">
                  <button
                    type="button"
                    onClick={() => ptGeneratedOtp && handlePtDirectConfirm(ptOtpModalBooking, ptGeneratedOtp)}
                    className="text-[11px] text-slate-400 hover:text-blue-600 underline cursor-pointer"
                  >
                    Học viên không mang điện thoại / nhờ điểm danh thay? Bấm vào đây
                  </button>
                </div>
              </>
            )}

            <button
              type="button"
              onClick={() => {
                setPtOtpModalBooking(null);
                setPtOtpError(null);
              }}
              className="w-full py-2.5 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            >
              Đóng hộp thoại
            </button>
          </div>
        </div>
      )}

      {/* Modal phóng to xem ảnh đối chứng */}
      {previewEvidenceImage && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-150"
          onClick={() => setPreviewEvidenceImage(null)}
        >
          <div
            className="relative max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 rounded-2xl overflow-hidden p-3 shadow-2xl border border-slate-200 dark:border-slate-800"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-center px-4 py-2 border-b border-slate-100 dark:border-slate-800">
              <h4 className="font-bold text-slate-800 dark:text-white text-sm truncate max-w-[70vw]">
                📷 Ảnh đối chứng: {previewEvidenceImage.name}
              </h4>
              <button
                type="button"
                onClick={() => setPreviewEvidenceImage(null)}
                className="p-1 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 hover:text-slate-700 dark:hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-3 flex items-center justify-center max-h-[75vh] overflow-auto bg-slate-950/5 dark:bg-slate-950/40 rounded-xl">
              <img
                src={previewEvidenceImage.url}
                alt={previewEvidenceImage.name}
                onError={(e) => {
                  const target = e.currentTarget as HTMLImageElement;
                  if (target.src && !target.src.includes('topology.jpg')) {
                    target.src = '/uploads/disputes/topology.jpg';
                  }
                }}
                className="max-h-[70vh] w-auto object-contain rounded-lg shadow-sm"
              />
            </div>
            <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between text-xs text-slate-500">
              <span>Bấm phím Esc hoặc bấm ra ngoài để đóng</span>
              <a
                href={previewEvidenceImage.url}
                target="_blank"
                rel="noreferrer"
                className="text-orange-600 dark:text-orange-400 hover:underline flex items-center gap-1 font-semibold"
              >
                Mở tab mới
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Modal Yêu Cầu Hủy Hợp Đồng Khóa Học từ PT */}
      {contractDisputeModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-in fade-in zoom-in-95 my-8">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-rose-600">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <h4 className="text-base font-bold text-slate-900 dark:text-white">
                  Yêu Cầu Hủy Hợp Đồng Khóa Học #{contractDisputeModal.id}
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setContractDisputeModal(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs">
              <div className="p-3 bg-rose-50 dark:bg-rose-950/40 rounded-xl border border-rose-200 dark:border-rose-900 text-rose-900 dark:text-rose-200 space-y-1">
                <div className="font-bold flex items-center justify-between">
                  <span>Khóa học: {contractDisputeModal.courseTitle}</span>
                  <span className="text-rose-600 font-extrabold">Còn {contractDisputeModal.remainingSessions}/{contractDisputeModal.totalSessions} buổi</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-600 dark:text-slate-400">
                  <span>Học viên: <b>{contractDisputeModal.studentName || 'Học viên'}</b></span>
                  <span>Tổng giá trị HĐ: {Number(contractDisputeModal.finalPrice || 0).toLocaleString('vi-VN')} ₫</span>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Lý do đề nghị hủy/thanh lý hợp đồng <span className="text-red-500">*</span>:
                </label>
                <select
                  value={contractDisputeReason}
                  onChange={(e) => setContractDisputeReason(e.target.value)}
                  className="w-full p-2.5 border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-medium focus:ring-2 focus:ring-rose-500 outline-none"
                >
                  {ptContractDisputeReasonOptions.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Trình bày chi tiết lý do &amp; bối cảnh vụ việc <span className="text-red-500">*</span>:
                </label>
                <textarea
                  rows={4}
                  value={contractDisputeStatement}
                  onChange={(e) => {
                    setContractDisputeStatement(e.target.value);
                    if (contractDisputeError) setContractDisputeError(null);
                  }}
                  placeholder="Nêu rõ quá trình liên hệ, số buổi đã hoàn thành, sự cố phát sinh khiến bạn không thể tiếp tục giảng dạy gói hợp đồng này..."
                  className="w-full p-3 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-rose-500 font-normal leading-relaxed"
                  required
                />
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Hình ảnh bằng chứng đính kèm (Tin nhắn, lịch sử cuộc gọi, giấy tờ y tế...):
                </label>
                <MultiImageUploader
                  files={contractDisputeFiles}
                  onChange={setContractDisputeFiles}
                  maxFiles={6}
                  subLabel="Ảnh chụp màn hình tin nhắn, biên bản làm việc hoặc tài liệu minh chứng"
                />
              </div>

              {contractDisputeError && (
                <div className="p-3 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl text-red-700 dark:text-red-300 text-xs">
                  ⚠️ {contractDisputeError}
                </div>
              )}

              <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200 dark:border-slate-700 text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                💡 <b>Lưu ý trọng tài:</b> Sau khi gửi, hồ sơ sẽ được chuyển tới Ban Quản Trị nền tảng. Admin sẽ đối soát số buổi thực tế và ra quyết định thanh toán thù lao các buổi hợp lệ cho PT hoặc bồi hoàn cho học viên theo quy chế hợp đồng.
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setContractDisputeModal(null)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl font-semibold transition cursor-pointer"
                >
                  Đóng
                </button>
                <button
                  type="button"
                  onClick={handleSubmitContractDispute}
                  disabled={contractDisputeSubmitting}
                  className="px-5 py-2.5 bg-rose-600 hover:bg-rose-700 disabled:opacity-50 text-white font-bold rounded-xl shadow-md transition flex items-center gap-1.5 cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  {contractDisputeSubmitting ? 'Đang gửi...' : 'Gửi yêu cầu hủy hợp đồng lên Admin'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast Alert với z-[9999] để không bao giờ bị mờ hay che khuất */}
      {toastMsg && (
        <div className="fixed bottom-5 right-5 z-[9999] bg-slate-900/95 text-white px-4 py-3 rounded-xl shadow-2xl text-sm flex items-center gap-2 border border-slate-700 backdrop-blur-md">
          <span>{toastMsg}</span>
        </div>
      )}
    </div>
  );
};
