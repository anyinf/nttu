import streamlit as st
import pandas as pd
import os
from datetime import date

# 1. 定義資料檔案路徑
DATA_FILE = "injury_records.csv"

# 2. 初始化或讀取資料庫
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # 建立初始欄位
        return pd.DataFrame(columns=["ID", "球員姓名", "受傷部位與敘述", "發生日期", "目前狀態"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 載入現有資料
df_records = load_data()

st.title("🏃‍♂️ 球員傷害紀錄資料庫系统")

# ================= 核心功能一：關鍵字搜尋 =================
st.header("🔍 查詢球員紀錄")
search_name = st.text_input("輸入球員姓名進行搜尋：")

if search_name:
    # 支援模糊搜尋
    filtered_df = df_records[df_records["球員姓名"].str.contains(search_name, na=False)]
    st.subheader(f"「{search_name}」的歷史紀錄：")
else:
    filtered_df = df_records

# 顯示查詢結果表格
if not filtered_df.empty:
    st.dataframe(filtered_df[["球員姓名", "受傷部位與敘述", "發生日期", "目前狀態"]], use_container_width=True)
else:
    st.info("目前沒有符合的紀錄。")


# ================= 核心功能二：新增紀錄 =================
st.header("➕ 新增傷害紀錄")
with st.form("add_record_form", clear_on_submit=True):
    player_name = st.text_input("球員姓名*")
    injury_desc = st.text_area("受傷部位與詳細敘述*")
    injury_date = st.date_input("發生日期", value=date.today())
    status = st.selectbox("目前狀態", ["休養中", "復健中", "已痊癒", "觀察中"])
    
    submit_btn = st.form_submit_button("提交紀錄")
    
    if submit_btn:
        if player_name and injury_desc:
            # 建立新一筆資料
            new_id = len(df_records) + 1
            new_row = {
                "ID": new_id,
                "球員姓名": player_name,
                "受傷部位與敘述": injury_desc,
                "發生日期": injury_date.strftime("%Y-%m-%d"),
                "目前狀態": status
            }
            # 更新 DataFrame 並儲存
            df_records = pd.concat([df_records, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df_records)
            st.success(f"成功新增 {player_name} 的傷害紀錄！")
            st.rerun() # 重新整理頁面以顯示最新資料
        else:
            st.error("請填寫球員姓名與受傷敘述。")


# ================= 核心功能三：刪除與管理 =================
st.header("⚙️ 資料管理 (刪除紀錄)")
if not df_records.empty:
    # 讓使用者選擇要刪除哪一筆 ID
    record_to_delete = st.selectbox(
        "選擇要刪除的紀錄：", 
        options=df_records["ID"].tolist(),
        format_func=lambda x: f"ID {x}: {df_records[df_records['ID']==x]['球員姓名'].values[0]} - {df_records[df_records['ID']==x]['受傷部位與敘述'].values[0][:15]}..."
    )
    
    if st.button("❌ 確認刪除該筆紀錄", type="primary"):
        df_records = df_records[df_records["ID"] != record_to_delete]
        # 重新整理 ID 排序
        df_records["ID"] = range(1, len(df_records) + 1)
        save_data(df_records)
        st.warning("紀錄已成功刪除。")
        st.rerun()
else:
    st.text("資料庫目前為空。")
    