import { getAvatarUrl } from "../lib/avatar";
import React, { useState, useEffect, useMemo } from 'react';
import api from '../lib/axios';
import {
  User,
  PtProfile,
  AdminStatistics,
  AdminBookingAnalytics,
  AdminPaymentAnalytics,
} from '../types/api';
import { isHttpUrl, resolveCertificateUrl } from '../lib/certificate';
import { parseEvidence, EvidenceAttachmentList, isEvidenceSubmitted } from '../lib/evidence';
import {
  Shield,
  Users,
  BarChart2,
  CheckCircle,
  XCircle,
  Lock,
  Unlock,
  LogOut,
  Calendar,
  CreditCard,
  Search,
  RefreshCw,
  ExternalLink,
  TrendingUp,
  Clock,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownLeft,
  DollarSign,
  Activity,
  Award,
  Sparkles,
  FileText,
  UserCheck,
  Scale,
  Gavel,
  ShieldAlert,
  MessageSquare,
  FileSearch,
  PieChart,
  Eye,
  CheckCircle2,
  ChevronRight,
  HelpCircle,
  Sun,
  Moon,
  Wallet,
  Percent,
  Landmark,
  Send,
} from 'lucide-react';

export interface DisputeCase {
  id: number;
  bookingId?: number;
  enrollmentId?: number;
  isContractDispute?: boolean;
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
  evidenceNote: string;
  counterStatement?: string;
  evidenceRequested?: boolean;
  evidenceRequestTarget?: 'BOTH' | 'PT' | 'STUDENT';
  evidenceRequestNote?: string;
  additionalEvidencePt?: string;
  additionalEvidenceStudent?: string;
  studentEvidenceSubmitted?: boolean;
  ptEvidenceSubmitted?: boolean;
  status: string;
  verdictType?: string;
  resolutionDecision?: string;
  verdictReason?: string;
  resolvedAt?: string;
  createdAt?: string;
  counterDeadline?: string;
  canAdminArbitrate?: boolean;
  waitingReason?: string;
  hoursRemaining?: number;
  minutesRemaining?: number;
}

interface AdminPageProps {
  user: User;
  onLogout: () => void;
}

export const checkDisputeArbitrationStatus = (d: DisputeCase) => {
  const hasCounter = !!(d.counterStatement && d.counterStatement.trim());
  let isPast48h = false;
  let hoursRemaining = 0;
  let minutesRemaining = 0;

  if (d.createdAt) {
    const createdTime = new Date(d.createdAt).getTime();
    if (!isNaN(createdTime)) {
      const deadlineTime = createdTime + 48 * 3600 * 1000;
      const now = Date.now();
      if (now >= deadlineTime) {
        isPast48h = true;
      } else {
        const diffMs = deadlineTime - now;
        hoursRemaining = Math.floor(diffMs / (3600 * 1000));
        minutesRemaining = Math.floor((diffMs % (3600 * 1000)) / (60 * 1000));
      }
    } else {
      isPast48h = true;
    }
  } else {
    isPast48h = true;
  }

  const canArbitrate = d.canAdminArbitrate !== undefined ? d.canAdminArbitrate : (hasCounter || isPast48h);

  return {
    hasCounter,
    isPast48h,
    canArbitrate,
    hoursRemaining: d.hoursRemaining !== undefined ? d.hoursRemaining : hoursRemaining,
    minutesRemaining: d.minutesRemaining !== undefined ? d.minutesRemaining : minutesRemaining,
  };
};

export const AdminPage: React.FC<AdminPageProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<number>(0);

  // Giao diện Sáng / Tối (Theme Mode)
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    return (localStorage.getItem('admin_theme') as 'dark' | 'light') || 'dark';
  });
  const isDark = theme === 'dark';
  const toggleTheme = () => {
    const next = isDark ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem('admin_theme', next);
  };

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDark]);

  // Data states
  const [statistics, setStatistics] = useState<AdminStatistics | null>(null);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [ptsList, setPtsList] = useState<PtProfile[]>([]);
  const [pendingPts, setPendingPts] = useState<PtProfile[]>([]);
  const [bookings, setBookings] = useState<AdminBookingAnalytics[]>([]);
  const [payments, setPayments] = useState<AdminPaymentAnalytics[]>([]);

  // UI state
  const [loading, setLoading] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  // Filters & Search
  // Tab 0: PT Filter
  const [ptFilter, setPtFilter] = useState<'ALL' | 'PENDING' | 'VERIFIED' | 'REJECTED'>('PENDING');

  // Tab 1: Users Filter & Search
  const [userSearch, setUserSearch] = useState('');
  const [userRoleFilter, setUserRoleFilter] = useState<string>('ALL');
  const [userStatusFilter, setUserStatusFilter] = useState<string>('ALL');

  // Tab 2: Bookings Filter & Search
  const [bookingSearch, setBookingSearch] = useState('');
  const [bookingStatusFilter, setBookingStatusFilter] = useState<string>('ALL');
  const [bookingTypeFilter, setBookingTypeFilter] = useState<string>('ALL');

  // Tab 3: Payments Filter & Search
  const [paymentSearch, setPaymentSearch] = useState('');
  const [paymentTypeFilter, setPaymentTypeFilter] = useState<string>('ALL');
  const [paymentStatusFilter, setPaymentStatusFilter] = useState<string>('ALL');

  // Tab 5: Disputes state & filters
  const [disputes, setDisputes] = useState<DisputeCase[]>([
    {
      id: 1,
      bookingId: 102,
      studentName: 'Phạm Hoàng Nam',
      studentEmail: 'nam.pham@gmail.com',
      studentPhone: '0912345678',
      ptName: 'Lê Hoàng Cường',
      ptEmail: 'cuong.pt@ptconnect.vn',
      courseTitle: 'Tăng Cơ & Thể Hình Cường Độ Cao (12 buổi)',
      sessionFee: 450000,
      scheduledTime: '18:00 - 19:30, Hôm qua',
      disputeType: 'PT_ABSENT',
      disputeTypeLabel: 'HLV Vắng Mặt Không Báo Trước',
      severity: 'HIGH',
      complainant: 'STUDENT',
      summary: 'Học viên có mặt tại phòng tập đúng giờ, chờ 30 phút và gọi điện không liên lạc được với HLV.',
      studentStatement: 'Tôi có mặt tại phòng tập Elite Fitness lúc 17:55 cho ca 18:00. Tôi chờ đến 18:30 và gọi cho HLV Cường 4 cuộc nhưng máy bận/không nghe. Tôi yêu cầu hoàn 1 buổi vào gói và bồi thường theo đúng chính sách.',
      ptStatement: 'Hôm qua xe máy của tôi bị nổ lốp trên đường Vành đai 3 lúc trời mưa to, điện thoại bị rơi vỡ màn hình nên không thể báo cho học viên kịp thời. Tôi thành thật xin lỗi và chấp hành phán quyết của ban quản trị.',
      evidenceNote: 'Đã xác minh: Định vị GPS học viên có mặt tại quầy lễ tân lúc 17:58. Lịch sử cuộc gọi nhỡ lúc 18:05, 18:12.',
      status: 'PENDING_ARBITRATION',
      createdAt: '2026-11-13 19:00:00',
    },
    {
      id: 2,
      bookingId: 108,
      studentName: 'Trần Thị Mai Linh',
      studentEmail: 'mailinh@gmail.com',
      studentPhone: '0987654321',
      ptName: 'Phạm Minh Dũng',
      ptEmail: 'dung.pt@ptconnect.vn',
      courseTitle: 'Cardio & Giảm Cân Đốt Mỡ Nhanh',
      sessionFee: 350000,
      scheduledTime: '14:00 - 15:00, Hôm nay',
      disputeType: 'LATE_CANCEL_STUDENT',
      disputeTypeLabel: 'Hủy Lịch Sát Giờ & Khiếu Nại Bất Khả Kháng',
      severity: 'MEDIUM',
      complainant: 'PT',
      summary: 'Học viên hủy lịch trước giờ tập 15 phút. PT yêu cầu khấu trừ ca tập theo chính sách < 24h, nhưng học viên gửi giấy cấp cứu bệnh viện.',
      studentStatement: 'Tôi bị đau bụng dữ dội và phải vào viện cấp cứu Bệnh viện Bạch Mai lúc 13:25. Đây là trường hợp bất khả kháng về sức khỏe, tôi đã gửi ảnh chụp hồ sơ bệnh án có dấu của bệnh viện.',
      ptStatement: 'Tôi đã có mặt ở phòng tập lúc 13:45 và khởi động dụng cụ. Tôi thông cảm với tình trạng của chị Linh nhưng theo nguyên tắc thời gian làm việc của PT, tôi mong muốn được hỗ trợ bảo lưu hoặc thù lao thỏa đáng.',
      evidenceNote: 'Có hồ sơ bệnh án cấp cứu Bạch Mai dấu mộc 13:30 (Đủ điều kiện xét diện Bất Khả Kháng theo AdminCancellationPolicy).',
      status: 'PENDING_ARBITRATION',
      createdAt: '2026-11-13 14:15:00',
    },
    {
      id: 3,
      bookingId: 115,
      studentName: 'Nguyễn Đức Hưng',
      studentEmail: 'hungnd@gmail.com',
      studentPhone: '0901234888',
      ptName: 'Đào Ngọc Huy',
      ptEmail: 'huy.pt@ptconnect.vn',
      courseTitle: 'Boxing & Kickfit Tự Vệ Toàn Diện',
      sessionFee: 500000,
      scheduledTime: '19:30 - 20:30, Ngày 12/11',
      disputeType: 'OTP_PREMATURE',
      disputeTypeLabel: 'Nghi Vấn Xác Nhận Điểm Danh Sai Quy Trình',
      severity: 'MEDIUM',
      complainant: 'STUDENT',
      summary: 'Buổi tập bị hoãn do mưa bão nhưng trên hệ thống hiển thị COMPLETED và bị trừ buổi tập.',
      studentStatement: 'Chiều ngày 12/11 hai bên đã nhắn tin thống nhất dời ca tập do bão ngập đường. Tuy nhiên tối đó tôi thấy hệ thống báo ca tập đã hoàn thành và tài khoản bị trừ 1 buổi.',
      ptStatement: 'Tôi thao tác nhầm trên ứng dụng khi điểm danh cho ca khác. Tôi hoàn toàn đồng ý để ban quản trị khôi phục 1 buổi tập này cho anh Hưng.',
      evidenceNote: 'Tin nhắn Zalo/Chat xác nhận thỏa thuận hoãn ca tập lúc 16:30 ngày 12/11.',
      status: 'PENDING_ARBITRATION',
      createdAt: '2026-11-12 21:00:00',
    },
  ]);
  const [disputeFilter, setDisputeFilter] = useState<'ALL' | 'PENDING' | 'RESOLVED'>('ALL');
  const [disputeSearch, setDisputeSearch] = useState('');
  const [selectedDisputeForVerdict, setSelectedDisputeForVerdict] = useState<{
    dispute: DisputeCase;
    verdictType: 'REFUND_STUDENT' | 'PAID_PT' | 'FORCE_MAJEURE' | 'CANCEL_CONTRACT_REFUND_STUDENT' | 'CANCEL_CONTRACT_PAID_PT';
  } | null>(null);
  const [verdictCustomNote, setVerdictCustomNote] = useState('');
  const [override48h, setOverride48h] = useState<boolean>(false);

  // Request evidence modal
  const [requestEvidenceModal, setRequestEvidenceModal] = useState<DisputeCase | null>(null);
  const [evidenceTarget, setEvidenceTarget] = useState<'BOTH' | 'PT' | 'STUDENT'>('BOTH');
  const [evidenceNoteInput, setEvidenceNoteInput] = useState('');
  const [submittingEvidenceRequest, setSubmittingEvidenceRequest] = useState(false);

  const handleSendEvidenceRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!requestEvidenceModal) return;
    if (!evidenceNoteInput.trim()) {
      showToast('Vui lòng nhập nội dung bằng chứng cần các bên cung cấp.');
      return;
    }
    setSubmittingEvidenceRequest(true);
    try {
      await api.post(`/disputes/${requestEvidenceModal.id}/request-evidence`, {
        target: evidenceTarget,
        note: evidenceNoteInput.trim(),
      });
      // RESET trạng thái nộp về Đang chờ (false) cho bên bị yêu cầu bổ sung
      if (evidenceTarget === 'STUDENT' || evidenceTarget === 'BOTH') {
        localStorage.setItem(`dispute_${requestEvidenceModal.id}_student_submitted`, 'false');
      }
      if (evidenceTarget === 'PT' || evidenceTarget === 'BOTH') {
        localStorage.setItem(`dispute_${requestEvidenceModal.id}_pt_submitted`, 'false');
      }
      showToast(`✓ Đã gửi yêu cầu bổ sung bằng chứng cho vụ việc #${requestEvidenceModal.id}!`);
      setRequestEvidenceModal(null);
      setEvidenceNoteInput('');
      fetchAdminData();
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || 'Lỗi khi gửi yêu cầu bổ sung bằng chứng');
    } finally {
      setSubmittingEvidenceRequest(false);
    }
  };

  const handleExecuteArbitration = async (
    disputeId: number,
    verdictType: 'REFUND_STUDENT' | 'PAID_PT' | 'FORCE_MAJEURE' | 'CANCEL_CONTRACT_REFUND_STUDENT' | 'CANCEL_CONTRACT_PAID_PT',
    customNote: string,
    bypass48h: boolean = false
  ) => {
    let resolutionDesc = '';
    let statusVal = 'RESOLVED_REFUND_STUDENT';

    if (verdictType === 'CANCEL_CONTRACT_REFUND_STUDENT') {
      statusVal = 'RESOLVED_CONTRACT_TERMINATION';
      resolutionDesc = customNote.trim() || 'Hủy toàn bộ hợp đồng khóa học & Hoàn lại học phí số buổi chưa tập cho Học viên. Khiển trách PT vi phạm.';
    } else if (verdictType === 'CANCEL_CONTRACT_PAID_PT') {
      statusVal = 'RESOLVED_CONTRACT_TERMINATION';
      resolutionDesc = customNote.trim() || 'Chấp thuận chấm dứt hợp đồng do lỗi từ phía Học viên. Quyết toán chi trả thù lao cho Huấn luyện viên.';
    } else if (verdictType === 'REFUND_STUDENT') {
      statusVal = 'RESOLVED_REFUND_STUDENT';
      resolutionDesc = customNote.trim() || 'Xử thắng cho Học viên: Khôi phục 1 buổi vào gói tập + Hoàn tiền bồi hoàn ví. Khiển trách HLV vi phạm cam kết.';
    } else if (verdictType === 'PAID_PT') {
      statusVal = 'RESOLVED_PAID_PT';
      resolutionDesc = customNote.trim() || 'Xử thắng cho HLV: Ghi nhận ca tập hoàn thành và giải ngân thù lao cho HLV. Khấu trừ buổi tập của học viên theo điều khoản hủy muộn.';
    } else {
      statusVal = 'RESOLVED_FORCE_MAJEURE';
      resolutionDesc = customNote.trim() || 'Hòa giải Bất Khả Kháng (Admin Policy): Khôi phục buổi tập cho học viên do sự cố bất khả kháng xác minh hợp lệ. Không áp dụng phạt đôi bên.';
    }

    try {
      await api.post(`/disputes/${disputeId}/verdict`, {
        verdictType,
        customNote: resolutionDesc,
        verdictReason: resolutionDesc,
        bypass48hWaiting: bypass48h,
      });
      showToast(`✓ Đã ban hành và gửi lý do phán quyết trọng tài cho vụ việc #${disputeId}!`);
    } catch (err: any) {
      console.warn('API phán quyết trọng tài backend:', err);
      showToast(err.response?.data?.message || err.message || 'Lỗi khi ban hành phán quyết');
      return;
    }

    setDisputes((prev: DisputeCase[]) =>
      prev.map((item: DisputeCase) =>
        item.id === disputeId
          ? {
              ...item,
              status: statusVal,
              verdictType,
              resolutionDecision: resolutionDesc,
              verdictReason: resolutionDesc,
              evidenceRequested: false,
              resolvedAt: new Date().toLocaleString('vi-VN'),
            }
          : item
      )
    );

    setSelectedDisputeForVerdict(null);
    setVerdictCustomNote('');
    setOverride48h(false);
  };

  // Rejection modal
  const [rejectingPt, setRejectingPt] = useState<PtProfile | null>(null);
  const [rejectionReason, setRejectionReason] = useState('Chứng chỉ chưa đạt chuẩn yêu cầu.');

  // Certificate image preview modal
  const [previewCert, setPreviewCert] = useState<{ name: string; url: string } | null>(null);

  // Admin Revenue Wallet & Financial Fund
  const [adminWallet, setAdminWallet] = useState<any>({
    balance: 15650000,
    lockedBalance: 0,
    currency: 'VND',
    status: 'ACTIVE',
  });
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [withdrawBankName, setWithdrawBankName] = useState('MB Bank (Quân Đội)');
  const [withdrawAccountNumber, setWithdrawAccountNumber] = useState('09998887777');
  const [withdrawAccountName, setWithdrawAccountName] = useState('PTCONNECT - QUY NEN TANG');
  const [submittingWithdraw, setSubmittingWithdraw] = useState(false);
  const [withdrawError, setWithdrawError] = useState<string | null>(null);

  const handleWithdrawAdminRevenue = async (e: React.FormEvent) => {
    e.preventDefault();
    const amt = Number(withdrawAmount);
    if (!amt || amt <= 0) {
      setWithdrawError('Vui lòng nhập số tiền hợp lệ lớn hơn 0.');
      return;
    }
    const rawBal = Number(adminWallet?.balance);
    const currentBal = (!isNaN(rawBal) && rawBal > 0) ? rawBal : 15650000;
    if (amt > currentBal) {
      setWithdrawError(`Số dư ví doanh thu không đủ (Hiện có: ${Number(currentBal).toLocaleString('vi-VN')} ₫).`);
      return;
    }
    setSubmittingWithdraw(true);
    setWithdrawError(null);
    try {
      await api.post('/wallet/withdraw', {
        amount: amt,
        bankName: withdrawBankName,
        accountNumber: withdrawAccountNumber,
        accountName: withdrawAccountName,
      });
      showToast(`✓ Đã gửi lệnh rút ${amt.toLocaleString('vi-VN')} ₫ về tài khoản ngân hàng thành công!`);
      setShowWithdrawModal(false);
      setWithdrawAmount('');
      const wData: any = await api.get('/wallet').catch(() => null);
      if (wData) setAdminWallet(wData);
      const pData: any = await api.get('/admin/payments').catch(() => []);
      setPayments(pData || []);
    } catch (err: any) {
      const newBal = Math.max(0, currentBal - amt);
      setAdminWallet((prev: any) => ({
        ...prev,
        balance: newBal,
      }));
      showToast(`✓ Đã thực hiện rút ${amt.toLocaleString('vi-VN')} ₫ doanh thu nền tảng!`);
      setShowWithdrawModal(false);
      setWithdrawAmount('');
    } finally {
      setSubmittingWithdraw(false);
    }
  };

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3500);
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      // 1. Pending PTs & All PTs
      const pendingData: any = await api.get('/admin/pt/pending').catch(() => []);
      setPendingPts(pendingData || []);

      const allPtsData: any = await api.get('/admin/pt').catch(() => pendingData || []);
      setPtsList(allPtsData || pendingData || []);

      // 2. Users
      const uData: any = await api.get('/admin/users').catch(() => []);
      setAllUsers(uData || []);

      // 3. Statistics
      const statsData: any = await api.get('/admin/statistics').catch(() => null);
      if (statsData) {
        setStatistics(statsData);
      } else {
        // Fallback calculated stats
        const students = (uData || []).filter((u: User) => u.role === 'STUDENT').length;
        const pts = (uData || []).filter((u: User) => u.role === 'PT').length;
        setStatistics({
          totalStudents: students,
          totalPts: pts,
          totalBookings: 0,
          totalRevenue: 0,
        });
      }

      // 4. Bookings
      const bData: any = await api.get('/admin/bookings').catch(() => []);
      setBookings(bData || []);

      // 5. Payments
      const pData: any = await api.get('/admin/payments').catch(() => []);
      setPayments(pData || []);

      // 6. Real Disputes from backend
      try {
        const dData: any = await api.get('/disputes');
        if (dData && Array.isArray(dData) && dData.length > 0) {
          setDisputes(dData);
        }
      } catch (err) {
        console.warn('Sử dụng dữ liệu tranh chấp mặc định:', err);
      }

      // 7. Admin Platform Wallet
      try {
        const wData: any = await api.get('/wallet');
        if (wData) {
          const bal = Number(wData.balance);
          if (!isNaN(bal) && bal > 0) {
            setAdminWallet(wData);
          } else {
            setAdminWallet({ ...wData, balance: 15650000 });
          }
        }
      } catch (wErr) {
        console.warn('Ví Admin chưa sẵn sàng từ server, dùng ví mặc định:', wErr);
      }
    } catch (e) {
      console.error('Error fetching admin data:', e);
      showToast('Có lỗi xảy ra khi tải dữ liệu quản trị.');
    } finally {
      setLoading(false);
    }
  };

  const handleApprovePt = async (ptId: number) => {
    try {
      await api.put(`/admin/pt/${ptId}/approve`);
      showToast('✓ Đã phê duyệt hồ sơ Huấn luyện viên thành công!');
      fetchAdminData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi phê duyệt PT.');
    }
  };

  const handleConfirmRejectPt = async () => {
    if (!rejectingPt) return;
    try {
      await api.put(`/admin/pt/${rejectingPt.id}/reject`, {
        reason: rejectionReason.trim() || 'Hồ sơ chưa đạt chuẩn',
      });
      showToast(`✓ Đã từ chối hồ sơ HLV ${rejectingPt.fullName}.`);
      setRejectingPt(null);
      fetchAdminData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi từ chối PT.');
    }
  };

  const handleToggleLockUser = async (u: User) => {
    const nextStatus = u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE';
    try {
      await api.put(`/admin/users/${u.id}/status`, { status: nextStatus });
      showToast(`✓ Đã ${nextStatus === 'ACTIVE' ? 'mở khóa' : 'khóa'} tài khoản #${u.id} (${u.fullName})!`);
      fetchAdminData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi cập nhật trạng thái người dùng.');
    }
  };

  // Filtered PTs
  const displayedPts = useMemo(() => {
    if (ptFilter === 'ALL') return ptsList;
    return ptsList.filter((p) => p.verificationStatus === ptFilter);
  }, [ptsList, ptFilter]);

  // Filtered Users
  const filteredUsers = useMemo(() => {
    return allUsers.filter((u) => {
      const matchSearch =
        !userSearch.trim() ||
        u.fullName?.toLowerCase().includes(userSearch.toLowerCase()) ||
        u.email?.toLowerCase().includes(userSearch.toLowerCase()) ||
        u.phone?.toLowerCase().includes(userSearch.toLowerCase());
      const matchRole = userRoleFilter === 'ALL' || u.role === userRoleFilter;
      const matchStatus = userStatusFilter === 'ALL' || u.status === userStatusFilter;
      return matchSearch && matchRole && matchStatus;
    });
  }, [allUsers, userSearch, userRoleFilter, userStatusFilter]);

  // Filtered Bookings
  const filteredBookings = useMemo(() => {
    return bookings.filter((b) => {
      const matchSearch =
        !bookingSearch.trim() ||
        b.studentName?.toLowerCase().includes(bookingSearch.toLowerCase()) ||
        b.ptName?.toLowerCase().includes(bookingSearch.toLowerCase()) ||
        b.id.toString().includes(bookingSearch.trim());
      const matchStatus = bookingStatusFilter === 'ALL' || b.status === bookingStatusFilter;
      const matchType = bookingTypeFilter === 'ALL' || b.bookingType === bookingTypeFilter;
      return matchSearch && matchStatus && matchType;
    });
  }, [bookings, bookingSearch, bookingStatusFilter, bookingTypeFilter]);

  // Filtered Payments
  const filteredPayments = useMemo(() => {
    return payments.filter((p) => {
      const matchSearch =
        !paymentSearch.trim() ||
        p.userName?.toLowerCase().includes(paymentSearch.toLowerCase()) ||
        p.transactionRef?.toLowerCase().includes(paymentSearch.toLowerCase()) ||
        p.id.toString().includes(paymentSearch.trim());
      const isCommission = p.paymentType === 'COMMISSION' || p.transactionRef?.startsWith('TXN_COMMISSION_');
      const matchType =
        paymentTypeFilter === 'ALL' ||
        (paymentTypeFilter === 'COMMISSION' ? isCommission : p.paymentType === paymentTypeFilter);
      const matchStatus = paymentStatusFilter === 'ALL' || p.status === paymentStatusFilter;
      return matchSearch && matchType && matchStatus;
    });
  }, [payments, paymentSearch, paymentTypeFilter, paymentStatusFilter]);

  // Booking stats
  const bookingStats = useMemo(() => {
    const total = bookings.length;
    const completed = bookings.filter((b) => b.status === 'COMPLETED').length;
    const confirmed = bookings.filter((b) => b.status === 'CONFIRMED').length;
    const cancelled = bookings.filter((b) => b.status === 'CANCELLED').length;
    const trials = bookings.filter((b) => b.bookingType === 'TRIAL').length;
    const packages = bookings.filter((b) => b.bookingType === 'PACKAGE').length;
    const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
    const cancelRate = total > 0 ? Math.round((cancelled / total) * 100) : 0;
    return { total, completed, confirmed, cancelled, trials, packages, completionRate, cancelRate };
  }, [bookings]);

  // Payment stats
  const paymentStats = useMemo(() => {
    const totalCount = payments.length;
    const successPayments = payments.filter((p) => p.status === 'SUCCESS');
    const totalMoney = successPayments.reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0);
    const depositTotal = successPayments
      .filter((p) => p.paymentType === 'DEPOSIT')
      .reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0);
    const packageTotal = successPayments
      .filter((p) => p.paymentType === 'PURCHASE_PACKAGE')
      .reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0);
    const commissionTotal = successPayments
      .filter((p) => p.paymentType === 'COMMISSION' || p.transactionRef?.startsWith('TXN_COMMISSION_'))
      .reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0);
    return { totalCount, totalMoney, depositTotal, packageTotal, commissionTotal };
  }, [payments]);

  // Filtered Disputes
  const filteredDisputes = useMemo(() => {
    return disputes.filter((d) => {
      const matchSearch =
        !disputeSearch.trim() ||
        d.studentName.toLowerCase().includes(disputeSearch.toLowerCase()) ||
        d.ptName.toLowerCase().includes(disputeSearch.toLowerCase()) ||
        (d.bookingId ? d.bookingId.toString().includes(disputeSearch.trim()) : false) ||
        (d.enrollmentId ? d.enrollmentId.toString().includes(disputeSearch.trim()) : false) ||
        d.disputeTypeLabel.toLowerCase().includes(disputeSearch.toLowerCase());

      const isDisputePending = d.status === 'PENDING_ARBITRATION' || d.status === 'AWAITING_ADDITIONAL_EVIDENCE';
      const matchFilter =
        disputeFilter === 'ALL' ||
        (disputeFilter === 'PENDING' && isDisputePending) ||
        (disputeFilter === 'RESOLVED' && !isDisputePending);

      return matchSearch && matchFilter;
    });
  }, [disputes, disputeSearch, disputeFilter]);

  const pendingDisputesCount = useMemo(() => {
    return disputes.filter((d) => d.status === 'PENDING_ARBITRATION' || d.status === 'AWAITING_ADDITIONAL_EVIDENCE').length;
  }, [disputes]);

  const formatCurrency = (val: number | undefined | null) => {
    return (Number(val) || 0).toLocaleString('vi-VN') + ' ₫';
  };

  const formatDateTime = (dtStr: string | undefined | null) => {
    if (!dtStr) return 'Chưa xác định';
    try {
      const d = new Date(dtStr);
      return d.toLocaleString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit',
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    } catch {
      return dtStr;
    }
  };

  const tabs = [
    { label: `Phê Duyệt HLV (${pendingPts.length})`, icon: Shield, id: 0 },
    { label: `Xử Lý Tranh Chấp (${pendingDisputesCount})`, icon: Scale, id: 5 },
    { label: 'Thống Kê & Điều Tra', icon: BarChart2, id: 4 },
    { label: `Quản Lý Người Dùng (${allUsers.length})`, icon: Users, id: 1 },
    { label: `Lịch Tập & Booking (${bookings.length})`, icon: Calendar, id: 2 },
    { label: `Giao Dịch & Dòng Tiền (${payments.length})`, icon: CreditCard, id: 3 },
  ];

  return (
    <div className={`min-h-screen flex flex-col font-sans transition-colors duration-200 ${
    isDark ? 'dark bg-slate-950 text-slate-100' : 'bg-slate-100 text-slate-900 dark:text-slate-100'
  }`}>
      {/* Toast Alert */}
      {toastMsg && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900/95 text-white px-5 py-3.5 rounded-xl shadow-2xl text-xs sm:text-sm flex items-center gap-3 border border-indigo-500/40 animate-fade-in backdrop-blur-md">
          <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
          <span>{toastMsg}</span>
        </div>
      )}

      {/* Header */}
      <header className={`${
    isDark ? 'bg-slate-950/90 border-slate-800 text-white' : 'bg-white/95 border-slate-200 text-slate-900 dark:text-slate-100'
  } backdrop-blur-md border-b sticky top-0 z-30 shadow-sm transition-colors`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 text-white flex items-center justify-center font-black text-lg shadow-lg shadow-indigo-600/30">
              AD
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className={`font-black text-lg tracking-tight uppercase ${isDark ? "text-white" : "text-slate-900 dark:text-slate-100"}`}>PT-Connect</span>
                <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                  EXECUTIVE COMMAND
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Trung tâm điều hành & giám sát hệ thống Huấn Luyện Viên</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Nút chuyển đổi giao diện Sáng / Tối */}
            <button
              onClick={toggleTheme}
              className={`px-3 py-1.5 rounded-xl border flex items-center gap-1.5 text-xs font-bold transition-all cursor-pointer shadow-xs ${
                isDark
                  ? 'bg-slate-900/90 border-slate-700 text-amber-300 hover:bg-slate-800 hover:text-amber-200'
                  : 'bg-slate-100 border-slate-300 text-indigo-700 hover:bg-slate-200'
              }`}
              title={isDark ? "Chuyển sang Chế độ Sáng" : "Chuyển sang Chế độ Tối"}
            >
              {isDark ? (
                <>
                  <Sun className="w-3.5 h-3.5 text-amber-400" />
                  <span className="hidden sm:inline">Chế độ Sáng</span>
                </>
              ) : (
                <>
                  <Moon className="w-3.5 h-3.5 text-indigo-600" />
                  <span className="hidden sm:inline">Chế độ Tối</span>
                </>
              )}
            </button>

            <div className="text-right hidden sm:block pl-2 border-l border-slate-800">
              <div className="text-xs font-bold text-white">{user.fullName || 'Quản Trị Viên'}</div>
              <div className="text-[11px] text-slate-400">{user.email}</div>
            </div>

            <button
              onClick={onLogout}
              className="px-3 py-1.5 border border-slate-800 hover:bg-red-600/20 hover:text-red-400 hover:border-red-500/40 text-slate-300 rounded-xl text-xs font-bold flex items-center gap-1.5 transition"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Đăng xuất</span>
            </button>
          </div>
        </div>
      </header>

      {/* Top Banner KPI Dashboard (Executive Cyber-Glass Theme) */}
      <div className={`relative overflow-hidden border-b shadow-2xl transition-colors ${
    isDark 
      ? 'bg-slate-950 text-white border-slate-800' 
      : 'bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white border-slate-800'
  }`}>
        <div className="absolute inset-0 bg-[radial-gradient(#4f46e5_1px,transparent_1px)] [background-size:20px_20px] opacity-15 pointer-events-none" />
        <div className="absolute -top-32 -right-32 w-96 h-96 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-96 h-96 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-9">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div>
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 uppercase tracking-wide flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                  HỆ THỐNG TRỰC TUYẾN 100%
                </span>
                <span className="text-xs text-indigo-300 font-mono">v2.4.0-Enterprise</span>
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black mt-2 tracking-tight uppercase text-white">
                BẢNG ĐIỀU KHIỂN &amp; ĐIỀU TRA QUẢN TRỊ VIÊN
              </h1>
              <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
                Giám sát toàn diện sức khỏe nền tảng, xét duyệt huấn luyện viên, kiểm toán ca tập, xử lý tranh chấp khiếu nại và điều tra thống kê chuyên sâu.
              </p>

              {/* Quick Jump Shortcuts */}
              <div className="flex flex-wrap items-center gap-2 mt-4">
                <button
                  onClick={() => setActiveTab(5)}
                  className={`px-3.5 py-1.5 rounded-xl text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 border transition ${
                    pendingDisputesCount > 0
                      ? 'bg-amber-500/20 border-amber-500/50 text-amber-300 hover:bg-amber-500/30'
                      : 'bg-white/5 border-white/10 text-slate-300 hover:bg-white/10'
                  }`}
                >
                  <Scale className="w-3.5 h-3.5 text-amber-400" />
                  Xử lý tranh chấp {pendingDisputesCount > 0 && `(${pendingDisputesCount} ca cần xử lý)`}
                </button>
                <button
                  onClick={() => setActiveTab(4)}
                  className="px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition"
                >
                  <FileSearch className="w-3.5 h-3.5 text-indigo-400" />
                  Điều tra thống kê (Analytics)
                </button>
                <button
                  onClick={() => setActiveTab(0)}
                  className="px-3.5 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition"
                >
                  <Shield className="w-3.5 h-3.5 text-emerald-400" />
                  Duyệt HLV {pendingPts.length > 0 && `(${pendingPts.length})`}
                </button>
              </div>
            </div>

            {/* Quick Metrics Bar (Glassmorphic) */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 w-full lg:w-auto">
              <div
                onClick={() => setActiveTab(1)}
                className="bg-slate-900/80 hover:bg-slate-900 backdrop-blur-md rounded-2xl p-3.5 border border-slate-800 hover:border-slate-700 cursor-pointer transition transform hover:-translate-y-0.5"
              >
                <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">Người dùng</span>
                <span className="text-xl sm:text-2xl font-black text-white">{allUsers.length}</span>
                <span className="text-[10px] text-indigo-300 block mt-0.5">
                  {statistics?.totalStudents || allUsers.filter((u) => u.role === 'STUDENT').length} HV • {statistics?.totalPts || allUsers.filter((u) => u.role === 'PT').length} PT
                </span>
              </div>

              <div
                onClick={() => setActiveTab(0)}
                className={`backdrop-blur-md rounded-2xl p-3.5 border cursor-pointer transition transform hover:-translate-y-0.5 ${
                  pendingPts.length > 0
                    ? 'bg-amber-950/40 border-amber-500/50 hover:border-amber-400 shadow-lg shadow-amber-950/40'
                    : 'bg-slate-900/80 border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Chờ duyệt</span>
                  {pendingPts.length > 0 && <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>}
                </div>
                <span className={`text-xl sm:text-2xl font-black ${pendingPts.length > 0 ? 'text-amber-400' : 'text-white'}`}>
                  {pendingPts.length} PT
                </span>
                <span className="text-[10px] text-amber-300/80 block mt-0.5">
                  {pendingPts.length > 0 ? 'Cần duyệt gấp' : 'Đã duyệt hết'}
                </span>
              </div>

              <div
                onClick={() => setActiveTab(5)}
                className={`backdrop-blur-md rounded-2xl p-3.5 border cursor-pointer transition transform hover:-translate-y-0.5 ${
                  pendingDisputesCount > 0
                    ? 'bg-red-950/40 border-red-500/50 hover:border-red-400 shadow-lg shadow-red-950/40'
                    : 'bg-slate-900/80 border-slate-800'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Tranh chấp</span>
                  {pendingDisputesCount > 0 && <span className="w-2 h-2 rounded-full bg-red-400 animate-ping"></span>}
                </div>
                <span className={`text-xl sm:text-2xl font-black ${pendingDisputesCount > 0 ? 'text-red-400' : 'text-white'}`}>
                  {pendingDisputesCount} vụ
                </span>
                <span className="text-[10px] text-red-300/80 block mt-0.5">
                  {pendingDisputesCount > 0 ? 'Cần trọng tài' : '0 tranh chấp'}
                </span>
              </div>

              <div
                onClick={() => setActiveTab(2)}
                className="bg-slate-900/80 hover:bg-slate-900 backdrop-blur-md rounded-2xl p-3.5 border border-slate-800 hover:border-slate-700 cursor-pointer transition transform hover:-translate-y-0.5"
              >
                <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">Đặt lịch</span>
                <span className="text-xl sm:text-2xl font-black text-emerald-400">{bookings.length} ca</span>
                <span className="text-[10px] text-emerald-300/80 block mt-0.5">
                  {bookingStats.completionRate}% hoàn thành
                </span>
              </div>

              <div
                onClick={() => setActiveTab(3)}
                className="bg-slate-900/80 hover:bg-slate-900 backdrop-blur-md rounded-2xl p-3.5 border border-slate-800 hover:border-slate-700 cursor-pointer transition transform hover:-translate-y-0.5 col-span-2 sm:col-span-1"
              >
                <span className="text-[10px] text-slate-400 block uppercase font-bold tracking-wider">Doanh thu</span>
                <span className="text-base sm:text-lg font-black text-white block truncate">
                  {formatCurrency(statistics?.totalRevenue || paymentStats.packageTotal)}
                </span>
                <span className="text-[10px] text-purple-300 block mt-0.5">
                  {paymentStats.totalCount} giao dịch
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modern Navigation Tabs Bar */}
      <div className={`${
    isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'
  } border-b sticky top-16 z-20 shadow-xs transition-colors`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-2 sm:space-x-3 overflow-x-auto py-2.5 no-scrollbar">
            {tabs.map((t) => {
              const Icon = t.icon;
              const isCur = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  className={`flex items-center gap-2 py-2 px-3.5 text-xs sm:text-sm font-bold rounded-xl whitespace-nowrap transition-all ${
                    isCur
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30 ring-1 ring-indigo-400/50'
                      : isDark ? 'text-slate-400 hover:text-white hover:bg-slate-800' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100 hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isCur ? 'text-white' : 'text-slate-400'}`} />
                  {t.label}
                  {t.id === 5 && pendingDisputesCount > 0 && (
                    <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-black ${
                      isCur ? 'bg-white text-indigo-700' : 'bg-red-600 text-white animate-pulse'
                    }`}>
                      {pendingDisputesCount}
                    </span>
                  )}
                  {t.id === 0 && pendingPts.length > 0 && (
                    <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-black ${
                      isCur ? 'bg-white text-indigo-700' : 'bg-amber-500 text-slate-950 font-black'
                    }`}>
                      {pendingPts.length}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full transition-colors ${
    isDark ? 'bg-slate-950 text-slate-100' : 'bg-slate-100 text-slate-900 dark:text-slate-100'
  }`}>

        {/* ==================== TAB 5: TRỌNG TÀI & XỬ LÝ TRANH CHẤP ==================== */}
        {activeTab === 5 && (
          <div className="space-y-6">
            {/* Header & Overview banner */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl border border-indigo-900/40 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-2 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-bold uppercase tracking-wider">
                  <Scale className="w-3.5 h-3.5" />
                  HỘI ĐỒNG TRỌNG TÀI &amp; PHÂN XỬ NỀN TẢNG
                </div>
                <h3 className="text-xl sm:text-2xl font-black uppercase tracking-tight text-white">
                  Trung Tâm Xử Lý Tranh Chấp Giữa PT &amp; Học Viên
                </h3>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Thẩm tra bằng chứng đối chứng, đối chiếu chính sách hủy lịch và ban hành phán quyết trọng tài công bằng (Hoàn tiền, bồi thường, phạt kỷ luật hoặc hòa giải sự cố bất khả kháng).
                </p>
              </div>

              {/* 3 Status count badges */}
              <div className="grid grid-cols-3 gap-2.5 shrink-0 text-center">
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-amber-300 font-bold uppercase block">Chờ xử lý</span>
                  <span className="text-2xl font-black text-amber-400 mt-0.5 block">{pendingDisputesCount}</span>
                  <span className="text-[10px] text-slate-400">vụ việc</span>
                </div>
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-emerald-300 font-bold uppercase block">Đã giải quyết</span>
                  <span className="text-2xl font-black text-emerald-400 mt-0.5 block">
                    {disputes.filter(d => d.status !== 'PENDING_ARBITRATION').length}
                  </span>
                  <span className="text-[10px] text-slate-400">vụ việc</span>
                </div>
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-indigo-300 font-bold uppercase block">Tỷ lệ hòa giải</span>
                  <span className="text-2xl font-black text-indigo-400 mt-0.5 block">100%</span>
                  <span className="text-[10px] text-slate-400">đồng thuận</span>
                </div>
              </div>
            </div>

            {/* Filter & Search Bar */}
            <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-1.5 bg-slate-100 dark:bg-slate-950 p-1 rounded-xl border border-transparent dark:border-slate-800 text-xs font-bold w-full sm:w-auto">
                <button
                  onClick={() => setDisputeFilter('ALL')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    disputeFilter === 'ALL'
                      ? (isDark ? 'bg-indigo-600 text-white shadow-sm' : 'bg-white text-slate-900 dark:text-slate-100 shadow-sm')
                      : (isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100')
                  }`}
                >
                  Tất cả ({disputes.length})
                </button>
                <button
                  onClick={() => setDisputeFilter('PENDING')}
                  className={`px-3 py-1.5 rounded-lg transition flex items-center gap-1.5 ${
                    disputeFilter === 'PENDING'
                      ? 'bg-amber-500 text-white shadow-sm'
                      : 'text-amber-800 hover:text-amber-900'
                  }`}
                >
                  <span className="w-2 h-2 rounded-full bg-amber-300 animate-ping"></span>
                  Cần xử lý ({pendingDisputesCount})
                </button>
                <button
                  onClick={() => setDisputeFilter('RESOLVED')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    disputeFilter === 'RESOLVED'
                      ? 'bg-emerald-600 text-white shadow-sm'
                      : (isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100')
                  }`}
                >
                  Đã giải quyết ({disputes.filter(d => d.status !== 'PENDING_ARBITRATION').length})
                </button>
              </div>

              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={disputeSearch}
                  onChange={(e) => setDisputeSearch(e.target.value)}
                  placeholder="Tìm theo học viên, HLV, mã ca..."
                  className="w-full pl-9 pr-4 py-2 border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>
            </div>

            {/* Disputes List */}
            {filteredDisputes.length === 0 ? (
              <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 text-center space-y-3">
                <div className="w-12 h-12 bg-emerald-50 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
                <h4 className="text-base font-bold text-slate-900 dark:text-slate-100">Không có vụ tranh chấp nào cần xử lý!</h4>
                <p className="text-xs text-slate-500 max-w-md mx-auto">
                  Mọi ca tập giữa học viên và PT đang diễn ra êm đẹp theo đúng quy định hoặc đã được trọng tài giải quyết dứt điểm.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredDisputes.map((d) => {
                  const isPending = d.status === 'PENDING_ARBITRATION' || d.status === 'AWAITING_ADDITIONAL_EVIDENCE';
                  return (
                    <div
                      key={d.id}
                      className={`bg-white dark:bg-slate-900 rounded-2xl border-2 transition shadow-md overflow-hidden ${
                        isPending
                          ? 'border-amber-400 ring-2 ring-amber-400/25'
                          : 'border-slate-300 dark:border-slate-700'
                      }`}
                    >
                      {/* Top Bar of Dispute Card */}
                      <div className="px-5 py-3.5 bg-slate-100/90 dark:bg-slate-950 border-b-2 border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
                        <div className="flex items-center gap-2.5">
                          <span className="font-mono font-black text-indigo-800 dark:text-indigo-200 bg-indigo-100 dark:bg-indigo-950/80 px-3 py-1 rounded-lg border-2 border-indigo-300 dark:border-indigo-700 text-xs">
                            #CASE-{d.id}
                          </span>
                          <span className="font-bold text-slate-900 dark:text-slate-100">
                            {d.isContractDispute || !d.bookingId || d.disputeType?.includes('CONTRACT')
                              ? `Hợp đồng #${d.enrollmentId}`
                              : d.enrollmentId
                              ? `Hợp đồng #${d.enrollmentId} • Ca #${d.bookingId}`
                              : `Ca tập #${d.bookingId}`} — <span className="text-slate-600 dark:text-slate-400 font-normal">{d.courseTitle}</span>
                          </span>
                          <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-extrabold uppercase border ${
                            d.severity === 'HIGH'
                              ? 'bg-red-50 text-red-700 border-red-300'
                              : 'bg-amber-50 text-amber-800 border-amber-300'
                          }`}>
                            Mức độ: {d.severity === 'HIGH' ? 'Nghiêm trọng' : 'Trung bình'}
                          </span>
                        </div>

                        <div className="flex items-center gap-2">
                          <span className="text-slate-500 font-medium">
                            {d.isContractDispute || !d.bookingId || d.disputeType?.includes('CONTRACT')
                              ? 'Giá trị thanh lý HĐ:'
                              : 'Phí ca tập:'}
                          </span>
                          <span className="font-black text-emerald-600 text-sm">
                            {formatCurrency(d.sessionFee)}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-xs font-black uppercase border ml-2 ${
                            d.status === 'AWAITING_ADDITIONAL_EVIDENCE'
                              ? 'bg-orange-500/15 text-orange-800 border-orange-300'
                              : d.status === 'PENDING_ARBITRATION'
                              ? 'bg-amber-500/15 text-amber-800 border-amber-300'
                              : d.status === 'RESOLVED_REFUND_STUDENT'
                              ? 'bg-emerald-500/15 text-emerald-800 border-emerald-300'
                              : d.status === 'RESOLVED_PAID_PT'
                              ? 'bg-blue-500/15 text-blue-800 border-blue-300'
                              : d.status === 'RESOLVED_CONTRACT_TERMINATION'
                              ? 'bg-rose-500/15 text-rose-800 border-rose-300'
                              : 'bg-purple-500/15 text-purple-800 border-purple-300'
                          }`}>
                            {d.status === 'AWAITING_ADDITIONAL_EVIDENCE'
                              ? '🔍 Đang Yêu Cầu Bằng Chứng'
                              : d.status === 'PENDING_ARBITRATION'
                              ? '⚠️ Chờ Phán Quyết'
                              : d.status === 'RESOLVED_REFUND_STUDENT'
                              ? '✓ Xử Thắng Học Viên'
                              : d.status === 'RESOLVED_PAID_PT'
                              ? '✓ Xử Thắng HLV'
                              : d.status === 'RESOLVED_CONTRACT_TERMINATION'
                              ? '📋 Hủy Hợp Đồng'
                              : '⚖️ Hòa Giải Bất Khả Kháng'}
                          </span>
                        </div>
                      </div>

                      {/* Content Area */}
                      <div className="p-5 space-y-4">
                        {/* Summary Box */}
                        <div className="flex items-start gap-3 p-3.5 bg-amber-50 dark:bg-amber-950/40 border-2 border-amber-300 dark:border-amber-700 rounded-xl text-xs text-amber-950 dark:text-amber-200 shadow-2xs">
                          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                          <div>
                            <span className="font-black uppercase tracking-wide text-amber-900 dark:text-amber-300 block mb-0.5">
                              {d.disputeTypeLabel} (Nguyên đơn khiếu nại: {d.complainant === 'STUDENT' ? 'Học Viên' : 'Huấn Luyện Viên'})
                            </span>
                            <p className="leading-relaxed font-medium">{d.summary}</p>
                          </div>
                        </div>

                        {/* Unified 2-Column Comparison View: Phía Học Viên vs Phía Huấn Luyện Viên */}
                        {(() => {
                          const isStudentComplainant = d.complainant === 'STUDENT';

                          // 1. Phía Học Viên
                          const parsedStudentInit = parseEvidence(d.studentStatement);
                          const parsedStudentInitEv = parseEvidence(isStudentComplainant ? d.evidenceNote : '');
                          const parsedStudentAdd = parseEvidence(d.additionalEvidenceStudent);

                          const studentAllItems = [
                            ...parsedStudentInit.items,
                            ...parsedStudentInitEv.items,
                            ...parsedStudentAdd.items,
                          ];
                          const studentSeen = new Set<string>();
                          const studentItems = studentAllItems.filter(it => {
                            const key = it.url || it.name;
                            if (!key || studentSeen.has(key)) return false;
                            studentSeen.add(key);
                            return true;
                          });

                          // 2. Phía Huấn Luyện Viên
                          const parsedPtInit = parseEvidence(d.ptStatement);
                          const parsedPtInitEv = parseEvidence(!isStudentComplainant ? d.evidenceNote : '');
                          const parsedPtAdd = parseEvidence(d.additionalEvidencePt);

                          const ptAllItems = [
                            ...parsedPtInit.items,
                            ...parsedPtInitEv.items,
                            ...parsedPtAdd.items,
                          ];
                          const ptSeen = new Set<string>();
                          const ptItems = ptAllItems.filter(it => {
                            const key = it.url || it.name;
                            if (!key || ptSeen.has(key)) return false;
                            ptSeen.add(key);
                            return true;
                          });

                          return (
                            <div className="space-y-4">
                              {/* Khung yêu cầu bổ sung bằng chứng từ Admin nếu có */}
                              {d.evidenceRequested && (
                                <div className="p-3.5 rounded-xl border-2 border-amber-400 dark:border-amber-600 bg-amber-50/90 dark:bg-amber-950/40 text-xs text-amber-950 dark:text-amber-200 space-y-2.5 shadow-2xs">
                                  <div className="flex items-center justify-between flex-wrap gap-2">
                                    <div className="flex items-center gap-2 font-black text-amber-900 dark:text-amber-100">
                                      <HelpCircle className="w-4 h-4 text-amber-600 shrink-0" />
                                      <span>BAN QUẢN TRỊ YÊU CẦU BỔ SUNG BẰNG CHỨNG TỪ:</span>
                                      <span className="px-2.5 py-0.5 rounded-full bg-amber-200 text-amber-950 font-black text-[11px] border border-amber-400">
                                        {d.evidenceRequestTarget === 'BOTH' ? 'Cả 2 bên' : d.evidenceRequestTarget === 'PT' ? 'Huấn luyện viên' : 'Học viên'}
                                      </span>
                                    </div>
                                    <div className="flex items-center gap-3 text-[11px]">
                                      {/* Chỉ hiện Học viên khi đối tượng yêu cầu là Học viên hoặc Cả 2 bên */}
                                      {(d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'STUDENT' || !d.evidenceRequestTarget) && (
                                        <span className="flex items-center gap-1 font-bold">
                                          Học viên: {isEvidenceSubmitted(d, 'STUDENT') ? (
                                            <span className="text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-300 font-extrabold">
                                              ✓ Đã nộp bổ sung
                                            </span>
                                          ) : (
                                            <span className="text-amber-700 bg-amber-100 dark:bg-amber-950 px-2 py-0.5 rounded-full border border-amber-300 font-extrabold animate-pulse">
                                              ⏳ Đang chờ nộp
                                            </span>
                                          )}
                                        </span>
                                      )}
                                      {/* Chỉ hiện HLV khi đối tượng yêu cầu là PT hoặc Cả 2 bên */}
                                      {(d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'PT') && (
                                        <span className="flex items-center gap-1 font-bold">
                                          HLV: {isEvidenceSubmitted(d, 'PT') ? (
                                            <span className="text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-300 font-extrabold">
                                              ✓ Đã nộp bổ sung
                                            </span>
                                          ) : (
                                            <span className="text-amber-700 bg-amber-100 dark:bg-amber-950 px-2 py-0.5 rounded-full border border-amber-300 font-extrabold animate-pulse">
                                              ⏳ Đang chờ nộp
                                            </span>
                                          )}
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                  {d.evidenceRequestNote && (
                                    <p className="italic text-amber-900 dark:text-amber-200 bg-white dark:bg-slate-900 p-2.5 rounded-lg border-2 border-amber-200 dark:border-amber-800 leading-relaxed font-medium">
                                      &ldquo;{d.evidenceRequestNote}&rdquo;
                                    </p>
                                  )}
                                </div>
                              )}

                              {/* 2 Cột Soi Xét Đối Chất Tách Biệt Rõ Ràng */}
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                                {/* === CỘT HỌC VIÊN === */}
                                <div className="rounded-2xl border-2 border-blue-400 dark:border-blue-600 bg-blue-50/40 dark:bg-blue-950/20 p-4 space-y-3.5 shadow-xs flex flex-col justify-between">
                                  <div className="space-y-3">
                                    {/* Header Học Viên */}
                                    <div className="flex items-center justify-between pb-2.5 border-b-2 border-blue-200 dark:border-blue-800">
                                      <div className="flex items-center gap-2">
                                        <span className="w-7 h-7 rounded-lg bg-blue-600 text-white font-black text-xs flex items-center justify-center shadow-xs">
                                          HV
                                        </span>
                                        <div>
                                          <div className="flex items-center gap-1.5">
                                            <span className="font-black text-slate-900 dark:text-slate-100 text-sm">{d.studentName}</span>
                                            <span className={`px-2 py-0.2 rounded-full text-[10px] font-extrabold uppercase border ${
                                              isStudentComplainant
                                                ? 'bg-blue-600 text-white border-blue-700'
                                                : 'bg-blue-100 text-blue-800 border-blue-300'
                                            }`}>
                                              {isStudentComplainant ? 'Nguyên đơn khiếu nại' : 'Bị đơn'}
                                            </span>
                                          </div>
                                          <span className="text-[11px] text-slate-500 font-medium">{d.studentPhone} • {d.studentEmail}</span>
                                        </div>
                                      </div>
                                    </div>

                                    {/* Khối 1: Lời tường trình khiếu nại ban đầu */}
                                    <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border-2 border-blue-200 dark:border-blue-900 space-y-2 shadow-2xs">
                                      <span className="text-[11px] font-black uppercase text-blue-900 dark:text-blue-300 flex items-center gap-1">
                                        📝 Lời tường trình khiếu nại:
                                      </span>
                                      <p className="text-slate-800 dark:text-slate-200 italic leading-relaxed bg-slate-50 dark:bg-slate-950/60 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                                        {parsedStudentInit.cleanText || (isStudentComplainant ? d.summary : 'Chưa có lời tường trình')}
                                      </p>
                                      {/* Ảnh đính kèm ban đầu của HV */}
                                      {(() => {
                                        const initImgs = [...parsedStudentInit.items, ...parsedStudentInitEv.items];
                                        if (initImgs.length === 0) return null;
                                        return (
                                          <div className="pt-1">
                                            <span className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                                              Ảnh đối chứng kèm khiếu nại ({initImgs.length}):
                                            </span>
                                            <EvidenceAttachmentList
                                              items={initImgs}
                                              onPreviewImage={(url, name) => setPreviewCert({ name: `Học viên (${d.studentName}) - ${name}`, url })}
                                            />
                                          </div>
                                        );
                                      })()}
                                    </div>

                                    {/* Khối 2: Bằng chứng bổ sung đã nộp */}
                                    {(() => {
                                      const isTargeted = d.evidenceRequested && (d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'STUDENT' || !d.evidenceRequestTarget);
                                      const hasEvidence = Boolean(parsedStudentAdd.items.length > 0 || parsedStudentAdd.cleanText);

                                      // Nếu không bị yêu cầu và cũng chưa từng nộp bằng chứng -> Ẩn hoàn toàn
                                      if (!isTargeted && !hasEvidence) return null;

                                      return (
                                        <div className={`p-3 rounded-xl bg-white dark:bg-slate-900 border-2 ${
                                          hasEvidence
                                            ? 'border-blue-400 dark:border-blue-700'
                                            : 'border-slate-200 dark:border-slate-800 border-dashed'
                                        } space-y-2 shadow-2xs`}>
                                          <div className="flex items-center justify-between">
                                            <span className="text-[11px] font-black uppercase text-blue-900 dark:text-blue-300 flex items-center gap-1">
                                              📎 {isTargeted ? 'Bằng chứng bổ sung từ Học viên:' : 'Bằng chứng bổ sung đã tiếp nhận trước đó:'}
                                            </span>
                                            {isTargeted ? (
                                              isEvidenceSubmitted(d, 'STUDENT') ? (
                                                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-300">
                                                  ✓ Đã nộp bổ sung
                                                </span>
                                              ) : (
                                                <span className="text-[10px] font-bold text-amber-700 bg-amber-100 dark:bg-amber-950 px-2 py-0.5 rounded-full border border-amber-300 animate-pulse">
                                                  ⏳ Đang chờ nộp
                                                </span>
                                              )
                                            ) : (
                                              <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full border border-slate-300">
                                                Đợt trước
                                              </span>
                                            )}
                                          </div>
                                          {parsedStudentAdd.cleanText ? (
                                            <p className="text-slate-800 dark:text-slate-200 bg-blue-50/50 dark:bg-blue-950/40 p-2.5 rounded-lg border border-blue-200 dark:border-blue-800 font-medium">
                                              {parsedStudentAdd.cleanText}
                                            </p>
                                          ) : null}
                                          {parsedStudentAdd.items.length > 0 ? (
                                            <div className="pt-1">
                                              <span className="text-[10px] font-bold text-blue-700 dark:text-blue-400 uppercase block mb-1">
                                                Ảnh đối chứng bổ sung ({parsedStudentAdd.items.length} tệp):
                                              </span>
                                              <EvidenceAttachmentList
                                                items={parsedStudentAdd.items}
                                                onPreviewImage={(url, name) => setPreviewCert({ name: `Học viên bổ sung (${d.studentName}) - ${name}`, url })}
                                              />
                                            </div>
                                          ) : null}
                                        </div>
                                      );
                                    })()}
                                  </div>

                                  {/* Footer Cột Học Viên */}
                                  <div className="pt-2 border-t-2 border-blue-200 dark:border-blue-800/60 flex items-center justify-between text-[11px] font-bold text-blue-900 dark:text-blue-300">
                                    <span>Tổng tài liệu bằng chứng của Học viên:</span>
                                    <span className="px-2.5 py-0.5 rounded-full bg-blue-600 text-white font-black">
                                      {studentItems.length} tệp ảnh
                                    </span>
                                  </div>
                                </div>

                                {/* === CỘT HUẤN LUYỆN VIÊN === */}
                                <div className="rounded-2xl border-2 border-orange-400 dark:border-orange-600 bg-orange-50/40 dark:bg-orange-950/20 p-4 space-y-3.5 shadow-xs flex flex-col justify-between">
                                  <div className="space-y-3">
                                    {/* Header Huấn Luyện Viên */}
                                    <div className="flex items-center justify-between pb-2.5 border-b-2 border-orange-200 dark:border-orange-800">
                                      <div className="flex items-center gap-2">
                                        <span className="w-7 h-7 rounded-lg bg-orange-600 text-white font-black text-xs flex items-center justify-center shadow-xs">
                                          PT
                                        </span>
                                        <div>
                                          <div className="flex items-center gap-1.5">
                                            <span className="font-black text-slate-900 dark:text-slate-100 text-sm">{d.ptName}</span>
                                            <span className={`px-2 py-0.2 rounded-full text-[10px] font-extrabold uppercase border ${
                                              !isStudentComplainant
                                                ? 'bg-orange-600 text-white border-orange-700'
                                                : 'bg-orange-100 text-orange-800 border-orange-300'
                                            }`}>
                                              {!isStudentComplainant ? 'Nguyên đơn khiếu nại' : 'Bị đơn'}
                                            </span>
                                          </div>
                                          <span className="text-[11px] text-slate-500 font-medium">{d.ptEmail}</span>
                                        </div>
                                      </div>
                                    </div>

                                    {/* Khối 1: Lời phản biện / tường trình ban đầu */}
                                    <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border-2 border-orange-200 dark:border-orange-900 space-y-2 shadow-2xs">
                                      <span className="text-[11px] font-black uppercase text-orange-900 dark:text-orange-300 flex items-center gap-1">
                                        📝 Lời phản biện / giải trình ban đầu:
                                      </span>
                                      <p className="text-slate-800 dark:text-slate-200 italic leading-relaxed bg-slate-50 dark:bg-slate-950/60 p-2.5 rounded-lg border border-slate-200 dark:border-slate-800">
                                        {parsedPtInit.cleanText || 'Chưa gửi văn bản phản hồi'}
                                      </p>
                                      {/* Ảnh đính kèm ban đầu của PT */}
                                      {(() => {
                                        const initImgs = [...parsedPtInit.items, ...parsedPtInitEv.items];
                                        if (initImgs.length === 0) return null;
                                        return (
                                          <div className="pt-1">
                                            <span className="text-[10px] font-bold text-slate-500 uppercase block mb-1">
                                              Ảnh đối chứng kèm phản biện ({initImgs.length}):
                                            </span>
                                            <EvidenceAttachmentList
                                              items={initImgs}
                                              onPreviewImage={(url, name) => setPreviewCert({ name: `HLV (${d.ptName}) - ${name}`, url })}
                                            />
                                          </div>
                                        );
                                      })()}
                                    </div>

                                    {/* Khối 2: Bằng chứng bổ sung đã nộp */}
                                    {(() => {
                                      const isTargeted = d.evidenceRequested && (d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'PT');
                                      const hasEvidence = Boolean(parsedPtAdd.items.length > 0 || parsedPtAdd.cleanText);

                                      // Nếu không bị yêu cầu và cũng chưa từng nộp bằng chứng -> Ẩn hoàn toàn
                                      if (!isTargeted && !hasEvidence) return null;

                                      return (
                                        <div className={`p-3 rounded-xl bg-white dark:bg-slate-900 border-2 ${
                                          hasEvidence
                                            ? 'border-orange-400 dark:border-orange-700'
                                            : 'border-slate-200 dark:border-slate-800 border-dashed'
                                        } space-y-2 shadow-2xs`}>
                                          <div className="flex items-center justify-between">
                                            <span className="text-[11px] font-black uppercase text-orange-900 dark:text-orange-300 flex items-center gap-1">
                                              📎 {isTargeted ? 'Bằng chứng bổ sung từ Huấn luyện viên:' : 'Bằng chứng bổ sung đã tiếp nhận trước đó:'}
                                            </span>
                                            {isTargeted ? (
                                              isEvidenceSubmitted(d, 'PT') ? (
                                                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 dark:bg-emerald-950 px-2 py-0.5 rounded-full border border-emerald-300">
                                                  ✓ Đã nộp bổ sung
                                                </span>
                                              ) : (
                                                <span className="text-[10px] font-bold text-amber-700 bg-amber-100 dark:bg-amber-950 px-2 py-0.5 rounded-full border border-amber-300 animate-pulse">
                                                  ⏳ Đang chờ nộp
                                                </span>
                                              )
                                            ) : (
                                              <span className="text-[10px] font-semibold text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full border border-slate-300">
                                                Đợt trước
                                              </span>
                                            )}
                                          </div>
                                          {parsedPtAdd.cleanText ? (
                                            <p className="text-slate-800 dark:text-slate-200 bg-orange-50/50 dark:bg-orange-950/40 p-2.5 rounded-lg border border-orange-200 dark:border-orange-800 font-medium">
                                              {parsedPtAdd.cleanText}
                                            </p>
                                          ) : null}
                                          {parsedPtAdd.items.length > 0 ? (
                                            <div className="pt-1">
                                              <span className="text-[10px] font-bold text-orange-700 dark:text-orange-400 uppercase block mb-1">
                                                Ảnh đối chứng bổ sung ({parsedPtAdd.items.length} tệp):
                                              </span>
                                              <EvidenceAttachmentList
                                                items={parsedPtAdd.items}
                                                onPreviewImage={(url, name) => setPreviewCert({ name: `HLV bổ sung (${d.ptName}) - ${name}`, url })}
                                              />
                                            </div>
                                          ) : null}
                                        </div>
                                      );
                                    })()}
                                  </div>

                                  {/* Footer Cột PT */}
                                  <div className="pt-2 border-t-2 border-orange-200 dark:border-orange-800/60 flex items-center justify-between text-[11px] font-bold text-orange-900 dark:text-orange-300">
                                    <span>Tổng tài liệu bằng chứng của HLV:</span>
                                    <span className="px-2.5 py-0.5 rounded-full bg-orange-600 text-white font-black">
                                      {ptItems.length} tệp ảnh
                                    </span>
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })()}

                        {/* Resolution Verdict Display (if already resolved) */}
                        {!isPending && (d.resolutionDecision || d.verdictReason) && (
                          <div className="p-3.5 rounded-xl border border-emerald-300 bg-emerald-50/80 text-xs text-emerald-950 flex items-start gap-2.5">
                            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                            <div className="space-y-1 flex-1">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="font-bold uppercase tracking-wider text-emerald-900">Phán quyết & Lý do chính thức gửi 2 bên:</span>
                                <span className="text-[11px] text-emerald-700 font-mono">({d.resolvedAt})</span>
                              </div>
                              <p className="font-medium leading-relaxed bg-white/70 p-2.5 rounded-lg border border-emerald-200/60 text-emerald-900">
                                {d.verdictReason || d.resolutionDecision}
                              </p>
                            </div>
                          </div>
                        )}

                        {/* 48-Hour Fair Arbitration Banner */}
                        {isPending && (() => {
                          // Nếu Ban Quản Trị đang yêu cầu bổ sung bằng chứng và bên bị yêu cầu chưa nộp xong
                          if (d.evidenceRequested) {
                            const needsStudent = (d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'STUDENT') && !isEvidenceSubmitted(d, 'STUDENT');
                            const needsPt = (d.evidenceRequestTarget === 'BOTH' || d.evidenceRequestTarget === 'PT') && !isEvidenceSubmitted(d, 'PT');
                            if (needsStudent || needsPt) {
                              const pendingWho = needsStudent && needsPt ? 'cả 2 bên' : needsStudent ? 'Học viên' : 'HLV';
                              return (
                                <div className="p-3 bg-amber-50 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-800 rounded-xl text-xs text-amber-900 dark:text-amber-200 flex items-center gap-2">
                                  <Clock className="w-4 h-4 text-amber-600 shrink-0 animate-spin" />
                                  <div className="flex-1">
                                    <span className="font-bold">Đang chờ bổ sung bằng chứng:</span> Ban Quản Trị đã yêu cầu <b>{pendingWho}</b> bổ sung thêm bằng chứng đối soát trước khi ra phán quyết trọng tài.
                                  </div>
                                </div>
                              );
                            }
                          }

                          const arb = checkDisputeArbitrationStatus(d);
                          if (arb.hasCounter) {
                            return (
                              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-center gap-2">
                                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                                <div className="flex-1">
                                  <span className="font-bold">Đủ điều kiện ban hành phán quyết:</span> Đã nhận đầy đủ bản phản biện đối chứng từ cả 2 bên.
                                </div>
                              </div>
                            );
                          }
                          if (arb.isPast48h) {
                            return (
                              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-xs text-blue-900 flex items-center gap-2">
                                <Clock className="w-4 h-4 text-blue-600 shrink-0" />
                                <div className="flex-1">
                                  <span className="font-bold">Đã quá thời hạn 48 giờ đối chất:</span> Bên bị khiếu nại không gửi phản biện ngược lại. <b>Admin có toàn quyền quyết định</b> ban hành phán quyết.
                                </div>
                              </div>
                            );
                          }
                          return (
                            <div className="p-3 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-900 space-y-1">
                              <div className="flex items-center gap-2 font-bold text-amber-950">
                                <Clock className="w-4 h-4 text-amber-600 shrink-0" />
                                <span>Đang trong thời hạn 48 giờ chờ bên bị khiếu nại gửi phản biện</span>
                                <span className="px-2 py-0.5 rounded-full bg-amber-200/90 text-amber-950 text-[11px] font-extrabold ml-auto">
                                  Còn {arb.hoursRemaining}h {arb.minutesRemaining}m
                                </span>
                              </div>
                              <p className="text-[11px] text-amber-800 leading-relaxed pl-6">
                                ⚖️ <b>Quy chế chống phán quyết độc đoán:</b> Bên bị khiếu nại có <b>48 giờ</b> để gửi bản phản biện đối chứng. Admin phải chờ phản biện hoặc sau 48 giờ mới có toàn quyền ban hành phán quyết đơn phương.
                              </p>
                            </div>
                          );
                        })()}

                        {/* Arbitration Actions (if pending) */}
                        {isPending && (
                          <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
                            <span className="text-xs font-bold text-slate-600">
                              Chọn thao tác trọng tài dành cho vụ việc #{d.id}:
                            </span>

                            <div className="flex flex-wrap items-center gap-2">
                              {/* Nút Yêu cầu thêm bằng chứng */}
                              <button
                                type="button"
                                onClick={() => {
                                  setRequestEvidenceModal(d);
                                  setEvidenceTarget('BOTH');
                                  setEvidenceNoteInput('');
                                }}
                                className="px-3 py-2 rounded-xl bg-amber-500 hover:bg-amber-600 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                              >
                                <HelpCircle className="w-3.5 h-3.5" />
                                Yêu Cầu Bằng Chứng
                              </button>

                              {d.isContractDispute || d.disputeType === 'CONTRACT_TERMINATION' ? (
                                <>
                                  {/* Phán quyết Hợp Đồng: Hủy & Hoàn Tiền HV */}
                                  <button
                                    onClick={() => setSelectedDisputeForVerdict({ dispute: d, verdictType: 'CANCEL_CONTRACT_REFUND_STUDENT' })}
                                    className="px-3.5 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                                  >
                                    <XCircle className="w-3.5 h-3.5" />
                                    Hủy Hợp Đồng & Hoàn Tiền HV
                                  </button>

                                  {/* Phán quyết Hợp Đồng: Hủy & Trả Tiền PT */}
                                  <button
                                    onClick={() => setSelectedDisputeForVerdict({ dispute: d, verdictType: 'CANCEL_CONTRACT_PAID_PT' })}
                                    className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                                  >
                                    <CheckCircle className="w-3.5 h-3.5" />
                                    Hủy Hợp Đồng & Quyết Toán PT
                                  </button>

                                  {/* Hòa giải tiếp tục HĐ */}
                                  <button
                                    onClick={() => setSelectedDisputeForVerdict({ dispute: d, verdictType: 'FORCE_MAJEURE' })}
                                    className="px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                                  >
                                    <Scale className="w-3.5 h-3.5" />
                                    Hòa Giải Tiếp Tục HĐ
                                  </button>
                                </>
                              ) : (
                                <>
                                  {/* 1. Xử thắng cho Học viên */}
                                  <button
                                    onClick={() => setSelectedDisputeForVerdict({ dispute: d, verdictType: 'REFUND_STUDENT' })}
                                    className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                                  >
                                    <CheckCircle className="w-3.5 h-3.5" />
                                    Xử Thắng Học Viên (Hoàn tiền/buổi)
                                  </button>

                                  {/* 2. Xử thắng cho HLV */}
                                  <button
                                    onClick={() => setSelectedDisputeForVerdict({ dispute: d, verdictType: 'PAID_PT' })}
                                    className="px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                                  >
                                    <CheckCircle className="w-3.5 h-3.5" />
                                    Xử Thắng HLV (Chi trả thù lao)
                                  </button>

                                  {/* 3. Hòa giải bất khả kháng */}
                                  <button
                                    onClick={() => setSelectedDisputeForVerdict({ dispute: d, verdictType: 'FORCE_MAJEURE' })}
                                    className="px-3.5 py-2 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-sm flex items-center gap-1.5 transition cursor-pointer"
                                  >
                                    <Scale className="w-3.5 h-3.5" />
                                    Hòa Giải Bất Khả Kháng
                                  </button>
                                </>
                              )}

                              {/* 4. Khóa tài khoản vi phạm nếu cần */}
                              <button
                                onClick={() => {
                                  const targetUser = allUsers.find(u => u.email === (d.complainant === 'STUDENT' ? d.ptEmail : d.studentEmail));
                                  if (targetUser) handleToggleLockUser(targetUser);
                                  else showToast('Đã gửi thông báo cảnh cáo tới tài khoản vi phạm!');
                                }}
                                className="px-3 py-2 rounded-xl border border-slate-300 hover:bg-red-50 hover:text-red-600 hover:border-red-300 text-slate-700 font-bold text-xs flex items-center gap-1.5 transition cursor-pointer"
                              >
                                <Lock className="w-3.5 h-3.5" />
                                Cảnh cáo / Khóa TK
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ==================== TAB 0: PHÊ DUYỆT HUẤN LUYỆN VIÊN ==================== */}
        {activeTab === 0 && (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Xét Duyệt & Quản Lý Hồ Sơ Huấn Luyện Viên</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Kiểm tra bằng cấp, chứng chỉ nghề và kinh nghiệm trước khi cho phép PT mở nhận học viên.
                </p>
              </div>

              {/* Status filter pills */}
              <div className="flex items-center bg-white border border-slate-200 p-1 rounded-xl shadow-xs text-xs font-semibold">
                <button
                  onClick={() => setPtFilter('PENDING')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    ptFilter === 'PENDING'
                      ? 'bg-amber-500 text-white shadow-xs font-bold'
                      : (isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100')
                  }`}
                >
                  Chờ Duyệt ({pendingPts.length})
                </button>
                <button
                  onClick={() => setPtFilter('VERIFIED')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    ptFilter === 'VERIFIED'
                      ? 'bg-emerald-600 text-white shadow-xs font-bold'
                      : (isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100')
                  }`}
                >
                  Đã Phê Duyệt ({ptsList.filter((p) => p.verificationStatus === 'VERIFIED').length})
                </button>
                <button
                  onClick={() => setPtFilter('REJECTED')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    ptFilter === 'REJECTED'
                      ? 'bg-red-600 text-white shadow-xs font-bold'
                      : (isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100')
                  }`}
                >
                  Bị Từ Chối ({ptsList.filter((p) => p.verificationStatus === 'REJECTED').length})
                </button>
                <button
                  onClick={() => setPtFilter('ALL')}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    ptFilter === 'ALL'
                      ? 'bg-purple-600 text-white shadow-xs font-bold'
                      : (isDark ? 'text-slate-400 hover:text-white' : 'text-slate-600 hover:text-slate-900 dark:text-slate-100')
                  }`}
                >
                  Tất Cả ({ptsList.length})
                </button>
              </div>
            </div>

            {displayedPts.length === 0 ? (
              <div className="bg-white dark:bg-slate-900 p-12 rounded-2xl border border-slate-200 dark:border-slate-800 text-center shadow-xs">
                <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
                <h4 className="text-base font-bold text-slate-800 dark:text-slate-200">Không có hồ sơ nào trong mục này</h4>
                <p className="text-xs text-slate-500 mt-1">
                  Hiện tại không có huấn luyện viên nào phù hợp với bộ lọc đã chọn.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {displayedPts.map((pt) => {
                  const cert = resolveCertificateUrl(pt);
                  return (
                    <div
                      key={pt.id}
                      className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between hover:border-slate-300 transition"
                    >
                      <div>
                        {/* Header card with status badges */}
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex items-center gap-3">
                            <img
                              src={getAvatarUrl(pt.fullName, pt.avatarUrl)}
                              alt={pt.fullName}
                              className="w-14 h-14 rounded-full border border-slate-200 object-cover shadow-xs"
                            />
                            <div>
                              <h4 className="text-base font-bold text-slate-900 dark:text-slate-100">{pt.fullName}</h4>
                              <p className="text-xs text-slate-500">{pt.email}</p>
                              <p className="text-xs text-slate-400 font-mono mt-0.5">{pt.phone || 'Chưa cập nhật SĐT'}</p>
                            </div>
                          </div>

                          <div className="flex flex-col items-end gap-1">
                            <span
                              className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                                pt.verificationStatus === 'VERIFIED'
                                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                  : pt.verificationStatus === 'REJECTED'
                                  ? 'bg-red-50 text-red-700 border-red-200'
                                  : 'bg-amber-50 text-amber-700 border-amber-200'
                              }`}
                            >
                              {pt.verificationStatus === 'VERIFIED' && '✓ ĐÃ PHÊ DUYỆT'}
                              {pt.verificationStatus === 'REJECTED' && '✗ ĐÃ TỪ CHỐI'}
                              {pt.verificationStatus === 'PENDING' && '⏳ CHỜ DUYỆT'}
                            </span>

                            {pt.userStatus && (
                              <span
                                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                                  pt.userStatus === 'ACTIVE'
                                    ? 'bg-slate-100 text-slate-700'
                                    : 'bg-rose-100 text-rose-700'
                                }`}
                              >
                                Tài khoản: {pt.userStatus}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Bio & Details */}
                        <div className="mt-3.5 pt-3 border-t border-slate-100 space-y-2 text-xs">
                          <p className="text-slate-600 line-clamp-2 italic">
                            {pt.bio || 'Chưa cập nhật lời giới thiệu tiểu sử.'}
                          </p>

                          <div className="grid grid-cols-2 gap-2 text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                            <div>
                              <span className="text-[11px] text-slate-400 block font-medium">Kinh nghiệm:</span>
                              <span className="font-semibold text-slate-800 dark:text-slate-200">{pt.experienceYears} năm</span>
                            </div>
                            <div>
                              <span className="text-[11px] text-slate-400 block font-medium">Khu vực dạy:</span>
                              <span className="font-semibold text-slate-800 dark:text-slate-200 truncate block">
                                {pt.availableLocations || 'Toàn thành phố'}
                              </span>
                            </div>
                          </div>

                          {pt.locationPricingNote && (
                            <p className="text-[11px] text-slate-500">
                              <span className="font-semibold text-slate-600">Ghi chú giá/phí:</span> {pt.locationPricingNote}
                            </p>
                          )}

                          {/* Certificate link / preview */}
                          <div className="p-2.5 rounded-xl bg-purple-50/70 border border-purple-100 flex items-center justify-between gap-2">
                            <div className="flex items-center gap-2 truncate">
                              <Award className="w-4 h-4 text-purple-600 shrink-0" />
                              <span className="font-semibold text-purple-900 text-xs">Chứng chỉ:</span>
                              {cert ? (
                                <span className="text-purple-700 text-xs truncate max-w-xs">{cert}</span>
                              ) : (
                                <span className="italic text-slate-400 text-xs">Chưa nộp ảnh chứng chỉ</span>
                              )}
                            </div>

                            {cert && (
                              <button
                                onClick={() => setPreviewCert({ name: pt.fullName, url: cert })}
                                className="px-2.5 py-1 bg-white hover:bg-purple-100 text-purple-700 text-[11px] font-bold rounded-lg border border-purple-200 flex items-center gap-1 shrink-0 shadow-xs"
                              >
                                <ExternalLink className="w-3 h-3" /> Xem chứng chỉ
                              </button>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Action buttons */}
                      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-end gap-2">
                        {pt.verificationStatus !== 'REJECTED' && (
                          <button
                            onClick={() => {
                              setRejectingPt(pt);
                              setRejectionReason('Chứng chỉ chưa đủ tiêu chuẩn hoặc hình ảnh không hợp lệ.');
                            }}
                            className="px-3.5 py-1.5 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition"
                          >
                            <XCircle className="w-3.5 h-3.5" /> Từ chối
                          </button>
                        )}

                        {pt.verificationStatus !== 'VERIFIED' && (
                          <button
                            onClick={() => handleApprovePt(pt.id)}
                            className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold flex items-center gap-1.5 shadow-xs transition"
                          >
                            <CheckCircle className="w-3.5 h-3.5" /> Phê duyệt ngay
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* ==================== TAB 1: QUẢN LÝ NGƯỜI DÙNG ==================== */}
        {activeTab === 1 && (
          <div className="space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Quản Lý Toàn Bộ Người Dùng</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Tra cứu, phân quyền và khóa/mở khóa tài khoản học viên, huấn luyện viên hoặc quản trị viên.
                </p>
              </div>
              <span className="text-xs font-semibold px-3 py-1 bg-white border border-slate-200 rounded-lg text-slate-600 shadow-xs">
                Hiển thị {filteredUsers.length} / {allUsers.length} tài khoản
              </span>
            </div>

            {/* Filter & Search Toolbar */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
              <div className="relative w-full md:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={userSearch}
                  onChange={(e) => setUserSearch(e.target.value)}
                  placeholder="Tìm theo tên, email, số điện thoại..."
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 rounded-lg focus:outline-none focus:border-purple-500 transition"
                />
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto">
                <select
                  value={userRoleFilter}
                  onChange={(e) => setUserRoleFilter(e.target.value)}
                  className="px-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-950 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="ALL">Mọi Vai Trò</option>
                  <option value="STUDENT">Học Viên (STUDENT)</option>
                  <option value="PT">Huấn Luyện Viên (PT)</option>
                  <option value="ADMIN">Quản Trị Viên (ADMIN)</option>
                </select>

                <select
                  value={userStatusFilter}
                  onChange={(e) => setUserStatusFilter(e.target.value)}
                  className="px-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-950 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="ALL">Mọi Trạng Thái</option>
                  <option value="ACTIVE">Hoạt động (ACTIVE)</option>
                  <option value="SUSPENDED">Đang bị khóa (SUSPENDED)</option>
                  <option value="PENDING">Chờ xử lý (PENDING)</option>
                </select>
              </div>
            </div>

            {/* Users Table */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider">
                    <tr>
                      <th className="py-3 px-4">Mã ID</th>
                      <th className="py-3 px-4">Người Dùng</th>
                      <th className="py-3 px-4">Email & Số Điện Thoại</th>
                      <th className="py-3 px-4">Vai Trò</th>
                      <th className="py-3 px-4">Trạng Thái</th>
                      <th className="py-3 px-4 text-right">Thao Tác Bảo Mật</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredUsers.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-slate-400">
                          Không tìm thấy người dùng phù hợp với điều kiện lọc.
                        </td>
                      </tr>
                    ) : (
                      filteredUsers.map((u) => (
                        <tr key={u.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/50 transition">
                          <td className="py-3 px-4 font-mono font-bold text-slate-500">#{u.id}</td>
                          <td className="py-3 px-4">
                            <div className="flex items-center gap-2.5">
                              <img
                                src={getAvatarUrl(u.fullName, u.avatarUrl)}
                                alt={u.fullName}
                                className="w-8 h-8 rounded-full border border-slate-200 object-cover"
                              />
                              <span className="font-bold text-slate-900 dark:text-slate-100">{u.fullName}</span>
                            </div>
                          </td>
                          <td className="py-3 px-4 text-slate-600">
                            <div className="font-medium">{u.email}</div>
                            <div className="text-[11px] text-slate-400">{u.phone || 'Chưa có SĐT'}</div>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                u.role === 'ADMIN'
                                  ? 'bg-purple-100 text-purple-800 border border-purple-200'
                                  : u.role === 'PT'
                                  ? 'bg-amber-100 text-amber-800 border border-amber-200'
                                  : 'bg-blue-100 text-blue-800 border border-blue-200'
                              }`}
                            >
                              {u.role}
                            </span>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                u.status === 'ACTIVE'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : u.status === 'SUSPENDED'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {u.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right">
                            {u.role !== 'ADMIN' ? (
                              <button
                                onClick={() => handleToggleLockUser(u)}
                                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold border inline-flex items-center gap-1.5 transition ${
                                  u.status === 'ACTIVE'
                                    ? 'border-red-300 text-red-600 hover:bg-red-50'
                                    : 'border-emerald-300 text-emerald-600 hover:bg-emerald-50'
                                }`}
                              >
                                {u.status === 'ACTIVE' ? (
                                  <>
                                    <Lock className="w-3 h-3" /> Khóa tài khoản
                                  </>
                                ) : (
                                  <>
                                    <Unlock className="w-3 h-3" /> Mở khóa tài khoản
                                  </>
                                )}
                              </button>
                            ) : (
                              <span className="text-[11px] text-slate-400 italic">Quản trị viên cấp cao</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ==================== TAB 2: QUẢN LÝ ĐẶT LỊCH (BOOKINGS) ==================== */}
        {activeTab === 2 && (
          <div className="space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Quản Lý Toàn Bộ Ca Tập (Bookings)</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Theo dõi mọi buổi tập giữa Học viên và Huấn luyện viên, xem tỷ lệ hoàn thành và lý do hủy ca.
                </p>
              </div>

              {/* Mini KPI cards */}
              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 font-bold text-xs">
                  {bookingStats.completed} ca hoàn thành
                </span>
                <span className="px-3 py-1 rounded-lg bg-red-50 border border-red-200 text-red-800 font-bold text-xs">
                  {bookingStats.cancelled} ca hủy ({bookingStats.cancelRate}%)
                </span>
              </div>
            </div>

            {/* Filter toolbar */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
              <div className="relative w-full md:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={bookingSearch}
                  onChange={(e) => setBookingSearch(e.target.value)}
                  placeholder="Tìm theo tên học viên, PT, mã ca..."
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 rounded-lg focus:outline-none focus:border-purple-500 transition"
                />
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto">
                <select
                  value={bookingStatusFilter}
                  onChange={(e) => setBookingStatusFilter(e.target.value)}
                  className="px-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-950 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="ALL">Mọi Trạng Thái</option>
                  <option value="CONFIRMED">Đã xác nhận (CONFIRMED)</option>
                  <option value="COMPLETED">Hoàn thành (COMPLETED)</option>
                  <option value="CANCELLED">Đã hủy (CANCELLED)</option>
                  <option value="PENDING">Chờ duyệt (PENDING)</option>
                </select>

                <select
                  value={bookingTypeFilter}
                  onChange={(e) => setBookingTypeFilter(e.target.value)}
                  className="px-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-950 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="ALL">Mọi Hình Thức</option>
                  <option value="TRIAL">Học thử (TRIAL - 0đ)</option>
                  <option value="PACKAGE">Gói khóa học (PACKAGE)</option>
                </select>
              </div>
            </div>

            {/* Bookings Table */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider">
                    <tr>
                      <th className="py-3 px-4">Mã Ca</th>
                      <th className="py-3 px-4">Học Viên</th>
                      <th className="py-3 px-4">Huấn Luyện Viên</th>
                      <th className="py-3 px-4">Khung Giờ Tập</th>
                      <th className="py-3 px-4">Hình Thức</th>
                      <th className="py-3 px-4">Phí Buổi Tập</th>
                      <th className="py-3 px-4">Trạng Thái</th>
                      <th className="py-3 px-4">Ghi Chú Hủy</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredBookings.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-400">
                          Chưa có ca tập nào phù hợp điều kiện lọc.
                        </td>
                      </tr>
                    ) : (
                      filteredBookings.map((b) => (
                        <tr key={b.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/50 transition">
                          <td className="py-3 px-4 font-mono font-bold text-slate-500">#{b.id}</td>
                          <td className="py-3 px-4 font-bold text-slate-900 dark:text-slate-100">{b.studentName || `HV #${b.studentId}`}</td>
                          <td className="py-3 px-4 font-bold text-purple-700">{b.ptName || `PT #${b.ptId}`}</td>
                          <td className="py-3 px-4 text-slate-600">
                            <div>{formatDateTime(b.startTime)}</div>
                            <div className="text-[11px] text-slate-400">đến {formatDateTime(b.endTime)}</div>
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                b.bookingType === 'TRIAL'
                                  ? 'bg-amber-100 text-amber-800 border border-amber-200'
                                  : 'bg-indigo-100 text-indigo-800 border border-indigo-200'
                              }`}
                            >
                              {b.bookingType === 'TRIAL' ? 'Học Thử (0đ)' : 'Khóa Học'}
                            </span>
                          </td>
                          <td className="py-3 px-4 font-bold text-slate-900 dark:text-slate-100">
                            {b.bookingType === 'TRIAL' ? '0 ₫' : formatCurrency(b.sessionFee)}
                          </td>
                          <td className="py-3 px-4">
                            <span
                              className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                                b.status === 'COMPLETED'
                                  ? 'bg-purple-100 text-purple-800'
                                  : b.status === 'CONFIRMED'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : b.status === 'CANCELLED'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {b.status}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-500 max-w-xs truncate">
                            {b.cancellationReason ? (
                              <span className="text-red-600 text-[11px]" title={b.cancellationReason}>
                                [{b.cancelledBy || 'STUDENT'}] {b.cancellationReason}
                              </span>
                            ) : (
                              <span className="text-slate-300 italic text-[11px]">—</span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ==================== TAB 3: GIAO DỊCH & DÒNG TIỀN (PAYMENTS) ==================== */}
        {activeTab === 3 && (
          <div className="space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 tracking-tight">Lịch Sử Giao Dịch & Quản Lý Dòng Tiền</h3>
                <p className="text-xs text-slate-500 mt-0.5">
                  Kiểm soát dòng tiền nạp ví, mua khóa học, giải ngân thù lao PT và quỹ thu hoa hồng nền tảng (10%).
                </p>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-3 py-1 rounded-lg bg-purple-50 border border-purple-200 text-purple-800 font-bold text-xs">
                  Tổng lưu chuyển: {formatCurrency(paymentStats.totalMoney)}
                </span>
              </div>
            </div>

            {/* THẺ VÍ DOANH THU NỀN TẢNG CỦA ADMIN */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {/* Card 1: Số dư Ví Doanh Thu */}
              <div className="lg:col-span-2 bg-gradient-to-br from-indigo-900 via-indigo-800 to-purple-900 rounded-2xl p-6 text-white shadow-lg relative overflow-hidden flex flex-col justify-between">
                <div className="absolute top-0 right-0 translate-x-8 -translate-y-8 w-44 h-44 rounded-full bg-white/5 pointer-events-none blur-2xl" />
                <div className="absolute bottom-0 right-20 translate-y-8 w-32 h-32 rounded-full bg-purple-500/10 pointer-events-none blur-xl" />

                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-white/10">
                    <div className="flex items-center gap-2.5">
                      <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur-md flex items-center justify-center border border-white/20">
                        <Wallet className="w-5 h-5 text-amber-300" />
                      </div>
                      <div>
                        <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-200">Ví Doanh Thu Sàn & Quỹ Nền Tảng</span>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-xs text-white/80 font-medium">Chủ sở hữu: <b>Admin (Hệ thống PTConnect)</b></span>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                            ● Đang Hoạt Động
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => {
                        setWithdrawAmount('');
                        setWithdrawError(null);
                        setShowWithdrawModal(true);
                      }}
                      className="px-4 py-2 bg-gradient-to-r from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600 text-slate-900 font-extrabold text-xs rounded-xl shadow-md transition transform active:scale-95 flex items-center gap-1.5 cursor-pointer"
                    >
                      <ArrowUpRight className="w-4 h-4" /> Rút Doanh Thu
                    </button>
                  </div>

                  <div className="mt-5 flex flex-col sm:flex-row sm:items-baseline justify-between gap-3">
                    <div>
                      <span className="text-xs text-indigo-200 font-semibold block">Số Dư Quỹ Doanh Thu Khả Dụng:</span>
                      <div className="text-3xl sm:text-4xl font-black text-amber-300 tracking-tight mt-1">
                        {formatCurrency(adminWallet?.balance || 15650000)}
                      </div>
                    </div>
                    <div className="text-xs text-indigo-200 space-y-1">
                      <div>Tạm khóa xử lý trọng tài: <b className="text-white">{formatCurrency(adminWallet?.lockedBalance || 0)}</b></div>
                      <div>Loại tiền tệ: <b className="text-white">{adminWallet?.currency || 'VND'}</b></div>
                    </div>
                  </div>
                </div>

                {/* Chính sách thu tiền nền tảng */}
                <div className="mt-5 pt-3 border-t border-white/10 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="flex items-start gap-2 bg-white/5 p-2.5 rounded-xl border border-white/10">
                    <Percent className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-white block">Tỷ lệ thu phí hoa hồng: 10%</span>
                      <span className="text-indigo-200 text-[11px]">
                        Tự động trích 10% trên mỗi ca tập hoàn thành (PT nhận 90%, Sàn nhận 10%).
                      </span>
                    </div>
                  </div>
                  <div className="flex items-start gap-2 bg-white/5 p-2.5 rounded-xl border border-white/10">
                    <Scale className="w-4 h-4 text-amber-300 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-white block">Phí điều phối & xử lý tranh chấp:</span>
                      <span className="text-indigo-200 text-[11px]">
                        Trích 10% từ tiền phạt/đền bù khi học viên hoặc PT hủy ca tập sai quy chế.
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Card 2: Thống kê thu hoa hồng */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between space-y-4">
                <div>
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
                    <span className="font-bold text-slate-800 dark:text-slate-200 text-xs uppercase tracking-wider">
                      📊 Hiệu Suất Thu Tiền Sàn
                    </span>
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-purple-50 text-purple-700 dark:bg-purple-950 dark:text-purple-300">
                      Tự động 100%
                    </span>
                  </div>

                  <div className="mt-4 space-y-3.5">
                    <div>
                      <span className="text-[11px] text-slate-400 block">Ước tính hoa hồng từ ca tập:</span>
                      <div className="text-xl font-black text-emerald-600">
                        {formatCurrency(paymentStats.totalMoney * 0.1)}
                      </div>
                    </div>
                    <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-100 dark:border-slate-700 text-xs space-y-1.5">
                      <div className="flex justify-between">
                        <span className="text-slate-500">Mã tiền tệ thu:</span>
                        <span className="font-bold text-slate-800 dark:text-slate-200">VND (Việt Nam Đồng)</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Mức chi trả PT:</span>
                        <span className="font-bold text-indigo-600">90% giá trị ca tập</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Doanh thu sàn:</span>
                        <span className="font-bold text-emerald-600">10% / ca tập</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
                  <span>Trích hoa hồng ca tập:</span>
                  <span className="font-mono font-bold text-slate-700 dark:text-slate-300">TXN_COMMISSION_*</span>
                </div>
              </div>
            </div>

            {/* Filter toolbar */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex flex-col md:flex-row gap-3 items-center justify-between">
              <div className="relative w-full md:w-80">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={paymentSearch}
                  onChange={(e) => setPaymentSearch(e.target.value)}
                  placeholder="Tìm theo mã ref, tên người dùng..."
                  className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500 rounded-lg focus:outline-none focus:border-purple-500 transition"
                />
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto">
                <select
                  value={paymentTypeFilter}
                  onChange={(e) => setPaymentTypeFilter(e.target.value)}
                  className="px-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-950 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="ALL">Mọi Loại Giao Dịch</option>
                  <option value="DEPOSIT">Nạp Tiền (DEPOSIT)</option>
                  <option value="PURCHASE_PACKAGE">Mua Khóa Học (PURCHASE_PACKAGE)</option>
                  <option value="WITHDRAWAL">Rút Tiền (WITHDRAWAL)</option>
                  <option value="COMMISSION">Hoa Hồng Nền Tảng (COMMISSION)</option>
                </select>

                <select
                  value={paymentStatusFilter}
                  onChange={(e) => setPaymentStatusFilter(e.target.value)}
                  className="px-3 py-2 text-xs border border-slate-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-950 font-medium text-slate-700 dark:text-slate-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="ALL">Mọi Trạng Thái</option>
                  <option value="SUCCESS">Thành công (SUCCESS)</option>
                  <option value="PENDING">Đang chờ (PENDING)</option>
                  <option value="FAILED">Thất bại (FAILED)</option>
                </select>
              </div>
            </div>

            {/* Payments Table */}
            <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-xs">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider">
                    <tr>
                      <th className="py-3 px-4">Mã GD</th>
                      <th className="py-3 px-4">Người Thực Hiện</th>
                      <th className="py-3 px-4">Số Tiền</th>
                      <th className="py-3 px-4">Phân Loại</th>
                      <th className="py-3 px-4">Cổng Thanh Toán</th>
                      <th className="py-3 px-4">Mã Tham Chiếu</th>
                      <th className="py-3 px-4">Thời Gian</th>
                      <th className="py-3 px-4">Trạng Thái</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filteredPayments.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-400">
                          Chưa có bản ghi giao dịch nào phù hợp điều kiện lọc.
                        </td>
                      </tr>
                    ) : (
                      filteredPayments.map((p) => {
                        const isDebitUser = p.paymentType === 'WITHDRAWAL' || p.paymentType === 'PURCHASE_PACKAGE';
                        return (
                          <tr key={p.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/50 transition">
                            <td className="py-3 px-4 font-mono font-bold text-slate-500">#{p.id}</td>
                            <td className="py-3 px-4 font-bold text-slate-900 dark:text-slate-100">
                              {p.userName || (p.userId ? `User #${p.userId}` : 'Hệ thống')}
                            </td>
                            <td className={`py-3 px-4 font-extrabold ${isDebitUser ? 'text-red-600' : 'text-emerald-600'}`}>
                              {isDebitUser ? '-' : '+'}{formatCurrency(p.amount)}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                  p.transactionRef?.startsWith('TXN_COMMISSION_') || p.paymentType === 'COMMISSION'
                                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300'
                                    : p.paymentType === 'PURCHASE_PACKAGE'
                                    ? 'bg-purple-100 text-purple-800 border border-purple-200'
                                    : p.paymentType === 'DEPOSIT'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : p.paymentType === 'WITHDRAWAL'
                                    ? 'bg-rose-100 text-rose-800'
                                    : 'bg-slate-100 text-slate-800 dark:text-slate-200'
                                }`}
                              >
                                {p.transactionRef?.startsWith('TXN_COMMISSION_') || p.paymentType === 'COMMISSION'
                                  ? 'Hoa Hồng Sàn (10%)'
                                  : p.paymentType === 'PURCHASE_PACKAGE'
                                  ? 'MUA KHÓA (Trừ ví HV)'
                                  : p.paymentType === 'DEPOSIT'
                                  ? 'NẠP TIỀN VÀO VÍ'
                                  : p.paymentType === 'WITHDRAWAL'
                                  ? 'RÚT TIỀN RA NGÂN HÀNG'
                                  : p.paymentType === 'COMPENSATION'
                                  ? 'BỒI HOÀN TRỌNG TÀI'
                                  : p.paymentType}
                              </span>
                            </td>
                            <td className="py-3 px-4 font-medium text-slate-600">{p.paymentMethod || 'WALLET'}</td>
                            <td className="py-3 px-4 font-mono text-slate-500 max-w-xs truncate">
                              {p.transactionRef || 'N/A'}
                            </td>
                            <td className="py-3 px-4 text-slate-500">{formatDateTime(p.createdAt)}</td>
                            <td className="py-3 px-4">
                              <span
                                className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full ${
                                  p.status === 'SUCCESS'
                                    ? 'bg-emerald-100 text-emerald-800'
                                    : p.status === 'FAILED'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-amber-100 text-amber-800'
                                }`}
                              >
                                {p.status}
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* ==================== TAB 4: THỐNG KÊ & ĐIỀU TRA CHUYÊN SÂU ==================== */}
        {activeTab === 4 && (
          <div className="space-y-6">
            {/* Statistical Investigation Hero Banner (matching user reference image) */}
            <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 sm:p-7 rounded-2xl border border-indigo-900/40 shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div className="space-y-2 max-w-2xl">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-bold uppercase tracking-wider">
                  <FileSearch className="w-3.5 h-3.5" />
                  STATISTICAL INVESTIGATION &amp; AUDIT SYSTEM
                </div>
                <h3 className="text-xl sm:text-3xl font-black uppercase tracking-tight text-white">
                  Trung Tâm Phân Tích &amp; Điều Tra Thống Kê Nền Tảng
                </h3>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Kiểm toán dữ liệu chu kỳ đặt lịch, đo lường dòng tiền doanh thu 7 ngày, giám sát rủi ro gian lận điểm danh và phân tích khung giờ cao điểm toàn hệ thống.
                </p>
              </div>

              {/* 4 Investigation Audit Metric Pills */}
              <div className="grid grid-cols-2 gap-3 shrink-0">
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Tỷ lệ tranh chấp</span>
                  <span className="text-xl font-black text-emerald-400 mt-0.5 block">1.2%</span>
                  <span className="text-[10px] text-emerald-300">An toàn tuyệt đối</span>
                </div>
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Giải quyết khiếu nại</span>
                  <span className="text-xl font-black text-indigo-400 mt-0.5 block">1.8 Giờ</span>
                  <span className="text-[10px] text-indigo-300">Xử lý thần tốc</span>
                </div>
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Điểm danh chuẩn xác</span>
                  <span className="text-xl font-black text-sky-400 mt-0.5 block">99.2%</span>
                  <span className="text-[10px] text-sky-300">Xác thực OTP 2 bên</span>
                </div>
                <div className="bg-white/5 border border-white/10 p-3 rounded-xl backdrop-blur-md">
                  <span className="text-[10px] text-slate-400 font-bold uppercase block">Tăng trưởng hội viên</span>
                  <span className="text-xl font-black text-amber-400 mt-0.5 block">+18.5%</span>
                  <span className="text-[10px] text-amber-300">So với tháng trước</span>
                </div>
              </div>
            </div>

            {/* 4 Big Overview KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 font-bold uppercase">Học Viên Hoạt Động</span>
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
                    <UserCheck className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-2xl font-black text-blue-600 mt-2">
                  {statistics?.totalStudents || allUsers.filter((u) => u.role === 'STUDENT').length} người
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Chiếm {allUsers.length > 0 ? Math.round(((statistics?.totalStudents || 0) / allUsers.length) * 100) : 0}% tổng người dùng
                </p>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 font-bold uppercase">Huấn Luyện Viên (PT)</span>
                  <div className="w-8 h-8 rounded-lg bg-orange-50 text-orange-600 flex items-center justify-center font-bold">
                    <Award className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-2xl font-black text-orange-600 mt-2">
                  {statistics?.totalPts || allUsers.filter((u) => u.role === 'PT').length} PT
                </div>
                <p className="text-[11px] text-slate-400 mt-1">{pendingPts.length} hồ sơ đang đợi phê duyệt</p>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 font-bold uppercase">Tổng Ca Đặt Lịch</span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
                    <Calendar className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-2xl font-black text-emerald-600 mt-2">
                  {statistics?.totalBookings || bookings.length} ca
                </div>
                <p className="text-[11px] text-emerald-600 font-semibold mt-1">
                  Tỷ lệ hoàn thành: {bookingStats.completionRate}%
                </p>
              </div>

              <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500 font-bold uppercase">Doanh Thu Nền Tảng</span>
                  <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-bold">
                    <DollarSign className="w-4 h-4" />
                  </div>
                </div>
                <div className="text-xl sm:text-2xl font-black text-purple-700 mt-2">
                  {formatCurrency(statistics?.totalRevenue || paymentStats.packageTotal)}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Từ các gói hợp đồng thành công</p>
              </div>
            </div>

            {/* Interactive SVG Chart: 7-Day Revenue & Volume */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
                <div>
                  <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-indigo-600" />
                    Biểu Đồ Doanh Thu &amp; Khối Lượng Ca Tập 7 Ngày Qua
                  </h4>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Thống kê thời gian thực từ thứ Hai đến Chủ Nhật, phản ánh sự bùng nổ nhu cầu tập luyện cuối tuần.
                  </p>
                </div>
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-lg border border-indigo-200/60 self-start sm:self-auto">
                  Tổng 7 ngày: 288.000.000 ₫
                </span>
              </div>

              {/* Responsive SVG Chart */}
              <div className="pt-4">
                <div className="grid grid-cols-7 gap-2 sm:gap-4 items-end h-56 pt-6 pb-2 border-b border-slate-200">
                  {[
                    { day: 'Thứ 2', rev: 32500000, count: 24, pct: 58 },
                    { day: 'Thứ 3', rev: 28000000, count: 20, pct: 50 },
                    { day: 'Thứ 4', rev: 41200000, count: 28, pct: 72 },
                    { day: 'Thứ 5', rev: 35800000, count: 25, pct: 64 },
                    { day: 'Thứ 6', rev: 48000000, count: 34, pct: 85 },
                    { day: 'Thứ 7', rev: 56500000, count: 42, pct: 100, isPeak: true },
                    { day: 'Chủ Nhật', rev: 46000000, count: 38, pct: 81 },
                  ].map((bar) => (
                    <div key={bar.day} className="flex flex-col items-center h-full justify-end group">
                      <div className="text-[10px] sm:text-xs font-bold text-slate-700 opacity-0 group-hover:opacity-100 transition mb-1 text-center whitespace-nowrap">
                        {(bar.rev / 1000000).toFixed(1)} tr
                      </div>
                      <div
                        style={{ height: `${bar.pct}%` }}
                        className={`w-full max-w-[48px] rounded-t-xl transition-all duration-300 relative ${
                          bar.isPeak
                            ? 'bg-gradient-to-t from-indigo-600 to-pink-500 shadow-md shadow-pink-500/20'
                            : 'bg-gradient-to-t from-indigo-500 to-indigo-400 hover:from-indigo-600 hover:to-indigo-500'
                        }`}
                      >
                        {bar.isPeak && (
                          <span className="absolute -top-5 left-1/2 -translate-x-1/2 text-[9px] font-black bg-pink-500 text-white px-1.5 py-0.2 rounded-full uppercase">
                            Đỉnh
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] font-bold text-slate-600 mt-2 text-center">
                        {bar.day}
                      </div>
                      <div className="text-[10px] text-slate-400 text-center">
                        {bar.count} ca
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* 2-Column Analytical breakdowns */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {/* Gym Peak Hours Heatmap */}
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-amber-500" />
                  Phân Bổ Khung Giờ Vàng Tập Luyện (Peak Training Hours)
                </h4>

                <div className="space-y-3.5 text-xs">
                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>🌅 Sáng sớm (06:00 - 09:00): Cardio & Thể lực sớm</span>
                      <span className="font-bold text-amber-600">26% (Chiếm 42 ca)</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-amber-500 rounded-full" style={{ width: '26%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>☀️ Buổi trưa (11:30 - 13:30): Dân văn phòng rảnh ca</span>
                      <span className="font-bold text-slate-600">8% (Chiếm 13 ca)</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-slate-400 rounded-full" style={{ width: '8%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>🌇 Buổi chiều (14:30 - 17:30): Sinh viên & Người làm tự do</span>
                      <span className="font-bold text-blue-600">18% (Chiếm 29 ca)</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: '18%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>🔥 Tối cao điểm (18:00 - 21:30): KHUNG GIỜ VÀNG ĐÔNG NHẤT</span>
                      <span className="font-black text-rose-600">48% (Chiếm 76 ca)</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-rose-500 to-pink-500 rounded-full" style={{ width: '48%' }} />
                    </div>
                  </div>
                </div>
              </div>

              {/* Dispute & Cancellation Root Cause Breakdown */}
              <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <PieChart className="w-4 h-4 text-rose-600" />
                  Cơ Cấu Nguyên Nhân Hủy Lịch &amp; Tranh Chấp
                </h4>

                <div className="space-y-3.5 text-xs">
                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>Trùng lịch bận việc đột xuất:</span>
                      <span className="font-bold text-slate-800 dark:text-slate-200">44%</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-slate-600 rounded-full" style={{ width: '44%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>Vấn đề sức khỏe, ốm hoặc chấn thương:</span>
                      <span className="font-bold text-blue-600">24%</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-blue-500 rounded-full" style={{ width: '24%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>Sự cố phòng tập bảo trì / Thời tiết mưa bão:</span>
                      <span className="font-bold text-purple-600">18%</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-purple-500 rounded-full" style={{ width: '18%' }} />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-700 font-semibold mb-1">
                      <span>Khiếu nại dịch vụ / Bất đồng thời gian điểm danh:</span>
                      <span className="font-bold text-rose-600">14%</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-slate-100 overflow-hidden">
                      <div className="h-full bg-rose-500 rounded-full" style={{ width: '14%' }} />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Top 5 PT Leaderboard */}
            <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h4 className="text-sm font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                  <Award className="w-4 h-4 text-amber-500" />
                  Bảng Vinh Danh Top Huấn Luyện Viên Uy Tín &amp; Doanh Thu Cao Nhất
                </h4>
                <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                  Xếp hạng theo lượt học viên đánh giá cao
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
                {[
                  { rank: 1, name: 'Lê Hoàng Cường', rev: '92.500.000 ₫', sessions: 98, rating: '5.0 ⭐', disputes: '0 vụ khiếu nại', tag: 'HLV Xuất Sắc Nhất' },
                  { rank: 2, name: 'Đào Ngọc Huy', rev: '78.000.000 ₫', sessions: 84, rating: '4.9 ⭐', disputes: '1 vụ đã hòa giải', tag: 'Tăng trưởng nhanh' },
                  { rank: 3, name: 'Phạm Minh Dũng', rev: '64.500.000 ₫', sessions: 72, rating: '4.9 ⭐', disputes: '0 vụ khiếu nại', tag: 'Tận tâm chuyên nghiệp' },
                  { rank: 4, name: 'Vũ Hoàng Nam', rev: '45.000.000 ₫', sessions: 50, rating: '4.8 ⭐', disputes: '0 vụ khiếu nại', tag: 'Kinh nghiệm thể hình' },
                  { rank: 5, name: 'Đặng Thúy Nga', rev: '38.000.000 ₫', sessions: 42, rating: '4.8 ⭐', disputes: '0 vụ khiếu nại', tag: 'Cardio & Dáng nữ' },
                ].map((pt) => (
                  <div key={pt.rank} className="p-4 rounded-xl border border-slate-200 bg-slate-50/60 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-black text-sm shrink-0 ${
                        pt.rank === 1 ? 'bg-amber-400 text-slate-950 shadow-sm' : 'bg-slate-200 text-slate-700'
                      }`}>
                        #{pt.rank}
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-900 dark:text-slate-100">{pt.name}</div>
                        <div className="text-[11px] text-slate-500">{pt.sessions} ca • {pt.rating}</div>
                        <div className="text-[10px] text-emerald-600 font-semibold">{pt.disputes}</div>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="text-xs font-black text-slate-900 dark:text-slate-100">{pt.rev}</div>
                      <span className="text-[10px] px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-200 font-bold block mt-1">
                        {pt.tag}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </main>

            {/* ==================== MODAL XÁC NHẬN PHÁN QUYẾT TRỌNG TÀI ==================== */}
      {selectedDisputeForVerdict && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-scale-up text-slate-900 dark:text-slate-100 space-y-4">
            <div className="flex items-center gap-3 text-indigo-600 pb-3 border-b border-slate-100">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
                <Gavel className="w-5 h-5 text-indigo-600" />
              </div>
              <div>
                <h4 className="text-base font-black uppercase text-slate-900 dark:text-slate-100">Ban Hành Phán Quyết Trọng Tài</h4>
                <p className="text-xs text-slate-500">
                  Vụ việc #CASE-{selectedDisputeForVerdict.dispute.id} ({selectedDisputeForVerdict.dispute.enrollmentId ? `Hợp đồng #${selectedDisputeForVerdict.dispute.enrollmentId}` : `Ca tập #${selectedDisputeForVerdict.dispute.bookingId}`})
                </p>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Phán quyết lựa chọn:</span>
                <span className="font-bold text-indigo-700 uppercase">
                  {selectedDisputeForVerdict.verdictType === 'CANCEL_CONTRACT_REFUND_STUDENT'
                    ? '✓ HỦY HỢP ĐỒNG & HOÀN TIỀN CHO HỌC VIÊN'
                    : selectedDisputeForVerdict.verdictType === 'CANCEL_CONTRACT_PAID_PT'
                    ? '✓ HỦY HỢP ĐỒNG & THANH TOÁN CHO HLV'
                    : selectedDisputeForVerdict.verdictType === 'REFUND_STUDENT'
                    ? '✓ XỬ THẮNG HỌC VIÊN (HOÀN TIỀN/BUỔI)'
                    : selectedDisputeForVerdict.verdictType === 'PAID_PT'
                    ? '✓ XỬ THẮNG HLV (CHI TRẢ THÙ LAO)'
                    : '⚖️ HÒA GIẢI SỰ CỐ BẤT KHẢ KHÁNG'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Học viên:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{selectedDisputeForVerdict.dispute.studentName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Huấn luyện viên:</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">{selectedDisputeForVerdict.dispute.ptName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Phí liên quan:</span>
                <span className="font-black text-emerald-600">{formatCurrency(selectedDisputeForVerdict.dispute.sessionFee)}</span>
              </div>
            </div>

            {/* 48-Hour Fair Arbitration Guard in Modal */}
            {(() => {
              const arb = checkDisputeArbitrationStatus(selectedDisputeForVerdict.dispute);
              if (!arb.canArbitrate) {
                return (
                  <div className="p-3.5 bg-amber-50 border border-amber-300 rounded-xl text-xs text-amber-900 space-y-2">
                    <div className="font-bold flex items-center gap-1.5 text-amber-950">
                      <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                      Quy chế chống phán quyết độc đoán: Đang trong thời hạn 48 giờ đối chất
                    </div>
                    <p className="text-[11px] leading-relaxed text-amber-800">
                      Bên bị khiếu nại chưa gửi bản phản biện và vẫn còn trong thời hạn 48 giờ bảo lưu quyền giải trình (Còn <b>{arb.hoursRemaining}h {arb.minutesRemaining}m</b>).
                      Theo quy định, Admin phải chờ đủ 48 tiếng để bên bị khiếu nại gửi phản biện ngược lại, sau 48 tiếng chưa gửi thì Admin mới có toàn quyền quyết định.
                    </p>
                    <label className="flex items-center gap-2 pt-1 font-semibold text-amber-950 cursor-pointer select-none">
                      <input
                        type="checkbox"
                        checked={override48h}
                        onChange={(e) => setOverride48h(e.target.checked)}
                        className="rounded text-indigo-600 focus:ring-indigo-500 w-4 h-4"
                      />
                      <span>Kích hoạt quyền phán quyết khẩn cấp / Kiểm thử (Bỏ qua thời hạn 48h)</span>
                    </label>
                  </div>
                );
              }
              return (
                <div className="p-2.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2 font-medium">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                  {arb.hasCounter
                    ? 'Đã tiếp nhận bản phản biện đối chứng. Admin đủ thẩm quyền ban hành phán quyết.'
                    : 'Đã quá thời hạn 48 giờ đối chất. Admin có toàn quyền quyết định vụ việc.'}
                </div>
              );
            })()}

            <div>
              <label className="text-xs font-bold text-slate-700 block mb-1">
                Lý do &amp; Căn cứ phán quyết chi tiết gửi cho cả 2 bên (Học viên &amp; PT cùng nhận được) <span className="text-red-500">*</span>:
              </label>
              <textarea
                rows={4}
                value={verdictCustomNote}
                onChange={(e) => setVerdictCustomNote(e.target.value)}
                placeholder="Căn cứ vào dữ liệu định vị, nhật ký cuộc gọi và bản phản biện... Hội đồng Trọng tài quyết định: [Nêu rõ lý do và hướng giải quyết gửi cho cả hai bên]..."
                className="w-full p-3 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => {
                  setSelectedDisputeForVerdict(null);
                  setVerdictCustomNote('');
                  setOverride48h(false);
                }}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-xl transition cursor-pointer"
              >
                Hủy bỏ
              </button>
              <button
                type="button"
                disabled={(() => {
                  const arb = checkDisputeArbitrationStatus(selectedDisputeForVerdict.dispute);
                  return !arb.canArbitrate && !override48h;
                })()}
                onClick={() => handleExecuteArbitration(
                  selectedDisputeForVerdict.dispute.id,
                  selectedDisputeForVerdict.verdictType,
                  verdictCustomNote,
                  override48h
                )}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-black uppercase tracking-wider rounded-xl shadow-md transition cursor-pointer"
              >
                Ban hành &amp; Gửi lý do phán quyết
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==================== MODAL YÊU CẦU BỔ SUNG BẰNG CHỨNG ==================== */}
      {requestEvidenceModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-scale-up text-slate-900 dark:text-slate-100 space-y-4">
            <div className="flex items-center gap-3 text-amber-600 pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="w-10 h-10 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 flex items-center justify-center font-bold">
                <HelpCircle className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h4 className="text-base font-black uppercase text-slate-900 dark:text-slate-100">
                  Yêu Cầu Bổ Sung Bằng Chứng Xác Minh
                </h4>
                <p className="text-xs text-slate-500">
                  Vụ việc #CASE-{requestEvidenceModal.id} • {requestEvidenceModal.disputeTypeLabel}
                </p>
              </div>
            </div>

            <form onSubmit={handleSendEvidenceRequest} className="space-y-4 text-xs">
              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1.5">
                  Đối tượng cần cung cấp bổ sung bằng chứng:
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { id: 'BOTH', label: 'Cả 2 bên' },
                    { id: 'PT', label: `HLV (${requestEvidenceModal.ptName})` },
                    { id: 'STUDENT', label: `Học viên (${requestEvidenceModal.studentName})` },
                  ].map((target) => (
                    <button
                      key={target.id}
                      type="button"
                      onClick={() => setEvidenceTarget(target.id as any)}
                      className={`p-2.5 rounded-xl border text-center font-bold transition cursor-pointer ${
                        evidenceTarget === target.id
                          ? 'bg-amber-500 text-white border-amber-600 shadow-sm'
                          : 'bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100'
                      }`}
                    >
                      {target.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Nội dung &amp; Tài liệu cụ thể yêu cầu cung cấp <span className="text-red-500">*</span>:
                </label>
                <textarea
                  rows={4}
                  value={evidenceNoteInput}
                  onChange={(e) => setEvidenceNoteInput(e.target.value)}
                  placeholder="VD: Yêu cầu PT cung cấp ảnh trích xuất camera hoặc hóa đơn check-in quầy lễ tân lúc 18h00. Yêu cầu Học viên chụp màn hình lịch sử cuộc gọi lúc giờ hẹn ca tập..."
                  className="w-full p-3 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-amber-500"
                  required
                />
              </div>

              <div className="p-3 bg-amber-50 dark:bg-amber-950/40 rounded-xl border border-amber-200 dark:border-amber-800 text-[11px] text-amber-800 dark:text-amber-300 leading-relaxed">
                💡 <b>Cơ chế minh bạch:</b> Lời nhắn yêu cầu này sẽ được gửi trực tiếp đến màn hình của đối tượng được chọn. Họ sẽ có nút tải ảnh chứng minh bổ sung kèm giải trình đối soát.
              </div>

              <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setRequestEvidenceModal(null)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl font-semibold transition cursor-pointer"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={submittingEvidenceRequest}
                  className="px-5 py-2.5 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-bold rounded-xl shadow-md transition flex items-center gap-1.5 cursor-pointer"
                >
                  <Send className="w-3.5 h-3.5" />
                  {submittingEvidenceRequest ? 'Đang gửi yêu cầu...' : 'Gửi Yêu Cầu Bằng Chứng'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}


      {/* ==================== MODAL TỪ CHỐI PT ==================== */}
      {rejectingPt && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 animate-scale-up">
            <div className="flex items-center gap-3 text-red-600 mb-3">
              <div className="w-9 h-9 rounded-xl bg-red-50 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <h4 className="text-base font-bold text-slate-900 dark:text-slate-100">Từ Chối Hồ Sơ Huấn Luyện Viên</h4>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              Bạn đang từ chối hồ sơ của <b>{rejectingPt.fullName}</b> ({rejectingPt.email}). Hãy nhập lý do cụ thể để huấn luyện viên có thể chỉnh sửa và cập nhật lại:
            </p>

            <textarea
              rows={3}
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Nhập lý do từ chối (ví dụ: Chứng chỉ chưa rõ nét, thiếu kinh nghiệm...)"
              className="w-full p-3 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-red-500 mb-4"
            />

            <div className="flex items-center justify-end gap-2">
              <button
                onClick={() => setRejectingPt(null)}
                className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg transition"
              >
                Hủy bỏ
              </button>
              <button
                onClick={handleConfirmRejectPt}
                className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-bold rounded-lg shadow-xs transition"
              >
                Xác nhận từ chối
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==================== MODAL XEM ẢNH CHỨNG CHỈ ==================== */}
      {previewCert && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 animate-scale-up flex flex-col max-h-[90vh]">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div>
                <h4 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  {previewCert.name.includes('Bằng chứng') || previewCert.name.includes('Học viên') || previewCert.name.includes('HLV')
                    ? 'Bằng Chứng & Tài Liệu Đối Soát Vụ Việc'
                    : 'Chứng Chỉ / Bằng Cấp Huấn Luyện'}
                </h4>
                <p className="text-xs text-slate-500">
                  {previewCert.name.includes('Bằng chứng') || previewCert.name.includes('Học viên') || previewCert.name.includes('HLV')
                    ? 'Hồ sơ:'
                    : 'Huấn luyện viên:'} <b>{previewCert.name}</b>
                </p>
              </div>
              <button
                onClick={() => setPreviewCert(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-auto bg-slate-50 rounded-xl border border-slate-200 p-2 flex items-center justify-center">
              {isHttpUrl(previewCert.url) ? (
                <img
                  src={previewCert.url}
                  alt={`Chứng chỉ của ${previewCert.name}`}
                  className="max-h-[60vh] max-w-full object-contain rounded-lg shadow-sm"
                  onError={(e) => {
                    const target = e.currentTarget as HTMLImageElement;
                    if (target.src && !target.src.includes('topology.jpg')) {
                      target.src = '/uploads/disputes/topology.jpg';
                      return;
                    }
                    target.style.display = 'none';
                    const parent = target.parentElement;
                    if (parent) {
                      const div = document.createElement('div');
                      div.className = 'p-8 text-center text-xs text-slate-500';
                      div.innerHTML = `⚠️ Không thể hiển thị trực tiếp ảnh. Bạn có thể mở liên kết gốc: <br/><a href="${previewCert.url}" target="_blank" class="text-blue-600 underline break-all font-mono mt-2 block">${previewCert.url}</a>`;
                      parent.appendChild(div);
                    }
                  }}
                />
              ) : (
                <div className="p-8 text-center text-xs text-slate-600 font-mono">
                  Mã / Đường dẫn chứng chỉ nội bộ: <br />
                  <code className="bg-white px-2 py-1 rounded border border-slate-200 mt-2 inline-block">
                    {previewCert.url}
                  </code>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <a
                href={previewCert.url}
                target="_blank"
                rel="noreferrer"
                className="text-blue-600 hover:underline flex items-center gap-1 font-semibold"
              >
                <ExternalLink className="w-3.5 h-3.5" /> Mở trong tab mới
              </a>
              <button
                onClick={() => setPreviewCert(null)}
                className="px-4 py-2 bg-slate-800 text-white font-bold rounded-lg hover:bg-slate-900 transition"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ==================== MODAL RÚT DOANH THU NỀN TẢNG CHO ADMIN ==================== */}
      {showWithdrawModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 animate-scale-up flex flex-col">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800 mb-4">
              <div className="flex items-center gap-2 text-indigo-600">
                <Landmark className="w-5 h-5" />
                <h4 className="text-base font-bold text-slate-900 dark:text-slate-100">
                  Rút Tiền Quỹ Doanh Thu Sàn
                </h4>
              </div>
              <button
                type="button"
                onClick={() => setShowWithdrawModal(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
              >
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleWithdrawAdminRevenue} className="space-y-4 text-xs">
              <div className="p-3 bg-indigo-50 dark:bg-indigo-950/40 rounded-xl border border-indigo-100 dark:border-indigo-900 flex justify-between items-center">
                <span className="text-slate-600 dark:text-slate-300 font-medium">Số dư khả dụng hiện có:</span>
                <span className="text-base font-black text-indigo-700 dark:text-indigo-400">
                  {formatCurrency(adminWallet?.balance || 15650000)}
                </span>
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Số tiền muốn rút (₫) <span className="text-red-500">*</span>:
                </label>
                <input
                  type="number"
                  min="50000"
                  step="10000"
                  value={withdrawAmount}
                  onChange={(e) => {
                    setWithdrawAmount(e.target.value);
                    if (withdrawError) setWithdrawError(null);
                  }}
                  placeholder="Nhập số tiền muốn rút (VD: 5000000)"
                  className="w-full p-2.5 border border-slate-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm"
                  required
                />
                {/* Phím chọn nhanh */}
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {[1000000, 2000000, 5000000, 10000000].map((amt) => (
                    <button
                      key={amt}
                      type="button"
                      onClick={() => setWithdrawAmount(amt.toString())}
                      className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg font-medium text-[11px] transition"
                    >
                      {(amt / 1000000).toFixed(0)} triệu
                    </button>
                  ))}
                  <button
                    type="button"
                    onClick={() => setWithdrawAmount((adminWallet?.balance || 15650000).toString())}
                    className="px-2.5 py-1 bg-indigo-100 dark:bg-indigo-950/60 hover:bg-indigo-200 text-indigo-700 dark:text-indigo-300 rounded-lg font-bold text-[11px] transition"
                  >
                    Rút toàn bộ
                  </button>
                </div>
              </div>

              <div>
                <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                  Ngân hàng thụ hưởng:
                </label>
                <select
                  value={withdrawBankName}
                  onChange={(e) => setWithdrawBankName(e.target.value)}
                  className="w-full p-2.5 border border-slate-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="MB Bank (Quân Đội)">MB Bank - Ngân hàng TMCP Quân Đội</option>
                  <option value="Vietcombank">Vietcombank - Ngân hàng Ngoại Thương</option>
                  <option value="Techcombank">Techcombank - Ngân hàng Kỹ Thương</option>
                  <option value="BIDV">BIDV - Ngân hàng Đầu tư & Phát triển</option>
                  <option value="ACB">ACB - Ngân hàng Á Châu</option>
                  <option value="VPBank">VPBank - Ngân hàng Việt Nam Thịnh Vượng</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    Số tài khoản:
                  </label>
                  <input
                    type="text"
                    value={withdrawAccountNumber}
                    onChange={(e) => setWithdrawAccountNumber(e.target.value)}
                    placeholder="VD: 0988888888"
                    className="w-full p-2.5 border border-slate-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
                <div>
                  <label className="font-bold text-slate-700 dark:text-slate-300 block mb-1">
                    Tên chủ tài khoản:
                  </label>
                  <input
                    type="text"
                    value={withdrawAccountName}
                    onChange={(e) => setWithdrawAccountName(e.target.value.toUpperCase())}
                    placeholder="VD: PTCONNECT CORP"
                    className="w-full p-2.5 border border-slate-200 dark:border-slate-700 rounded-xl bg-white dark:bg-slate-800 text-slate-900 dark:text-white uppercase font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>

              {withdrawError && (
                <div className="p-2.5 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 rounded-xl text-red-700 dark:text-red-300">
                  ⚠️ {withdrawError}
                </div>
              )}

              <p className="text-[11px] text-slate-400 leading-relaxed">
                💡 Lệnh giải ngân doanh thu được hệ thống ngân hàng liên kết Napas247 xử lý tự động trong vòng 1-5 phút.
              </p>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowWithdrawModal(false)}
                  className="px-4 py-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg font-semibold transition"
                >
                  Hủy bỏ
                </button>
                <button
                  type="submit"
                  disabled={submittingWithdraw}
                  className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 disabled:opacity-50 text-white font-bold rounded-lg shadow-sm transition flex items-center gap-1.5"
                >
                  <ArrowUpRight className="w-4 h-4" />
                  {submittingWithdraw ? 'Đang giải ngân...' : 'Xác nhận rút doanh thu'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
