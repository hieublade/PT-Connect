package view.user;

import model.User;
import view.wallet.WalletFrm;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class StudentHomeFrm extends JFrame implements ActionListener {
    private static final long serialVersionUID = 1L;

    // Attributes theo đúng Class Diagram
    private JButton btnDiscoveryPt;
    private JButton btnBookSchedule;
    private JButton btnPTDetail;
    private JButton btnMySchedule;
    private JButton btnMyCourse;
    private JButton btnWallet;
    private JButton btnProfile;
    private User u;

    public StudentHomeFrm(User u) {
        this.u = u;
        initComponents();
        setLocationRelativeTo(null);
    }

    private void initComponents() {
        setTitle("Trang Chủ Học Viên - PT-Connect");
        setSize(700, 480);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(15, 15));

        // Header
        JPanel pnlHeader = new JPanel(new BorderLayout());
        pnlHeader.setBackground(new Color(30, 41, 59));
        pnlHeader.setBorder(new EmptyBorder(15, 20, 15, 20));

        JLabel lblGreeting = new JLabel("Chào mừng, " + (u != null ? u.getFullName() : "Học viên") + "!");
        lblGreeting.setFont(new Font("Segoe UI", Font.BOLD, 18));
        lblGreeting.setForeground(Color.WHITE);

        JLabel lblRole = new JLabel("Vai trò: " + (u != null ? u.getRole() : "STUDENT"));
        lblRole.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        lblRole.setForeground(new Color(203, 213, 225));

        pnlHeader.add(lblGreeting, BorderLayout.WEST);
        pnlHeader.add(lblRole, BorderLayout.EAST);
        add(pnlHeader, BorderLayout.NORTH);

        // Grid Menu Buttons
        JPanel pnlCenter = new JPanel(new GridLayout(3, 3, 15, 15));
        pnlCenter.setBorder(new EmptyBorder(20, 30, 20, 30));
        pnlCenter.setBackground(new Color(248, 250, 252));

        btnDiscoveryPt = createMenuButton("Khám phá HLV");
        btnBookSchedule = createMenuButton("Đặt lịch tập");
        btnPTDetail = createMenuButton("Chi tiết HLV");
        btnMySchedule = createMenuButton("Lịch tập của tôi");
        btnMyCourse = createMenuButton("Khóa học đã mua");
        btnWallet = createMenuButton("Ví tiền của tôi");
        btnProfile = createMenuButton("Hồ sơ cá nhân");

        // Nhấn mạnh nút Ví tiền
        btnWallet.setBackground(new Color(37, 99, 235));
        btnWallet.setForeground(Color.WHITE);

        pnlCenter.add(btnDiscoveryPt);
        pnlCenter.add(btnBookSchedule);
        pnlCenter.add(btnPTDetail);
        pnlCenter.add(btnMySchedule);
        pnlCenter.add(btnMyCourse);
        pnlCenter.add(btnWallet);
        pnlCenter.add(btnProfile);

        add(pnlCenter, BorderLayout.CENTER);

        // Footer
        JPanel pnlFooter = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        pnlFooter.setBorder(new EmptyBorder(5, 20, 10, 20));
        JLabel lblStatus = new JLabel("Hệ thống PT-Connect • Sẵn sàng");
        lblStatus.setForeground(Color.GRAY);
        lblStatus.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        pnlFooter.add(lblStatus);
        add(pnlFooter, BorderLayout.SOUTH);
    }

    private JButton createMenuButton(String text) {
        JButton btn = new JButton(text);
        btn.setFont(new Font("Segoe UI", Font.BOLD, 14));
        btn.setBackground(Color.WHITE);
        btn.setForeground(new Color(30, 41, 59));
        btn.setFocusPainted(false);
        btn.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(203, 213, 225), 1),
                new EmptyBorder(10, 10, 10, 10)
        ));
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btn.addActionListener(this);
        return btn;
    }

    // Bước 2: actionPerformed(e)
    @Override
    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == btnWallet) {
            btnWalletClick();
        } else {
            JButton source = (JButton) e.getSource();
            JOptionPane.showMessageDialog(this, "Chức năng '" + source.getText() + "' đang được hoàn thiện.");
        }
    }

    // Bước 3: btnWalletClick()
    public void btnWalletClick() {
        // Bước 4, 5: Gọi lớp WalletFrm(u : User)
        WalletFrm walletFrm = new WalletFrm(this.u);
        walletFrm.setVisible(true);
    }

    public static void main(String[] args) {
        // Test nhanh giao diện
        User testUser = new User();
        testUser.setId(1);
        testUser.setFullName("Nguyen Van Hoc Vien");
        testUser.setEmail("hocvien@ptconnect.com");
        testUser.setRole("STUDENT");

        SwingUtilities.invokeLater(() -> {
            new StudentHomeFrm(testUser).setVisible(true);
        });
    }
}
