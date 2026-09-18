import streamlit as st
from pathlib import Path
from utils.auth import authenticate, init_session

st.set_page_config(
    page_title="نظام المخازن",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session()

# المسار الأساسي للمشروع (مطلق)
BASE_DIR = Path(__file__).resolve().parent
PAGES_DIR = BASE_DIR / "pages"

st.markdown("""
<style>
    * { font-family: 'Cairo', 'Tahoma', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #2b7a62, #1a3a5c);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    }
    .stButton > button {
        background-color: #2b7a62;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============ تسجيل الدخول ============
if st.session_state.get("user") is None:
    st.markdown("""
    <div class="main-header">
        <h1>📦 نظام إدارة المخازن المتكامل</h1>
        <p>يرجى تسجيل الدخول للمتابعة</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("📧 البريد الإلكتروني")
            password = st.text_input("🔒 كلمة المرور", type="password")
            submitted = st.form_submit_button("🔓 تسجيل الدخول", use_container_width=True)
            
            if submitted:
                user = authenticate(email, password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        st.info("💡 استخدم بيانات المدير المسجلة في ملف المستخدمين.")
    st.stop()

user = st.session_state["user"]

# معلومات المستخدم في الشريط الجانبي
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center; padding:15px; background:#f0f4f8; border-radius:10px;">
        <h3>👤 {user['name']}</h3>
        <p style="color:#2b7a62;">{user['role']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state["user"] = None
        st.rerun()
    st.markdown("---")

# ============ تعريف الصفحات (بمسار مطلق) ============
pages_config = [
    ("1_Dashboard.py", "لوحة التحكم", "📊", True),
    ("2_Items.py", "الأصناف", "📦", False),
    ("3_Incoming.py", "الوارد", "📥", False),
    ("4_Outgoing.py", "الصادر", "📤", False),
    ("5_Reports.py", "التقارير", "📈", False),
    ("6_Settings.py", "الإعدادات", "⚙️", False),
]

pages = []
for filename, title, icon, is_default in pages_config:
    file_path = PAGES_DIR / filename
    if file_path.exists():
        if title == "الإعدادات" and user["role"] != "مدير":
            continue
        pages.append(st.Page(str(file_path), title=title, icon=icon, default=is_default))
    else:
        st.sidebar.warning(f"⚠️ ملف مفقود: {filename}")

if not pages:
    st.error("❌ لم يتم العثور على أي صفحات!")
    st.stop()

pg = st.navigation(pages)
pg.run()
