import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

# --- ตั้งค่าหน้าจอแบบกว้างเต็มตา ---
st.set_page_config(page_title="ระบบบันทึกและจัดการนัดหมาย", layout="wide")

# --- 1. ตั้งค่าการเชื่อมต่อ Google API ผ่าน st.secrets ---
def get_sheets_connection():
    try:
        creds_dict = dict(st.secrets["gsheets"])
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/calendar"
            ]
        )
        client = gspread.authorize(creds)
        return client, creds
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Credentials: {e}")
        return None, None

# --- 2. ฟังก์ชันเพิ่มนัดหมายลง Google Calendar (เตือน 3 เวลา) ---
def add_event_to_calendar(creds, title, date_str, time_str, description=""):
    try:
        service = build('calendar', 'v3', credentials=creds)
        start_datetime = f"{date_str}T{time_str}:00"
        
        event = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start_datetime, 'timeZone': 'Asia/Bangkok'},
            'end': {'dateTime': start_datetime, 'timeZone': 'Asia/Bangkok'},
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 60},
                ],
            },
        }
        service.events().insert(calendarId='primary', body=event).execute()
        return True
    except Exception as e:
        st.error(f"Calendar Error: {e}")
        return False

# --- 3. ส่วนหัวข้อเว็บแอป ---
st.title("📅 ระบบบันทึกและจัดการนัดหมาย")
st.write("เชื่อมต่อ Google Sheets & Google Calendar แบบเรียลไทม์ (ซ้ายฟอร์มกรอก | ขวาตารางจัดการ)")

client, creds = get_sheets_connection()

if client:
    try:
        spreadsheet = client.open("AppointmentDB")
        sheet = spreadsheet.worksheet("Sheet1") 
        rows = sheet.get_all_values() 
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            # เก็บ Row index จริงใน Google Sheets (แถวที่ 2 เริ่มต้นที่ index 2 ของ gspread)
            df['Row_Index'] = range(2, len(rows) + 1)
        else:
            df = pd.DataFrame()
    except Exception as e:
        sheet = None
        df = pd.DataFrame()
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลชีท: {e}")

    # --- 4. แบ่งหน้าจอเป็น 2 ฝั่ง ซ้าย / ขวา ---
    col_left, col_right = st.columns([1, 1.3])

    with col_left:
        with st.form("appointment_form"):
            st.subheader("📌 บันทึกนัดหมายใหม่")
            date_input = st.text_input("วันที่นัด (YYYY-MM-DD)", value="2026-08-24")
            time_input = st.selectbox("เวลานัด", ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"])
            title_input = st.text_input("รายการนัด", placeholder="เช่น ประชุมงาน, หาหมอ")
            organizer_input = st.text_input("นัดโดย", placeholder="ชื่อผู้ทำรายการนัด")
            owner_input = st.text_input("เจ้าของนัด", placeholder="ชื่อเจ้าของนัดหมาย")
            location_input = st.text_input("สถานที่", placeholder="สถานที่นัดหมาย")
            phone_input = st.text_input("เบอร์โทร", placeholder="เบอร์โทรติดต่อ")
            note_input = st.text_area("หมายเหตุ", placeholder="รายละเอียดเพิ่มเติม...")
            
            # ปุ่มบันทึก
            submit_button = st.form_submit_button(label="💾 บันทึกข้อมูลนัดหมาย")

            if submit_button:
                if title_input and organizer_input:
                    try:
                        if sheet:
                            sheet.append_row([date_input, time_input, title_input, organizer_input, owner_input, location_input, phone_input, note_input])
                        
                        formatted_date = date_input.replace("/", "-")
                        cal_success = add_event_to_calendar(creds, title_input, formatted_date, time_input, f"สถานที่: {location_input} | นัดโดย: {organizer_input} | โทร: {phone_input}")
                        
                        if cal_success:
                            st.success("🎉 บันทึกลง Google Sheets และตั้งเตือนใน Google Calendar เรียบร้อยแล้วครับ!")
                            st.rerun()
                        else:
                            st.warning("⚠️ บันทึกลง Google Sheets แล้ว แต่ Calendar มีปัญหา")
                            
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการบันทึก: {e}")
                else:
                    st.warning("⚠️ กรุณากรอกข้อมูล 'รายการนัด' และ 'นัดโดย' ให้ครบถ้วนครับ")

    with col_right:
        # หัวข้อตาราง พร้อมปุ่มรีเฟรชข้อมูล
        col_title, col_btn = st.columns([3, 1])
        with col_title:
            st.subheader("📋 รายการนัดหมายทั้งหมด")
        with col_btn:
            if st.button("🔄 รีเฟรชข้อมูล"):
                st.rerun()

        if not df.empty:
            # แสดงตารางแบบขยายเต็มจอได้ (มีปุ่ม Expand ขวาบนของตาราง)
            st.dataframe(df.drop(columns=['Row_Index']), use_container_width=True, height=350)
            
            # --- ส่วนจัดการลบรายการ ---
            st.markdown("---")
            st.subheader("🗑️ ลบรายการนัดหมาย")
            
            # สร้างตัวเลือกให้เลือกรายการที่จะลบจากหัวข้อรายการนัด
            delete_options = {f"{row['วันที่นัด']} | {row['เวลานัด']} | {row['รายการนัด']} (แถวที่ {row['Row_Index']})": row['Row_Index'] for _, row in df.iterrows()}
            
            selected_to_delete = st.selectbox("เลือกรายการที่ต้องการลบ", options=list(delete_options.keys()))
            
            if st.button("❌ ลบรายการที่เลือก"):
                row_to_delete = delete_options[selected_to_delete]
                try:
                    sheet.delete_rows(row_to_delete)
                    st.success(f"🗑️ ลบข้อมูลเรียบร้อยแล้วครับ!")
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการลบ: {e}")
        else:
            st.info("📌 ยังไม่มีข้อมูลในระบบ กรุณากรอกข้อมูลทางด้านซ้ายครับ")
else:
    st.error("❌ ไม่สามารถเชื่อมต่อกับ Google API ได้ กรุณาตรวจสอบไฟล์ secrets.toml")