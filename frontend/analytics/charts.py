"""Biểu đồ trực quan hóa dữ liệu bằng Plotly cho PT Connect Admin (Milestone 8)."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_booking_status(df_counts: pd.DataFrame) -> go.Figure:
    """Biểu đồ 1: Phân bố trạng thái ca tập (Cột & Tỷ lệ phần trăm)."""
    if df_counts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu ca tập", showarrow=False, font=dict(size=16))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    color_map = {
        "COMPLETED": "#2e7d32",   # Xanh lá
        "CONFIRMED": "#1976d2",   # Xanh dương
        "PENDING": "#f57c00",     # Cam
        "CANCELLED": "#d32f2f",   # Đỏ
        "NO_SHOW": "#7b1fa2"      # Tím
    }

    colors = [color_map.get(s, "#757575") for s in df_counts["status"]]

    fig = go.Figure(data=[
        go.Bar(
            x=df_counts["status"],
            y=df_counts["count"],
            text=[f"{c} ca ({p}%)" for c, p in zip(df_counts["count"], df_counts["percentage"])],
            textposition="auto",
            marker=dict(
                color=colors,
                line=dict(color="#ffffff", width=1.5)
            ),
            hovertemplate="<b>Trạng thái:</b> %{x}<br><b>Số lượng:</b> %{y} ca<extra></extra>"
        )
    ])

    fig.update_layout(
        title="Phân Bố Trạng Thái Ca Tập (Booking Status)",
        xaxis_title="Trạng thái",
        yaxis_title="Số ca tập",
        template="plotly_white",
        height=380,
        margin=dict(l=30, r=30, t=50, b=30)
    )
    return fig


def plot_monthly_trends(df_trends: pd.DataFrame) -> go.Figure:
    """Biểu đồ 2: Xu hướng ca tập và doanh thu bán khóa theo tháng (Hai trục tung kết hợp)."""
    if df_trends.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu doanh thu và ca tập theo tháng", showarrow=False, font=dict(size=16))
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    fig = go.Figure()

    # Cột doanh thu (Trục trái)
    fig.add_trace(
        go.Bar(
            x=df_trends["month"],
            y=df_trends["revenue"],
            name="Doanh thu bán khóa (VNĐ)",
            marker_color="#1e88e5",
            opacity=0.85,
            yaxis="y",
            hovertemplate="<b>Tháng %{x}</b><br>Doanh thu: %{y:,.0f} đ<extra></extra>"
        )
    )

    # Đường số ca đặt lịch (Trục phải)
    fig.add_trace(
        go.Scatter(
            x=df_trends["month"],
            y=df_trends["booking_count"],
            name="Số lượng ca tập",
            mode="lines+markers+text",
            text=df_trends["booking_count"],
            textposition="top center",
            line=dict(color="#ff8f00", width=3),
            marker=dict(size=8, color="#ff8f00"),
            yaxis="y2",
            hovertemplate="<b>Tháng %{x}</b><br>Số ca tập: %{y}<extra></extra>"
        )
    )

    fig.update_layout(
        title="Xu Hướng Doanh Thu Bán Khóa & Lượng Ca Tập Theo Tháng",
        xaxis=dict(title=dict(text="Tháng (YYYY-MM)")),
        yaxis=dict(
            title=dict(text="Doanh thu (VNĐ)", font=dict(color="#1e88e5")),
            tickfont=dict(color="#1e88e5")
        ),
        yaxis2=dict(
            title=dict(text="Số ca tập", font=dict(color="#ff8f00")),
            tickfont=dict(color="#ff8f00"),
            overlaying="y",
            side="right"
        ),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def plot_top_pts(df_top_pts: pd.DataFrame) -> go.Figure:
    """Biểu đồ 3: Top Huấn luyện viên theo số ca tập đã hoàn thành (Cột ngang)."""
    if df_top_pts.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu Huấn luyện viên", showarrow=False, font=dict(size=16))
        fig.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    df_sorted = df_top_pts.sort_values("completed_count", ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            x=df_sorted["completed_count"],
            y=df_sorted["pt_name"],
            orientation="h",
            text=[f"{c} ca ({r}%)" for c, r in zip(df_sorted["completed_count"], df_sorted["completion_rate"])],
            textposition="auto",
            marker=dict(
                color=df_sorted["completed_count"],
                colorscale="Viridis",
                showscale=False
            ),
            hovertemplate="<b>HLV:</b> %{y}<br><b>Số ca hoàn thành:</b> %{x}<extra></extra>"
        )
    ])

    fig.update_layout(
        title="Top Huấn Luyện Viên Có Số Ca Dạy Hoàn Thành Cao Nhất",
        xaxis_title="Số ca hoàn thành (COMPLETED)",
        yaxis_title="Huấn luyện viên",
        template="plotly_white",
        height=380,
        margin=dict(l=60, r=30, t=50, b=30)
    )
    return fig


def plot_cancellation_reasons(df_cancel: pd.DataFrame) -> go.Figure:
    """Biểu đồ mở rộng: Tỷ lệ hủy ca tập theo đối tượng (STUDENT vs PT vs SYSTEM)."""
    if df_cancel.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có ca tập nào bị hủy", showarrow=False, font=dict(size=16))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    fig = px.pie(
        df_cancel,
        values="count",
        names="cancelled_by",
        title="Tỷ Lệ Ca Bị Hủy Theo Đối Tượng Hủy",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=50, b=20))
    return fig


def plot_popular_hours(df_hourly: pd.DataFrame) -> go.Figure:
    """Biểu đồ mở rộng: Phân bố khung giờ tập được đặt nhiều nhất trong ngày."""
    if df_hourly.empty:
        fig = go.Figure()
        fig.add_annotation(text="Chưa có dữ liệu khung giờ", showarrow=False, font=dict(size=16))
        fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        return fig

    fig = px.bar(
        df_hourly,
        x="hour_label",
        y="count",
        title="Phân Bố Khung Giờ Tập Được Học Viên Đặt Lịch Nhiều Nhất",
        labels={"hour_label": "Khung giờ", "count": "Số ca đặt"},
        color="count",
        color_continuous_scale="Teal"
    )
    fig.update_layout(
        template="plotly_white",
        height=320,
        xaxis_tickangle=-30,
        margin=dict(l=30, r=30, t=50, b=40)
    )
    return fig
