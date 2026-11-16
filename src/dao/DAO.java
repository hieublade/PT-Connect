package dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DAO {
    public static Connection con;

    public DAO() {
        if (con == null) {
            String dbUrl = System.getenv("DB_URL");
            if (dbUrl == null || dbUrl.isEmpty()) {
                dbUrl = "jdbc:mysql://localhost:3306/ptconnect?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Ho_Chi_Minh";
            }
            String dbUser = System.getenv("DB_USER");
            if (dbUser == null || dbUser.isEmpty()) {
                dbUser = "ptuser";
            }
            String dbPassword = System.getenv("DB_PASSWORD");
            if (dbPassword == null || dbPassword.isEmpty()) {
                dbPassword = "ptpassword";
            }

            try {
                Class.forName("com.mysql.cj.jdbc.Driver");
                con = DriverManager.getConnection(dbUrl, dbUser, dbPassword);
            } catch (ClassNotFoundException e) {
                System.err.println("Không tìm thấy MySQL Driver: " + e.getMessage());
            } catch (SQLException e) {
                System.err.println("Lỗi kết nối cơ sở dữ liệu: " + e.getMessage());
            }
        }
    }

    public static Connection getConnection() {
        return con;
    }

    public static void setConnection(Connection connection) {
        con = connection;
    }
}
