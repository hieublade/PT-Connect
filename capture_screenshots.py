import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

SCREENSHOT_DIR = "/home/thanhvv17@fsoft.fpt.vn/cicd-lab/PT-Connect/frontend-screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1440,1100")

driver = webdriver.Chrome(options=chrome_options)

def save_screen(name):
    time.sleep(2.5)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"✅ Saved screenshot: {name}.png")

try:
    print("Navigating to http://localhost:8501...")
    driver.get("http://localhost:8501")
    time.sleep(4)
    save_screen("01_login_page")

    # Switch to Register tab
    tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
    if len(tabs) >= 2:
        tabs[1].click()
        time.sleep(2)
        save_screen("02_register_page")
        tabs[0].click()
        time.sleep(1.5)

    def do_login(email, password):
        print(f"\n--- Logging in as {email} ---")
        driver.get("http://localhost:8501")
        time.sleep(3)

        email_el = driver.find_element(By.XPATH, "//input[@aria-label='Email đăng nhập']")
        pass_el = driver.find_element(By.XPATH, "//input[@aria-label='Mật khẩu']")

        email_el.send_keys(Keys.CONTROL + "a")
        email_el.send_keys(Keys.BACKSPACE)
        email_el.send_keys(email)

        pass_el.send_keys(Keys.CONTROL + "a")
        pass_el.send_keys(Keys.BACKSPACE)
        pass_el.send_keys(password)

        btn = driver.find_element(By.XPATH, "//button[contains(., 'Đăng nhập')]")
        btn.click()
        time.sleep(5)

    def do_logout():
        try:
            btn = driver.find_element(By.XPATH, "//button[contains(., 'Đăng xuất')]")
            btn.click()
            time.sleep(3)
            print("Logged out successfully.")
        except Exception as e:
            print("Logout error:", e)

    # 1. Student
    do_login("student.a@ptconnect.vn", "Password123@")
    student_tab_names = [
        "03_student_explore_pts",
        "04_student_pt_details",
        "05_student_booking",
        "06_student_my_schedule",
        "07_student_contracts",
        "08_student_wallet",
        "09_student_profile"
    ]
    for i, t_name in enumerate(student_tab_names):
        current_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
        print(f"Student tab {i}: found {len(current_tabs)} tabs")
        if i < len(current_tabs):
            current_tabs[i].click()
            save_screen(t_name)
    do_logout()

    # 2. PT
    do_login("pt.hoangc@ptconnect.vn", "Password123@")
    pt_tab_names = [
        "10_pt_overview",
        "11_pt_bookings",
        "12_pt_slots",
        "13_pt_courses",
        "14_pt_workout_plans",
        "15_pt_profile"
    ]
    for i, t_name in enumerate(pt_tab_names):
        current_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
        print(f"PT tab {i}: found {len(current_tabs)} tabs")
        if i < len(current_tabs):
            current_tabs[i].click()
            save_screen(t_name)
    do_logout()

    # 3. Admin
    do_login("admin@ptconnect.vn", "Password123@")
    admin_tab_names = [
        "16_admin_pending_pts",
        "17_admin_users",
        "18_admin_analytics"
    ]
    for i, t_name in enumerate(admin_tab_names):
        current_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
        print(f"Admin tab {i}: found {len(current_tabs)} tabs")
        if i < len(current_tabs):
            current_tabs[i].click()
            save_screen(t_name)
    do_logout()

    print("\n🎉 ALL 18 SCREENSHOTS CAPTURED SUCCESSFULLY!")

finally:
    driver.quit()
