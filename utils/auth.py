import streamlit as st
import bcrypt
from utils.sheets import read_sheet

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return password == hashed

def authenticate(email: str, password: str):
    users_df = read_sheet("users")
    if users_df.empty:
        return None
    
    user = users_df[users_df["الإيميل"] == email]
    if user.empty:
        return None
    
    user_row = user.iloc[0]
    if verify_password(password, str(user_row["كلمة المرور"])):
        return {
            "email": email,
            "name": user_row["الاسم"],
            "role": user_row["الدور"]
        }
    return None

def login_required(role=None):
    if "user" not in st.session_state or st.session_state["user"] is None:
        st.warning("⚠️ يجب تسجيل الدخول أولاً")
        st.stop()
    if role and st.session_state["user"]["role"] not in role:
        st.error(f"❌ هذا القسم متاح فقط لـ: {role}")
        st.stop()

def init_session():
    if "user" not in st.session_state:
        st.session_state["user"] = None
