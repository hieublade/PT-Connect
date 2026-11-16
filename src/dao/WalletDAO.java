package dao;

import model.Wallet;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class WalletDAO extends DAO {

    public WalletDAO() {
        super();
    }

    public Wallet getWallet(int userId) {
        String selectSql = "SELECT id, user_id, balance, locked_balance, currency, status, updated_at " +
                           "FROM wallets WHERE user_id = ?";
        String insertSql = "INSERT INTO wallets (user_id, balance, locked_balance, currency, status) " +
                           "VALUES (?, 0.00, 0.00, 'VND', 'ACTIVE')";

        Connection connection = getConnection();
        if (connection == null) {
            return null;
        }

        try {
            try (PreparedStatement ps = connection.prepareStatement(selectSql)) {
                ps.setInt(1, userId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (rs.next()) {
                        Wallet w = new Wallet();
                        w.setId(rs.getInt("id"));
                        w.setUserId(rs.getInt("user_id"));
                        w.setBalance(rs.getFloat("balance"));
                        w.setLockedBalance(rs.getFloat("locked_balance"));
                        w.setCurrency(rs.getString("currency"));
                        w.setStatus(rs.getString("status"));
                        w.setUpdatedAt(rs.getTimestamp("updated_at"));
                        return w;
                    }
                }
            }

            // Nếu user chưa có ví, tự động tạo ví mới cho user
            try (PreparedStatement psInsert = connection.prepareStatement(insertSql, Statement.RETURN_GENERATED_KEYS)) {
                psInsert.setInt(1, userId);
                int affected = psInsert.executeUpdate();
                if (affected > 0) {
                    try (ResultSet genKeys = psInsert.getGeneratedKeys()) {
                        if (genKeys.next()) {
                            int newWalletId = genKeys.getInt(1);
                            Wallet w = new Wallet();
                            w.setId(newWalletId);
                            w.setUserId(userId);
                            w.setBalance(0.0f);
                            w.setLockedBalance(0.0f);
                            w.setCurrency("VND");
                            w.setStatus("ACTIVE");
                            return w;
                        }
                    }
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return null;
    }

    public float getCredit(int walletId) {
        String sql = "SELECT balance FROM wallets WHERE id = ?";
        Connection connection = getConnection();
        if (connection == null) {
            return 0.0f;
        }

        try (PreparedStatement ps = connection.prepareStatement(sql)) {
            ps.setInt(1, walletId);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return rs.getFloat("balance");
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return 0.0f;
    }
}
