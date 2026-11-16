package view.wallet;

import dao.PaymentDAO;
import dao.WalletDAO;
import model.Payment;
import model.User;
import model.Wallet;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.UUID;

public class WalletFrm extends JFrame implements ActionListener {
    private static final long serialVersionUID = 1L;

    // Attributes theo đúng Class Diagram
    private JLabel lblWalletInfo;
    private JTable tblListTransaction;
    private JComboBox<String> cmbQuickAmount;
    private JTextField txtCustomAmount;
    private JButton btnTopUp;
    private JComboBox<String> cmbPaymentMethod;
    private User u;
    private Wallet w;

    // Các thành phần hỗ trợ UI
    private DefaultTableModel tableModel;
    private WalletDAO walletDAO;
    private PaymentDAO paymentDAO;
    private DecimalFormat currencyFormatter = new DecimalFormat("#,##0.00");
    private SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

    public WalletFrm(User u) {
        this.u = u;
        this.walletDAO = new WalletDAO();
        this.paymentDAO = new PaymentDAO();

        initComponents();

        // Bước 6, 7: Gọi getWallet(userId)
        this.w = walletDAO.getWallet(u.getId());

        // Bước 12, 13: Gọi getPayments(walletId)
        if (this.w != null) {
            ArrayList<Payment> payments = paymentDAO.getPayments(this.w.getId());
            this.w.setPayments(payments);
        }

        // Bước 18: Hiển thị thông tin số dư ví và danh sách giao dịch
        renderWalletData();

        setLocationRelativeTo(null);
    }

    private void initComponents() {
        setTitle("Quản Lý Ví Tiền - PT-Connect");
        setSize(850, 600);
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        // Header Panel: Logo/Title & Card số dư (lblWalletInfo)
        JPanel topPanel = new JPanel(new BorderLayout(10, 10));
        topPanel.setBorder(new EmptyBorder(15, 20, 10, 20));
        topPanel.setBackground(new Color(245, 247, 250));

        JLabel lblTitle = new JLabel("VÍ ĐIỆN TỬ HỌC VIÊN", JLabel.LEFT);
        lblTitle.setFont(new Font("Segoe UI", Font.BOLD, 18));
        lblTitle.setForeground(new Color(30, 41, 59));
        topPanel.add(lblTitle, BorderLayout.NORTH);

        JPanel balanceCard = new JPanel(new GridLayout(2, 1, 5, 5));
        balanceCard.setBackground(new Color(37, 99, 235));
        balanceCard.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(29, 78, 216), 1),
                new EmptyBorder(12, 20, 12, 20)
        ));

        JLabel lblOwner = new JLabel("Chủ tài khoản: " + (u != null ? u.getFullName() : "Học viên"), JLabel.LEFT);
        lblOwner.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        lblOwner.setForeground(Color.WHITE);

        lblWalletInfo = new JLabel("Số dư khả dụng: 0.00 VND", JLabel.LEFT);
        lblWalletInfo.setFont(new Font("Segoe UI", Font.BOLD, 22));
        lblWalletInfo.setForeground(Color.WHITE);

        balanceCard.add(lblOwner);
        balanceCard.add(lblWalletInfo);
        topPanel.add(balanceCard, BorderLayout.CENTER);

        add(topPanel, BorderLayout.NORTH);

        // Center Panel: Bảng lịch sử giao dịch (tblListTransaction)
        JPanel centerPanel = new JPanel(new BorderLayout(5, 5));
        centerPanel.setBorder(new EmptyBorder(0, 20, 10, 20));

        JLabel lblHistoryTitle = new JLabel("Lịch sử giao dịch", JLabel.LEFT);
        lblHistoryTitle.setFont(new Font("Segoe UI", Font.BOLD, 15));
        lblHistoryTitle.setForeground(new Color(51, 65, 85));
        centerPanel.add(lblHistoryTitle, BorderLayout.NORTH);

        String[] columnNames = {"Mã GD", "Mã tham chiếu", "Số tiền (VND)", "Loại GD", "Phương thức", "Trạng thái", "Thời gian"};
        tableModel = new DefaultTableModel(columnNames, 0) {
            private static final long serialVersionUID = 1L;
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };

        tblListTransaction = new JTable(tableModel);
        tblListTransaction.setRowHeight(26);
        tblListTransaction.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        JTableHeader header = tblListTransaction.getTableHeader();
        header.setFont(new Font("Segoe UI", Font.BOLD, 13));
        header.setBackground(new Color(226, 232, 240));

        DefaultTableCellRenderer centerRenderer = new DefaultTableCellRenderer();
        centerRenderer.setHorizontalAlignment(JLabel.CENTER);
        tblListTransaction.getColumnModel().getColumn(0).setCellRenderer(centerRenderer);
        tblListTransaction.getColumnModel().getColumn(3).setCellRenderer(centerRenderer);
        tblListTransaction.getColumnModel().getColumn(4).setCellRenderer(centerRenderer);
        tblListTransaction.getColumnModel().getColumn(5).setCellRenderer(centerRenderer);

        JScrollPane scrollPane = new JScrollPane(tblListTransaction);
        centerPanel.add(scrollPane, BorderLayout.CENTER);

        add(centerPanel, BorderLayout.CENTER);

        // Bottom Panel: Form nạp tiền (TopUp Form)
        JPanel bottomPanel = new JPanel(new BorderLayout(10, 10));
        bottomPanel.setBorder(new EmptyBorder(10, 20, 20, 20));

        JPanel topUpPanel = new JPanel(new GridLayout(2, 4, 12, 10));
        topUpPanel.setBorder(BorderFactory.createTitledBorder(
                BorderFactory.createLineBorder(new Color(203, 213, 225)),
                "Nạp tiền vào ví",
                0,
                0,
                new Font("Segoe UI", Font.BOLD, 14),
                new Color(30, 41, 59)
        ));

        // Row 1: Labels
        JLabel lblQuick = new JLabel("Chọn nhanh mức nạp:");
        lblQuick.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        JLabel lblCustom = new JLabel("Hoặc nhập số tiền tùy chọn:");
        lblCustom.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        JLabel lblMethod = new JLabel("Phương thức nạp:");
        lblMethod.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        JLabel lblAction = new JLabel("");

        // Row 2: Inputs
        String[] quickAmounts = {"-- Tùy chọn nhanh --", "100,000", "200,000", "500,000", "1,000,000", "2,000,000", "5,000,000"};
        cmbQuickAmount = new JComboBox<>(quickAmounts);
        cmbQuickAmount.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        cmbQuickAmount.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                int selectedIndex = cmbQuickAmount.getSelectedIndex();
                if (selectedIndex > 0) {
                    String selected = (String) cmbQuickAmount.getSelectedItem();
                    txtCustomAmount.setText(selected.replace(",", ""));
                }
            }
        });

        txtCustomAmount = new JTextField();
        txtCustomAmount.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        String[] methods = {"BANK_TRANSFER", "WALLET", "CREDIT_CARD", "CASH"};
        cmbPaymentMethod = new JComboBox<>(methods);
        cmbPaymentMethod.setFont(new Font("Segoe UI", Font.PLAIN, 13));

        btnTopUp = new JButton("Nạp tiền");
        btnTopUp.setFont(new Font("Segoe UI", Font.BOLD, 13));
        btnTopUp.setBackground(new Color(16, 185, 129));
        btnTopUp.setForeground(Color.WHITE);
        btnTopUp.setFocusPainted(false);
        btnTopUp.setCursor(new Cursor(Cursor.HAND_CURSOR));
        btnTopUp.addActionListener(this);

        topUpPanel.add(lblQuick);
        topUpPanel.add(lblCustom);
        topUpPanel.add(lblMethod);
        topUpPanel.add(lblAction);

        topUpPanel.add(cmbQuickAmount);
        topUpPanel.add(txtCustomAmount);
        topUpPanel.add(cmbPaymentMethod);
        topUpPanel.add(btnTopUp);

        bottomPanel.add(topUpPanel, BorderLayout.CENTER);
        add(bottomPanel, BorderLayout.SOUTH);
    }

    private void renderWalletData() {
        if (this.w != null) {
            lblWalletInfo.setText("Số dư khả dụng: " + currencyFormatter.format(this.w.getBalance()) + " " + this.w.getCurrency());

            tableModel.setRowCount(0);
            ArrayList<Payment> payments = this.w.getPayments();
            if (payments != null) {
                for (Payment p : payments) {
                    tableModel.addRow(new Object[]{
                            p.getId(),
                            p.getTransactionRef(),
                            currencyFormatter.format(p.getAmount()),
                            p.getPaymentType(),
                            p.getPaymentMethod(),
                            p.getStatus(),
                            p.getCreatedAt() != null ? dateFormat.format(p.getCreatedAt()) : ""
                    });
                }
            }
        } else {
            lblWalletInfo.setText("Chưa tìm thấy ví của tài khoản!");
        }
    }

    // Bước 20: actionPerformed(e)
    @Override
    public void actionPerformed(ActionEvent e) {
        if (e.getSource() == btnTopUp) {
            btnTopUpClick();
        }
    }

    // Bước 21: btnTopUpClick()
    public void btnTopUpClick() {
        if (this.w == null) {
            JOptionPane.showMessageDialog(this, "Không tìm thấy thông tin ví của người dùng!", "Lỗi", JOptionPane.ERROR_MESSAGE);
            return;
        }

        String amountText = txtCustomAmount.getText().trim();
        if (amountText.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Vui lòng nhập số tiền hoặc chọn mức nạp nhanh!", "Cảnh báo", JOptionPane.WARNING_MESSAGE);
            return;
        }

        float amount;
        try {
            amount = Float.parseFloat(amountText);
            if (amount <= 0) {
                JOptionPane.showMessageDialog(this, "Số tiền nạp phải lớn hơn 0!", "Cảnh báo", JOptionPane.WARNING_MESSAGE);
                return;
            }
        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Số tiền không hợp lệ! Vui lòng chỉ nhập số.", "Lỗi", JOptionPane.ERROR_MESSAGE);
            return;
        }

        String paymentMethod = (String) cmbPaymentMethod.getSelectedItem();
        String paymentType = "TOPUP";
        String status = "SUCCESS";
        String transactionRef = "TOPUP-" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 6).toUpperCase();

        // Bước 22, 23: Gọi lớp Payment để đóng gói
        Payment p = new Payment(amount, paymentType, paymentMethod, status, transactionRef);
        p.setWalletId(this.w.getId());

        // Bước 25, 26: Gọi PaymentDAO.createPayment(p)
        boolean isSuccess = paymentDAO.createPayment(p);

        // Bước 27: Trả về kết quả thực thi
        if (isSuccess) {
            // Bước 28, 29: Gọi WalletDAO.getCredit(walletId) để lấy số dư mới
            float newBalance = walletDAO.getCredit(this.w.getId());
            this.w.setBalance(newBalance);

            // Bước 31, 32: Gọi PaymentDAO.getPayments(walletId) để cập nhật lại danh sách GD
            ArrayList<Payment> updatedPayments = paymentDAO.getPayments(this.w.getId());
            this.w.setPayments(updatedPayments);

            // Bước 37: Hiển thị thông báo và cập nhật số dư + bảng giao dịch
            renderWalletData();
            txtCustomAmount.setText("");
            cmbQuickAmount.setSelectedIndex(0);

            JOptionPane.showMessageDialog(this,
                    "Nạp tiền thành công: " + currencyFormatter.format(amount) + " " + this.w.getCurrency() +
                            "\nSố dư mới: " + currencyFormatter.format(newBalance) + " " + this.w.getCurrency(),
                    "Thành công",
                    JOptionPane.INFORMATION_MESSAGE);
        } else {
            JOptionPane.showMessageDialog(this, "Giao dịch nạp tiền thất bại, vui lòng thử lại!", "Lỗi", JOptionPane.ERROR_MESSAGE);
        }
    }
}
