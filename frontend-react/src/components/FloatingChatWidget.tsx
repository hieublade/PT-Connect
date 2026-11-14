import React, { useState, useEffect, useRef } from 'react';
import { 
  MessageCircle, 
  X, 
  Minus, 
  Send, 
  Search, 
  ChevronLeft, 
  CheckCheck, 
  Sparkles,
  RefreshCw,
  User as UserIcon,
  Smile,
  ShieldCheck
} from 'lucide-react';
import api from '../lib/axios';
import { User, ChatMessage, ChatConversation } from '../types/api';

interface FloatingChatWidgetProps {
  currentUser: User;
}

export const FloatingChatWidget: React.FC<FloatingChatWidgetProps> = ({ currentUser }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [selectedPartner, setSelectedPartner] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputContent, setInputContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [totalUnread, setTotalUnread] = useState(0);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Helper unwrappers (tương thích cả khi Axios interceptor đã bóc tách dữ liệu)
  const unwrapList = (res: any): any[] => {
    if (!res) return [];
    if (Array.isArray(res)) return res;
    if (Array.isArray(res.data)) return res.data;
    if (Array.isArray(res.data?.data)) return res.data.data;
    return [];
  };

  const unwrapItem = (res: any): any => {
    if (!res) return null;
    if (res.id) return res;
    if (res.data?.id) return res.data;
    if (res.data?.data?.id) return res.data.data;
    return res;
  };

  // Cuộn xuống tin nhắn mới nhất
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Tải danh sách hội thoại
  const fetchConversations = async () => {
    try {
      const res: any = await api.get('/chat/conversations');
      setConversations(unwrapList(res));
    } catch (err) {
      console.error('Lỗi lấy danh sách hội thoại:', err);
    }
  };

  // Tải số lượng tin nhắn chưa đọc
  const fetchUnreadCount = async () => {
    try {
      const res: any = await api.get('/chat/unread-count');
      const count = typeof res === 'number'
        ? res
        : (typeof res?.data === 'number' ? res.data : (typeof res?.data?.data === 'number' ? res.data.data : 0));
      setTotalUnread(count);
    } catch (err) {
      console.error('Lỗi đếm tin chưa đọc:', err);
    }
  };

  // Tải tin nhắn của hội thoại hiện tại
  const fetchMessages = async (partnerId: number) => {
    try {
      setLoading(true);
      setErrorMessage(null);
      const res: any = await api.get(`/chat/messages/${partnerId}`);
      setMessages(unwrapList(res));
      // Đọc xong thì cập nhật lại số lượng chưa đọc
      fetchUnreadCount();
      fetchConversations();
    } catch (err: any) {
      console.error('Lỗi lấy tin nhắn:', err);
      setErrorMessage(err.message || 'Không thể tải tin nhắn.');
    } finally {
      setLoading(false);
    }
  };

  // Chu kỳ polling cập nhật tin nhắn định kỳ mỗi 4 giây
  useEffect(() => {
    fetchUnreadCount();
    fetchConversations();

    const interval = setInterval(() => {
      fetchUnreadCount();
      if (isOpen && selectedPartner) {
        // Cập nhật ngầm tin nhắn không đổi trạng thái loading
        api.get(`/chat/messages/${selectedPartner.partnerId}`)
          .then((res: any) => {
            const list = unwrapList(res);
            setMessages(list);
          })
          .catch(e => console.error(e));
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [isOpen, selectedPartner]);

  // Lắng nghe sự kiện toàn cục mở chat với PT cụ thể từ bất kỳ trang nào
  useEffect(() => {
    const handleOpenChat = (e: any) => {
      const detail = e.detail;
      if (!detail || !detail.partnerId) return;

      const partnerId = Number(detail.partnerId);
      const existing = conversations.find(c => c.partnerId === partnerId);

      const targetPartner: ChatConversation = existing || {
        partnerId,
        partnerName: detail.partnerName || 'Huấn Luyện Viên',
        partnerEmail: detail.partnerEmail || '',
        partnerAvatar: detail.partnerAvatar,
        partnerRole: detail.partnerRole || 'PT',
        lastMessage: 'Bắt đầu cuộc trò chuyện',
        unreadCount: 0,
      };

      setSelectedPartner(targetPartner);
      setIsOpen(true);
      setIsMinimized(false);
      setErrorMessage(null);
      if (detail.initialMessage) {
        setInputContent(detail.initialMessage);
      }
      fetchMessages(partnerId);
    };

    window.addEventListener('ptconnect:open_chat' as any, handleOpenChat);
    return () => window.removeEventListener('ptconnect:open_chat' as any, handleOpenChat);
  }, [conversations]);

  // Gửi tin nhắn
  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputContent).trim();
    if (!text || !selectedPartner || sending) return;

    // Không cho phép nhắn tin cho chính tài khoản của mình
    if (currentUser?.id && selectedPartner.partnerId === currentUser.id) {
      setErrorMessage('Bạn đang đăng nhập chính tài khoản này nên không thể tự nhắn tin cho bản thân!');
      return;
    }

    setSending(true);
    setErrorMessage(null);
    try {
      const res: any = await api.post('/chat/send', {
        recipientId: selectedPartner.partnerId,
        content: text,
      });

      const newMsg = unwrapItem(res);
      if (newMsg && newMsg.id) {
        setMessages(prev => {
          if (prev.some(m => m.id === newMsg.id)) return prev;
          return [...prev, newMsg];
        });
        setInputContent('');
        fetchConversations();
      } else {
        fetchMessages(selectedPartner.partnerId);
        setInputContent('');
      }
    } catch (err: any) {
      console.error('Lỗi gửi tin nhắn:', err);
      setErrorMessage(err.message || 'Lỗi gửi tin nhắn, vui lòng thử lại!');
    } finally {
      setSending(false);
    }
  };

  // Gợi ý tin nhắn nhanh
  const quickChips = currentUser.role === 'STUDENT' ? [
    '👋 Chào PT, mình muốn trao đổi về lịch tập tuần này',
    '💪 Hôm nay bài tập thể lực thế nào vậy ạ?',
    '🥗 Nhờ PT gợi ý thực đơn ăn uống giảm mỡ',
    '⏱️ PT có thể đổi ca sang buổi tối được không ạ?'
  ] : [
    '👋 Chào bạn, sẵn sàng cho buổi tập hôm nay chưa?',
    '💧 Nhớ uống đủ nước và khởi động kỹ nhé!',
    '🎯 Hôm nay chúng ta sẽ tập trung vào nhóm cơ ngực và vai',
    '✅ Mình đã cập nhật giáo án mới, bạn vào xem nhé'
  ];

  // Lọc danh sách hội thoại
  const filteredConversations = conversations.filter(c => 
    c.partnerName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.partnerEmail.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatMessageTime = (iso?: string) => {
    if (!iso) return '';
    try {
      const d = new Date(iso);
      return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    } catch {
      return '';
    }
  };

  return (
    <>
      {/* 1. NÚT CHAT BONG BÓNG GÓC PHẢI DƯỚI (FLOATING CHAT BUBBLE) */}
      {!isOpen && (
        <div className="fixed bottom-6 right-6 z-30 flex items-center gap-3">
          <div className="hidden md:flex items-center bg-white px-3.5 py-1.5 rounded-full shadow-lg border border-slate-200 text-xs font-semibold text-slate-700 animate-fade-in">
            <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-ping" />
            Hỗ trợ & Trò chuyện trực tiếp
          </div>
          <button
            onClick={() => {
              setIsOpen(true);
              setIsMinimized(false);
              fetchConversations();
            }}
            className="group relative w-14 h-14 rounded-full bg-gradient-to-tr from-red-600 via-orange-500 to-amber-500 text-white shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95 transition-all duration-300 flex items-center justify-center cursor-pointer border-2 border-white/60 focus:outline-none"
            aria-label="Mở cửa sổ Chat"
          >
            <MessageCircle className="w-7 h-7 drop-shadow-md group-hover:rotate-6 transition-transform" />
            
            {/* Badge tin nhắn chưa đọc nhấp nháy */}
            {totalUnread > 0 && (
              <span className="absolute -top-1 -right-1 min-w-[22px] h-[22px] px-1 bg-red-600 border-2 border-white text-white text-[11px] font-extrabold rounded-full flex items-center justify-center animate-bounce shadow-md">
                {totalUnread > 99 ? '99+' : totalUnread}
              </span>
            )}
          </button>
        </div>
      )}

      {/* 2. CỬA SỔ CHAT FLOATING POPUP (SHOPEE / MESSENGER STYLE) */}
      {isOpen && (
        <div 
          className={`fixed bottom-6 right-6 z-30 w-[380px] sm:w-[410px] bg-white rounded-2xl shadow-2xl border border-slate-200/90 flex flex-col overflow-hidden transition-all duration-300 ${
            isMinimized ? 'h-[60px]' : 'h-[580px]'
          }`}
          style={{ boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.25)' }}
        >
          {/* HEADER CỬA SỔ CHAT */}
          <div className="h-[60px] bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 text-white px-4 flex items-center justify-between border-b border-slate-800 select-none">
            <div className="flex items-center gap-2.5 min-w-0">
              {selectedPartner ? (
                <>
                  <button 
                    onClick={() => setSelectedPartner(null)} 
                    className="p-1 -ml-1 text-slate-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                    title="Quay lại danh sách"
                  >
                    <ChevronLeft className="w-5 h-5" />
                  </button>
                  <div className="relative flex-shrink-0">
                    <img 
                      src={selectedPartner.partnerAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${selectedPartner.partnerEmail}`} 
                      alt="" 
                      className="w-9 h-9 rounded-full object-cover border border-orange-500/50 bg-slate-800"
                    />
                    <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-slate-950" />
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-bold text-white truncate flex items-center gap-1.5">
                      <span>{selectedPartner.partnerName}</span>
                      <span className="text-[10px] px-1.5 py-0.2 bg-orange-500/20 text-orange-400 border border-orange-500/30 rounded font-semibold">
                        {selectedPartner.partnerRole === 'PT' ? 'HLV' : 'Học Viên'}
                      </span>
                    </div>
                    <div className="text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> Đang hoạt động
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-red-500 to-orange-500 flex items-center justify-center shadow-inner">
                    <MessageCircle className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-white tracking-wide flex items-center gap-1.5">
                      PTConnect Chat
                      <span className="px-1.5 py-0.5 rounded text-[10px] bg-red-500/20 text-red-400 border border-red-500/30 font-semibold">1-1</span>
                    </h3>
                    <p className="text-[11px] text-slate-400">Trò chuyện trực tiếp HLV & Học viên</p>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={() => {
                  if (selectedPartner) fetchMessages(selectedPartner.partnerId);
                  else fetchConversations();
                }}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                title="Làm mới"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
                title={isMinimized ? 'Mở rộng' : 'Thu nhỏ'}
              >
                <Minus className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  setIsOpen(false);
                  setSelectedPartner(null);
                }}
                className="p-1.5 text-slate-400 hover:text-red-400 rounded-lg hover:bg-white/10 transition-colors"
                title="Đóng chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* NỘI DUNG CHAT (NẾU KHÔNG BỊ THU NHỎ) */}
          {!isMinimized && (
            <div className="flex-1 flex flex-col bg-slate-50/50 overflow-hidden">
              {/* VIEW 1: DANH SÁCH CUỘC TRÒ CHUYỆN */}
              {!selectedPartner ? (
                <div className="flex-1 flex flex-col overflow-hidden">
                  {/* Ô tìm kiếm liên hệ */}
                  <div className="p-3 bg-white border-b border-slate-200">
                    <div className="relative">
                      <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <input 
                        type="text" 
                        placeholder="Tìm kiếm theo tên HLV hoặc học viên..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-9 pr-3 py-2 bg-slate-100 hover:bg-slate-50 focus:bg-white border border-transparent focus:border-orange-500 rounded-xl text-xs text-slate-800 placeholder-slate-400 outline-none transition-all"
                      />
                    </div>
                  </div>

                  {/* Danh sách người chat */}
                  <div className="flex-1 overflow-y-auto divide-y divide-slate-100 p-1">
                    {filteredConversations.length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center p-6 text-center text-slate-400">
                        <div className="w-16 h-16 rounded-full bg-orange-50 flex items-center justify-center mb-3 text-orange-500">
                          <MessageCircle className="w-8 h-8" />
                        </div>
                        <p className="text-sm font-semibold text-slate-700">Chưa có cuộc trò chuyện nào</p>
                        <p className="text-xs text-slate-400 mt-1 max-w-[240px]">
                          {currentUser.role === 'STUDENT' 
                            ? 'Bấm nút "Nhắn tin" trên hồ sơ bất kỳ HLV nào để bắt đầu trao đổi lịch tập!'
                            : 'Khi học viên đặt lịch hoặc nhắn tin, cuộc trò chuyện sẽ hiển thị tại đây.'}
                        </p>
                      </div>
                    ) : (
                      filteredConversations.map((conv) => (
                        <div
                          key={conv.partnerId}
                          onClick={() => {
                            setSelectedPartner(conv);
                            fetchMessages(conv.partnerId);
                          }}
                          className="flex items-center gap-3 p-3 hover:bg-white rounded-xl cursor-pointer transition-all border border-transparent hover:border-slate-200 hover:shadow-xs group"
                        >
                          <div className="relative flex-shrink-0">
                            <img 
                              src={conv.partnerAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${conv.partnerEmail}`}
                              alt=""
                              className="w-12 h-12 rounded-full object-cover border border-slate-200 group-hover:border-orange-400 transition-colors"
                            />
                            <span className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-emerald-500 ring-2 ring-white" />
                          </div>

                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between mb-0.5">
                              <h4 className="text-sm font-bold text-slate-800 truncate group-hover:text-orange-600 transition-colors">
                                {conv.partnerName}
                              </h4>
                              {conv.lastMessageTime && (
                                <span className="text-[10px] text-slate-400 flex-shrink-0 ml-1">
                                  {formatMessageTime(conv.lastMessageTime)}
                                </span>
                              )}
                            </div>

                            <div className="flex items-center justify-between">
                              <p className={`text-xs truncate max-w-[190px] ${conv.unreadCount > 0 ? 'font-bold text-slate-900' : 'text-slate-500'}`}>
                                {conv.lastMessage}
                              </p>
                              {conv.unreadCount > 0 && (
                                <span className="min-w-[18px] h-[18px] px-1.5 bg-red-600 text-white text-[10px] font-extrabold rounded-full flex items-center justify-center flex-shrink-0 ml-1">
                                  {conv.unreadCount}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              ) : (
                /* VIEW 2: KHUNG CHAT CHI TIẾT 1-1 */
                <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
                  {/* Dòng thông báo mã hóa bảo mật */}
                  <div className="px-3 py-1.5 bg-amber-50 border-b border-amber-200/60 text-[11px] text-amber-800 flex items-center justify-center gap-1.5 font-medium">
                    <ShieldCheck className="w-3.5 h-3.5 text-amber-600" />
                    Kênh trao đổi chính thức giữa HLV & Học viên PTConnect
                  </div>

                  {/* Cảnh báo lỗi nếu có */}
                  {errorMessage && (
                    <div className="px-3.5 py-2 bg-red-50 border-b border-red-200 text-xs text-red-600 flex items-center justify-between">
                      <span className="font-semibold">⚠️ {errorMessage}</span>
                      <button
                        onClick={() => setErrorMessage(null)}
                        className="text-red-400 hover:text-red-700 font-bold ml-2 text-sm cursor-pointer"
                        title="Đóng thông báo"
                      >
                        ×
                      </button>
                    </div>
                  )}

                  {/* Lịch sử tin nhắn */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {loading ? (
                      <div className="h-full flex items-center justify-center text-slate-400 text-xs gap-2">
                        <RefreshCw className="w-4 h-4 animate-spin text-orange-500" />
                        Đang tải lịch sử tin nhắn...
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center text-center p-6 text-slate-400">
                        <div className="w-12 h-12 rounded-full bg-slate-200 flex items-center justify-center mb-2 text-slate-500">
                          <Smile className="w-6 h-6" />
                        </div>
                        <p className="text-xs font-semibold text-slate-600">Bắt đầu cuộc trò chuyện với {selectedPartner.partnerName}</p>
                        <p className="text-[11px] text-slate-400 mt-0.5">Gửi tin nhắn hoặc chọn nhanh một câu hỏi bên dưới.</p>
                      </div>
                    ) : (
                      messages.map((msg) => {
                        const isMe = msg.senderId === currentUser.id;
                        return (
                          <div 
                            key={msg.id} 
                            className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
                          >
                            <div className="flex items-end gap-1.5 max-w-[82%]">
                              {!isMe && (
                                <img 
                                  src={msg.senderAvatar || selectedPartner.partnerAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${msg.senderName}`}
                                  alt=""
                                  className="w-6 h-6 rounded-full object-cover mb-1 border border-slate-200 flex-shrink-0"
                                />
                              )}
                              <div
                                className={`px-3.5 py-2 text-xs leading-relaxed shadow-xs ${
                                  isMe
                                    ? 'bg-gradient-to-r from-red-600 to-orange-500 text-white rounded-2xl rounded-br-xs'
                                    : 'bg-white text-slate-800 rounded-2xl rounded-bl-xs border border-slate-200'
                                }`}
                              >
                                {msg.content}
                              </div>
                            </div>
                            <div className="flex items-center gap-1 mt-0.5 px-1 text-[10px] text-slate-400">
                              <span>{formatMessageTime(msg.createdAt)}</span>
                              {isMe && (
                                <CheckCheck className={`w-3 h-3 ${msg.isRead ? 'text-blue-500' : 'text-slate-400'}`} />
                              )}
                            </div>
                          </div>
                        );
                      })
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Thanh gợi ý tin nhắn nhanh (Quick Chips) */}
                  <div className="px-3 py-1.5 bg-white border-t border-slate-200 overflow-x-auto whitespace-nowrap scrollbar-none flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-orange-500 flex-shrink-0" />
                    {quickChips.map((chip, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSendMessage(chip)}
                        className="px-2.5 py-1 bg-slate-100 hover:bg-orange-50 hover:text-orange-600 border border-slate-200 hover:border-orange-200 rounded-full text-[11px] text-slate-600 transition-colors flex-shrink-0"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>

                  {/* Ô nhập tin nhắn */}
                  <div className="p-3 bg-white border-t border-slate-200 flex items-center gap-2">
                    <input
                      type="text"
                      placeholder={`Nhắn tin cho ${selectedPartner.partnerName}...`}
                      value={inputContent}
                      onChange={(e) => setInputContent(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      className="flex-1 px-3.5 py-2 bg-slate-100 hover:bg-slate-50 focus:bg-white border border-transparent focus:border-orange-500 rounded-xl text-xs text-slate-800 placeholder-slate-400 outline-none transition-all"
                    />
                    <button
                      onClick={() => handleSendMessage()}
                      disabled={!inputContent.trim() || sending}
                      className="w-9 h-9 rounded-xl bg-gradient-to-r from-red-600 to-orange-500 hover:from-red-700 hover:to-orange-600 disabled:opacity-40 text-white flex items-center justify-center transition-all shadow-sm flex-shrink-0 cursor-pointer disabled:cursor-not-allowed"
                      title="Gửi (Enter)"
                    >
                      {sending ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Send className="w-4 h-4 -ml-0.5" />
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
};
