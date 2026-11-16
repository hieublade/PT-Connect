package model;

import java.io.Serializable;
import java.sql.Timestamp;

public class Payment implements Serializable {
    private static final long serialVersionUID = 1L;

    private int id;
    private int walletId;
    private Integer enrollmentId;
    private float amount;
    private String paymentType;
    private String paymentMethod;
    private String status;
    private String transactionRef;
    private Timestamp createdAt;

    public Payment() {
    }

    public Payment(float amount, String paymentType, String paymentMethod, String status, String transactionRef) {
        this.amount = amount;
        this.paymentType = paymentType;
        this.paymentMethod = paymentMethod;
        this.status = status;
        this.transactionRef = transactionRef;
    }

    public Payment(int id, int walletId, Integer enrollmentId, float amount, String paymentType,
                   String paymentMethod, String status, String transactionRef, Timestamp createdAt) {
        this.id = id;
        this.walletId = walletId;
        this.enrollmentId = enrollmentId;
        this.amount = amount;
        this.paymentType = paymentType;
        this.paymentMethod = paymentMethod;
        this.status = status;
        this.transactionRef = transactionRef;
        this.createdAt = createdAt;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public int getWalletId() {
        return walletId;
    }

    public void setWalletId(int walletId) {
        this.walletId = walletId;
    }

    public Integer getEnrollmentId() {
        return enrollmentId;
    }

    public void setEnrollmentId(Integer enrollmentId) {
        this.enrollmentId = enrollmentId;
    }

    public float getAmount() {
        return amount;
    }

    public void setAmount(float amount) {
        this.amount = amount;
    }

    public String getPaymentType() {
        return paymentType;
    }

    public void setPaymentType(String paymentType) {
        this.paymentType = paymentType;
    }

    public String getPaymentMethod() {
        return paymentMethod;
    }

    public void setPaymentMethod(String paymentMethod) {
        this.paymentMethod = paymentMethod;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getTransactionRef() {
        return transactionRef;
    }

    public void setTransactionRef(String transactionRef) {
        this.transactionRef = transactionRef;
    }

    public Timestamp getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Timestamp createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public String toString() {
        return "Payment{" +
                "id=" + id +
                ", walletId=" + walletId +
                ", amount=" + amount +
                ", paymentType='" + paymentType + '\'' +
                ", paymentMethod='" + paymentMethod + '\'' +
                ", status='" + status + '\'' +
                ", transactionRef='" + transactionRef + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
