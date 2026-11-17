"""
benchmark/run_benchmark.py
Script tu dong chay do luong hieu nang cho 6 kich ban truy van,
ve bieu do truc quan hoa va xuat bao cao Markdown / Word.
"""

import sys
import os
import time
import pymysql
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'DejaVu Sans']
matplotlib.rcParams['font.family'] = 'sans-serif'

from queries import BENCHMARK_CASES

def get_connection(host="127.0.0.1", port=3307, user="root", password="root123", database="ptconnect"):
    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4",
        autocommit=True,
    )

def measure_query(conn, sql, iterations=5):
    cursor = conn.cursor()
    times = []
    
    # Chay thu 1 lan de warm-up bo dem
    try:
        cursor.execute(sql)
        cursor.fetchall()
    except Exception as e:
        print(f"Loi khi chay warm-up query: {e}")
        return 0, 0, str(e)

    for _ in range(iterations):
        st = time.perf_counter()
        cursor.execute(sql)
        cursor.fetchall()
        et = time.perf_counter()
        times.append((et - st) * 1000)  # ms

    avg_ms = sum(times) / len(times)
    
    # Lay EXPLAIN
    explain_info = ""
    rows_scanned = 0
    try:
        cursor.execute(f"EXPLAIN {sql}")
        rows = cursor.fetchall()
        notes = []
        for r in rows:
            table_name = r[2]
            access_type = r[4]
            key_used = r[6]
            r_count = r[9] if len(r) > 9 and r[9] is not None else 0
            extra = r[11] if len(r) > 11 else ""
            if r_count:
                rows_scanned += int(r_count)
            notes.append(f"{table_name} (type={access_type}, key={key_used}, extra={extra})")
        explain_info = "; ".join(notes)
    except Exception as ex:
        explain_info = str(ex)

    cursor.close()
    return round(avg_ms, 2), rows_scanned, explain_info

def run_all_benchmarks(host="127.0.0.1", port=3307, user="root", password="root123", database="ptconnect"):
    print(f"Ket noi toi MySQL {host}:{port}...")
    conn = get_connection(host, port, user, password, database)
    cursor = conn.cursor()

    # Dam bao foreign key index cho payments ton tai de khong bi loi khoa ngoai khi xoa index toi uu
    try:
        cursor.execute("CREATE INDEX idx_payments_wallet ON payments (wallet_id);")
    except Exception:
        pass

    results = []
    os.makedirs("benchmark_charts", exist_ok=True)

    for case in BENCHMARK_CASES:
        c_id = case["id"]
        role = case["role"]
        title = case["title"]
        print(f"\n========================================================")
        print(f"Dang thuc hien Case {c_id} [{role}]: {title}")
        print(f"========================================================")

        # 1. Xoa cac chi muc toi uu neu da ton tai
        for drop_sql in case["indexes_to_drop"]:
            try:
                cursor.execute(drop_sql)
            except Exception:
                pass

        # 2. Do truy van CHUA toi uu
        print("-> Dang do truy van CHUA toi uu...")
        unopt_ms, unopt_rows, unopt_plan = measure_query(conn, case["unoptimized_sql"])
        print(f"   Thoi gian: {unopt_ms} ms | So dong duyet: {unopt_rows}")

        # 3. Tao cac chi muc toi uu
        print("-> Dang tao chi muc toi uu...")
        for create_sql in case["indexes_to_create"]:
            try:
                cursor.execute(create_sql)
            except Exception as e:
                print(f"   Luu y tao chi muc: {e}")

        # 4. Do truy van DA toi uu
        print("-> Dang do truy van DA toi uu...")
        opt_ms, opt_rows, opt_plan = measure_query(conn, case["optimized_sql"])
        print(f"   Thoi gian: {opt_ms} ms | So dong duyet: {opt_rows}")

        # 5. Tinh toan ty le cai thien
        improvement = round(unopt_ms / opt_ms, 1) if opt_ms > 0 else 1.0
        print(f"==> TIEU CHUAN CAI THIEN: Nhanh hon {improvement} lan!")

        results.append({
            "id": c_id,
            "role": role,
            "title": title,
            "technique": case["technique"],
            "unopt_ms": unopt_ms,
            "unopt_rows": unopt_rows,
            "unopt_plan": unopt_plan,
            "opt_ms": opt_ms,
            "opt_rows": opt_rows,
            "opt_plan": opt_plan,
            "improvement": improvement,
            "unoptimized_sql": case["unoptimized_sql"].strip(),
            "optimized_sql": case["optimized_sql"].strip(),
        })

    cursor.close()
    conn.close()

    # 6. Ve bieu do cot Matplotlib
    generate_charts(results)

    # 7. Xuat bao cao Markdown
    generate_markdown_report(results)
    print("\nHOAN TAT TOAN BO QUA TRINH BENCHMARK!")

def generate_charts(results):
    print("\nDang xuat bieu do hinh anh PNG...")
    
    # Bieu do 1: So sanh thoi gian thuc thi 6 chuc nang
    labels = [f"CN {r['id']}\n({r['role']})" for r in results]
    unopt_times = [r["unopt_ms"] for r in results]
    opt_times = [r["opt_ms"] for r in results]

    x = list(range(len(labels)))
    width = 0.35

    plt.figure(figsize=(13, 6.5), dpi=300)
    plt.bar([i - width/2 for i in x], unopt_times, width, label="Chưa tối ưu (Unoptimized)", color="#d9534f")
    plt.bar([i + width/2 for i in x], opt_times, width, label="Đã tối ưu (Optimized)", color="#5cb85c")

    plt.title("SO SÁNH THỜI GIAN THỰC THI TRUY VẤN (MILLISECONDS - CÀNG THẤP CÀNG TỐT)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Chức năng kiểm thử", fontsize=11, fontweight="bold")
    plt.ylabel("Thời gian phản hồi (ms)", fontsize=11, fontweight="bold")
    plt.xticks(x, labels, fontsize=10)
    plt.legend(fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    max_val = max(unopt_times + opt_times)
    for i in x:
        plt.text(i - width/2, unopt_times[i] + (max_val*0.015), f"{unopt_times[i]}ms", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#c9302c")
        plt.text(i + width/2, opt_times[i] + (max_val*0.015), f"{opt_times[i]}ms", ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#2b542c")

    plt.tight_layout()
    chart_path = os.path.join("benchmark_charts", "tong_quan_so_sanh_6_chuc_nang.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"-> Da luu bieu do: {chart_path}")

    # Bieu do 2: He so tang toc (Speedup ratio)
    improvements = [r["improvement"] for r in results]
    plt.figure(figsize=(12, 5.5), dpi=300)
    bars = plt.bar(labels, improvements, color="#0275d8", width=0.45)
    plt.title("HỆ SỐ TĂNG TỐC HIỆU NĂNG SAU KHI TỐI ƯU (SỐ LẦN NHANH HƠN)", fontsize=13, fontweight="bold", pad=15)
    plt.xlabel("Chức năng kiểm thử", fontsize=11, fontweight="bold")
    plt.ylabel("Hệ số tăng tốc (Lần)", fontsize=11, fontweight="bold")
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    max_imp = max(improvements)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + (max_imp*0.015), f"{yval}x", ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    speedup_path = os.path.join("benchmark_charts", "he_so_tang_toc.png")
    plt.savefig(speedup_path)
    plt.close()
    print(f"-> Da luu bieu do: {speedup_path}")

def generate_markdown_report(results):
    print("\nDang xuat bao cao BAO_CAO_TOI_UU_TRUY_VAN.md...")
    lines = []
    lines.append("# BÁO CÁO KẾT QUẢ THỰC NGHIỆM TỐI ƯU HÓA TRUY VẤN CƠ SỞ DỮ LIỆU")
    lines.append("\n**Dự án:** Nền tảng kết nối Huấn luyện viên cá nhân PT Connect")
    lines.append("\n**Hệ quản trị CSDL:** MySQL 8.0 (Cấu trúc 16 bảng chuẩn Boyce-Codd - BCNF)")
    lines.append("\n**Quy mô dữ liệu thử nghiệm:** Hơn 500,000 bản ghi trên các bảng trọng tâm (Bookings, Slots, Payments, Users, Disputes)")
    lines.append("\n---\n")

    lines.append("## 1. TỔNG HỢP KẾT QUẢ ĐO LƯỜNG HIỆU NĂNG (6 CHỨC NĂNG)\n")
    lines.append("*(Bảng dưới đây được định dạng sẵn, bạn có thể copy và dán trực tiếp vào Microsoft Word)*\n")

    lines.append("| STT | Vai trò | Tên chức năng nghiệp vụ | Kỹ thuật tối ưu áp dụng | Chưa tối ưu (ms) | Đã tối ưu (ms) | Tăng tốc (lần) |")
    lines.append("| :--- | :--- | :--- | :--- | :---: | :---: | :---: |")
    for r in results:
        lines.append(f"| **{r['id']}** | **{r['role']}** | {r['title']} | {r['technique']} | **{r['unopt_ms']} ms** | **{r['opt_ms']} ms** | **{r['improvement']}x** |")

    lines.append("\n---\n")
    lines.append("## 2. BIỂU ĐỒ TRỰC QUAN HÓA SO SÁNH HIỆU NĂNG\n")
    lines.append("*(Chèn 2 file ảnh trong thư mục `benchmark_charts/` vào bài báo cáo Word)*\n")
    lines.append("- **Biểu đồ 1: So sánh thời gian thực thi (ms)**: `benchmark_charts/tong_quan_so_sanh_6_chuc_nang.png`")
    lines.append("- **Biểu đồ 2: Hệ số tăng tốc hiệu năng**: `benchmark_charts/he_so_tang_toc.png`\n")

    lines.append("\n---\n")
    lines.append("## 3. PHÂN TÍCH CHI TIẾT TỪNG KỊCH BẢN TRUY VẤN\n")

    for r in results:
        lines.append(f"### Kịch bản {r['id']} ({r['role']}): {r['title']}\n")
        lines.append(f"- **Kỹ thuật tối ưu**: {r['technique']}.")
        lines.append(f"- **Thời gian thực thi ban đầu**: **{r['unopt_ms']} ms** (Duyệt ~{r['unopt_rows']} dòng).")
        lines.append(f"- **Thời gian sau khi tối ưu**: **{r['opt_ms']} ms** (Duyệt ~{r['opt_rows']} dòng).")
        lines.append(f"- **Hiệu quả cải thiện**: **Nhanh hơn {r['improvement']} lần**.\n")

        lines.append("#### Câu lệnh SQL Chưa tối ưu:")
        lines.append("```sql")
        lines.append(r["unoptimized_sql"])
        lines.append("```\n")

        lines.append("#### Câu lệnh SQL Đã tối ưu:")
        lines.append("```sql")
        lines.append(r["optimized_sql"])
        lines.append("```\n")

        lines.append(f"- **Kế hoạch thực thi (Execution Plan)**:")
        lines.append(f"  - *Chưa tối ưu*: `{r['unopt_plan']}`")
        lines.append(f"  - *Đã tối ưu*: `{r['opt_plan']}`\n")
        lines.append("---\n")

    lines.append("## 4. KẾT LUẬN VÀ BÀI HỌC KINH NGHIỆM CHO BÁO CÁO\n")
    lines.append("1. **Tránh quét chuỗi LIKE trên bảng lớn**: Tách thuộc tính đa trị thành bảng riêng đạt chuẩn BCNF (`pt_locations`) kết hợp Composite Index giúp triệt tiêu hoàn toàn Full Table Scan.")
    lines.append("2. **Giải quyết bài toán phân trang sâu (Deep Paging)**: Kỹ thuật Deferred Join chỉ đọc khóa chính trên Index trước khi JOIN dữ liệu thực tế giúp giảm tải I/O bộ nhớ khi OFFSET lên tới hàng chục nghìn dòng.")
    lines.append("3. **Bảo toàn tính SARGability**: Tuyệt đối không dùng hàm xử lý ngày tháng (`YEAR()`, `MONTH()`, `DATE()`) trực tiếp lên cột truy vấn. Luôn dùng truy vấn khoảng (`Range Query`) để tận dụng trọn vẹn chỉ mục B-Tree.")
    lines.append("4. **Khử bẫy N+1 và Correlated Subqueries**: Thay thế các truy vấn con quét lặp lại bằng kỹ thuật gom nhóm điều kiện (`Single-Pass SUM CASE`) và bảng dẫn xuất (`Derived Table`).")
    lines.append("5. **Khử chi phí Filesort ngoài đĩa**: Đánh Composite Index bao gồm cả các cột trong mệnh đề `ORDER BY` theo đúng chiều sắp xếp giúp MySQL trả về kết quả tức thì mà không cần tốn bộ nhớ RAM để sắp xếp lại.")

    with open("BAO_CAO_TOI_UU_TRUY_VAN.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("-> Da luu file bao cao BAO_CAO_TOI_UU_TRUY_VAN.md")

if __name__ == "__main__":
    h = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 3307
    u = sys.argv[3] if len(sys.argv) > 3 else "root"
    pwd = sys.argv[4] if len(sys.argv) > 4 else "root123"
    db = sys.argv[5] if len(sys.argv) > 5 else "ptconnect"
    run_all_benchmarks(h, p, u, pwd, db)
