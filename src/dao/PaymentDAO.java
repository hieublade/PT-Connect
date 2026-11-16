package dao;

import model.Payment;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.ArrayList;

public class PaymentDAO extends DAO {

    public PaymentDAO() {
        super();
    }

    public ArrayList<Payment> getPayments(int walletId) {
        ArrayList<Payment> list = new ArrayList<>();
        String sql = "SELECT id, wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at " +
                     "FROM payments WHERE wallet_id = ? ORDER BY created_at DESC, id DESC";

        try {
            Connection connection = getConnection();
            if (connection == null) {
                return list;
            }
            try (PreparedStatement ps = connection.prepareStatement(sql)) {
                ps.setInt(1, walletId);
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) {
                        Payment p = new Payment();
                        p.setId(rs.getInt("id"));
                        p.setWalletId(rs.getInt("wallet_id"));
                        int enrollId = rs.getInt("enrollment_id");
                        if (rs.wasNull()) {
                            p.setEnrollmentId(null);
                        } else {
                            p.setEnrollmentId(enrollId);
                        }
                        p.setAmount(rs.getFloat("amount"));
                        p.setPaymentType(rs.getString("payment_type"));
                        p.setPaymentMethod(rs.getString("payment_method"));
                        p.setStatus(rs.getString("status"));
                        p.setTransactionRef(rs.getString("transaction_ref"));
                        p.setCreatedAt(rs.getTimestamp("created_at"));
                        list.add(p);
                    }
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean createPayment(Payment p) {
        Connection connection = getConnection();
        if (connection == null) {
            return false;
        }

        String insertPaymentSql = "INSERT INTO payments (wallet_id, enrollment_id, amount, payment_type, payment_method, status, transaction_ref, created_at) " +
                                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
        String updateWalletSql = "UPDATE wallets SET balance = balance + ?, updated_at = ? WHERE id = ?";

        boolean originalAutoCommit = true;
        try {
            originalAutoCommit = connection.getAutoCommit();
            connection.setAutoCommit(false);

            Timestamp now = new Timestamp(System.currentTimeMillis());
            if (p.getCreatedAt() == null) {
                p.setCreatedAt(now);
            }

            try (PreparedStatement psInsert = connection.prepareStatement(insertPaymentSql)) {
                psInsert.setInt(1, p.getWalletId());
                if (p.getEnrollmentId() == null) {
                    psInsert.setNull(2, java.sql.Types.BIGINT);
                } else {
                    psInsert.setInt(2, p.getEnrollmentId());
                }
                psInsert.setFloat(3, p.getAmount());
                psInsert.setString(4, p.getPaymentType());
                psInsert.setString(5, p.getPaymentMethod());
                psInsert.setString(6, p.getStatus());
                psInsert.setString(7, p.getTransactionRef());
                psInsert.setTimestamp(8, p.getCreatedAt());

                int affected = psInsert.executeUpdate();
                if (affected <= 0) {
                    connection.rollback();
                    return false;
                }
            }

            // Nếu nạp tiền TOPUP thành công (SUCCESS), cộng tiền vào số dư ví
            if ("SUCCESS".equalsIgnoreCase(p.getStatus()) && "TOPUP".equalsIgnoreCase(p.getPaymentType())) {
                try (PreparedStatement psUpdate = connection.prepareStatement(updateWalletSql)) {
                    psUpdate.setFloat(1, p.getAmount());
                    psUpdate.setTimestamp(2, now);
                    psUpdate.setInt(3, p.getWalletId());

                    int rows = psUpdate.executeUpdate();
                    if (rows <= 0) {
                        connection.rollback();
                        return false;
                    }
                }
            }

            connection.commit();
            return true;
        } catch (SQLException e) {
            try {
                connection.rollback();
            } catch (SQLException ex) {
                ex.printStackTrace();
            }
            e.printStackTrace();
            return false;
        } finally {
            try {
                connection.setAutoCommit(originalAutoCommit);
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
