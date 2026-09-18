import streamlit as st
import pandas as pd
from utils.auth import login_required
from utils.sheets import read_sheet, calculate_stock

login_required()
st.title("📊 لوحة التحكم")

items_df = read_sheet("items")
transactions_df = read_sheet("transactions")

if items_df.empty:
    st.warning("⚠️ لا توجد أصناف مسجلة بعد")
    st.stop()

stock_df = calculate_stock(items_df, transactions_df)

col1, col2 = st.columns(2)
col1.metric("📦 عدد الأصناف", len(stock_df))
col2.metric("📊 إجمالي الحركات", len(transactions_df) if not transactions_df.empty else 0)

if not transactions_df.empty:
    st.markdown("### 📋 آخر 10 حركات")
    st.dataframe(transactions_df.tail(10).iloc[::-1], use_container_width=True)
