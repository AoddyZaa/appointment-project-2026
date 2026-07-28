from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Appointment Project 2026", page_icon="📅", layout="wide")

@st.cache_resource
def init_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # ดึงค่าจาก Secrets และแปลงร่าง \\n ให้เป็นบรรทัดใหม่ที่ถูกต้อง
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
        
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/1l1BNsov2CzmbSgdpoi_zSkcyPIgiOtBVHcuyRDYb3EA/edit?usp=sharing"
    sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
    return sheet

try:
    sheet = init_sheet()
except Exception as e:
    st.error(f"⚠️ เชื่อมต่อ Google Sheets ไม่สำเร็จ: {e}")
    st.stop()

# --- ส่วน UI หน้าจอหลัก (ซ้ายกรอก | ขวาแสดงตาราง) ---
st.title("📅 ระบบบันทึกตารางนัดหมาย (Appointment Project 2026)")
st.markdown("---")

left_col, right_col = st.columns([1, 1.5], gap="large")

with left_col:
    st.subheader("📝 กรอกข้อมูลนัดหมาย")
    with st.form("appointment_form", clear_on_submit=True):
        date_val = st.date_input("📅 วันที่นัด", value=datetime.today())
        time_val = st.time_input("⏰ เวลานัด", value=datetime.strptime("09:00", "%H:%M").time())
        title_val = st.text_input("📝 รายการนัด / หัวข้อเรื่อง")
        by_val = st.text_input("👤 นัดโดย (ผู้ติดต่อ)")
        owner_val = st.text_input("⭐ เจ้าของนัด (ผู้รับผิดชอบ)")
        location_val = st.text_input("📍 สถานที่นัดหมาย")
        phone_val = st.text_input("📞 เบอร์โทรศัพท์ติดต่อ")
        note_val = st.text_area("💬 หมายเหตุเพิ่มเติม")

        submitted = st.form_submit_button("💾 บันทึกรายการลง Google Sheets", use_container_width=True)

    if submitted:
        if not title_val:
            st.warning("⚠️ กรุณากรอก 'รายการนัด / หัวข้อเรื่อง' ก่อนครับ!")
        else:
            try:
                date_str = date_val.strftime("%Y-%m-%d")
                time_str = time_val.strftime("%H:%M")
                row_data = [date_str, time_str, title_val, by_val, owner_val, location_val, phone_val, note_val]
                sheet.append_row(row_data)
                st.success("🎉 บันทึกข้อมูลสำเร็จ!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")

with right_col:
    st.subhfrom datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(page_title="Appointment Project 2026", page_icon="📅", layout="wide")

# --- ฟังก์ชันอ่านไฟล์ credentials.json ตรงๆ แบบดั้งเดิมที่เสถียรที่สุด ---
@st.cache_resource
def init_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # อ่านจากไฟล์ credentials.json โดยตรง ไม่ต้องพึ่ง Secrets ให้ปวดหัว
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    
    client = gspread.authorize(creds)
    sheet_url = "https://docs.google.com/spreadsheets/d/1l1BNsov2CzmbSgdpoi_zSkcyPIgiOtBVHcuyRDYb3EA/edit?usp=sharing"
    sheet = client.open_by_url(sheet_url).worksheet("Sheet1")
    return sheet

try:
    sheet = init_sheet()
except Exception as e:
    st.error(f"⚠️ เชื่อมต่อ Google Sheets ไม่สำเร็จ: {e}")
    st.stop()

# --- ส่วน UI หน้าจอหลัก (ซ้ายกรอก | ขวาแสดงตาราง) ---
st.title("📅 ระบบบันทึกตารางนัดหมาย (Appointment Project 2026)")
st.markdown("---")

left_col, right_col = st.columns([1, 1.5], gap="large")

with left_col:
    st.subheader("📝 กรอกข้อมูลนัดหมาย")
    with st.form("appointment_form", clear_on_submit=True):
        date_val = st.date_input("📅 วันที่นัด", value=datetime.today())
        time_val = st.time_input("⏰ เวลานัด", value=datetime.strptime("09:00", "%H:%M").time())
        title_val = st.text_input("📝 รายการนัด / หัวข้อเรื่อง")
        by_val = st.text_input("👤 นัดโดย (ผู้ติดต่อ)")
        owner_val = st.text_input("⭐ เจ้าของนัด (ผู้รับผิดชอบ)")
        location_val = st.text_input("📍 สถานที่นัดหมาย")
        phone_val = st.text_input("📞 เบอร์โทรศัพท์ติดต่อ")
        note_val = st.text_area("💬 หมายเหตุเพิ่มเติม")

        submitted = st.form_submit_button("💾 บันทึกรายการลง Google Sheets", use_container_width=True)

    if submitted:
        if not title_val:
            st.warning("⚠️ กรุณากรอก 'รายการนัด / หัวข้อเรื่อง' ก่อนครับ!")
        else:
            try:
                date_str = date_val.strftime("%Y-%m-%d")
                time_str = time_val.strftime("%H:%M")
                row_data = [date_str, time_str, title_val, by_val, owner_val, location_val, phone_val, note_val]
                sheet.append_row(row_data)
                st.success("🎉 บันทึกข้อมูลสำเร็จ!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ เกิดข้อผิดพลาด: {e}")

with right_col:
    st.subheader("📋 รายการนัดหมายทั้งหมดในระบบ")
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("ยังไม่มีข้อมูลนัดหมายในระบบครับ")
    except Exception as e:
        st.warning(f"ยังไม่สามารถดึงข้อมูลตารางมาแสดงได้: {e}")eader("📋 รายการนัดหมายทั้งหมดในระบบ")
    try:
        data = sheet.get_all_records()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=500)
        else:
            st.info("ยังไม่มีข้อมูลนัดหมายในระบบครับ")
    except Exception as e:
        st.warning(f"ยังไม่สามารถดึงข้อมูลตารางมาแสดงได้: {e}")