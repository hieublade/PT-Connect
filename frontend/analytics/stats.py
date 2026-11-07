"""Xử lý và thống kê dữ liệu bằng Pandas cho PT Connect (Milestone 8)."""

from typing import Any, Dict, List
import pandas as pd


def prepare_bookings_df(bookings: List[Dict[str, Any]]) -> pd.DataFrame:
    """Chuyển đổi danh sách bookings thô thành Pandas DataFrame có cấu trúc chuẩn."""
    if not bookings:
        return pd.DataFrame(columns=[
            "id", "student_id", "student_name", "pt_id", "pt_name",
            "course_title", "booking_type", "status", "slot_start",
            "slot_end", "session_fee", "cancelled_by", "cancellation_reason",
            "created_at", "month", "hour"
        ])

    df = pd.DataFrame(bookings)
    # Chuẩn hóa tên cột snake_case
    rename_map = {
        "studentId": "student_id",
        "studentName": "student_name",
        "ptId": "pt_id",
        "ptName": "pt_name",
        "courseTitle": "course_title",
        "bookingType": "booking_type",
        "startTime": "slot_start",
        "slotStartTime": "slot_start",
        "endTime": "slot_end",
        "slotEndTime": "slot_end",
        "sessionFee": "session_fee",
        "cancelledBy": "cancelled_by",
        "cancellationReason": "cancellation_reason",
        "createdAt": "created_at"
    }
    df = df.rename(columns=rename_map)

    # Chuyển đổi thời gian tạo & tháng
    if "created_at" in df.columns:
        df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["month"] = df["created_at_dt"].dt.strftime("%Y-%m")
    else:
        df["month"] = "N/A"

    # Chuyển đổi thời gian bắt đầu ca tập & phân bổ khung giờ
    if "slot_start" in df.columns and df["slot_start"].notna().any():
        df["slot_start_dt"] = pd.to_datetime(df["slot_start"], errors="coerce")
        if "created_at_dt" in df.columns:
            df["hour"] = df["slot_start_dt"].dt.hour.fillna(df["created_at_dt"].dt.hour).fillna(8).astype(int)
        else:
            df["hour"] = df["slot_start_dt"].dt.hour.fillna(8).astype(int)
    elif "created_at_dt" in df.columns:
        df["hour"] = df["created_at_dt"].dt.hour.fillna(8).astype(int)
    else:
        df["hour"] = 8

    if "session_fee" in df.columns:
        df["session_fee"] = pd.to_numeric(df["session_fee"], errors="coerce").fillna(0.0)

    return df


def prepare_payments_df(payments: List[Dict[str, Any]]) -> pd.DataFrame:
    """Chuyển đổi danh sách payments thô thành Pandas DataFrame có cấu trúc chuẩn."""
    if not payments:
        return pd.DataFrame(columns=[
            "id", "user_id", "user_name", "payment_type",
            "amount", "payment_method", "status", "created_at", "month"
        ])

    df = pd.DataFrame(payments)
    rename_map = {
        "userId": "user_id",
        "userName": "user_name",
        "paymentType": "payment_type",
        "paymentMethod": "payment_method",
        "createdAt": "created_at"
    }
    df = df.rename(columns=rename_map)

    if "created_at" in df.columns:
        df["created_at_dt"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["month"] = df["created_at_dt"].dt.strftime("%Y-%m")
    else:
        df["month"] = "N/A"

    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

    return df


def get_booking_status_counts(df_bookings: pd.DataFrame) -> pd.DataFrame:
    """Đếm số lượng ca tập theo từng trạng thái (PENDING, CONFIRMED, COMPLETED, CANCELLED)."""
    if df_bookings.empty or "status" not in df_bookings.columns:
        return pd.DataFrame(columns=["status", "count", "percentage"])

    counts = df_bookings["status"].value_counts().reset_index()
    counts.columns = ["status", "count"]
    total = counts["count"].sum()
    counts["percentage"] = (counts["count"] / total * 100).round(1) if total > 0 else 0
    return counts


def get_monthly_trends(df_bookings: pd.DataFrame, df_payments: pd.DataFrame) -> pd.DataFrame:
    """Tổng hợp xu hướng doanh thu và lượng ca đặt theo tháng."""
    # 1. Doanh thu theo tháng từ các giao dịch mua khóa thành công
    rev_monthly = pd.DataFrame(columns=["month", "revenue"])
    if not df_payments.empty and "month" in df_payments.columns and "amount" in df_payments.columns:
        success_packages = df_payments[
            (df_payments["payment_type"] == "PURCHASE_PACKAGE") &
            (df_payments["status"] == "SUCCESS")
        ]
        if not success_packages.empty:
            rev_monthly = success_packages.groupby("month")["amount"].sum().reset_index()
            rev_monthly.columns = ["month", "revenue"]

    # 2. Số lượng booking theo tháng
    booking_monthly = pd.DataFrame(columns=["month", "booking_count"])
    if not df_bookings.empty and "month" in df_bookings.columns:
        valid_months = df_bookings[df_bookings["month"].notna() & (df_bookings["month"] != "N/A")]
        if not valid_months.empty:
            booking_monthly = valid_months.groupby("month")["id"].count().reset_index()
            booking_monthly.columns = ["month", "booking_count"]

    # Hợp nhất dữ liệu theo tháng
    all_months = sorted(list(set(rev_monthly["month"].tolist() + booking_monthly["month"].tolist())))
    if not all_months:
        return pd.DataFrame(columns=["month", "revenue", "booking_count"])

    trend_df = pd.DataFrame({"month": all_months})
    trend_df = trend_df.merge(rev_monthly, on="month", how="left").fillna({"revenue": 0.0})
    trend_df = trend_df.merge(booking_monthly, on="month", how="left").fillna({"booking_count": 0})
    trend_df["booking_count"] = trend_df["booking_count"].astype(int)
    return trend_df.sort_values("month")


def get_top_pts(df_bookings: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Thống kê top Huấn luyện viên theo số ca tập đã hoàn thành."""
    if df_bookings.empty or "pt_name" not in df_bookings.columns:
        return pd.DataFrame(columns=["pt_name", "completed_count", "total_count", "completion_rate"])

    # Thống kê tổng số booking và số ca hoàn thành
    total_by_pt = df_bookings.groupby("pt_name")["id"].count().reset_index(name="total_count")
    completed = df_bookings[df_bookings["status"] == "COMPLETED"]
    completed_by_pt = completed.groupby("pt_name")["id"].count().reset_index(name="completed_count")

    merged = total_by_pt.merge(completed_by_pt, on="pt_name", how="left").fillna({"completed_count": 0})
    merged["completed_count"] = merged["completed_count"].astype(int)
    merged["completion_rate"] = ((merged["completed_count"] / merged["total_count"]) * 100).round(1)

    return merged.sort_values("completed_count", ascending=False).head(limit)


def get_cancellation_analysis(df_bookings: pd.DataFrame) -> pd.DataFrame:
    """Phân tích các ca bị hủy theo người hủy (STUDENT / PT / SYSTEM)."""
    if df_bookings.empty or "status" not in df_bookings.columns:
        return pd.DataFrame(columns=["cancelled_by", "count"])

    cancelled = df_bookings[df_bookings["status"] == "CANCELLED"]
    if cancelled.empty:
        return pd.DataFrame(columns=["cancelled_by", "count"])

    cancelled = cancelled.copy()
    label_map = {
        "STUDENT": "Học viên (STUDENT)",
        "PT": "HLV (PT)",
        "SYSTEM": "Hệ thống (SYSTEM)"
    }
    if "cancelled_by" not in cancelled.columns:
        cancelled["cancelled_by"] = "Học viên (STUDENT)"
    else:
        cancelled["cancelled_by"] = cancelled["cancelled_by"].fillna("STUDENT").map(
            lambda x: label_map.get(str(x), str(x) if str(x) != "None" else "Học viên (STUDENT)")
        )

    res = cancelled["cancelled_by"].value_counts().reset_index()
    res.columns = ["cancelled_by", "count"]
    return res


def get_popular_training_hours(df_bookings: pd.DataFrame) -> pd.DataFrame:
    """Phân tích khung giờ được học viên đặt lịch nhiều nhất trong ngày."""
    if df_bookings.empty or "hour" not in df_bookings.columns:
        return pd.DataFrame(columns=["hour", "count"])

    valid_hours = df_bookings[df_bookings["hour"].notna()]
    if valid_hours.empty:
        return pd.DataFrame(columns=["hour", "count"])

    res = valid_hours["hour"].value_counts().sort_index().reset_index()
    res.columns = ["hour", "count"]
    res["hour_label"] = res["hour"].apply(lambda h: f"{int(h):02d}:00 - {int(h)+1:02d}:00")
    return res
