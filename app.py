import streamlit as st
import pandas as pd
from datetime import datetime

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
            # เพิ่มข้อมูลใหม่เข้าไปใน session_state ทันที
            new_entry = {
                "เลือก": False,
                "วันที่นัด_Eng": app_date.strftime('%Y-%m-%d'),
                "เวลานัด": app_time.strftime('%H:%M'), 
                "รายการนัด": title, 
                "นัดโดย": booked_by if booked_by else "-", 
                "เจ้าของนัด": owner if owner else "-", 
                "สถานที่": location if location else "-", 
                "เบอร์โทร": phone if phone else "-", 
                "หมายเหตุ": note if note else "-"
            }
            if 'appointments_data' not in st.session_state:
                st.session_state.appointments_data = []
            st.session_state.appointments_data.append(new_entry)
            
            formatted_date = format_thai_date(app_date)
            st.success(f"🎉 บันทึก '{title}' (วันที่ {formatted_date}) เรียบร้อย!")
            st.rerun()
        else:
            st.error("⚠️ กรุณากรอกรายการนัดด้วยครับ!")

# ================= 📋 หน้าจอหลัก: แสดงตารางรายการนัดหมาย =================
st.markdown("<h1>📅 ระบบบันทึกและจัดการนัดหมาย</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #7F8C8D; font-size: 16px;'>แสดงรายการนัดหมาย (รูปแบบวันที่ไทย) เรียงตามวันและเวลา พร้อมช่องเลือกจัดการ</p>", unsafe_allow_html=True)
st.write("---")

# กำหนด Session State ตั้งต้น
if 'appointments_data' not in st.session_state:
    st.session_state.appointments_data = [
        {
            "เลือก": False, "วันที่นัด_Eng": "2026-06-01", "เวลานัด": "09:00", 
            "รายการนัด": "นัดเก่าที่ผ่านมาแล้ว", "นัดโดย": "คุณอ๊อด", "เจ้าของนัด": "ทีมงาน", "สถานที่": "ที่เก่า", "เบอร์โทร": "081-111-1111", "หมายเหตุ": "-"
        },
        {
            "เลือก": False, "วันที่นัด_Eng": "2026-08-01", "เวลานัด": "14:30", 
            "รายการนัด": "จ่ายค่าน้ำค่าไฟ", "นัดโดย": "คุณอ๊อด", "เจ้าของนัด": "ส่วนตัว", "สถานที่": "การไฟฟ้า", "เบอร์โทร": "089-876-5432", "หมายเหตุ": "กำหนดจ่ายวันสุดท้าย"
        },
        {
            "เลือก": False, "วันที่นัด_Eng": "2026-07-30", "เวลานัด": "10:00", 
            "รายการนัด": "ประชุมวางแผนโปรเจกต์", "นัดโดย": "คุณอ๊อด", "เจ้าofนัด": "ทีมงาน", "สถานที่": "ห้องประชุม A", "เบอร์โทร": "081-234-5678", "หมายเหตุ": "เตรียมเอกสารไปด้วย"
        }
    ]

if len(st.session_state.appointments_data) > 0:
    df = pd.DataFrame(st.session_state.appointments_data)
    
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
            # หา index ในหน้าจอที่ถูกติ๊กเลือก
            selected_rows = edited_df[edited_df["เลือก"] == True]
            
            if not selected_rows.empty:
                # ดึงรายการที่ *ไม่ได้ถูกติ๊ก* เก็บไว้ใน session_state โดยเทียบจากข้อมูลเดิม
                indices_to_delete = selected_rows.index.tolist()
                # แปลงกลับเป็นแถวใน df หลัก
                original_rows_to_delete = df.iloc[indices_to_delete]
                
                # กรองเอาเฉพาะข้อมูลที่ไม่ตรงกับแถวที่จะลบออก
                updated_list = []
                for idx, item in enumerate(st.session_state.appointments_data):
                    # เช็คเทียบความเหมือนจากค่าในดิบ
                    is_match = False
                    for _, del_row in original_rows_to_delete.iterrows():
                        if (item['วันที่นัด_Eng'] == del_row['วันที่นัด_Eng'] and 
                            item['เวลานัด'] == del_row['เวลานัด'] and 
                            item['รายการนัด'] == del_row['รายการนัด']):
                            is_match = True
                            break
                    if not is_match:
                        updated_list.append(item)
                
                st.session_state.appointments_data = updated_list
                st.success(f"🗑️ ลบออกเรียบร้อยแล้ว {len(indices_to_delete)} รายการ")
                st.rerun()
            else:
                st.warning("⚠️ กรุณาติ๊กช่อง 'เลือก' หน้าแถวที่ต้องการลบก่อนครับ")

    with col_btn2:
        if st.button("🔄 รีเฟรชข้อมูล"):
            st.rerun()
else:
    st.info("📌 ไม่มีรายการนัดหมายในระบบตอนนี้ครับ สามารถกรอกเพิ่มทางซ้ายได้เลยครับ")

# ส่วนท้าย
st.write("---")
st.markdown("<p style='text-align: center; color: #B7950B;'>Developed with 💛 for Khun Adul | Appointment Project 2026</p>", unsafe_allow_html=True)