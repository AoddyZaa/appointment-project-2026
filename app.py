from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

# --- ตั้งค่าหน้าจอเว็บ ---
st.set_page_config(
    page_title="Appointment Project 2026", page_icon="📅", layout="wide"
)

# --- ฟังก์ชันเชื่อมต่อ Google Sheets และ Google Calendar ---


@st.cache_resource
def init_connections():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
      "https://www.googleapis.com/auth/calendar",
  ]
  creds = ServiceAccountCredentials.from_json_keyfile_name(
      "credentials.json", scope
  )
  client = gspread.authorize(creds)
  return client, creds


try:
  client, creds = init_connections()
  # เปิดไฟล์ Google Sheets ชื่อ "AppointmentDB"
  sheet = client.open("AppointmentDB").worksheet("Sheet1")
except Exception as e:
  st.error(
      f"⚠️ เชื่อมต่อ Google ไม่สำเร็จ: กรุณาตรวจสอบชื่อไฟล์ Sheets หรือ"
      f" credentials.json ว่าถูกต้องไหม ({e})"
  )
  st.stop()

# --- ส่วนหัวโปรแกรม ---
st.title("📅 ระบบบันทึกตารางนัดหมาย (Appointment Project 2026)")
st.write(
    "กรอกข้อมูลด้านล่าง ระบบจะบันทึกลง Google Sheets และ **ยิงเข้า Google"
    " Calendar พร้อมตั้งเตือนอัตโนมัติ** ให้ทันที!"
)
st.markdown("---")

# --- ฟอร์มกรอกข้อมูลนัดหมาย ---
with st.form("appointment_form", clear_on_submit=True):
  col1, col2 = st.columns(2)

  with col1:
    date_val = st.date_input("📅 วันที่นัด", value=datetime.today())
    time_val = st.time_input("⏰ เวลานัด", value=datetime.strptime("09:00", "%H:%M").time())
    title_val = st.text_input("📝 รายการนัด / หัวข้อเรื่อง")
    by_val = st.text_input("👤 นัดโดย (ผู้ติดต่อ)")

  with col2:
    owner_val = st.text_input("⭐ เจ้าของนัด (ผู้รับผิดชอบ)")
    location_val = st.text_input("📍 สถานที่นัดหมาย")
    phone_val = st.text_input("📞 เบอร์โทรศัพท์ติดต่อ")
    note_val = st.text_area("💬 หมายเหตุเพิ่มเติม")

  submitted = st.form_submit_button(
      "💾 บันทึกรายการ และส่งเข้า Google Calendar อัตโนมัติ"
  )

# --- เมื่อกดปุ่มบันทึก ---
if submitted:
  if not title_val:
    st.warning("⚠️ กรุณากรอก 'รายการนัด / หัวข้อเรื่อง' ก่อนบันทึกครับท่านลุงอ๊อด!")
  else:
    try:
      # 1. แปลงรูปแบบวันที่และเวลา
      date_str = date_val.strftime("%Y-%m-%d")
      time_str = time_val.strftime("%H:%M")

      # 2. บันทึกลง Google Sheets
      row_data = [
          date_str,
          time_str,
          title_val,
          by_val,
          owner_val,
          location_val,
          phone_val,
          note_val,
      ]
      sheet.append_row(row_data)

      # 3. ยิงเข้า Google Calendar อัตโนมัติ พร้อมตั้งเตือน 3 เวลา
      from googleapiclient.discovery import build

      # สร้าง Service สำหรับ Calendar โดยใช้ Credentials เดียวกัน
      calendar_service = build("calendar", "v3", credentials=creds)

      # กำหนดเวลาเริ่มต้นและสิ้นสุด (ให้นัดมีความยาว 1 ชั่วโมง)
      start_datetime = f"{date_str}T{time_str}:00"
      # คำนวณเวลาสิ้นสุด (บวกไป 1 ชม.)
      from datetime import timedelta

      end_time_obj = (
          datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
          + timedelta(hours=1)
      )
      end_datetime = end_time_obj.strftime("%Y-%m-%dT%H:%M:00")

      event_body = {
          "summary": f"นัดหมาย: {title_val}",
          "location": location_val,
          "description": (
              f"ผู้ติดต่อ: {by_val}\nเจ้าของนัด: {owner_val}\nเบอร์โทร:"
              f" {phone_val}\nหมายเหตุ: {note_val}"
          ),
          "start": {"dateTime": start_datetime, "timeZone": "Asia/Bangkok"},
          "end": {"dateTime": end_datetime, "timeZone": "Asia/Bangkok"},
          "reminders": {
              "useDefault": False,
              "overrides": [
                  {"method": "popup", "minutes": 1440},  # เตือนล่วงหน้า 1 วัน
                  {"method": "popup", "minutes": 120},  # เตือนล่วงหน้า 2 ชั่วโมง
                  {"method": "popup", "minutes": 30},  # เตือนล่วงหน้า 30 นาที
              ],
          },
      }

      # ส่งคำขอสร้าง Event ไปยังปฏิทินหลัก ('primary')
      calendar_service.events().insert(
          calendarId="primary", body=event_body
      ).execute()

      st.success(
          "🎉 บันทึกข้อมูลลง Google Sheets และส่งเข้า Google Calendar"
          " พร้อมตั้งเตือนอัตโนมัติสำเร็จเรียบร้อยแล้วครับ!"
      )

    except Exception as e:
      st.error(
          f"❌ เกิดข้อผิดพลาดระหว่างบันทึกข้อมูล: {e} (โปรดตรวจสอบอีเมล"
          " Service Account ว่าได้แชร์สิทธิ์เข้าปฏิทินหรือยัง)"
      )

# --- แสดงตารางประวัติการนัดหมายทั้งหมด ---
st.markdown("---")
st.subheader("📋 รายการนัดหมายทั้งหมดในระบบ")
try:
  data = sheet.get_all_records()
  if data:
    import pandas as pd

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
  else:
    st.info("ยังไม่มีข้อมูลนัดหมายในระบบ ลองกรอกและบันทึกรายการแรกกันเลยครับ!")
except Exception as e:
  st.warning(f"ยังไม่สามารถดึงข้อมูลตารางมาแสดงได้: {e}")