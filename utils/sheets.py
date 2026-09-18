import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials
from datetime import datetime
import uuid

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_sheet(sheet_key: str):
    client = get_gspread_client()
    sheet_id = st.secrets["sheets_ids"][sheet_key]
    return client.open_by_key(sheet_id).sheet1

def read_sheet(sheet_key: str) -> pd.DataFrame:
    try:
        sheet = get_sheet(sheet_key)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"خطأ في قراءة {sheet_key}: {e}")
        return pd.DataFrame()

def append_row(sheet_key: str, row_dict: dict):
    try:
        sheet = get_sheet(sheet_key)
        headers = sheet.row_values(1)
        row = [row_dict.get(h, "") for h in headers]
        sheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"خطأ في إضافة بيانات: {e}")
        return False

def update_row(sheet_key: str, row_index: int, row_dict: dict):
    try:
        sheet = get_sheet(sheet_key)
        headers = sheet.row_values(1)
        row = [row_dict.get(h, "") for h in headers]
        sheet.update(f"A{row_index}", [row])
        return True
    except Exception as e:
        st.error(f"خطأ في التحديث: {e}")
        return False

def delete_row(sheet_key: str, row_index: int):
    try:
        sheet = get_sheet(sheet_key)
        sheet.delete_rows(row_index)
        return True
    except Exception as e:
        st.error(f"خطأ في الحذف: {e}")
        return False

def generate_id(prefix: str) -> str:
    year = datetime.now().year
    short_uuid = str(uuid.uuid4())[:6].upper()
    return f"{prefix}-{year}-{short_uuid}"

def calculate_stock(items_df: pd.DataFrame, transactions_df: pd.DataFrame) -> pd.DataFrame:
    if items_df.empty:
        return pd.DataFrame()
    
    result = items_df.copy()
    result["الرصيد الافتتاحي"] = pd.to_numeric(result.get("الرصيد الافتتاحي", 0), errors="coerce").fillna(0)
    
    if transactions_df.empty:
        result["إجمالي الوارد"] = 0
        result["إجمالي الصادر"] = 0
        result["الرصيد الحالي"] = result["الرصيد الافتتاحي"]
        return result
    
    transactions_df["الكمية"] = pd.to_numeric(transactions_df["الكمية"], errors="coerce").fillna(0)
    
    in_qty = transactions_df[transactions_df["النوع"] == "وارد"].groupby("كود الصنف")["الكمية"].sum()
    out_qty = transactions_df[transactions_df["النوع"] == "صادر"].groupby("كود الصنف")["الكمية"].sum()
    
    result["إجمالي الوارد"] = result["كود الصنف"].map(in_qty).fillna(0)
    result["إجمالي الصادر"] = result["كود الصنف"].map(out_qty).fillna(0)
    result["الرصيد الحالي"] = result["الرصيد الافتتاحي"] + result["إجمالي الوارد"] - result["إجمالي الصادر"]
    
    return result
