import streamlit as st
from utils.auth import authenticate, init_session
from utils.sheets import read_sheet

st.set_page_config(
    page_title="نظام المخازن",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session()

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
    .stButton > button:hover { background-color: #1e5c4a; }
</style>
""", unsafe_allow_html=True)

if st.session_state["user"] is None:
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
                    st.success(f"✅ مرحباً {user['name']}")
                    st.rerun()
                else:
                    st.error("❌ بيانات الدخول غير صحيحة")
        
        st.info("💡 **لأول استخدام**: استخدم بيانات المدير التي أنشأتها في ملف المستخدمين.")
    st.stop()

user = st.session_state["user"]

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

st.markdown("""
<div class="main-header">
    <h1>📦 مرحباً بك في نظام إدارة المخازن</h1>
    <p>نظام متكامل لإدارة الوارد والصادر والرصيد</p>
</div>
""", unsafe_allow_html=True)

items_df = read_sheet("items")
if not items_df.empty:
    st.metric("📦 عدد الأصناف المسجلة", len(items_df))
else:
    st.info("🚀 ابدأ بإضافة أصنافك من صفحة الأصناف في القائمة الجانبية")

st.markdown("### 🎯 اختر العملية من القائمة الجانبية")
st.info("""
- **📦 الأصناف**: إضافة وتعديل بيانات الأصناف
- **📥 الوارد**: تسجيل توريدات جديدة
- **📤 الصادر**: تسجيل عمليات الصرف
- **📈 التقارير**: عرض الرصيد والتقارير التفصيلية
- **⚙️ الإعدادات**: إدارة المستخدمين والمخازن (للمدير فقط)
""")
