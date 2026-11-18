import React, { useState, useEffect } from 'react';
import { Course } from '../types/api';
import {
  X,
  Calendar,
  Clock,
  DollarSign,
  Sparkles,
  CheckCircle2,
  Dumbbell,
  Target,
  Flame,
  Award,
  BookOpen,
  Apple,
  ShieldCheck,
  Zap,
  Activity,
  HeartPulse,
  Edit3,
  Save,
  RotateCcw,
  Plus,
  Trash2,
  Eye,
} from 'lucide-react';

interface CoursePreviewModalProps {
  course: Course | null;
  isOpen: boolean;
  onClose: () => void;
  onEnroll?: (course: Course) => void;
  isPtView?: boolean;
}

interface SyllabusStage {
  stage: string;
  sessions: string;
  title: string;
  description: string;
  keyTopics: string[];
}

interface DemoExercise {
  name: string;
  targetMuscle: string;
  equipment: string;
  benefit: string;
}

interface CourseSyllabusData {
  categoryLabel: string;
  stages: SyllabusStage[];
  demoExercises: DemoExercise[];
  outcomes: string[];
  prepNotes: string[];
}

// Hàm sinh dữ liệu mẫu mặc định theo tiêu đề/mô tả khóa học
const getDefaultSyllabus = (course: Course): CourseSyllabusData => {
  const titleLower = (course.title || '').toLowerCase();
  const descLower = (course.description || '').toLowerCase();

  const isGlute =
    titleLower.includes('mông') || titleLower.includes('đít') || titleLower.includes('dit') ||
    titleLower.includes('glute') || titleLower.includes('booty') || titleLower.includes('hip') ||
    descLower.includes('mông') || descLower.includes('đít') || descLower.includes('dit') ||
    descLower.includes('glute') || descLower.includes('booty') || descLower.includes('hip');

  const total = course.totalSessions || 12;

  if (isGlute) {
    return {
      categoryLabel: 'Tăng Cơ Mông & Định Hình Thân Dưới (Glutes & Lower Body Focus)',
      stages: [
        {
          stage: 'Giai đoạn 1',
          sessions: `Buổi 1 - ${Math.max(2, Math.round(total * 0.25))}`,
          title: 'Đánh Thức Cơ Mông Lớn (Glute Activation) & Kỹ Thuật Gập Hông (Hip Hinge)',
          description: 'Khắc phục triệt để hội chứng "quên cơ mông" do ngồi nhiều, học cách dùng lực cơ mông thay vì mỏi thắt lưng.',
          keyTopics: [
            'Học chuyển động gập hông (Hip Hinge) chuẩn xác để bảo vệ tuyệt đối đĩa đệm lưng dưới',
            'Kích hoạt cơ mông nhỡ với dây kháng lực Mini-band: Banded Clamshell, Lateral Walk',
            'Đo đạc chu vi vòng 3, tỷ lệ eo/hông (WHR) và chụp ảnh form dáng ban đầu',
          ],
        },
        {
          stage: 'Giai đoạn 2',
          sessions: `Buổi ${Math.round(total * 0.25) + 1} - ${Math.round(total * 0.6)}`,
          title: 'Tăng Tải Tạ Nặng Cho Bài Tập Vua (Barbell Hip Thrust & RDL Mastery)',
          description: 'Tập trung vào 2 bài tập phát triển kích thước cơ mông hiệu quả nhất theo nguyên lý tăng tiến trọng lượng.',
          keyTopics: [
            'Kỹ thuật Barbell Hip Thrust chuyên sâu: Điểm khóa khớp hông, gồng cơ bụng nén lực',
            'Romanian Deadlift (RDL) chuẩn form: Kéo căng cơ đùi sau và nâng mông cao tự nhiên',
            'Cách hít thở gồng bụng (Bracing) giữ lưng thẳng tắp khi nâng tạ nặng',
          ],
        },
        {
          stage: 'Giai đoạn 3',
          sessions: `Buổi ${Math.round(total * 0.6) + 1} - ${Math.round(total * 0.85)}`,
          title: 'Cô Lập Từng Bên Mông (Unilateral) & Khắc Phục Lõm Hông (Hip Dip)',
          description: 'Khắc phục bất đối xứng cơ thể giữa hai bên chân, làm đầy bờ hông giúp đường cong chữ S mềm mại, quyến rũ.',
          keyTopics: [
            'Bulgarian Split Squat: Tác động cực sâu vào phần nọng mông và cơ đùi trước',
            'Cable Glute Kickback & Hip Abduction: Đánh vào nhóm cơ mông trên và mông nhỡ',
            'Superset kết hợp bài tập tạ và tạ chuông đốt cháy sợi cơ tối đa',
          ],
        },
        {
          stage: 'Giai đoạn 4',
          sessions: `Buổi ${Math.round(total * 0.85) + 1} - ${total}`,
          title: 'Siết Nét Đường Cong, Thon Gọn Đùi & Đánh Giá Số Đo Tổng Kết',
          description: 'Định hình form dáng sắc nét, đo lại chỉ số chu vi vòng 3 tăng ròng và bàn giao giáo án tự tập duy trì.',
          keyTopics: [
            'Đo lại chu vi vòng 3 và chụp ảnh đối chiếu Before/After (cam kết tăng 2 - 5cm)',
            'Ghép chuỗi bài tập Booty Burner kết thúc buổi tập giúp mông căng tròn',
            'Bàn giao lịch tập mẫu 3 buổi/tuần và thực đơn bổ sung Protein nuôi cơ mông',
          ],
        },
      ],
      demoExercises: [
        {
          name: 'Barbell Hip Thrust (Vua bài tập mông)',
          targetMuscle: 'Cơ mông lớn (Gluteus Maximus), Cơ lõi',
          equipment: 'Thanh đòn Barbell & Đệm mút kê hông',
          benefit: 'Kích thích tăng kích thước vòng 3 nhanh nhất mà không làm to bắp chân.',
        },
        {
          name: 'Romanian Deadlift (RDL)',
          targetMuscle: 'Cơ mông, Cơ đùi sau (Hamstrings), Lưng dưới',
          equipment: 'Thanh đòn hoặc Cặp tạ đơn Dumbbell',
          benefit: 'Nâng cao nọng mông, tạo bờ mông cong vút và đôi chân thon dài.',
        },
        {
          name: 'Bulgarian Split Squat',
          targetMuscle: 'Cơ mông, Đùi trước, Thăng bằng hông',
          equipment: 'Ghế tập phẳng Bench & Tạ đơn',
          benefit: 'Sửa lỗi lệch cơ giữa hai chân, khắc phục triệt để tình trạng mông lép một bên.',
        },
        {
          name: 'Cable Glute Kickback & Abduction',
          targetMuscle: 'Cơ mông nhỡ (Gluteus Medius), Hõm hông',
          equipment: 'Máy kéo cáp Cable Station & Đai cổ chân',
          benefit: 'Làm đầy hõm hông hai bên, tạo đường thắt eo đồng hồ cát quyến rũ.',
        },
      ],
      outcomes: [
        'Tăng từ 2cm đến 5cm chu vi vòng 3 sau trọn vẹn khóa học (tùy thể trạng ban đầu).',
        'Định hình dáng mông cao tròn, đẩy lùi hoàn toàn tình trạng mông chảy xệ hay hõm hông.',
        'Đùi thon gọn, săn chắc, triệt tiêu mỡ thừa nọng đùi sau.',
        'Chấm dứt hoàn toàn cảm giác mỏi thắt lưng khi đứng lâu nhờ cơ mông đã chịu lực thay cột sống.',
      ],
      prepNotes: [
        'Nên chuẩn bị một chiếc đệm bọc đòn tạ (Barbell Pad) cá nhân để tập Hip Thrust êm ái.',
        'Chuẩn bị bộ dây kháng lực vải (Fabric Booty Bands) để khởi động cơ mông.',
        'Ăn bữa phụ giàu đạm và tinh bột tốt trước giờ tập 60 phút (bánh mì đen, chuối, sữa chua Hy Lạp).',
      ],
    };
  }

  if (titleLower.includes('pilates') || titleLower.includes('chỉnh dáng') || titleLower.includes('cột sống')) {
    return {
      categoryLabel: 'Pilates Chỉnh Dáng & Phục Hồi Cột Sống (Posture Rehab)',
      stages: [
        {
          stage: 'Giai đoạn 1',
          sessions: `Buổi 1 - ${Math.max(2, Math.round(total * 0.2))}`,
          title: 'Đánh Giá Sai Lệch Khung Xương & Kỹ Thuật Thở Khung Sườn',
          description: 'Đo quét tư thế tĩnh và động, xác định mức độ gù lưng, cổ rùa và võng thắt lưng.',
          keyTopics: [
            'Học nhịp thở cơ hoành (Lateral Diaphragmatic Breathing) giúp giải tỏa áp lực cơ cổ',
            'Tìm điểm cân bằng khung chậu (Neutral Pelvis) và kích hoạt cơ sàn chậu',
            'Chuỗi bài tập kéo giãn giải phóng cơ co cứng: Cat-Cow, Spine Stretch Forward',
          ],
        },
        {
          stage: 'Giai đoạn 2',
          sessions: `Buổi ${Math.round(total * 0.2) + 1} - ${Math.round(total * 0.55)}`,
          title: 'Kích Hoạt Nhóm Cơ Lõi Sâu (Deep Core) & Thắt Lưng Bụng',
          description: 'Tập trung đánh thức nhóm cơ bụng sâu và cơ mông yếu để ổn định cột sống thắt lưng.',
          keyTopics: [
            'Bài tập The Hundred cổ điển trên thảm giúp kích hoạt tuần hoàn và làm săn chắc cơ bụng',
            'Single Leg Stretch, Double Leg Stretch kiểm soát thăng bằng cơ thể',
            'Pelvic Curl và Shoulder Bridge hỗ trợ linh hoạt từng đốt sống lưng',
          ],
        },
        {
          stage: 'Giai đoạn 3',
          sessions: `Buổi ${Math.round(total * 0.55) + 1} - ${Math.round(total * 0.85)}`,
          title: 'Tập Luyện Với Máy Reformer & Khắc Phục Tư Thế Vai Cuộn',
          description: 'Ứng dụng hệ thống lò xo kháng lực của máy Reformer để kéo giãn giải nén đốt sống không trọng lực.',
          keyTopics: [
            'Reformer Footwork & Straps: Căn chỉnh xương hông và trục đầu gối chuẩn',
            'Chest Expansion & Swan Dive: Mở rộng khớp vai, xóa bỏ triệt để tật lưng gù văn phòng',
            'Spine Twist & Mermaid Stretch: Tăng độ dẻo dai cơ liên sườn và cột sống xoay',
          ],
        },
        {
          stage: 'Giai đoạn 4',
          sessions: `Buổi ${Math.round(total * 0.85) + 1} - ${total}`,
          title: 'Nâng Cao Khả Năng Thăng Bằng & Tự Duy Trì Vóc Dáng Chuẩn',
          description: 'Ghép chuỗi động tác Flow Pilates liền mạch, đo lại chỉ số cơ xương khớp và bàn giao giáo án duy trì.',
          keyTopics: [
            'Bài tập thăng bằng nâng cao với bóng Mini Ball và Foam Roller',
            'Chụp ảnh đối chiếu Before - After tư thế đứng và đi lại tự nhiên',
            'Bàn giao bộ bài tập 10 phút tại bàn làm việc để giữ dáng lâu dài',
          ],
        },
      ],
      demoExercises: [
        {
          name: 'The Hundred (Pilates Mat)',
          targetMuscle: 'Cơ bụng sâu, Cơ liên sườn, Tuần hoàn máu',
          equipment: 'Thảm Mat chuyên dụng',
          benefit: 'Tạo cơ bụng thon gọn, kích thích lưu thông máu và ổn định khung chậu.',
        },
        {
          name: 'Reformer Chest Expansion',
          targetMuscle: 'Cơ lưng trên, Cơ vai sau, Cơ tam đầu',
          equipment: 'Máy Reformer & Lò xo kháng lực',
          benefit: 'Mở rộng lồng ngực tự nhiên, đẩy lùi tình trạng gù lưng do ngồi vi tính lâu.',
        },
        {
          name: 'Pelvic Curl & Spine Articulation',
          targetMuscle: 'Cơ mông, Cơ đùi sau, Cột sống thắt lưng',
          equipment: 'Thảm & Vòng Magic Circle',
          benefit: 'Giảm đau mỏi thắt lưng dưới, giải nén từng đốt sống bị chèn ép.',
        },
        {
          name: 'Mermaid Side Stretch',
          targetMuscle: 'Cơ vuông thắt lưng, Cơ liên sườn',
          equipment: 'Khung Cadillac / Thảm',
          benefit: 'Cải thiện độ mềm dẻo lồng ngực, thon gọn rãnh eo hai bên hông.',
        },
      ],
      outcomes: [
        'Giảm trên 80% triệu chứng đau mỏi vai gáy và đau thắt lưng dưới do ngồi sai tư thế.',
        'Khắc phục hoàn toàn tật cổ rùa và vai cuộn, tạo dáng đứng kiêu hãnh, tự tin.',
        'Vòng eo thon gọn, phẳng lì nhờ kích hoạt đúng nhóm cơ bụng sâu.',
        'Tăng dung tích phổi và sự thư thái tinh thần thông qua kỹ thuật thở Pilates chuẩn xác.',
      ],
      prepNotes: [
        'Trang phục ôm sát co giãn để Huấn luyện viên dễ quan sát đường cong cột sống.',
        'Nên sử dụng tất có hạt cao su chống trượt (Grip Socks) khi tập trên máy Reformer.',
        'Nên uống một cốc nước ấm trước buổi tập 15 phút, tránh ăn quá no sát giờ tập.',
      ],
    };
  }

  // Mặc định chung cho khóa khác
  return {
    categoryLabel: 'Giáo Trình Huấn Luyện Thể Hình Cá Nhân Hóa',
    stages: [
      {
        stage: 'Giai đoạn 1',
        sessions: `Buổi 1 - ${Math.max(2, Math.round(total * 0.25))}`,
        title: 'Khảo Sát Thể Trạng & Kỹ Thuật Nền Tảng An Toàn',
        description: 'Đánh giá chỉ số InBody, kiểm tra biên độ khớp và rèn kỹ thuật các bài tập cơ bản.',
        keyTopics: [
          'Đo quét chỉ số cơ xương mỡ InBody và xác định mức calo tiêu thụ hàng ngày',
          'Chuẩn hóa form động tác an toàn, học kỹ thuật hít thở phát lực',
          'Khởi động động và giãn cơ tĩnh tránh chấn thương khớp',
        ],
      },
      {
        stage: 'Giai đoạn 2',
        sessions: `Buổi ${Math.round(total * 0.25) + 1} - ${Math.round(total * 0.6)}`,
        title: 'Tăng Cường Cường Độ & Tối Ưu Hóa Kích Thích Cơ Bắp',
        description: `Tập trung chuyên sâu vào nội dung ${course.description || 'huấn luyện cá nhân hóa theo từng buổi tập'}.`,
        keyTopics: [
          'Tăng tải trọng lượng theo nguyên lý Progressive Overload an toàn',
          'Tối ưu hóa thời gian co cơ (Time-Under-Tension) kích thích sợi cơ phát triển',
          'Theo dõi nhật ký tập luyện và mức tạ tăng dần qua từng tuần',
        ],
      },
      {
        stage: 'Giai đoạn 3',
        sessions: `Buổi ${Math.round(total * 0.6) + 1} - ${Math.round(total * 0.85)}`,
        title: 'Cô Lập Nhóm Cơ Trọng Điểm & Khắc Phục Điểm Yếu',
        description: 'Đột phá điểm chững thể lực, áp dụng bài tập Superset và rèn luyện thể lực bền.',
        keyTopics: [
          'Tập luyện các bài tập cô lập (Isolation) cho nhóm cơ mục tiêu',
          'Khắc phục bất đối xứng cơ thể giữa bên trái và bên phải',
          'Điều chỉnh chế độ dinh dưỡng hàng ngày phù hợp với cường độ tập',
        ],
      },
      {
        stage: 'Giai đoạn 4',
        sessions: `Buổi ${Math.round(total * 0.85) + 1} - ${total}`,
        title: 'Siết Nét Form Dáng, Đo Lại Chỉ Số & Bàn Giao Tự Tập',
        description: 'Đánh giá tiến bộ tổng kết sau toàn bộ khóa học và chuyển giao giáo án duy trì.',
        keyTopics: [
          'Đo lại chỉ số InBody tổng kết: đối chiếu lượng cơ nạc và lượng mỡ đã thay đổi',
          'Xây dựng thời gian biểu sinh hoạt và chế độ ăn uống khoa học bền vững',
          'Bàn giao lịch tập mẫu 3 buổi/tuần để học viên tự tập tự tin',
        ],
      },
    ],
    demoExercises: [
      {
        name: 'Compound Movement (Bài tập đa khớp then chốt)',
        targetMuscle: 'Nhóm cơ lớn trọng tâm',
        equipment: 'Thanh đòn / Tạ đơn',
        benefit: 'Xây dựng nền tảng sức mạnh và kích thích trao đổi chất mạnh mẽ.',
      },
      {
        name: 'Isolation Exercise (Bài tập cô lập mục tiêu)',
        targetMuscle: 'Nhóm cơ chuyên biệt của khóa',
        equipment: 'Máy kéo cáp / Tạ chuông',
        benefit: 'Tác động chính xác vào vùng cơ mong muốn, định hình đường cong săn chắc.',
      },
      {
        name: 'Core & Stability Drill (Cơ lõi & Thăng bằng)',
        targetMuscle: 'Cơ bụng sâu, Cơ lưng, Khung chậu',
        equipment: 'Thảm tập / Bóng thể lực',
        benefit: 'Bảo vệ cột sống, tăng sức bền và tạo vòng eo thon gọn.',
      },
      {
        name: 'Cool-down Mobility & Stretch (Phục hồi)',
        targetMuscle: 'Toàn thân',
        equipment: 'Ống lăn Foam Roller & Dây kéo giãn',
        benefit: 'Giải tỏa axit lactic, giảm đau cơ sau tập và tăng độ dẻo dai cơ bắp.',
      },
    ],
    outcomes: [
      'Đạt được mục tiêu cam kết theo đúng nội dung khóa học.',
      'Nắm vững 100% kỹ thuật chuẩn xác của các bài tập, tự tin tập luyện an toàn.',
      'Vóc dáng thay đổi tích cực, số đo các vòng được cải thiện rõ nét.',
      'Hình thành lối sống kỷ luật và thói quen rèn luyện thể chất bền vững suốt đời.',
    ],
    prepNotes: [
      'Trang phục thể thao thoải mái, giày tập vừa vặn êm chân.',
      'Ăn nhẹ trước giờ tập từ 45 - 60 phút, không để bụng quá đói hoặc quá no.',
      'Mang theo bình nước cá nhân để uống từng ngụm nhỏ trong buổi tập.',
    ],
  };
};

export const CoursePreviewModal: React.FC<CoursePreviewModalProps> = ({
  course,
  isOpen,
  onClose,
  onEnroll,
  isPtView = false,
}) => {
  const [activeTab, setActiveTab] = useState<'ROADMAP' | 'EXERCISES' | 'OUTCOMES' | 'PREP'>('ROADMAP');
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [syllabusData, setSyllabusData] = useState<CourseSyllabusData | null>(null);
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null);

  // Nạp giáo trình từ localStorage nếu HLV đã từng tùy chỉnh, hoặc sinh dữ liệu mặc định
  useEffect(() => {
    if (!course) return;
    setIsEditing(false);
    setSaveSuccessMsg(null);

    const storageKey = `ptconnect_course_custom_syllabus_${course.id}`;
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      try {
        setSyllabusData(JSON.parse(saved));
        return;
      } catch {
        // Fallback to default
      }
    }
    setSyllabusData(getDefaultSyllabus(course));
  }, [course]);

  if (!isOpen || !course || !syllabusData) return null;

  // Xử lý lưu giáo trình tùy chỉnh của Huấn luyện viên
  const handleSaveCustomSyllabus = () => {
    if (!course || !syllabusData) return;
    const storageKey = `ptconnect_course_custom_syllabus_${course.id}`;
    try {
      localStorage.setItem(storageKey, JSON.stringify(syllabusData));
      setSaveSuccessMsg('✓ Đã lưu bản demo giáo trình thành công! Học viên giờ đây sẽ nhìn thấy bản lộ trình này khi xem.');
      setIsEditing(false);
      setTimeout(() => setSaveSuccessMsg(null), 4000);
    } catch {
      setSaveSuccessMsg('Lỗi khi lưu giáo trình vào bộ nhớ.');
    }
  };

  // Nạp nhanh mẫu giáo trình gợi ý theo chuyên môn
  const handleApplyTemplate = (type: 'GLUTES' | 'PILATES' | 'MUSCLE' | 'FAT_LOSS') => {
    const total = course.totalSessions || 12;
    let mockCourse = { ...course };
    if (type === 'GLUTES') mockCourse.title = 'Tăng cơ mông đùi';
    if (type === 'PILATES') mockCourse.title = 'Pilates chỉnh dáng cột sống';
    if (type === 'MUSCLE') mockCourse.title = 'Tăng cơ thể hình';
    if (type === 'FAT_LOSS') mockCourse.title = 'Giảm mỡ chuyên sâu';
    setSyllabusData(getDefaultSyllabus(mockCourse));
  };

  const sessionFee = Math.round(course.basePrice / (course.totalSessions || 1));

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/75 backdrop-blur-xs flex items-center justify-center p-3 sm:p-5 overflow-y-auto animate-fade-in">
      <div className="relative w-full max-w-4xl max-h-[92vh] flex flex-col rounded-3xl bg-white dark:bg-slate-900 text-slate-800 dark:text-slate-100 shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden">
        {/* Banner Header */}
        <div className="px-6 py-5 bg-gradient-to-r from-rose-600 via-pink-600 to-orange-500 text-white shrink-0 relative overflow-hidden">
          <div className="absolute right-0 top-0 translate-x-8 -translate-y-8 w-44 h-44 rounded-full bg-white/10 blur-xl pointer-events-none" />

          <div className="flex items-start justify-between gap-4 relative z-10">
            <div className="space-y-1.5 max-w-2xl">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-bold bg-white/20 backdrop-blur-md border border-white/30 text-white uppercase tracking-wider">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>{syllabusData.categoryLabel}</span>
                </span>
                {!isPtView && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/30 text-white border border-emerald-300/40">
                    <CheckCircle2 className="w-3 h-3 text-emerald-300" /> Giáo trình chính thức từ HLV
                  </span>
                )}
              </div>
              <h2 className="text-xl sm:text-2xl font-black tracking-tight leading-snug">
                {course.title}
              </h2>
              <p className="text-xs sm:text-sm text-white/90 line-clamp-2 leading-relaxed">
                {course.description || 'Chương trình huấn luyện 1-kèm-1 bài bản, thiết kế theo thể trạng học viên.'}
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              {/* Nút dành riêng cho Huấn luyện viên: Biên soạn / Sửa Demo */}
              {isPtView && (
                <button
                  type="button"
                  onClick={() => setIsEditing(!isEditing)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-bold transition flex items-center gap-1.5 cursor-pointer shadow-md ${
                    isEditing
                      ? 'bg-white text-rose-700 hover:bg-slate-100'
                      : 'bg-white/20 hover:bg-white/30 text-white border border-white/30'
                  }`}
                  title={isEditing ? 'Thoát chế độ sửa để xem giao diện học viên' : 'Biên soạn nội dung lộ trình demo cho khóa này'}
                >
                  {isEditing ? (
                    <>
                      <Eye className="w-3.5 h-3.5" />
                      <span>Xem Giao Diện Học Viên</span>
                    </>
                  ) : (
                    <>
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>Biên Soạn Lộ Trình Demo</span>
                    </>
                  )}
                </button>
              )}

              <button
                onClick={onClose}
                className="p-2 rounded-xl bg-white/10 hover:bg-white/20 text-white transition cursor-pointer"
                title="Đóng xem trước"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mt-4 pt-3 border-t border-white/20 text-white">
            <div className="bg-black/15 backdrop-blur-xs px-3 py-2 rounded-xl border border-white/10">
              <span className="text-[10px] text-white/80 flex items-center gap-1 font-medium">
                <DollarSign className="w-3 h-3" /> Học phí trọn gói
              </span>
              <span className="text-sm sm:text-base font-black block mt-0.5">
                {course.basePrice.toLocaleString('vi-VN')} ₫
              </span>
              <span className="text-[10px] text-white/70 block">
                (~{sessionFee.toLocaleString('vi-VN')} ₫ / buổi)
              </span>
            </div>

            <div className="bg-black/15 backdrop-blur-xs px-3 py-2 rounded-xl border border-white/10">
              <span className="text-[10px] text-white/80 flex items-center gap-1 font-medium">
                <Calendar className="w-3 h-3" /> Tổng số buổi
              </span>
              <span className="text-sm sm:text-base font-black block mt-0.5">
                {course.totalSessions} buổi tập
              </span>
              <span className="text-[10px] text-white/70 block">
                Kèm 1-1 trực tiếp
              </span>
            </div>

            <div className="bg-black/15 backdrop-blur-xs px-3 py-2 rounded-xl border border-white/10">
              <span className="text-[10px] text-white/80 flex items-center gap-1 font-medium">
                <Clock className="w-3 h-3" /> Thời hạn hợp đồng
              </span>
              <span className="text-sm sm:text-base font-black block mt-0.5">
                {course.validityDays} ngày
              </span>
              <span className="text-[10px] text-white/70 block">
                Linh hoạt sắp xếp lịch
              </span>
            </div>

            <div className="bg-black/15 backdrop-blur-xs px-3 py-2 rounded-xl border border-white/10">
              <span className="text-[10px] text-white/80 flex items-center gap-1 font-medium">
                <ShieldCheck className="w-3 h-3" /> Cam kết hợp đồng
              </span>
              <span className="text-sm sm:text-base font-black block mt-0.5">
                Hợp đồng điện tử
              </span>
              <span className="text-[10px] text-white/70 block">
                Xuất file PDF chuẩn
              </span>
            </div>
          </div>
        </div>

        {/* Thanh thông báo trạng thái chỉnh sửa của HLV */}
        {isPtView && isEditing && (
          <div className="px-6 py-2.5 bg-amber-50 dark:bg-amber-950/40 border-b border-amber-200 dark:border-amber-900/60 flex flex-wrap items-center justify-between gap-3 text-xs text-amber-900 dark:text-amber-200 shrink-0">
            <div className="flex items-center gap-2">
              <Edit3 className="w-4 h-4 text-amber-600" />
              <span>
                <b>Chế độ biên soạn của HLV:</b> Bạn có thể chỉnh sửa từng giai đoạn, đổi bài tập và cam kết đầu ra cho khóa học này. Học viên sẽ xem đúng nội dung bạn đã lưu!
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] text-slate-500">Mẫu nạp nhanh:</span>
              <button
                type="button"
                onClick={() => handleApplyTemplate('GLUTES')}
                className="px-2 py-1 rounded bg-white dark:bg-slate-800 border text-[11px] font-bold text-rose-600 hover:bg-rose-50"
              >
                🍑 Cơ mông đùi
              </button>
              <button
                type="button"
                onClick={() => handleApplyTemplate('PILATES')}
                className="px-2 py-1 rounded bg-white dark:bg-slate-800 border text-[11px] font-bold text-teal-600 hover:bg-teal-50"
              >
                🧘 Pilates
              </button>
              <button
                type="button"
                onClick={() => handleApplyTemplate('FAT_LOSS')}
                className="px-2 py-1 rounded bg-white dark:bg-slate-800 border text-[11px] font-bold text-orange-600 hover:bg-orange-50"
              >
                🔥 Giảm mỡ
              </button>
            </div>
          </div>
        )}

        {saveSuccessMsg && (
          <div className="px-6 py-2 bg-emerald-100 text-emerald-800 dark:bg-emerald-950/50 dark:text-emerald-300 text-xs font-bold flex items-center gap-2 border-b border-emerald-200">
            <CheckCircle2 className="w-4 h-4" />
            <span>{saveSuccessMsg}</span>
          </div>
        )}

        {/* Tab Switcher */}
        <div className="px-6 py-2.5 bg-slate-50 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between gap-2 overflow-x-auto shrink-0">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab('ROADMAP')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap cursor-pointer ${
                activeTab === 'ROADMAP'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/70 dark:hover:bg-slate-800'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>1. Lộ Trình {course.totalSessions} Buổi</span>
            </button>

            <button
              onClick={() => setActiveTab('EXERCISES')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap cursor-pointer ${
                activeTab === 'EXERCISES'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/70 dark:hover:bg-slate-800'
              }`}
            >
              <Dumbbell className="w-3.5 h-3.5" />
              <span>2. Bài Tập Tiêu Biểu</span>
            </button>

            <button
              onClick={() => setActiveTab('OUTCOMES')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap cursor-pointer ${
                activeTab === 'OUTCOMES'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/70 dark:hover:bg-slate-800'
              }`}
            >
              <Award className="w-3.5 h-3.5" />
              <span>3. Cam Kết Đầu Ra</span>
            </button>

            <button
              onClick={() => setActiveTab('PREP')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 transition whitespace-nowrap cursor-pointer ${
                activeTab === 'PREP'
                  ? 'bg-rose-600 text-white shadow-xs'
                  : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/70 dark:hover:bg-slate-800'
              }`}
            >
              <Apple className="w-3.5 h-3.5" />
              <span>4. Dinh Dưỡng &amp; Chuẩn Bị</span>
            </button>
          </div>

          {/* Nút lưu nhanh cho HLV khi đang sửa */}
          {isPtView && isEditing && (
            <button
              type="button"
              onClick={handleSaveCustomSyllabus}
              className="px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded-xl shadow flex items-center gap-1.5 cursor-pointer shrink-0"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Lưu Giáo Trình Này</span>
            </button>
          )}
        </div>

        {/* Scrollable Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm flex-1">
          {/* TAB 1: ROADMAP */}
          {activeTab === 'ROADMAP' && (
            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/50 flex items-start gap-2.5 text-xs text-blue-900 dark:text-blue-200">
                <Sparkles className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                <p>
                  {isPtView ? (
                    <span>
                      <b>Dành cho Huấn luyện viên:</b> Đây là bản lộ trình học viên sẽ xem trước khi quyết định mua khóa học của bạn. Bấm nút <b>"Biên Soạn Lộ Trình Demo"</b> ở góc trên bên phải nếu bạn muốn chỉnh sửa nội dung bài dạy theo phong cách riêng của mình.
                    </span>
                  ) : (
                    <span>
                      <b>Lộ trình huấn luyện chuẩn từ Huấn luyện viên:</b> Bạn sẽ được HLV trực tiếp hướng dẫn theo từng giai đoạn dưới đây. Khi bắt đầu khóa học, HLV sẽ căn cứ thêm vào chỉ số InBody thực tế của bạn để tối ưu bài tập.
                    </span>
                  )}
                </p>
              </div>

              {/* Chế độ Sửa của HLV */}
              {isPtView && isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                      Tên chuyên môn / Nhãn khóa học:
                    </label>
                    <input
                      type="text"
                      value={syllabusData.categoryLabel}
                      onChange={(e) => setSyllabusData({ ...syllabusData, categoryLabel: e.target.value })}
                      className="w-full px-3 py-2 text-xs border border-slate-300 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-900 font-bold"
                    />
                  </div>

                  {syllabusData.stages.map((stg, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl border-2 border-rose-200 dark:border-rose-900/60 bg-rose-50/20 dark:bg-rose-950/10 space-y-3"
                    >
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div className="sm:col-span-2">
                          <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-0.5">
                            Tiêu đề giai đoạn {idx + 1}
                          </label>
                          <input
                            type="text"
                            value={stg.title}
                            onChange={(e) => {
                              const updated = [...syllabusData.stages];
                              updated[idx].title = e.target.value;
                              setSyllabusData({ ...syllabusData, stages: updated });
                            }}
                            className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg bg-white dark:bg-slate-900 font-bold"
                          />
                        </div>
                        <div>
                          <label className="block text-[11px] font-bold text-slate-700 dark:text-slate-300 mb-0.5">
                            Số buổi phân bổ
                          </label>
                          <input
                            type="text"
                            value={stg.sessions}
                            onChange={(e) => {
                              const updated = [...syllabusData.stages];
                              updated[idx].sessions = e.target.value;
                              setSyllabusData({ ...syllabusData, stages: updated });
                            }}
                            className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg bg-white dark:bg-slate-900 font-bold text-rose-600"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-0.5">
                          Mô tả mục tiêu giai đoạn:
                        </label>
                        <textarea
                          rows={2}
                          value={stg.description}
                          onChange={(e) => {
                            const updated = [...syllabusData.stages];
                            updated[idx].description = e.target.value;
                            setSyllabusData({ ...syllabusData, stages: updated });
                          }}
                          className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg bg-white dark:bg-slate-900"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 dark:text-slate-400 mb-1">
                          Các bài tập / Trọng tâm luyện tập (mỗi dòng một ý):
                        </label>
                        <textarea
                          rows={3}
                          value={stg.keyTopics.join('\n')}
                          onChange={(e) => {
                            const updated = [...syllabusData.stages];
                            updated[idx].keyTopics = e.target.value.split('\n').filter((s) => s.trim().length > 0);
                            setSyllabusData({ ...syllabusData, stages: updated });
                          }}
                          className="w-full px-3 py-1.5 text-xs border border-slate-300 rounded-lg bg-white dark:bg-slate-900"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                /* Chế độ Xem của Học viên (và PT khi không edit) */
                <div className="space-y-3.5">
                  {syllabusData.stages.map((stg, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-800/40 hover:border-slate-300 transition-all space-y-2.5"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 rounded-lg bg-rose-600 text-white text-xs font-black flex items-center justify-center shrink-0">
                            {idx + 1}
                          </span>
                          <h4 className="font-bold text-slate-900 dark:text-white text-sm">
                            {stg.title}
                          </h4>
                        </div>
                        <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-100 dark:bg-rose-900/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 w-fit">
                          {stg.sessions}
                        </span>
                      </div>

                      <p className="text-xs text-slate-600 dark:text-slate-400 pl-8 leading-relaxed">
                        {stg.description}
                      </p>

                      <div className="pl-8 space-y-1.5 pt-1">
                        <span className="text-[11px] font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">
                          Trọng tâm luyện tập:
                        </span>
                        <ul className="space-y-1">
                          {stg.keyTopics.map((topic, tIdx) => (
                            <li
                              key={tIdx}
                              className="text-xs text-slate-600 dark:text-slate-400 flex items-start gap-2"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0 mt-0.5" />
                              <span>{topic}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 2: EXERCISES */}
          {activeTab === 'EXERCISES' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center justify-between">
                <span>
                  {isPtView && isEditing
                    ? 'Bạn có thể chỉnh sửa các bài tập mẫu mà học viên sẽ được tập luyện trong khóa:'
                    : 'Các bài tập demo tiêu biểu bạn sẽ được Huấn luyện viên trực tiếp hướng dẫn và chỉnh form trong khóa học:'}
                </span>
                {isPtView && isEditing && (
                  <button
                    type="button"
                    onClick={() => {
                      const newEx: DemoExercise = {
                        name: 'Bài tập mới',
                        targetMuscle: 'Cơ mục tiêu',
                        equipment: 'Dụng cụ tập',
                        benefit: 'Lợi ích bài tập',
                      };
                      setSyllabusData({
                        ...syllabusData,
                        demoExercises: [...syllabusData.demoExercises, newEx],
                      });
                    }}
                    className="px-2.5 py-1 bg-rose-600 text-white rounded-lg text-xs font-bold flex items-center gap-1 cursor-pointer"
                  >
                    <Plus className="w-3 h-3" /> Thêm bài tập
                  </button>
                )}
              </div>

              {isPtView && isEditing ? (
                <div className="space-y-3">
                  {syllabusData.demoExercises.map((ex, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 space-y-2.5"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-bold text-xs text-rose-600">Bài tập #{idx + 1}</span>
                        <button
                          type="button"
                          onClick={() => {
                            const updated = syllabusData.demoExercises.filter((_, i) => i !== idx);
                            setSyllabusData({ ...syllabusData, demoExercises: updated });
                          }}
                          className="text-red-500 hover:text-red-700 text-xs p-1"
                          title="Xóa bài tập này"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                        <div>
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Tên bài tập:</label>
                          <input
                            type="text"
                            value={ex.name}
                            onChange={(e) => {
                              const updated = [...syllabusData.demoExercises];
                              updated[idx].name = e.target.value;
                              setSyllabusData({ ...syllabusData, demoExercises: updated });
                            }}
                            className="w-full px-2.5 py-1 text-xs border rounded bg-slate-50 dark:bg-slate-850 font-bold"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Nhóm cơ tác động:</label>
                          <input
                            type="text"
                            value={ex.targetMuscle}
                            onChange={(e) => {
                              const updated = [...syllabusData.demoExercises];
                              updated[idx].targetMuscle = e.target.value;
                              setSyllabusData({ ...syllabusData, demoExercises: updated });
                            }}
                            className="w-full px-2.5 py-1 text-xs border rounded bg-slate-50 dark:bg-slate-850"
                          />
                        </div>
                        <div>
                          <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Dụng cụ tập:</label>
                          <input
                            type="text"
                            value={ex.equipment}
                            onChange={(e) => {
                              const updated = [...syllabusData.demoExercises];
                              updated[idx].equipment = e.target.value;
                              setSyllabusData({ ...syllabusData, demoExercises: updated });
                            }}
                            className="w-full px-2.5 py-1 text-xs border rounded bg-slate-50 dark:bg-slate-850"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-[10px] font-bold text-slate-600 mb-0.5">Lợi ích thực tế:</label>
                        <input
                          type="text"
                          value={ex.benefit}
                          onChange={(e) => {
                            const updated = [...syllabusData.demoExercises];
                            updated[idx].benefit = e.target.value;
                            setSyllabusData({ ...syllabusData, demoExercises: updated });
                          }}
                          className="w-full px-2.5 py-1 text-xs border rounded bg-slate-50 dark:bg-slate-850"
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {syllabusData.demoExercises.map((ex, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 shadow-2xs hover:shadow-sm transition-all space-y-2.5"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-bold text-slate-900 dark:text-white text-sm flex items-center gap-1.5">
                          <Dumbbell className="w-4 h-4 text-rose-500 shrink-0" />
                          <span>{ex.name}</span>
                        </h4>
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                          Bài #{idx + 1}
                        </span>
                      </div>

                      <div className="space-y-1 text-xs">
                        <div className="flex items-center gap-1 text-slate-500">
                          <span className="font-semibold text-slate-700 dark:text-slate-300">Nhóm cơ:</span>
                          <span>{ex.targetMuscle}</span>
                        </div>
                        <div className="flex items-center gap-1 text-slate-500">
                          <span className="font-semibold text-slate-700 dark:text-slate-300">Dụng cụ:</span>
                          <span>{ex.equipment}</span>
                        </div>
                      </div>

                      <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200/80 dark:border-emerald-900/40 text-xs text-emerald-800 dark:text-emerald-300 leading-relaxed font-medium">
                        💡 <b>Lợi ích:</b> {ex.benefit}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: OUTCOMES */}
          {activeTab === 'OUTCOMES' && (
            <div className="space-y-4">
              <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 to-rose-500/10 border border-amber-300/40 dark:border-amber-800/40 space-y-2">
                <div className="flex items-center gap-2 font-bold text-amber-900 dark:text-amber-300 text-sm">
                  <Award className="w-5 h-5 text-amber-500" />
                  <span>Cam Kết Chất Lượng Đào Tạo 1-Kèm-1</span>
                </div>
                <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                  Tại PTConnect, mỗi khóa học đều có cam kết kết quả rõ ràng. Khi học viên tuân thủ đầy đủ lịch tập và giáo án dinh dưỡng:
                </p>
              </div>

              {isPtView && isEditing ? (
                <div className="space-y-2">
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Chỉnh sửa các cam kết đầu ra (mỗi dòng một cam kết):
                  </label>
                  <textarea
                    rows={5}
                    value={syllabusData.outcomes.join('\n')}
                    onChange={(e) => {
                      setSyllabusData({
                        ...syllabusData,
                        outcomes: e.target.value.split('\n').filter((s) => s.trim().length > 0),
                      });
                    }}
                    className="w-full p-3 text-xs border border-slate-300 rounded-xl bg-slate-50 dark:bg-slate-900 font-medium"
                  />
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                  {syllabusData.outcomes.map((out, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-start gap-3"
                    >
                      <div className="w-7 h-7 rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-900/40 dark:text-emerald-400 font-bold flex items-center justify-center shrink-0 text-xs">
                        ✓
                      </div>
                      <span className="text-xs text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                        {out}
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 text-xs">
                <h5 className="font-bold text-slate-900 dark:text-white flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-blue-500" />
                  <span>Quyền lợi bảo vệ học viên trong suốt khóa học:</span>
                </h5>
                <ul className="list-disc pl-5 space-y-1 text-slate-600 dark:text-slate-400">
                  <li>Tiền học phí được lưu trữ an toàn trong ví ký quỹ, chỉ giải ngân từng buổi sau khi bạn xác nhận mã OTP.</li>
                  <li>Được ký Hợp đồng điện tử có giá trị cam kết địa điểm tập cố định, xuất file PDF minh bạch.</li>
                  <li>Nếu HLV vi phạm đạo đức hoặc không đáp ứng cam kết, bạn có quyền gửi khiếu nại lên Ban Quản Trị để hoàn tiền.</li>
                </ul>
              </div>
            </div>
          )}

          {/* TAB 4: PREP & NUTRITION */}
          {activeTab === 'PREP' && (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 space-y-2.5">
                  <h4 className="font-bold text-xs uppercase text-slate-900 dark:text-white flex items-center gap-2">
                    <Apple className="w-4 h-4 text-emerald-500" />
                    <span>Hỗ Trợ Tư Vấn Dinh Dưỡng Đi Kèm</span>
                  </h4>
                  <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2 list-disc pl-4">
                    <li>Huấn luyện viên sẽ tính toán chỉ số TDEE (tổng năng lượng tiêu hao hàng ngày) dành riêng cho bạn.</li>
                    <li>Hướng dẫn cách chọn thực phẩm giàu Protein, Carbohydrate hấp thu chậm và chất béo tốt trong bữa ăn hàng ngày.</li>
                    <li>Không áp dụng các chế độ ăn kiêng hà khắc, nhịn ăn gây suy nhược cơ thể.</li>
                    <li>Tư vấn cách uống nước và bổ sung khoáng chất khoa học trước, trong và sau buổi tập.</li>
                  </ul>
                </div>

                <div className="p-4 rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 space-y-2.5">
                  <h4 className="font-bold text-xs uppercase text-slate-900 dark:text-white flex items-center gap-2">
                    <Dumbbell className="w-4 h-4 text-rose-500" />
                    <span>Những Thứ Cần Chuẩn Bị Trước Buổi Đầu</span>
                  </h4>
                  {isPtView && isEditing ? (
                    <textarea
                      rows={4}
                      value={syllabusData.prepNotes.join('\n')}
                      onChange={(e) => {
                        setSyllabusData({
                          ...syllabusData,
                          prepNotes: e.target.value.split('\n').filter((s) => s.trim().length > 0),
                        });
                      }}
                      className="w-full p-2.5 text-xs border border-slate-300 rounded-lg bg-white"
                    />
                  ) : (
                    <ul className="text-xs text-slate-600 dark:text-slate-400 space-y-2 list-disc pl-4">
                      {syllabusData.prepNotes.map((note, idx) => (
                        <li key={idx}>{note}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>

              <div className="p-3.5 rounded-xl border border-amber-200 dark:border-amber-900/50 bg-amber-50/50 dark:bg-amber-950/20 text-xs text-amber-800 dark:text-amber-300">
                💡 <b>Mẹo nhỏ cho học viên:</b> Sau khi đăng ký khóa học thành công, bạn có thể nhắn tin trao đổi trực tiếp 1-1 với Huấn luyện viên thông qua widget <b>"Chat Trực Tiếp"</b> ở góc dưới màn hình để chia sẻ mong muốn cá nhân trước buổi tập đầu tiên!
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3.5 bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0">
          <div className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <span className="font-semibold text-slate-700 dark:text-slate-300">Học phí:</span>
            <span className="text-base font-black text-rose-600 dark:text-rose-400">
              {course.basePrice.toLocaleString('vi-VN')} ₫
            </span>
            <span className="text-slate-400">({course.totalSessions} buổi)</span>
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto">
            {isPtView && isEditing ? (
              <button
                type="button"
                onClick={handleSaveCustomSyllabus}
                className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-md transition flex items-center justify-center gap-1.5 cursor-pointer"
              >
                <Save className="w-3.5 h-3.5" />
                <span>Lưu &amp; Cập Nhật Giáo Trình</span>
              </button>
            ) : (
              <>
                <button
                  onClick={onClose}
                  className="flex-1 sm:flex-none px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold transition cursor-pointer"
                >
                  Đóng xem trước
                </button>
                {!isPtView && onEnroll && (
                  <button
                    onClick={() => {
                      onClose();
                      onEnroll(course);
                    }}
                    className="flex-1 sm:flex-none px-5 py-2.5 rounded-xl bg-[#FF4B4B] hover:bg-[#E03E3E] text-white text-xs font-bold shadow-md shadow-rose-500/20 transition flex items-center justify-center gap-1.5 cursor-pointer active:scale-[0.98]"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-amber-200" />
                    <span>Đăng ký khóa học này ngay</span>
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoursePreviewModal;
