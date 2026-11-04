import { getAvatarUrl } from "../lib/avatar";
import React, { useState, useEffect } from 'react';
import api from '../lib/axios';
import { User, PtProfile } from '../types/api';
import { isHttpUrl, resolveCertificateUrl } from '../lib/certificate';
import { Shield, Users, BarChart2, CheckCircle, XCircle, Lock, Unlock, LogOut } from 'lucide-react';

interface AdminPageProps {
  user: User;
  onLogout: () => void;
}

export const AdminPage: React.FC<AdminPageProps> = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [pendingPts, setPendingPts] = useState<PtProfile[]>([]);
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const ptsData: any = await api.get('/admin/pt/pending');
      setPendingPts(ptsData || []);
      const uData: any = await api.get('/admin/users');
      setAllUsers(uData || []);
    } catch (e) {
      console.error(e);
    }
  };

  const handleApprovePt = async (ptId: number) => {
    try {
      await api.put(`/admin/pt/${ptId}/approve`);
      showToast('Đã phê duyệt hồ sơ Huấn luyện viên!');
      fetchAdminData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi phê duyệt PT.');
    }
  };

  const handleRejectPt = async (ptId: number) => {
    try {
      await api.put(`/admin/pt/${ptId}/reject`, { reason: 'Chứng chỉ chưa đạt chuẩn' });
      showToast('Đã từ chối hồ sơ PT.');
      fetchAdminData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi từ chối PT.');
    }
  };

  const handleToggleLockUser = async (u: User) => {
    try {
      await api.put(`/admin/users/${u.id}/status`, {
        status: u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE',
      });
      showToast(`Đã ${u.status === 'ACTIVE' ? 'khóa' : 'mở khóa'} tài khoản #${u.id}!`);
      fetchAdminData();
    } catch (err: any) {
      showToast(err.message || 'Lỗi cập nhật trạng thái.');
    }
  };

  const tabs = [
    { label: `Phê Duyệt (${pendingPts.length})`, icon: Shield },
    { label: 'Quản Lý Người Dùng', icon: Users },
    { label: 'Thống Kê', icon: BarChart2 },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-700 text-white flex items-center justify-center font-bold text-lg shadow-sm">
              AD
            </div>
            <div>
              <span className="font-extrabold text-slate-900 text-lg tracking-tight">PT Connect</span>
              <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-purple-100 text-purple-800">
                Quản trị viên
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-bold text-slate-900">{user.fullName}</div>
              <div className="text-xs text-slate-500">{user.email}</div>
            </div>
            <button
              onClick={onLogout}
              className="px-3 py-1.5 border border-slate-300 hover:bg-slate-50 text-slate-700 rounded-lg text-xs font-semibold flex items-center gap-1.5"
            >
              <LogOut className="w-3.5 h-3.5" /> Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Hero Header Banner */}
      <div className="bg-gradient-to-r from-purple-800 to-indigo-900 text-white py-6 px-4 sm:px-8 shadow-md">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-extrabold">Bảng Điều Khiển Quản Trị Viên (Admin)</h2>
            <p className="text-purple-200 text-xs sm:text-sm mt-0.5">
              Xin chào, <b>{user.fullName}</b>! Giám sát hệ thống, quản lý người dùng và phân tích dữ liệu toàn diện.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 border border-white/20 flex items-center gap-6">
            <div>
              <span className="text-[11px] text-purple-200 block uppercase font-medium">Tổng người dùng</span>
              <span className="text-xl font-extrabold text-white">{allUsers.length} tài khoản</span>
            </div>
            <div className="border-l border-white/20 pl-6">
              <span className="text-[11px] text-purple-200 block uppercase font-medium">Hồ sơ chờ duyệt</span>
              <span className="text-xl font-extrabold text-amber-300">{pendingPts.length} PT</span>
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
                      ? 'bg-purple-50 text-purple-700'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isCur ? 'text-purple-700' : 'text-slate-400'}`} />
                  {t.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Body */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full">
        {/* TAB 0: PHÊ DUYỆT PT */}
        {activeTab === 0 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Danh Sách Huấn Luyện Viên Đang Chờ Phê Duyệt</h3>
            {pendingPts.length === 0 ? (
              <div className="bg-white p-8 rounded-xl border border-slate-200 text-center text-slate-500">
                <CheckCircle className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
                <p>Tuyệt vời! Hiện không có hồ sơ Huấn luyện viên nào đang chờ xét duyệt.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {pendingPts.map((pt) => (
                  <div key={pt.id} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                    <div>
                      <div className="flex items-center gap-3">
                        <img
                          src={getAvatarUrl(pt.fullName, pt.avatarUrl)}
                          alt={pt.fullName}
                          className="w-12 h-12 rounded-full border border-slate-200 object-cover"
                        />
                        <div>
                          <h4 className="text-base font-bold text-slate-900">{pt.fullName}</h4>
                          <span className="text-xs text-slate-500">{pt.email} • {pt.phone}</span>
                        </div>
                      </div>
                      <p className="text-xs text-slate-600 mt-3">{pt.bio}</p>
                      <div className="text-xs text-slate-500 mt-2">
                        <span><b>Khu vực:</b> {pt.availableLocations}</span> • <span><b>Kinh nghiệm:</b> {pt.experienceYears} năm</span>
                      </div>
                      {pt.locationPricingNote && (
                        <div className="text-xs text-slate-500 mt-1"><b>Ghi chú giá:</b> {pt.locationPricingNote}</div>
                      )}
                      {(() => {
                        const cert = resolveCertificateUrl(pt);
                        return (
                          <div className="text-xs text-slate-600 mt-2">
                            <b>Chứng chỉ / Bằng cấp:</b>{' '}
                            {cert ? (
                              isHttpUrl(cert) ? (
                                <a href={cert} target="_blank" rel="noreferrer" className="text-blue-600 underline break-all">{cert}</a>
                              ) : (
                                <code className="bg-slate-100 px-1 rounded break-all">{cert}</code>
                              )
                            ) : (
                              <span className="italic text-slate-400">Chưa cập nhật</span>
                            )}
                          </div>
                        );
                      })()}
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex gap-2 justify-end">
                      <button
                        onClick={() => handleRejectPt(pt.id)}
                        className="px-3 py-1.5 border border-red-300 text-red-600 hover:bg-red-50 rounded-lg text-xs font-semibold flex items-center gap-1"
                      >
                        <XCircle className="w-3.5 h-3.5" /> Từ chối
                      </button>
                      <button
                        onClick={() => handleApprovePt(pt.id)}
                        className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow-sm"
                      >
                        <CheckCircle className="w-3.5 h-3.5" /> Phê duyệt
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 1: QUẢN LÝ NGƯỜI DÙNG */}
        {activeTab === 1 && (
          <div className="space-y-4">
            <h3 className="text-xl font-bold text-slate-900">Quản Lý Người Dùng & Trạng Thái Hoạt Động</h3>
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 border-b border-slate-200 text-xs text-slate-600 font-semibold uppercase">
                  <tr>
                    <th className="py-3 px-4">ID</th>
                    <th className="py-3 px-4">Họ Và Tên</th>
                    <th className="py-3 px-4">Email / SĐT</th>
                    <th className="py-3 px-4">Vai Trò</th>
                    <th className="py-3 px-4">Trạng Thái</th>
                    <th className="py-3 px-4 text-right">Thao Tác</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {allUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-slate-50/70">
                      <td className="py-3 px-4 font-mono font-semibold text-slate-600">#{u.id}</td>
                      <td className="py-3 px-4 font-semibold text-slate-900">{u.fullName}</td>
                      <td className="py-3 px-4 text-xs text-slate-600">
                        <div>{u.email}</div>
                        <div className="text-slate-400">{u.phone}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-800">
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                            u.status === 'ACTIVE'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {u.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleToggleLockUser(u)}
                          className={`px-2.5 py-1 rounded text-xs font-medium border flex items-center gap-1 ml-auto ${
                            u.status === 'ACTIVE'
                              ? 'border-red-300 text-red-600 hover:bg-red-50'
                              : 'border-emerald-300 text-emerald-600 hover:bg-emerald-50'
                          }`}
                        >
                          {u.status === 'ACTIVE' ? (
                            <>
                              <Lock className="w-3.5 h-3.5" /> Khóa tài khoản
                            </>
                          ) : (
                            <>
                              <Unlock className="w-3.5 h-3.5" /> Mở khóa tài khoản
                            </>
                          )}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 2: THỐNG KÊ */}
        {activeTab === 2 && (
          <div className="space-y-6">
            <h3 className="text-xl font-bold text-slate-900">Hệ Thống Phân Tích Dữ Liệu Nền Tảng</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Tổng Học Viên</span>
                <div className="text-2xl font-extrabold text-blue-600 mt-1">30 người</div>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Huấn Luyện Viên</span>
                <div className="text-2xl font-extrabold text-orange-600 mt-1">8 PT</div>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Tổng Ca Đặt Lịch</span>
                <div className="text-2xl font-extrabold text-emerald-600 mt-1">151 ca</div>
              </div>
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                <span className="text-xs text-slate-500 font-medium">Tổng Doanh Thu</span>
                <div className="text-2xl font-extrabold text-purple-600 mt-1">277.200.000 ₫</div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};
