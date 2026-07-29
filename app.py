import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บแบบ Wide Mode
st.set_page_config(
    page_title="ระบบบันทึกและแจ้งเตือนนัดหมาย",
    page_icon="📅",
    layout="wide"
)

# 🎨 ธีมสีสดใส สไตล์โมเดิร์น
st.markdown("""
    <style>
    .main {
        background-color: #F8F9FA;
    }
    .stButton>button {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF5252 0%, #FF7043 100%);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    h1, h2, h3 {
        color: #2C3E50;
        font-family: 'Prompt', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# ================= 📝 ฟอร์มกรอกข้อมูลอยู่ใน Sidebar (กดซ่อน/ขยายด้วยปุ่มก้างปลาได้) =================
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
            st.success(f"🎉 บันทึก '{title}' เรียบร้อย!")
        else:
            st.error("⚠️ กรุณากรอกรายการนัดด้วยครับ!")

# ================= 📋 หน้าจอหลัก: แสดงตารางรายการนัดหมายทั้งหมด =================
st.markdown("<h1>📅 ระบบบันทึกและจัดการนัดหมาย</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #7F8C8D; font-size: 16px;'>แสดงรายการนัดหมายทั้งหมดในระบบ (สามารถกดพับเมนูด้านซ้ายเพื่อขยายตารางให้กว้างขึ้นได้)</p>", unsafe_allow_html=True)
st.write("---")

# จำลองข้อมูลตารางตามหัวข้อใน Google Sheets ของท่านลุงอ๊อด
sample_data = [
    {
        "วันที่นัด": "2026-07-30", 
        "เวลานัด": "10:00", 
        "รายการนัด": "ประชุมวางแผนโปรเจกต์", 
        "นัดโดย": "คุณอ๊อด", 
        "เจ้าของนัด": "ทีมงาน", 
        "สถานที่": "ห้องประชุม A", 
        "เบอร์โทร": "081-234-5678", 
        "หมายเหตุ": "เตรียมเอกสารไปด้วย"
    },
    {
        "วันที่นัด": "2026-08-01", 
        "เวลานัด": "14:30", 
        "รายการนัด": "จ่ายค่าน้ำค่าไฟ", 
        "นัดโดย": "คุณอ๊อด", 
        "เจ้าของนัด": "ส่วนตัว", 
        "สถานที่": "การไฟฟ้า", 
        "เบอร์โทร": "089-876-5432", 
        "หมายเหตุ": "กำหนดจ่ายวันสุดท้าย"
    }
]

df = pd.DataFrame(sample_data)

# แสดงตารางแบบเต็มจอ
st.dataframe(df, use_container_width=True, height=500)

# ปุ่มจัดการตาราง
col_btn1, col_btn2, col_spacer = st.columns([1, 1, 3])
with col_btn1:
    if st.button("🔄 รีเฟรชข้อมูล"):
        st.rerun()
with col_btn2:
    if st.button("🗑️ ลบรายการ"):
        st.info("ฟังก์ชันลบรายการพร้อมใช้งาน")

# ส่วนท้าย
st.write("---")
st.markdown("<p style='text-align: center; color: #BDC3C7;'>Developed with ❤️ for Khun Adul | Appointment Project 2026</p>", unsafe_allow_html=True)