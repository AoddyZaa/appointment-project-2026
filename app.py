from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.set_page_config(
    page_title="Appointment Project 2026",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #FFFDF0;
    }
    .stButton>button {
        background-color: #FFC107;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #FFB300;
        color: #000000;
    }
    h1, h2, h3 {
        color: #D38312;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # ใช้กุญแจแบบสตริงยาวบรรทัดเดียว แล้ว replace \n ธรรมดา ชัวร์ที่สุด ไม่เพี้ยน
    raw_key = "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDbyPC+T8YvWZUE\\nbH2DU34q1+1MEAidthIfgfA91/pPUAl4zCe9wof/1m61PRunpht/dVOJOMwSxsdp\\nwvL+2/UXwRHjIlxcDg11PKGvE4st7tX8Igg/ZW74FnBGrMU/VkOikMSRWmxkTNti\\n8ZGnpPgGGjVIo0M2XDs/ne4zOU2XdSU6EEVGh3nRuJ2pg62nVsfd8gbNIPhnvAMF\\nU2/Fxpd9yx+L6YXv6Dd7Z6gB09pUyXkvdvBCBimNhAMHQl8SuTJpW6yZrn41wCkZ\\ndCfdBriO772gf0TuIVpB6gRepWhD+bkReFQ1j7LtZ/5d1J0/sLOAH0in+wsA1MOg\\njov5ZL29AgMBAAECggEASqr8pxtBEGsVzy06gvhFn9aV5sZ3tuTZSV0Cum/6uSFO\\n5nwtcDl7rL40BFzLXWyAYRACHldudV6U9uhlV5JwtO5B3nGZASlBBzhfEbTJDwTa\\nK/t/49HZHm25HTmrFXaAKeWW8m7O7lByJC4/tr3ECYaz3Yah2gEBm/5So5JvOunP\\nMHfulIPNkEhJX+AdFjI8La7ulBoq0GwTSGKAsYbGeseMZYkT9gjesA9/oKhrxsyh\\nTc0MFJHC7pLzsKnLruq+aDQsAE9G6/i+8MPJ3xYsCcGSYUTQZ1r/Vh0JCZXFgTSQ\\nXfkEvcMzZNCTC6Rh9v6aJDTjE3mcF4g/rFnWB8HgnQKBgQD4cIARv6oeVPGfw814\\ns4+zTmRsoZeSji8jkfgQoYGKsgS1se8d/ZhidJoJTkXBKh4rxRvLBzqOlVfcp+2M\\nQZFotV0iPnT7bVENrt4p4cldhvL9dID8/i3vC2k/Ano+nyP1Qw9XNtuYb/IrFIN+\\n2vXUcePQa96fk9m99GV9Brq2vwKBgQDieTQLmeCzzTHy6jx9qUSNXqm2JNv/3lK7\\nReWWK43R5cV66dEWp8L5lzD3D4mWDdD6z1CUi4Asb8Na9ODl5TD4kaqgbT0VhA9d\\niOLKYWLfJ21NPbKg+Y73KeWmx7Lny7417Y2rdF+Us2K3rXJl5+cRSr7IltgjhyVS\\nCNDal19GgwKBgQDHlkms+JeIqqE6wqjNcSPe3vmas+77FDMWlmv9oGJbtExIU9xP\\n8a18W0RseW9ckaOPclizsOkAJ0ZgxJ/4b6yLvDhIDHkajGXzYiqk5vlIo+OObww5\\nM1JfmoFA15KxwFO489jdLfsY6cZZia9iODIKLDzi8eX1uWfSTQdDfCaALQKBgQCs\\n5Z0/MhXjDseQTRUrVjuYtelYviEa4S9F+6HAGLYnxYQTR0gyRJdMlwlxxHHkld2y\\nbO12yl1rD1QUL5k2ydeuHP8nhN46e9yDKwsBOIIUHXSLoIur63oi5eCGiDTkU55+\\na0JZ3/lMe/rkgU0x0W6NvAOU/dw6m2V5kHNqPmAlYwKBgA7TVlw+rW+eWKnzM+ac\\nhp+VGDXS3Xdjw/Y40DOaMgp5J2PsVr2iA7hh+3er4scV/4J49B1bxm5q0IjEedJd\\nrqPUM+Q+BzVN6lQUnQ5wmMD1Wqkq/0c5wupkauccV2Cq5LcMLndvrPVueS9qPl9o\\nCauyS9O95fkSW53AbfA6s8Lz\\n-----END PRIVATE KEY-----"
    formatted_key = raw_key.replace("\\n", "\n")

    creds_dict = {
        "type": "service_account",
        "project_id": "appointment2026",
        "private_key_id": "a63d42d30b864ec1233777bedb23b8598dee",
        "private_key": formatted_key,
        "client_email": "appointment-bot@appointment2026.iam.gserviceaccount.com",
        "client_id": "108634656719463519344",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/appointment-bot%40appointment2026.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
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
        st.warning(f"ยังไม่สามารถดึงข้อมูลตารางมาแสดงได้: {e}")