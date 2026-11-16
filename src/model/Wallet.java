package model;

import java.io.Serializable;
import java.sql.Timestamp;
import java.util.ArrayList;

public class Wallet implements Serializable {
    private static final long serialVersionUID = 1L;

    private int id;
    private int userId;
    private float balance;
    private float lockedBalance;
    private String currency;
    private String status;
    private Timestamp updatedAt;
    private ArrayList<Payment> payments;

    public Wallet() {
        this.payments = new ArrayList<>();
        this.currency = "VND";
        this.status = "ACTIVE";
    }

    public Wallet(int id, int userId, float balance, float lockedBalance, String currency, String status, Timestamp updatedAt) {
        this.id = id;
        this.userId = userId;
        this.balance = balance;
        this.lockedBalance = lockedBalance;
        this.currency = currency;
        this.status = status;
        this.updatedAt = updatedAt;
        this.payments = new ArrayList<>();
    }

    public Wallet(int id, float balance, float lockedBalance, String currency, String status, Timestamp updatedAt, ArrayList<Payment> payments) {
        this.id = id;
        this.balance = balance;
        this.lockedBalance = lockedBalance;
        this.currency = currency;
        this.status = status;
        this.updatedAt = updatedAt;
        this.payments = payments != null ? payments : new ArrayList<>();
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getUserId() {
        return userId;
    }

    public void setUserId(int userId) {
        this.userId = userId;
    }

    public float getBalance() {
        return balance;
    }

    public void setBalance(float balance) {
        this.balance = balance;
    }

    public float getLockedBalance() {
        return lockedBalance;
    }

    public void setLockedBalance(float lockedBalance) {
        this.lockedBalance = lockedBalance;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Timestamp getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Timestamp updatedAt) {
        this.updatedAt = updatedAt;
    }

    public ArrayList<Payment> getPayments() {
        return payments;
    }

    public void setPayments(ArrayList<Payment> payments) {
        this.payments = payments != null ? payments : new ArrayList<>();
    }

    @Override
    public String toString() {
        return "Wallet{" +
                "id=" + id +
                ", userId=" + userId +
                ", balance=" + balance +
                ", lockedBalance=" + lockedBalance +
                ", currency='" + currency + '\'' +
                ", status='" + status + '\'' +
                ", updatedAt=" + updatedAt +
                ", totalPayments=" + (payments != null ? payments.size() : 0) +
                '}';
    }
}
