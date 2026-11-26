import React, { useState } from 'react';
import {
  ShieldAlert,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  X,
  User,
  Dumbbell,
  BookOpen,
  Scale,
  Sparkles,
  PhoneCall,
  Calendar,
  KeyRound,
  FileText,
  Star,
} from 'lucide-react';

interface PolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultRole?: 'ALL' | 'STUDENT' | 'PT';
  isDark?: boolean;
}

export const PolicyModal: React.FC<PolicyModalProps> = ({
  isOpen,
  onClose,
  defaultRole = 'ALL',
  isDark = false,
}) => {
  const [activeTab, setActiveTab] = useState<'CANCELLATION' | 'ATTENDANCE' | 'TRIAL_CONTRACT' | 'CONDUCT'>('CANCELLATION');
  const [roleFilter, setRoleFilter] = useState<'ALL' | 'STUDENT' | 'PT'>(defaultRole);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5 overflow-y-auto animate-fade-in">
      <div
        className={`relative w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl shadow-2xl border overflow-hidden ${
          isDark
            ? 'bg-slate-900 border-slate-700 text-slate-100'
            : 'bg-white border-slate-200 text-slate-800'
        }`}
      >
        <div className={`px-6 py-4 border-b flex items-center justify-between shrink-0 ${
          isDark ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-200'
        }`}>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-rose-600 text-white flex items-center justify-center shadow-sm">
              <Scale className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-base sm:text-lg font-black tracking-tight">
                  Quy Chuẩn Hoạt Động & Bộ Quy Tắc Ứng Xử PTConnect
                </h3>
                <span className="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                  Chuẩn 2026
                </span>
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Minh bạch quyền lợi, phòng tránh tranh chấp & chế tài xử phạt khi hủy lịch sát giờ
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title="Đóng"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className={`px-6 py-2.5 border-b flex flex-wrap items-center justify-between gap-3 shrink-0 ${
          isDark ? 'bg-slate-950/40 border-slate-800' : 'bg-slate-50/80 border-slate-200'
        }`}>
          <div className="flex items-center gap-1.5 overflow-x-auto py-1">
            <button
              onClick={() => setActiveTab('CANCELLATION')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap ${
                activeTab === 'CANCELLATION'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800'
              }`}
            >
              <Clock className="w-3.5 h-3.5" />
              <span>1. Quy Định Hủy Lịch & Đền Bù</span>
            </button>

            <button
              onClick={() => setActiveTab('ATTENDANCE')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap ${
                activeTab === 'ATTENDANCE'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800'
              }`}
            >
              <KeyRound className="w-3.5 h-3.5" />
              <span>2. Điểm Danh OTP & Báo Vắng</span>
            </button>

            <button
              onClick={() => setActiveTab('TRIAL_CONTRACT')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap ${
                activeTab === 'TRIAL_CONTRACT'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>3. Khóa Học & Học Thử (Trial)</span>
            </button>

            <button
              onClick={() => setActiveTab('CONDUCT')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap ${
                activeTab === 'CONDUCT'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/60 dark:hover:bg-slate-800'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>4. Quy Tắc Ứng Xử & Trọng Tài</span>
            </button>
          </div>

          <div className="flex items-center gap-1 text-[11px] font-semibold bg-white dark:bg-slate-800 p-0.5 rounded-lg border border-slate-200 dark:border-slate-700">
            <span className="px-2 text-slate-400">Xem theo vai trò:</span>
            <button
              onClick={() => setRoleFilter('ALL')}
              className={`px-2.5 py-1 rounded-md transition ${
                roleFilter === 'ALL'
                  ? 'bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900 font-bold'
                  : 'text-slate-600 dark:text-slate-300 hover:text-slate-900'
              }`}
            >
              Cả hai
            </button>
            <button
              onClick={() => setRoleFilter('STUDENT')}
              className={`px-2.5 py-1 rounded-md flex items-center gap-1 transition ${
                roleFilter === 'STUDENT'
                  ? 'bg-blue-600 text-white font-bold'
                  : 'text-slate-600 dark:text-slate-300 hover:text-blue-600'
              }`}
            >
              <User className="w-3 h-3" />
              Học viên
            </button>
            <button
              onClick={() => setRoleFilter('PT')}
              className={`px-2.5 py-1 rounded-md flex items-center gap-1 transition ${
                roleFilter === 'PT'
                  ? 'bg-emerald-600 text-white font-bold'
                  : 'text-slate-600 dark:text-slate-300 hover:text-emerald-600'
              }`}
            >
              <Dumbbell className="w-3 h-3" />
              HLV (PT)
            </button>
          </div>
        </div>

        <div className="p-6 overflow-y-auto space-y-6 text-sm leading-relaxed">
          {activeTab === 'CANCELLATION' && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-900 dark:text-amber-200 flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div className="text-xs space-y-1">
                  <p className="font-bold text-amber-800 dark:text-amber-300 text-sm">
                    ⚠️ QUY TẮC VÀNG: MỐC THỜI GIAN 24 GIỜ TRƯỚC GIỜ TẬP
                  </p>
                  <p>
                    Hệ thống PTConnect áp dụng nguyên tắc tự động kiểm soát mốc <b>24 giờ</b> trước khi ca tập diễn ra.
                    Việc hủy lịch sát giờ làm ảnh hưởng nghiêm trọng đến thời gian biểu và thu nhập của đối phương, do đó hệ thống áp dụng chế tài khấu trừ ví điện tử và hoàn buổi học tự động.
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-xs">
                <div className="bg-slate-100 dark:bg-slate-950 px-4 py-2.5 font-bold text-xs uppercase tracking-wide border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
                  <span>Bảng Ma Trận Xử Lý Hủy Ca Tập Chi Tiết</span>
                  <span className="text-[11px] text-slate-500 font-normal">Tự động áp dụng bởi hệ thống</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 dark:bg-slate-900 text-slate-600 dark:text-slate-400 font-semibold border-b border-slate-200 dark:border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">Đối tượng</th>
                        <th className="py-2.5 px-3">Trạng thái ca</th>
                        <th className="py-2.5 px-3">Mốc thời gian hủy</th>
                        <th className="py-2.5 px-3">Kho buổi học</th>
                        <th className="py-2.5 px-3">Chế tài tài chính & Bồi thường</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {(roleFilter === 'ALL' || roleFilter === 'STUDENT') && (
                        <>
                          <tr className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                            <td className="py-3 px-3 font-bold text-blue-600 flex items-center gap-1.5">
                              <User className="w-3.5 h-3.5" /> Học viên
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300">
                                PENDING (Chờ duyệt)
                              </span>
                            </td>
                            <td className="py-3 px-3 text-slate-500">Mọi thời điểm</td>
                            <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                              ✓ Hoàn 1 buổi
                            </td>
                            <td className="py-3 px-3 text-slate-600 dark:text-slate-300">
                              Không phạt, không mất phí
                            </td>
                          </tr>

                          <tr className="bg-amber-50/30 dark:bg-amber-950/20 hover:bg-amber-50/50">
                            <td className="py-3 px-3 font-bold text-blue-600 flex items-center gap-1.5">
                              <User className="w-3.5 h-3.5" /> Học viên
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300">
                                CONFIRMED (Đã duyệt)
                              </span>
                            </td>
                            <td className="py-3 px-3 font-medium text-slate-700 dark:text-slate-300">
                              Trước <span className="font-bold text-emerald-600">&ge; 24 giờ</span>
                            </td>
                            <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                              ✓ Hoàn 1 buổi vào hợp đồng
                            </td>
                            <td className="py-3 px-3 text-amber-700 dark:text-amber-300">
                              <b>Phạt 50% tiền buổi:</b> Trừ ví học viên và đền bù 50% cho HLV vì đã giữ chỗ
                            </td>
                          </tr>

                          <tr className="bg-red-50/40 dark:bg-red-950/30 hover:bg-red-50/60">
                            <td className="py-3 px-3 font-bold text-blue-600 flex items-center gap-1.5">
                              <User className="w-3.5 h-3.5" /> Học viên
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300">
                                CONFIRMED (Đã duyệt)
                              </span>
                            </td>
                            <td className="py-3 px-3 font-bold text-red-600">
                              Sát giờ <span className="underline">&lt; 24 giờ</span>
                            </td>
                            <td className="py-3 px-3 text-red-600 dark:text-red-400 font-bold">
                              ✕ MẤT BUỔI (Không hoàn)
                            </td>
                            <td className="py-3 px-3 text-red-700 dark:text-red-300 font-medium">
                              <b>HLV hưởng 100% tiền buổi:</b> Chuyển vào ví HLV (sàn thu 10% phí điều phối)
                            </td>
                          </tr>
                        </>
                      )}

                      {(roleFilter === 'ALL' || roleFilter === 'PT') && (
                        <>
                          <tr className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                            <td className="py-3 px-3 font-bold text-emerald-600 flex items-center gap-1.5">
                              <Dumbbell className="w-3.5 h-3.5" /> HLV (PT)
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300">
                                PENDING (Từ chối)
                              </span>
                            </td>
                            <td className="py-3 px-3 text-slate-500">Mọi thời điểm</td>
                            <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                              ✓ Hoàn 1 buổi
                            </td>
                            <td className="py-3 px-3 text-slate-600 dark:text-slate-300">
                              Không phạt HLV, slot trở lại trạng thái AVAILABLE
                            </td>
                          </tr>

                          <tr className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40">
                            <td className="py-3 px-3 font-bold text-emerald-600 flex items-center gap-1.5">
                              <Dumbbell className="w-3.5 h-3.5" /> HLV (PT)
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300">
                                CONFIRMED (Đã duyệt)
                              </span>
                            </td>
                            <td className="py-3 px-3 font-medium text-slate-700 dark:text-slate-300">
                              Trước <span className="font-bold text-emerald-600">&ge; 24 giờ</span>
                            </td>
                            <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                              ✓ Hoàn 1 buổi
                            </td>
                            <td className="py-3 px-3 text-slate-600 dark:text-slate-300">
                              Không phạt hay đền bù tài chính
                            </td>
                          </tr>

                          <tr className="bg-red-50/40 dark:bg-red-950/30 hover:bg-red-50/60">
                            <td className="py-3 px-3 font-bold text-emerald-600 flex items-center gap-1.5">
                              <Dumbbell className="w-3.5 h-3.5" /> HLV (PT)
                            </td>
                            <td className="py-3 px-3">
                              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 dark:bg-blue-900/40 text-blue-800 dark:text-blue-300">
                                CONFIRMED (Đã duyệt)
                              </span>
                            </td>
                            <td className="py-3 px-3 font-bold text-red-600">
                              Sát giờ <span className="underline">&lt; 24 giờ</span>
                            </td>
                            <td className="py-3 px-3 text-emerald-600 dark:text-emerald-400 font-bold">
                              ✓ Hoàn 1 buổi cho học viên
                            </td>
                            <td className="py-3 px-3 text-red-700 dark:text-red-300 font-medium">
                              <b>Phạt 100% tiền buổi:</b> Trừ trực tiếp ví HLV và đền bù 100% tiền vào ví Học viên
                            </td>
                          </tr>
                        </>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-blue-200 dark:border-blue-900/60 bg-blue-50/40 dark:bg-blue-950/20 space-y-2">
                  <div className="flex items-center gap-2 font-bold text-blue-800 dark:text-blue-300 text-xs uppercase">
                    <User className="w-4 h-4 text-blue-600" />
                    <span>Ví dụ thực tế: Học viên hủy ca</span>
                  </div>
                  <div className="text-xs text-slate-700 dark:text-slate-300 space-y-1.5">
                    <p>Giả sử bạn đăng ký khóa học với đơn giá <b>300.000 ₫/buổi</b>, lịch hẹn lúc 18:00 Thứ Bảy:</p>
                    <ul className="list-disc pl-4 space-y-1 text-slate-600 dark:text-slate-400">
                      <li>
                        <b>Nếu hủy lúc 10:00 Thứ Sáu (trước 32h &ge; 24h):</b> Bạn được hoàn lại 1 buổi tập vào hợp đồng, nhưng hệ thống trừ phí hủy <b>150.000 ₫ (50%)</b> để đền bù cho HLV đã giữ slot.
                      </li>
                      <li>
                        <b>Nếu hủy lúc 14:00 Thứ Bảy (trước 4h &lt; 24h):</b> Bạn <b>bị mất 1 buổi tập</b> trong hợp đồng, và 300.000 ₫ tiền buổi học được giải ngân cho HLV (sau phí sàn).
                      </li>
                    </ul>
                  </div>
                </div>

                <div className="p-4 rounded-xl border border-emerald-200 dark:border-emerald-900/60 bg-emerald-50/40 dark:bg-emerald-950/20 space-y-2">
                  <div className="flex items-center gap-2 font-bold text-emerald-800 dark:text-emerald-300 text-xs uppercase">
                    <Dumbbell className="w-4 h-4 text-emerald-600" />
                    <span>Ví dụ thực tế: Huấn luyện viên hủy ca</span>
                  </div>
                  <div className="text-xs text-slate-700 dark:text-slate-300 space-y-1.5">
                    <p>Ca tập đơn giá <b>300.000 ₫/buổi</b> đã được HLV xác nhận lúc 07:00 sáng:</p>
                    <ul className="list-disc pl-4 space-y-1 text-slate-600 dark:text-slate-400">
                      <li>
                        <b>Nếu HLV hủy trước &ge; 24h:</b> Học viên nhận lại 1 buổi tập vào kho. HLV không bị phạt tài chính.
                      </li>
                      <li>
                        <b>Nếu HLV bận đột xuất hủy lúc 05:00 sáng (&lt; 24h):</b> Học viên vừa được hoàn lại 1 buổi tập, vừa nhận được <b>300.000 ₫ bồi thường</b> vào ví tiền. HLV bị hệ thống tự động trừ <b>300.000 ₫ tiền phạt</b>.
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ATTENDANCE' && (
            <div className="space-y-5">
              <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-900 dark:text-blue-200 flex items-start gap-3">
                <KeyRound className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
                <div className="text-xs space-y-1">
                  <p className="font-bold text-blue-800 dark:text-blue-300 text-sm">
                    🔐 ĐIỂM DANH HAI CHIỀU BẰNG MÃ OTP BẢO MẬT
                  </p>
                  <p>
                    Mỗi buổi tập chỉ được tính là hoàn thành khi cả Học viên và Huấn luyện viên cùng có mặt tại phòng tập để xác thực mã số OTP.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2">
                  <div className="w-8 h-8 rounded-lg bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-400 font-black flex items-center justify-center text-sm">
                    1
                  </div>
                  <h4 className="font-bold text-xs uppercase text-slate-800 dark:text-white">Học viên lấy mã OTP</h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Khi đến địa điểm tập, Học viên mở mục <b>"Lịch Của Tôi"</b> → bấm nút <b>"Lấy OTP Điểm Danh"</b>. Mã OTP gồm 6 chữ số có hiệu lực trong 15 phút.
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2">
                  <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-400 font-black flex items-center justify-center text-sm">
                    2
                  </div>
                  <h4 className="font-bold text-xs uppercase text-slate-800 dark:text-white">HLV nhập xác thực</h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    HLV mở danh sách ca tập → nhập mã OTP học viên cung cấp. Nếu chính xác, ca tập chuyển sang <b>COMPLETED</b> và tiền buổi tập được mở khóa giải ngân.
                  </p>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2">
                  <div className="w-8 h-8 rounded-lg bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-400 font-black flex items-center justify-center text-sm">
                    3
                  </div>
                  <h4 className="font-bold text-xs uppercase text-slate-800 dark:text-white">Quy chế Vắng mặt (No-Show)</h4>
                  <p className="text-xs text-slate-600 dark:text-slate-400">
                    Nếu sau <b>30 phút</b> kể từ giờ bắt đầu mà Học viên không có mặt và không liên lạc được, HLV có quyền đánh dấu <b>"Học viên Vắng mặt"</b> (trừ 1 buổi của học viên).
                  </p>
                </div>
              </div>

              <div className="p-4 rounded-xl border border-red-200 dark:border-red-900/60 bg-red-50/40 dark:bg-red-950/20 text-xs space-y-2">
                <div className="flex items-center gap-2 font-bold text-red-800 dark:text-red-300 uppercase">
                  <XCircle className="w-4 h-4 text-red-600" />
                  <span>Hành vi nghiêm cấm khi điểm danh:</span>
                </div>
                <ul className="list-disc pl-5 space-y-1 text-slate-700 dark:text-slate-300">
                  <li>Nghiêm cấm học viên chụp màn hình gửi mã OTP qua Zalo/Facebook/Tin nhắn cho HLV khi chưa có mặt trực tiếp tại phòng tập.</li>
                  <li>Nghiêm cấm HLV thúc ép học viên đọc OTP trước buổi tập để "chấm công khống".</li>
                  <li>Nếu phát hiện gian lận OTP điểm danh từ xa, Ban Quản Trị có quyền thu hồi tiền buổi học và tạm khóa tài khoản 14 ngày.</li>
                </ul>
              </div>
            </div>
          )}

          {activeTab === 'TRIAL_CONTRACT' && (
            <div className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-3">
                  <div className="flex items-center gap-2 font-bold text-xs uppercase text-slate-900 dark:text-white">
                    <Sparkles className="w-4 h-4 text-amber-500" />
                    <span>Quy định Học Thử (Trial Booking)</span>
                  </div>
                  <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2 pl-4 list-disc">
                    <li>
                      <b>Mỗi học viên chỉ được đặt học thử tối đa 1 lần duy nhất với mỗi Huấn luyện viên.</b>
                    </li>
                    <li>
                      Học phí buổi học thử là <b>0 ₫</b>. Khung giờ được giữ cho bạn đến khi HLV phê duyệt.
                    </li>
                    <li>
                      Nếu hủy buổi học thử, khung giờ sẽ được giải phóng cho học viên khác đặt. Buổi học thử không tạo hợp đồng khóa học.
                    </li>
                    <li>
                      Nghiêm cấm hành vi lập nhiều tài khoản ảo nhằm mục đích học thử miễn phí liên tục từ nhiều HLV.
                    </li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-3">
                  <div className="flex items-center gap-2 font-bold text-xs uppercase text-slate-900 dark:text-white">
                    <FileText className="w-4 h-4 text-blue-500" />
                    <span>Hợp Đồng Điện Tử Khóa Học (PDF)</span>
                  </div>
                  <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2 pl-4 list-disc">
                    <li>
                      Khi mua gói khóa học, hợp đồng điện tử được sinh tự động và có mã đối soát ngân quỹ độc nhất.
                    </li>
                    <li>
                      Hợp đồng quy định rõ: Địa điểm tập luyện cam kết, tổng số buổi, thời hạn ngày bắt đầu và kết thúc.
                    </li>
                    <li>
                      Học viên chỉ được đặt lịch khi hợp đồng ở trạng thái <b>ACTIVE</b>, chưa quá hạn và số buổi còn lại <b>&gt; 0</b>.
                    </li>
                    <li>
                      Cả Học viên và HLV đều có thể tải file PDF hợp đồng bất kỳ lúc nào tại mục <b>"Khóa Của Tôi"</b>.
                    </li>
                  </ul>
                </div>
              </div>

              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs space-y-2">
                <h4 className="font-bold text-slate-800 dark:text-white flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-rose-500" />
                  <span>Quy định về thời hạn hợp đồng & Bảo lưu khóa học:</span>
                </h4>
                <p className="text-slate-600 dark:text-slate-400">
                  Học viên cần sắp xếp lịch tập hoàn thành trước ngày hết hạn hợp đồng (thường là 30 - 90 ngày tùy gói).
                  Nếu có lý do y tế hoặc công tác đột xuất cần tạm dừng, Học viên cần gửi thỏa thuận bảo lưu hoặc tạo đơn khiếu nại qua hệ thống trước ít nhất 7 ngày để BQT và HLV gia hạn hợp đồng.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'CONDUCT' && (
            <div className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2.5">
                  <h4 className="font-bold text-xs uppercase text-slate-900 dark:text-white flex items-center gap-2">
                    <User className="w-4 h-4 text-blue-600" />
                    <span>Nghĩa vụ của Học viên</span>
                  </h4>
                  <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1.5 list-disc pl-4">
                    <li>Đến phòng tập đúng giờ đã hẹn trên hệ thống (nên đến sớm 5 - 10 phút để khởi động).</li>
                    <li>Trang bị trang phục, giày thể thao sạch sẽ, phù hợp quy định của phòng tập.</li>
                    <li>Tôn trọng Huấn luyện viên, lắng nghe hướng dẫn an toàn tạ và động tác để tránh chấn thương.</li>
                    <li>Đánh giá trung thực, khách quan sau mỗi buổi tập (không dùng từ ngữ thô tục xúc phạm).</li>
                  </ul>
                </div>

                <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 space-y-2.5">
                  <h4 className="font-bold text-xs uppercase text-slate-900 dark:text-white flex items-center gap-2">
                    <Dumbbell className="w-4 h-4 text-emerald-600" />
                    <span>Nghĩa vụ của Huấn luyện viên (PT)</span>
                  </h4>
                  <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-1.5 list-disc pl-4">
                    <li>Có mặt trước buổi tập ít nhất 10 phút, kiểm tra sẵn máy móc, thiết bị an toàn.</li>
                    <li>Soạn giáo án bài tập cá nhân hóa phù hợp với thể trạng và mục tiêu của học viên.</li>
                    <li>Giữ thái độ chuẩn mực, văn minh, tận tình; nghiêm cấm mọi hành vi quấy rối hoặc phân biệt đối xử.</li>
                    <li>Mở khung giờ làm việc thực tế, phê duyệt lịch hẹn trong vòng 12 giờ kể từ khi học viên đặt.</li>
                  </ul>
                </div>
              </div>

              <div className="p-4 rounded-xl border border-red-200 dark:border-red-900/60 bg-red-500/10 text-xs space-y-2">
                <div className="flex items-center gap-2 font-bold text-red-800 dark:text-red-300 uppercase">
                  <ShieldAlert className="w-4 h-4 text-red-600" />
                  <span>Điều cấm kỵ tuyệt đối: Giao dịch ngầm ngoài hệ thống</span>
                </div>
                <p className="text-slate-700 dark:text-slate-300">
                  PTConnect bảo vệ 100% số dư tiền của bạn bằng cơ chế ký quỹ thông minh (Tiền chỉ chuyển cho PT khi có OTP xác nhận).
                  <b>Nếu Học viên và HLV tự ý giao dịch chuyển khoản cá nhân ngoài sàn:</b>
                </p>
                <ul className="list-disc pl-5 space-y-1 text-slate-600 dark:text-slate-400">
                  <li>Hệ thống từ chối can thiệp và từ chối hỗ trợ trọng tài khi xảy ra bùng tiền, bỏ ca hoặc tranh chấp.</li>
                  <li>Tài khoản HLV có thể bị đình chỉ hoạt động vĩnh viễn và chấm dứt tư cách đối tác.</li>
                </ul>
              </div>

              <div className="p-4 rounded-xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/50 dark:bg-amber-950/20 text-xs space-y-2">
                <h4 className="font-bold text-amber-900 dark:text-amber-300 flex items-center gap-2">
                  <Scale className="w-4 h-4 text-amber-600" />
                  <span>Quy chế Trọng tài & Giải quyết tranh chấp trong 48 Giờ:</span>
                </h4>
                <p className="text-slate-600 dark:text-slate-400">
                  Nếu xảy ra mâu thuẫn (như HLV vắng mặt không lý do, hủy lịch sai quy định, thái độ không đạt chuẩn), bạn có quyền bấm nút <b>"Khiếu nại"</b> tại bảng ca tập.
                  Ban Quản Trị Hệ Thống sẽ đối soát log điện tử, bằng chứng kèm theo và ra phán quyết hoàn tiền / xử phạt trong vòng tối đa <b>48 giờ làm việc</b>.
                </p>
              </div>

              <div className="p-4 rounded-xl border border-rose-200 dark:border-rose-900/60 bg-rose-50/40 dark:bg-rose-950/20 text-xs space-y-2">
                <h4 className="font-bold text-rose-900 dark:text-rose-300 flex items-center gap-2">
                  <Star className="w-4 h-4 fill-rose-500 text-rose-500" />
                  <span>Quy chế Đánh Giá & Quyền Phản Biện Của HLV (1 - 3 Sao):</span>
                </h4>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">
                  • <b>Đánh giá 4 - 5 sao:</b> Được hệ thống tự động ghi nhận và công khai ngay lập tức trên hồ sơ công khai của Huấn luyện viên.<br />
                  • <b>Đánh giá 1 - 3 sao (tiêu cực):</b> Hệ thống sẽ chuyển vào quy trình bảo vệ uy tín (FLAGGED). Huấn luyện viên có toàn quyền gửi phản biện, giải trình và bằng chứng đối chứng (APPEALED).<br />
                  • <b>Thẩm quyền của Quản trị viên (Admin):</b> Căn cứ theo ý kiến hai bên, Admin sẽ ra phán quyết: <b>Xóa bỏ đánh giá</b> (nếu học viên vu khống, đánh giá ác ý sai sự thật - không tính điểm sao cho PT), <b>Giữ lại đánh giá</b> (nếu phản ánh đúng thực tế dịch vụ - công khai kèm phản hồi giải trình của PT), hoặc <b>Yêu cầu hai bên bổ sung thêm bằng chứng</b>.
                </p>
              </div>
            </div>
          )}
        </div>

        <div className={`px-6 py-3 border-t flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0 ${
          isDark ? 'bg-slate-950 border-slate-800' : 'bg-slate-50 border-slate-100'
        }`}>
          <div className="text-[11px] text-slate-500 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>Áp dụng thống nhất cho toàn bộ thành viên hệ thống PTConnect.</span>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-5 py-2 text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white rounded-xl transition shadow-xs"
            >
              Tôi đã hiểu & Đồng ý tuân thủ
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PolicyModal;
