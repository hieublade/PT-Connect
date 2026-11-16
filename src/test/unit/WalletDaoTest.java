package test.unit;

import dao.DAO;
import dao.PaymentDAO;
import dao.WalletDAO;
import model.Payment;
import model.Wallet;
import org.junit.jupiter.api.*;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class WalletDaoTest {

    private static Connection inMemoryConnection;
    private static WalletDAO walletDAO;
    private static PaymentDAO paymentDAO;
    private static int testUserId = 1;
    private static Wallet testWallet;

    @BeforeAll
    public static void setUp() throws Exception {
        // Sử dụng MySQL nếu có kết nối, hoặc fallback sang H2 in-memory MySQL Mode để test độc lập
        String dbUrl = System.getenv("DB_URL");
        if (dbUrl != null && !dbUrl.isEmpty()) {
            new DAO();
            if (DAO.getConnection() != null) {
                walletDAO = new WalletDAO();
                paymentDAO = new PaymentDAO();
                return;
            }
        }

        // Tạo H2 In-Memory Database tương thích MySQL
        Class.forName("org.h2.Driver");
        inMemoryConnection = DriverManager.getConnection("jdbc:h2:mem:ptconnect;MODE=MySQL;DB_CLOSE_DELAY=-1", "sa", "");
        DAO.setConnection(inMemoryConnection);

        try (Statement st = inMemoryConnection.createStatement()) {
            st.execute("CREATE TABLE users (" +
                    "id BIGINT PRIMARY KEY AUTO_INCREMENT, " +
                    "full_name VARCHAR(100), " +
                    "email VARCHAR(150), " +
                    "password_hash VARCHAR(255), " +
                    "phone VARCHAR(20), " +
                    "role VARCHAR(20), " +
                    "status VARCHAR(20), " +
                    "avatar_url VARCHAR(500), " +
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
                    "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
                    ")");

            st.execute("CREATE TABLE wallets (" +
                    "id BIGINT PRIMARY KEY AUTO_INCREMENT, " +
                    "user_id BIGINT UNIQUE NOT NULL, " +
                    "balance DECIMAL(14,2) DEFAULT 0, " +
                    "locked_balance DECIMAL(14,2) DEFAULT 0, " +
                    "currency VARCHAR(10) DEFAULT 'VND', " +
                    "status VARCHAR(20) DEFAULT 'ACTIVE', " +
                    "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
                    ")");

            st.execute("CREATE TABLE payments (" +
                    "id BIGINT PRIMARY KEY AUTO_INCREMENT, " +
                    "wallet_id BIGINT NOT NULL, " +
                    "enrollment_id BIGINT, " +
                    "amount DECIMAL(14,2) NOT NULL, " +
                    "payment_type VARCHAR(30) NOT NULL, " +
                    "payment_method VARCHAR(30) NOT NULL, " +
                    "status VARCHAR(20) NOT NULL, " +
                    "transaction_ref VARCHAR(100) UNIQUE, " +
                    "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
                    ")");

            // Seed user mẫu
            st.execute("INSERT INTO users (id, full_name, email, password_hash, phone, role, status) " +
                    "VALUES (1, 'Nguyen Van Hoc Vien', 'hocvien@ptconnect.com', 'hash123', '0912345678', 'STUDENT', 'ACTIVE')");
            // Seed ví ban đầu với 100,000 VND
            st.execute("INSERT INTO wallets (id, user_id, balance, locked_balance, currency, status) " +
                    "VALUES (1, 1, 100000.00, 0.00, 'VND', 'ACTIVE')");
        }

        walletDAO = new WalletDAO();
        paymentDAO = new PaymentDAO();
    }

    @AfterAll
    public static void tearDown() throws Exception {
        if (inMemoryConnection != null && !inMemoryConnection.isClosed()) {
            inMemoryConnection.close();
        }
    }

    @Test
    @Order(1)
    public void testGetWallet_ExistingUser() {
        testWallet = walletDAO.getWallet(testUserId);
        assertNotNull(testWallet, "Ví của user không được null");
        assertTrue(testWallet.getId() > 0, "Wallet ID phải là số nguyên dương");
        assertEquals(testUserId, testWallet.getUserId(), "User ID trong ví phải khớp với ID yêu cầu");
    }

    @Test
    @Order(2)
    public void testGetCredit() {
        assertNotNull(testWallet, "Phải lấy được testWallet trước");
        float balance = walletDAO.getCredit(testWallet.getId());
        assertTrue(balance >= 0, "Số dư ví phải >= 0");
    }

    @Test
    @Order(3)
    public void testGetPayments() {
        assertNotNull(testWallet, "Phải lấy được testWallet trước");
        ArrayList<Payment> payments = paymentDAO.getPayments(testWallet.getId());
        assertNotNull(payments, "Danh sách giao dịch không được null");
    }

    @Test
    @Order(4)
    public void testCreatePayment_TopUp() {
        assertNotNull(testWallet, "Phải lấy được testWallet trước");
        float initialBalance = walletDAO.getCredit(testWallet.getId());

        float topUpAmount = 50000.0f;
        String ref = "TEST-" + System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 5);
        Payment p = new Payment(topUpAmount, "TOPUP", "BANK_TRANSFER", "SUCCESS", ref);
        p.setWalletId(testWallet.getId());

        boolean result = paymentDAO.createPayment(p);
        assertTrue(result, "Tạo giao dịch nạp tiền phải thành công");

        float newBalance = walletDAO.getCredit(testWallet.getId());
        assertEquals(initialBalance + topUpAmount, newBalance, 0.01f, "Số dư mới phải được cộng thêm số tiền vừa nạp");

        ArrayList<Payment> payments = paymentDAO.getPayments(testWallet.getId());
        assertFalse(payments.isEmpty(), "Danh sách giao dịch không được rỗng sau khi nạp");
        assertEquals(ref, payments.get(0).getTransactionRef(), "Giao dịch mới nhất phải khớp transactionRef");
    }
}
