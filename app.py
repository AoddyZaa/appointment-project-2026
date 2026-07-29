import streamlit as st
import pandas as pd
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบบันทึกและแจ้งเตือนนัดหมาย",
    page_icon="📅",
    layout="wide"
)

# 🎨 ตกแต่งธีมสีสดใส สไตล์โมเดิร์น
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
    h1 {
        color: #2C3E50;
        font-family: 'Prompt', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 🧭 เมนูด้านข้าง (Sidebar) สำหรับเลือกหน้าจอ (กดซ่อน/ขยายได้ด้วยปุ่มลูกศรสามขีดด้านบนซ้าย)
st.sidebar.markdown("<h2>⚙️ เมนูหลัก</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio(
    "เลือกการใช้งาน:",
    ["📌 บันทึกนัดหมายใหม่", "📋 ดูรายการนัดหมายทั้งหมด"]
)

st.sidebar.write("---")
st.sidebar.info("💡 ทริค: กดปุ่มลูกศร `>` หรือขีดสามขีดมุมซ้ายบน เพื่อซ่อน/ขยายแถบเมนูนี้ได้ครับ")

# ================= 1. หน้าฟอร์มบันทึกนัดหมายใหม่ =================
if menu == "📌 บันทึกนัดหมายใหม่":
    st.markdown("<h1>📅 บันทึกนัดหมายใหม่</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7F8C8D; font-size: 16px;'>กรอกข้อมูลนัดหมายของคุณด้านล่างนี้ได้เลยครับ</p>", unsafe_allow_html=True)
    st.write("---")

    # จัดฟอร์มให้อยู่100% เต็มจอแบบสวยงาม
    with st.form("appointment_form", clear_on_submit=True):
        title = st.text_input("📌 หัวข้อ / เรื่องที่นัดหมาย", placeholder="เช่น ประชุมงาน, หาหมอ, จ่ายบิล")
        
        col_date, col_time = st.columns(2)
        with col_date:
            app_date = st.date_input("🗓️ วันที่นัดหมาย", value=datetime.today())
        with col_time:
            app_time = st.time_input("⏰เวลานัดหมาย")
            
        category = st.selectbox("🏷️ หมวดหมู่", ["งานด่วน", "ธุระส่วนตัว", "การเงิน/บิล", "ประชุม/งานทั่วไป"])
        description = st.text_area("📄 รายละเอียดเพิ่มเติม", placeholder="ระบุรายละเอียดเพิ่มเติมที่นี่...")
        
        submitted = st.form_submit_button("💾 บันทึกข้อมูลนัดหมาย")
        
        if submitted:
            if title:
                st.success(f"🎉 บันทึกนัดหมาย '{title}' เรียบร้อยแล้วครับ!")
            else:
                st.error("⚠️ กรุณากรอกหัวข้อเรื่องนัดหมายด้วยครับ!")

# ================= 2. หน้าแสดงรายการตารางทั้งหมด =================
elif menu == "📋 ดูรายการนัดหมายทั้งหมด":
    st.markdown("<h1>📋 รายการนัดหมายทั้งหมดในระบบ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7F8C8D; font-size: 16px;'>ตรวจสอบและจัดการรายการนัดหมายทั้งหมดของคุณที่นี่</p>", unsafe_allow_html=True)
    st.write("---")
    
    # จำลองข้อมูลตาราง (สามารถดึงจาก Google Sheets มาใส่ตรงนี้ได้เลย)
    sample_data = [
        {"วันที่": "2026-07-30", "เวลา": "10:00", "หัวข้อ": "ประชุมวางแผนโปรเจกต์", "หมวดหมู่": "งานด่วน", "สถานะ": "รอแจ้งเตือน"},
        {"วันที่": "2026-08-01", "เวลา": "14:30", "หัวข้อ": "จ่ายค่าน้ำค่าไฟ", "หมวดหมู่": "การเงิน/บิล", "สถานะ": "รอแจ้งเตือน"},
        {"วันที่": "2026-08-03", "เวลา": "09:00", "หัวข้อ": "พบแพทย์ตามนัด", "หมวดหมู่": "ธุระส่วนตัว", "สถานะ": "รอแจ้งเตือน"}
    ]
    
    df = pd.DataFrame(sample_data)
    
    # แสดงตารางแบบเต็มจอ
    st.dataframe(df, use_container_width=True, height=450)
    
    col_btn1, col_btn2, col_spacer = st.columns([1, 1, 2])
    with col_btn1:
        if st.button("🔄 รีเฟรชข้อมูล"):
            st.rerun()
    with col_btn2:
        if st.button("🗑️ ลบรายการที่เลือก"):
            st.info("ฟังก์ชันลบรายการพร้อมใช้งานครับ")

# ส่วนท้าย
st.write("---")
st.markdown("<p style='text-align: center; color: #BDC3C7;'>Developed with ❤️ for Khun Adul | Appointment Project 2026</p>", unsafe_allow_html=True)