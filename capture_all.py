import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

SCREENSHOT_DIR = "/home/thanhvv17@fsoft.fpt.vn/cicd-lab/PT-Connect/frontend-screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")
opts.add_argument("--window-size=1440,1100")
driver = webdriver.Chrome(options=opts)

def save_screen(name):
    time.sleep(2)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"✅ Saved screenshot: {name}.png")

def login(email, password):
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
    time.sleep(0.5)
    pass_el.send_keys(Keys.ENTER)
    time.sleep(4)

def logout():
    try:
        # Logout button in sidebar
        btn = driver.find_element(By.XPATH, "//section[@data-testid='stSidebar']//button[contains(., 'Đăng xuất')]")
        btn.click()
        time.sleep(3)
        print("  Logged out cleanly.")
    except Exception as e:
        print("  Logout button not found in sidebar, reloading page...")
        driver.get("http://localhost:8501")
        time.sleep(2)

try:
    print("1. Capturing Login & Register...")
    driver.get("http://localhost:8501")
    time.sleep(3)
    save_screen("01_login_page")

    tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
    if len(tabs) >= 2:
        tabs[1].click()
        save_screen("02_register_page")

    # 2. Student Portal
    print("\n2. Logging in as Student...")
    login("student.a@ptconnect.vn", "Password123@")
    student_tab_names = [
        "03_student_explore_pts",
        "04_student_pt_details",
        "05_student_booking",
        "06_student_my_schedule",
        "07_student_contracts",
        "08_student_wallet",
        "09_student_profile"
    ]
    for i, name in enumerate(student_tab_names):
        cur_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
        if i < len(cur_tabs):
            print(f"  Switching to Student tab {i}: {cur_tabs[i].text}")
            cur_tabs[i].click()
            save_screen(name)
    logout()

    # 3. PT Portal
    print("\n3. Logging in as PT...")
    login("pt.hoangc@ptconnect.vn", "Password123@")
    pt_tab_names = [
        "10_pt_overview",
        "11_pt_bookings",
        "12_pt_slots",
        "13_pt_courses",
        "14_pt_workout_plans",
        "15_pt_profile"
    ]
    for i, name in enumerate(pt_tab_names):
        cur_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
        if i < len(cur_tabs):
            print(f"  Switching to PT tab {i}: {cur_tabs[i].text}")
            cur_tabs[i].click()
            save_screen(name)
    logout()

    # 4. Admin Portal
    print("\n4. Logging in as Admin...")
    login("admin@ptconnect.vn", "Password123@")
    admin_tab_names = [
        "16_admin_pending_pts",
        "17_admin_users",
        "18_admin_analytics"
    ]
    for i, name in enumerate(admin_tab_names):
        cur_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-baseweb='tab']")
        if i < len(cur_tabs):
            print(f"  Switching to Admin tab {i}: {cur_tabs[i].text}")
            cur_tabs[i].click()
            save_screen(name)
    logout()

    print("\n🎉 ALL 18 SCREENSHOTS CAPTURED!")

finally:
    driver.quit()
