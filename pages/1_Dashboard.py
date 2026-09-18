import streamlit as st
from utils.ui import setup_page
from utils.auth import login_required
from utils.sheets import read_sheet, calculate_stock

setup_page("لوحة التحكم", "📊")
login_required()
st.title("📊 لوحة التحكم")

items_df = read_sheet("items")
transactions_df = read_sheet("transactions")

if items_df.empty:
    st.warning("⚠️ لا توجد أصناف مسجلة بعد")
    st.stop()

stock_df = calculate_stock(items_df, transactions_df)

col1, col2, col3 = st.columns(3)
col1.metric("📦 عدد الأصناف", len(stock_df))
col2.metric("📊 إجمالي الحركات", len(transactions_df) if not transactions_df.empty else 0)

if not transactions_df.empty:
    incoming_count = len(transactions_df[transactions_df["النوع"] == "وارد"])
    outgoing_count = len(transactions_df[transactions_df["النوع"] == "صادر"])
    col3.metric("📥 وارد / 📤 صادر", f"{incoming_count} / {outgoing_count}")

st.markdown("---")

# الأصناف المنخفضة
if not stock_df.empty and "حد الطلب" in stock_df.columns:
    stock_df["حد الطلب"] = stock_df["حد الطلب"].astype(float)
    low_stock = stock_df[stock_df["الرصيد الحالي"] <= stock_df["حد الطلب"]]
    if not low_stock.empty:
        st.error("### ⚠️ أصناف تحتاج إعادة طلب")
        st.dataframe(
            low_stock[["كود الصنف", "اسم الصنف", "الرصيد الحالي", "حد الطلب"]],
            use_container_width=True
        )

# آخر 10 حركات
if not transactions_df.empty:
    st.markdown("### 📋 آخر 10 حركات")
    st.dataframe(transactions_df.tail(10).iloc[::-1], use_container_width=True)
