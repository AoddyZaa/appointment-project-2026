import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ตั้งค่าหน้าเว็บแบบ Wide Mode
st.set_page_config(
    page_title="ระบบบันทึกและแจ้งเตือนนัดหมาย",
    page_icon="📅",
    layout="wide"
)

# 🎨 ธีมสีเหลืองทองสุดพรีเมียม สไตล์โมเดิร์น
st.markdown("""
    <style>
    .main {
        background-color: #FFFDF9;
    }
    .stButton>button {
        background: linear-gradient(135deg, #F39C12 0%, #F1C40F 100%);
        color: #2C3E50;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #D68910 0%, #F39C12 100%);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
        color: white;
    }
    h1, h2, h3 {
        color: #B7950B;
        font-family: 'Prompt', sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #FEF9E7;
    }
    </style>
""", unsafe_allow_html=True)

# 📅 ฟังก์ชันแปลงวันที่ ค.ศ. เป็น วันที่ไทย
thai_months = {
    1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.",
    7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."
}

def format_thai_date(date_obj):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
    day = date_obj.day
    month = thai_months[date_obj.month]
    thai_year = date_obj.year + 543
    return f"{day} {month} {thai_year}"

# ================= 🔗 ฟังก์ชันเชื่อมต่อ Google Sheets =================
def get_google_sheet_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gpex"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)
        
        # เปิดไฟล์ Google Sheet ชื่อ AppointmentDB (หรือปรับชื่อตามจริง)
        sheet = client.open("AppointmentDB").sheet1
        data = sheet.get_all_records()
        return sheet, pd.DataFrame(data)
    except Exception as e:
        # กรณีดึงไม่ได้ หรือยังไม่ได้ตั้งค่า Secrets ให้ใช้ข้อมูลจำลองสำรองไว้ก่อน
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
        return None, pd.DataFrame()

# โหลดข้อมูลจาก Google Sheet
sheet_connection, df_remote = get_google_sheet_data()

# ================= 📝 ฟอร์มกรอกข้อมูล (อยู่ใน Sidebar) =================
st.sidebar.markdown("<h2>📌 บันทึกนัดหมายใหม่</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: #7F8C8D; font-size: 14px;'>กรอกข้อมูลด้านซ้าย แล้วกดพับซ่อนเมนูก้างปลาเพื่อดูตารางเต็มจอได้ครับ</p>", unsafe_allow_html=True)
st.sidebar.write("---")

with st.sidebar.form("appointment_form", clear_on_submit=True):
    app_date = st.date_input("🗓️ วันที่นัด", value=datetime.today())
    app_time = st.time_input("⏰ เวลานัด")
    title = st.text_input("📝 รายการนัด", placeholder="เช่น ประชุมงาน, หาหมอ")
    booked_by = st.text_input("👤 นัดโดย", placeholder="ชื่อผู้ทำรายการนัด")
    owner = st.text_input("⭐ เจ้าของนัด", placeholder="ชื่อเจ้าของนัดหมาย")
    location = st.text_input("📍 สถานที่", placeholder="สถานที่นัดหมาย")
    phone = st.text_input("📞 เบอร์โทร", placeholder="เบอร์โทรติดต่อ")
    note = st.text_area("📄 หมายเหตุ", placeholder="รายละเอียดเพิ่มเติม...")
    
    submitted = st.form_submit_button("💾 บันทึกข้อมูลนัดหมาย")
    
    if submitted:
        if title:
            new_row = [
                app_date.strftime('%Y-%m-%d'),
                app_time.strftime('%H:%M'),
                title,
                booked_by if booked_by else "-",
                owner if owner else "-",
                location if location else "-",
                phone if phone else "-",
                note if note else "-"
            ]
            
            if sheet_connection is not None:
                sheet_connection.append_row(new_row)
                formatted_date = format_thai_date(app_date)
                st.sidebar.success(f"🎉 บันทึก '{title}' ลง Google Sheets เรียบร้อย!")
                st.rerun()
            else:
                st.sidebar.error("⚠️ ยังไม่ได้เชื่อมต่อไฟล์ Google Sheet จริง")
        else:
            st.sidebar.error("⚠️ กรุณากรอกรายการนัดด้วยครับ!")

# ================= 📋 หน้าจอหลัก: แสดงตารางรายการนัดหมาย =================
st.markdown("<h1>📅 ระบบบันทึกและจัดการนัดหมาย</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #7F8C8D; font-size: 16px;'>แสดงรายการนัดหมายจาก Google Sheets (รูปแบบวันที่ไทย) เรียงตามวันและเวลา พร้อมช่องเลือกจัดการ</p>", unsafe_allow_html=True)
st.write("---")

if not df_remote.empty and 'วันที่นัด_Eng' in df_remote.columns:
    df = df_remote.copy()
    df['เลือก'] = False
    
    # แปลงวันที่และเรียงลำดับ
    df['tmp_date'] = pd.to_datetime(df['วันที่นัด_Eng'])
    df = df.sort_values(by=['tmp_date', 'เวลานัด']).reset_index(drop=True)
    df['วันที่นัด'] = df['tmp_date'].apply(format_thai_date)

    display_df = df[['เลือก', 'วันที่นัด', 'เวลานัด', 'รายการนัด', 'นัดโดย', 'เจ้าของนัด', 'สถานที่', 'เบอร์โทร', 'หมายเหตุ']].copy()

    # แสดงตาราง
    edited_df = st.data_editor(
        display_df,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        column_config={
            "เลือก": st.column_config.CheckboxColumn(
                "☑️ เลือก",
                help="ติ๊กเลือกแถวที่ต้องการลบ",
                default=False,
            )
        },
        height=400
    )

    # ปุ่มจัดการลบข้อมูล
    col_btn1, col_btn2, col_spacer = st.columns([1, 1, 3])
    with col_btn1:
        if st.button("🗑️ ลบรายการที่เลือก"):
            selected_rows = edited_df[edited_df["เลือก"] == True]
            if not selected_rows.empty:
                indices_to_delete = selected_rows.index.tolist()
                original_rows_to_delete = df.iloc[indices_to_delete]
                
                # ลบแถวออกจาก Google Sheet (อิงตาม row index ในชีท โดยบวก 2 เพราะติด Header และเริ่มแถวที่ 2)
                if sheet_connection is not None:
                    # ดึงข้อมูลทั้งหมดใหม่เพื่อเทียบแถว
                    all_records = sheet_connection.get_all_records()
                    rows_to_delete_indices = []
                    
                    for idx, record in enumerate(all_records):
                        for _, del_row in original_rows_to_delete.iterrows():
                            if (str(record.get('วันที่นัด_Eng')) == str(del_row['วันที่นัด_Eng']) and 
                                str(record.get('เวลานัด')) == str(del_row['เวลานัด']) and 
                                str(record.get('รายการนัด')) == str(del_row['รายการนัด'])):
                                rows_to_delete_indices.append(idx + 2) # บวก 2 เพราะแถว 1 คือ Header
                                break
                    
                    # ลบจากล่างขึ้นบนเพื่อไม่ให้ index เคลื่อน
                    for r_idx in sorted(rows_to_delete_indices, reverse=True):
                        sheet_connection.delete_rows(r_idx)
                        
                    st.success(f"🗑️ ลบออกจาก Google Sheets เรียบร้อยแล้ว {len(indices_to_delete)} รายการ")
                    st.rerun()
            else:
                st.warning("⚠️ กรุณาติ๊กช่อง 'เลือก' หน้าแถวที่ต้องการลบก่อนครับ")

    with col_btn2:
        if st.button("🔄 รีเฟรชข้อมูล"):
            st.rerun()
else:
    st.info("📌 กำลังดึงข้อมูลจาก Google Sheets หรือยังไม่มีข้อมูลในระบบครับ")

# ส่วนท้าย
st.write("---")
st.markdown("<p style='text-align: center; color: #B7950B;'>Developed with 💛 for Khun Adul | Appointment Project 2026</p>", unsafe_allow_html=True)