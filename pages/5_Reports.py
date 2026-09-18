import streamlit as st
import pandas as pd
from utils.ui import setup_page
from utils.auth import login_required
from utils.sheets import read_sheet, calculate_stock

setup_page("التقارير", "📈")
login_required()
st.title("📈 التقارير")

items_df = read_sheet("items")
transactions_df = read_sheet("transactions")

tab1, tab2, tab3 = st.tabs(["📊 الرصيد الحالي", "📥 الوارد", "📤 الصادر"])

with tab1:
    stock_df = calculate_stock(items_df, transactions_df)
    if stock_df.empty:
        st.info("لا توجد بيانات")
    else:
        st.dataframe(stock_df, use_container_width=True)
        csv = stock_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 تحميل CSV", csv, "stock.csv", "text/csv", use_container_width=True)

if not transactions_df.empty:
    with tab2:
        incoming = transactions_df[transactions_df["النوع"] == "وارد"]
        if incoming.empty:
            st.info("لا توجد واردات")
        else:
            st.dataframe(incoming, use_container_width=True)
            st.metric("إجمالي الواردات", len(incoming))
            csv = incoming.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 تحميل CSV", csv, "incoming.csv", "text/csv", key="dl_in")
    
    with tab3:
        outgoing = transactions_df[transactions_df["النوع"] == "صادر"]
        if outgoing.empty:
            st.info("لا توجد صرفيات")
        else:
            st.dataframe(outgoing, use_container_width=True)
            st.metric("إجمالي الصرفيات", len(outgoing))
            csv = outgoing.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 تحميل CSV", csv, "outgoing.csv", "text/csv", key="dl_out")
