import streamlit as st
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime

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

# --- 3. ระบบแปลงเดือนไทย <-> ตัวเลข ---
thai_months = {
    "ม.ค.": 1, "ก.พ.": 2, "มี.ค.": 3, "เม.ย.": 4, "พ.ค.": 5, "มิ.ย.": 6,
    "ก.ค.": 7, "ส.ค.": 8, "ก.ย.": 9, "ต.ค.": 10, "พ.ย.": 11, "ธ.ค.": 12
}

thai_months_inverse = {v: k for k, v in thai_months.items()}

def convert_to_thai_date(date_str):
    try:
        dt = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
        day = dt.day
        month = thai_months_inverse.get(dt.month, "ม.ค.")
        year = dt.year + 543
        return f"{day} {month} {year}"
    except:
        return date_str

# --- 4. ส่วนหัวข้อเว็บแอปหลัก ---
st.title("📅 ระบบบันทึกและจัดการนัดหมาย")
st.write("เชื่อมต่อ Google Sheets & Google Calendar (แก้แค่วันที่ในตารางได้ตามใจชอบ)")

client, creds = get_sheets_connection()

if client:
    try:
        spreadsheet = client.open("AppointmentDB")
        sheet = spreadsheet.worksheet("Sheet1") 
        rows = sheet.get_all_values() 
        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            df['Row_Index'] = [int(x) for x in range(2, len(rows) + 1)]
        else:
            df = pd.DataFrame()
    except Exception as e:
        sheet = None
        df = pd.DataFrame()
        st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลชีท: {e}")

    # --- 5. เมนูด้านซ้าย (Sidebar) ฟอร์มบันทึกรายการใหม่ ---
    with st.sidebar:
        with st.form("appointment_form"):
            st.subheader("📌 บันทึกนัดหมายใหม่")
            
            thai_months_list = [
                "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
            ]
            now_dt = datetime.now()
            current_thai_year = now_dt.year + 543
            
            col_d, col_m, col_y = st.columns([1, 1.5, 1.2])
            with col_d:
                selected_day = st.selectbox("วัน", list(range(1, 32)), index=now_dt.day - 1)
            with col_m:
                selected_month_name = st.selectbox("เดือน", thai_months_list, index=now_dt.month - 1)
                selected_month_num = thai_months_list.index(selected_month_name) + 1
            with col_y:
                selected_thai_year = st.number_input("ปี พ.ศ.", min_value=2500, max_value=2600, value=current_thai_year, step=1)
            
            eng_year = selected_thai_year - 543
            date_input = f"{eng_year:04d}-{selected_month_num:02d}-{selected_day:02d}"
            
            st.caption(f"🗓️ วันที่เลือก: **{selected_day} {selected_month_name} {selected_thai_year}**")

            time_input = st.selectbox("เวลานัด", ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00"])
            
            title_input = st.text_input("รายการนัด", placeholder="เช่น ประชุมงาน, หาหมอ")
            organizer_input = st.text_input("นัดโดย", placeholder="ชื่อผู้ทำรายการนัด")
            owner_input = st.text_input("เจ้าของนัด", placeholder="ชื่อเจ้าของนัดหมาย")
            location_input = st.text_input("สถานที่", placeholder="สถานที่นัดหมาย")
            phone_input = st.text_input("เบอร์โทร", placeholder="เบอร์โทรติดต่อ")
            note_input = st.text_area("หมายเหตุ", placeholder="รายละเอียดเพิ่มเติม...")
            
            submit_button = st.form_submit_button(label="💾 บันทึกข้อมูลนัดหมาย", use_container_width=True)

            if submit_button:
                if title_input and organizer_input:
                    try:
                        if sheet:
                            sheet.append_row([date_input, time_input, title_input, organizer_input, owner_input, location_input, phone_input, note_input])
                        
                        cal_success = add_event_to_calendar(creds, title_input, date_input, time_input, f"สถานที่: {location_input} | นัดโดย: {organizer_input} | โทร: {phone_input}")
                        
                        if cal_success:
                            st.success("🎉 บันทึกสำเร็จ!")
                            st.rerun()
                        else:
                            st.warning("⚠️ บันทึกลง Sheets แล้ว แต่ Calendar มีปัญหา")
                            
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")
                else:
                    st.warning("⚠️ กรุณากรอก 'รายการนัด' และ 'นัดโดย'")

    # --- 6. พื้นที่แสดงตารางฝั่งขวา ---
    col_title, col_btn_save_edit, col_btn_del, col_btn_ref = st.columns([1.5, 1.2, 1, 1])
    with col_title:
        st.subheader("📋 รายการนัดหมาย")
    with col_btn_save_edit:
        save_edit_clicked = st.button("💾 บันทึกแก้ไข")
    with col_btn_del:
        delete_clicked = st.button("🗑️ ลบที่เลือก")
    with col_btn_ref:
        refresh_clicked = st.button("🔄 รีเฟรช")

    if refresh_clicked:
        st.rerun()

    if not df.empty:
        display_df = df.copy()
        display_df['วันที่นัด'] = display_df['วันที่นัด'].apply(convert_to_thai_date)
        display_df.insert(0, "เลือก", False)
        
        edited_df = st.data_editor(
            display_df.drop(columns=['Row_Index']),
            use_container_width=True,
            hide_index=True,
            key="grid_table"
        )
        
        # --- จัดการบันทึกการแก้ไข (แปลงวันที่ไทยที่แก้ ให้เป็น ค.ศ. อัตโนมัติ) ---
        if save_edit_clicked:
            try:
                updated_count = 0
                for idx, row in edited_df.iterrows():
                    real_row_idx = int(df.loc[idx, 'Row_Index'])
                    orig_row = df.iloc[idx] # ข้อมูลเดิมใน ค.ศ. (เช่น 2026-09-11)
                    
                    user_date_text = str(row["วันที่นัด"]).strip() # ข้อความที่ผู้ใช้แก้ เช่น "13 ก.ย. 2569"
                    
                    # แกะข้อความวันที่ที่ผู้ใช้แก้ เพื่อแปลงกลับเป็น YYYY-MM-DD ให้ Google Sheets
                    target_date = orig_row['วันที่นัด'] # ค่าเริ่มต้นเอาของเดิมไว้ก่อน
                    try:
                        parts = user_date_text.split()
                        if len(parts) >= 3:
                            new_day = int(parts[0])
                            new_month_str = parts[1]
                            new_year_thai = int(parts[2])
                            
                            new_month_num = thai_months.get(new_month_str, 9)
                            new_year_eng = new_year_thai - 543
                            
                            target_date = f"{new_year_eng:04d}-{new_month_num:02d}-{new_day:02d}"
                    except:
                        pass # ถ้าแกะไม่ได้ให้ใช้ค่าเดิมป้องกันพัง
                    
                    new_time = row["เวลานัด"]
                    new_title = row["รายการนัด"]
                    new_organizer = row["นัดโดย"]
                    new_owner = row["เจ้าจากนัด" if "เจ้าจากนัด" in row else "เจ้าของนัด"]
                    new_location = row["สถานที่"]
                    new_phone = row["เบอร์โทร"]
                    new_note = row["หมายเหตุ"]
                    
                    sheet.update(f"A{real_row_idx}:H{real_row_idx}", [[target_date, new_time, new_title, new_organizer, row["เจ้าของนัด"], new_location, new_phone, new_note]])
                    updated_count += 1
                
                if updated_count > 0:
                    st.success("💾 บันทึกการแก้ไขข้อมูลเรียบร้อยแล้วครับ!")
                    st.rerun()
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการบันทึกแก้ไข: {e}")

        if delete_clicked:
            rows_to_delete = []
            for idx, row in edited_df.iterrows():
                if row["เลือก"] == True:
                    real_row_idx = int(df.loc[idx, 'Row_Index'])
                    rows_to_delete.append(real_row_idx)
            
            if rows_to_delete:
                try:
                    for r_idx in sorted(rows_to_delete, reverse=True):
                        sheet.delete_rows(r_idx)
                    st.success("🗑️ ลบรายการที่เลือกเรียบร้อยแล้วครับ!")
                    st.rerun()
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการลบ: {e}")
            else:
                st.warning("⚠️ กรุณาติ๊กเครื่องหมายถูก (✔) หน้าแถวที่ต้องการลบก่อนกดปุ่มถังขยะครับ")
    else:
        st.info("📌 ยังไม่มีข้อมูลในระบบ สามารถกรอกข้อมูลใหม่จากฟอร์มด้านซ้ายได้เลยครับ")
else:
    st.error("❌ ไม่สามารถเชื่อมต่อกับ Google API ได้ กรุณาตรวจสอบไฟล์ secrets.toml")