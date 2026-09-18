import streamlit as st
from datetime import datetime
from utils.auth import login_required
from utils.sheets import read_sheet, append_row, generate_id, calculate_stock

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
    available = float(stock_df[stock_df["كود الصنف"].astype(str) == code]["الرصيد الحالي"].values[0])
    
    st.info(f"📦 المتاح حالياً: {available}")
    qty = col1.number_input("الكمية *", min_value=0.01, max_value=float(available) if available > 0 else 1000.0, step=1.0)
    
    warehouse_opts = warehouses_df["اسم المخزن"].tolist() if not warehouses_df.empty else ["افتراضي"]
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
            st.success(f"✅ تم الصرف بإذن رقم {receipt_no}")
