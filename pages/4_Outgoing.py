import streamlit as st
from datetime import datetime
from utils.ui import setup_page
from utils.auth import login_required
from utils.sheets import read_sheet, append_row, generate_id, calculate_stock

setup_page("الصادر", "📤")
login_required(role=["مدير", "أمين مخزن"])
st.title("📤 تسجيل صادر جديد")

items_df = read_sheet("items")
transactions_df = read_sheet("transactions")
warehouses_df = read_sheet("warehouses")

if items_df.empty:
    st.warning("⚠️ أضف أصنافاً أولاً")
    st.stop()

stock_df = calculate_stock(items_df, transactions_df)

with st.form("outgoing_form"):
    col1, col2 = st.columns(2)
    
    item_options = (stock_df["كود الصنف"].astype(str) + " - " + stock_df["اسم الصنف"].astype(str) + " (متاح: " + stock_df["الرصيد الحالي"].astype(str) + ")").tolist()
    item = col1.selectbox("الصنف *", item_options)
    code = item.split(" - ")[0]
    available_series = stock_df[stock_df["كود الصنف"].astype(str) == code]["الرصيد الحالي"]
    available = float(available_series.values[0]) if not available_series.empty else 0
    
    st.info(f"📦 الرصيد المتاح حالياً: **{available}**")
    
    max_qty = float(available) if available > 0 else 1.0
    qty = col1.number_input("الكمية *", min_value=0.01, max_value=max_qty, step=1.0)
    
    warehouse_opts = warehouses_df["اسم المخزن"].tolist() if not warehouses_df.empty else ["المخزن الرئيسي"]
    warehouse = col2.selectbox("المخزن *", warehouse_opts)
    entity = col2.text_input("الجهة الطالبة *")
    receiver = col2.text_input("اسم المستلم *")
    notes = st.text_area("ملاحظات", height=80)
    
    if st.form_submit_button("✅ صرف الصنف", use_container_width=True):
        if not entity or not receiver:
            st.error("⚠️ املأ اسم الجهة والمستلم")
        else:
            receipt_no = generate_id("OUT")
            append_row("transactions", {
                "رقم الإذن": receipt_no,
                "النوع": "صادر",
                "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "كود الصنف": code,
                "الكمية": qty,
                "كود المخزن": warehouse,
                "المورد/الجهة": entity,
                "سعر الوحدة": 0,
                "الموظف": st.session_state["user"]["name"],
                "ملاحظات": f"{notes} | المستلم: {receiver}"
            })
            st.success(f"✅ تم الصرف بنجاح - رقم الإذن: {receipt_no}")
            st.balloons()

# عرض آخر 5 صرفيات
st.markdown("---")
st.markdown("### 📋 آخر 5 صرفيات")
transactions_df = read_sheet("transactions")
if not transactions_df.empty:
    outgoing = transactions_df[transactions_df["النوع"] == "صادر"].tail(5).iloc[::-1]
    st.dataframe(outgoing, use_container_width=True)
