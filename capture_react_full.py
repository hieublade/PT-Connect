import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

SCREENSHOT_DIR = "/home/thanhvv17@fsoft.fpt.vn/cicd-lab/PT-Connect/frontend-screenshots/react_full"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--disable-gpu")
opts.add_argument("--window-size=1440,1050")
driver = webdriver.Chrome(options=opts)

def save_screen(name):
    time.sleep(1.5)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"✅ Saved: {name}.png")

def login(email, password):
    driver.get("http://localhost:3000")
    time.sleep(2)
    inputs = driver.find_elements(By.TAG_NAME, "input")
    inputs[0].send_keys(Keys.CONTROL + "a")
    inputs[0].send_keys(Keys.BACKSPACE)
    inputs[0].send_keys(email)
    inputs[1].send_keys(Keys.CONTROL + "a")
    inputs[1].send_keys(Keys.BACKSPACE)
    inputs[1].send_keys(password)
    time.sleep(0.5)
    inputs[1].send_keys(Keys.ENTER)
    time.sleep(3)

def logout():
    try:
        btn = driver.find_element(By.XPATH, "//button[contains(., 'Đăng xuất')]")
        btn.click()
        time.sleep(2)
    except Exception as e:
        print("Logout error:", e)
        driver.execute_script("localStorage.clear(); window.location.reload();")
        time.sleep(2)

try:
    print("1. Testing Login & Register screens...")
    driver.get("http://localhost:3000")
    time.sleep(2)
    save_screen("01_react_login")

    # Switch to register
    reg_btn = driver.find_element(By.XPATH, "//button[contains(., 'Đăng ký tài khoản')]")
    reg_btn.click()
    save_screen("02_react_register")

    # 2. Student Portal
    print("\n2. Testing Student Portal...")
    login("student.a@ptconnect.vn", "Password123@")
    save_screen("03_react_student_explore")

    student_tab_names = [
        ("Chi Tiết PT", "04_react_student_pt_details"),
        ("Đặt Lịch", "05_react_student_booking"),
        ("Lịch Của Tôi", "06_react_student_schedule"),
        ("Khóa Của Tôi", "07_react_student_contracts"),
        ("Ví Tiền", "08_react_student_wallet"),
        ("Hồ Sơ", "09_react_student_profile"),
    ]

    for tab_text, filename in student_tab_names:
        try:
            tab_el = driver.find_element(By.XPATH, f"//button[contains(., '{tab_text}')]")
            tab_el.click()
            save_screen(filename)
        except Exception as e:
            print(f"Error navigating {tab_text}:", e)

    logout()

    # 3. PT Portal
    print("\n3. Testing PT Portal...")
    login("pt.hoangc@ptconnect.vn", "Password123@")
    save_screen("10_react_pt_overview")

    pt_tab_names = [
        ("Duyệt Lịch", "11_react_pt_bookings"),
        ("Khung Giờ", "12_react_pt_slots"),
        ("Quản Lý Khóa", "13_react_pt_courses"),
        ("Giáo Án", "14_react_pt_workout_plans"),
        ("Hồ Sơ", "15_react_pt_profile"),
    ]

    for tab_text, filename in pt_tab_names:
        try:
            tab_el = driver.find_element(By.XPATH, f"//button[contains(., '{tab_text}')]")
            tab_el.click()
            save_screen(filename)
        except Exception as e:
            print(f"Error navigating {tab_text}:", e)

    logout()

    # 4. Admin Portal
    print("\n4. Testing Admin Portal...")
    login("admin@ptconnect.vn", "Password123@")
    save_screen("16_react_admin_pending_pts")

    admin_tab_names = [
        ("Quản Lý Người Dùng", "17_react_admin_users"),
        ("Thống Kê", "18_react_admin_analytics"),
    ]

    for tab_text, filename in admin_tab_names:
        try:
            tab_el = driver.find_element(By.XPATH, f"//button[contains(., '{tab_text}')]")
            tab_el.click()
            save_screen(filename)
        except Exception as e:
            print(f"Error navigating {tab_text}:", e)

    logout()

    print("\n🎉 ALL REACT INTERFACES TESTED & CAPTURED SUCCESSFULLY!")

finally:
    driver.quit()
