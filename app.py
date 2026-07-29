import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="ระบบบันทึกและแจ้งเตือนนัดหมาย", page_icon="📅", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #FFFDF9; }
    .stButton>button {
        background: linear-gradient(135deg, #F39C12 0%, #F1C40F 100%);
        color: #2C3E50; font-weight: bold; border-radius: 12px; padding: 0.6rem 1.2rem; border: none;
    }
    h1, h2, h3 { color: #B7950B; font-family: 'Prompt', sans-serif; }
    [data-testid="stSidebar"] { background-color: #FEF9E7; }
    </style>
""", unsafe_allow_html=True)

thai_months = {1: "ม.ค.", 2: "ก.พ.", 3: "มี.ค.", 4: "เม.ย.", 5: "พ.ค.", 6: "มิ.ย.", 7: "ก.ค.", 8: "ส.ค.", 9: "ก.ย.", 10: "ต.ค.", 11: "พ.ย.", 12: "ธ.ค."}

def format_thai_date(date_obj):
    if isinstance(date_obj, str):
        date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
    return f"{date_obj.day} {thai_months[date_obj.month]} {date_obj.year + 543}"

# เชื่อมต่อผ่าน st.secrets
def get_google_sheet_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["gspread"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(crez := creds)
        
        sheet = client.open("AppointmentDB").sheet1
        data = sheet.get_all_records()
        return sheet, pd.DataFrame(data)
    except Exception as e:
        st.error(f"⚠️ ไม่สามารถเชื่อมต่อ Google Sheets ได้: {e}")
        return None, pd.DataFrame()

sheet_connection, df_remote = get_google_sheet_data()

st.sidebar.markdown("<h2>📌 บันทึกนัดหมายใหม่</h2>", unsafe_allow_html=True)
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
                st.sidebar.success(f"🎉 บันทึก '{title}' เรียบร้อย!")
                st.rerun()
        else:
            st.sidebar.error("⚠️ กรุณากรอกรายการนัดด้วยครับ!")

st.markdown("<h1>📅 ระบบบันทึกและจัดการนัดหมาย</h1>", unsafe_allow_html=True)
st.write("---")

if not df_remote.empty and 'วันที่นัด_Eng' in df_remote.columns:
    df = df_remote.copy()
    df['เลือก'] = False
    df['tmp_date'] = pd.to_datetime(df['วันที่นัด_Eng'])
    df = df.sort_values(by=['tmp_date', 'เวลานัด']).reset_index(drop=True)
    df['วันที่นัด'] = df['tmp_date'].apply(format_thai_date)

    display_df = df[['เลือก', 'วันที่นัด', 'เวลานัด', 'รายการนัด', 'นัดโดย', 'เจ้าของนัด', 'สถานที่', 'เบอร์โทร', 'หมายเหตุ']].copy()

    edited_df = st.data_editor(display_df, use_container_width=True, hide_index=True, num_rows="fixed",
        column_config={"เลือก": st.column_config.CheckboxColumn("☑️ เลือก", default=False)}, height=400)

    if st.button("🗑️ ลบรายการที่เลือก"):
        selected_rows = edited_df[edited_df["เลือก"] == True]
        if not selected_rows.empty and sheet_connection is not None:
            all_records = sheet_connection.get_all_records()
            rows_to_delete_indices = []
            for idx, record in enumerate(all_records):
                for _, del_row in selected_rows.iterrows():
                    if (str(record.get('วันที่นัด_Eng')) == str(del_row['วันที่นัด_Eng']) and 
                        str(record.get('เวลานัด')) == str(del_row['เวลานัด']) and 
                        str(record.get('รายการนัด')) == str(del_row['รายการนัด'])):
                        rows_to_delete_indices.append(idx + 2)
                        break
            for r_idx in sorted(rows_to_delete_indices, reverse=True):
                sheet_connection.delete_rows(r_idx)
            st.success("🗑️ ลบข้อมูลเรียบร้อย!")
            st.rerun()
else:
    st.info("📌 กำลังดึงข้อมูลจาก Google Sheets หรือยังไม่มีข้อมูลในระบบครับ")