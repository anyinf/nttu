import streamlit as st
import pandas as pd
import os
from datetime import date

# ================= 1. 定義資料檔案路徑與設定 =================
DATA_FILE = "injury_records.csv"
MEDICAL_FILE = "medical_records.csv"
UPLOAD_DIR = "uploaded_images"

# 建立圖片儲存資料夾
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- 球員名單 ---
PLAYER_LIST = [
    "許少捷", "顏子謙", "吳誌珈", "林承恩(大)","李雚喆","林誠恩","葉一鋐","王弘彥","朱宸益","李冠中","王浩臣","曾顯恩","陳培力",
    "高恆恩","林丞圻","李佳昊","林承恩(小)","廖元億","尹蓋·法拉斯","吳星樺","李振綸","張甯翔","李聖韓","陳培安","徐巳凱","李振陽",
    "林浩震","蔣林昱辰","余彥偉","陳宏宇","楊博隆","王弘恩","邱承葦","吳天豪","王聖恩","陳逸恩","葉澄泰","邱彥祖","高士凱","黃皓揚"
]

# ================= 2. 功能函數定義 =================
def load_data(file_path, default_columns):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame(columns=default_columns)

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# 載入資料
df_records = load_data(DATA_FILE, ["ID", "球員姓名", "受傷部位與敘述", "發生日期", "目前狀態"])
df_medical = load_data(MEDICAL_FILE, ["姓名", "就醫時間", "診斷結果", "圖片路徑"])

# ================= 3. 側邊欄功能導覽 =================
st.sidebar.title("📌 導覽選單")
menu = st.sidebar.radio("請選擇功能：", ["傷害紀錄管理", "新增就醫紀錄"])

st.title("🏃‍♂️ 球員傷害紀錄資料庫系统")
st.divider()

# ================= 功能一：傷害紀錄管理 =================
if menu == "傷害紀錄管理":
    
    # ---- 區塊 A：關鍵字搜尋 ----
    st.header("🔍 查詢球員紀錄")
    search_options = ["全部顯示"] + PLAYER_LIST
    selected_player = st.selectbox("選擇球員姓名進行查詢：", options=search_options)

    if selected_player != "全部顯示":
        filtered_df = df_records[df_records["球員姓名"] == selected_player]
        st.subheader(f"「{selected_player}」的歷史紀錄：")
    else:
        filtered_df = df_records
        st.subheader("顯示所有紀錄：")

    if not filtered_df.empty:
        st.dataframe(filtered_df[["ID", "球員姓名", "受傷部位與敘述", "發生日期", "目前狀態"]], use_container_width=True)
    else:
        st.info("目前沒有符合的紀錄。")

    st.divider()

    # ---- 區塊 B：新增紀錄 ----
    st.header("➕ 新增傷害紀錄")
    with st.form("add_record_form", clear_on_submit=True):
        player_name = st.selectbox("球員姓名*", PLAYER_LIST) # 改為下拉選單避免打錯字
        injury_desc = st.text_area("受傷部位與詳細敘述*")
        injury_date = st.date_input("發生日期", value=date.today())
        status = st.selectbox("目前狀態", ["休養中", "復健中", "已痊癒", "觀察中"])
        
        submit_btn = st.form_submit_button("提交紀錄")
        
        if submit_btn:
            if injury_desc:
                new_id = len(df_records) + 1
                new_row = {
                    "ID": new_id,
                    "球員姓名": player_name,
                    "受傷部位與敘述": injury_desc,
                    "發生日期": injury_date.strftime("%Y-%m-%d"),
                    "目前狀態": status
                }
                df_records = pd.concat([df_records, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df_records, DATA_FILE)
                st.success(f"成功新增 {player_name} 的傷害紀錄！")
                st.rerun()
            else:
                st.error("請填寫受傷敘述。")

    st.divider()

    # ---- 區塊 C：刪除與管理 ----
    st.header("⚙️ 資料管理 (刪除紀錄)")
    if not df_records.empty:
        record_to_delete = st.selectbox(
            "選擇要刪除的紀錄：", 
            options=df_records["ID"].tolist(),
            format_func=lambda x: f"ID {x}: {df_records[df_records['ID']==x]['球員姓名'].values[0]} - {str(df_records[df_records['ID']==x]['受傷部位與敘述'].values[0])[:15]}..."
        )
        
        if st.button("❌ 確認刪除該筆紀錄", type="primary"):
            df_records = df_records[df_records["ID"] != record_to_delete]
            # 重新整理 ID 排序
            df_records["ID"] = range(1, len(df_records) + 1)
            save_data(df_records, DATA_FILE)
            st.warning("紀錄已成功刪除。")
            st.rerun()
    else:
        st.text("資料庫目前為空。")

# ================= 功能二：新增就醫紀錄 =================
elif menu == "新增就醫紀錄":
    st.header("🩺 新增就醫診療紀錄")
    
    with st.form("medical_record_form", clear_on_submit=True):
        med_name = st.selectbox("球員姓名*", PLAYER_LIST)
        med_date = st.date_input("就醫時間", value=date.today())
        med_result = st.text_area("診斷結果與醫囑*", placeholder="請輸入醫生的診斷內容...")
        uploaded_file = st.file_uploader("上傳就醫證明或處方箋圖片", type=['png', 'jpg', 'jpeg'])
        
        submit_med = st.form_submit_button("儲存就醫紀錄")
        
        if submit_med:
            if med_result:
                img_path = "無圖片"
                if uploaded_file is not None:
                    # 重新命名圖片以防覆蓋
                    img_name = f"{med_name}_{med_date.strftime('%Y%m%d')}_{uploaded_file.name}"
                    img_path = os.path.join(UPLOAD_DIR, img_name)
                    with open(img_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                new_med_row = {
                    "姓名": med_name,
                    "就醫時間": med_date.strftime("%Y-%m-%d"),
                    "診斷結果": med_result,
                    "圖片路徑": img_path
                }
                df_medical = pd.concat([df_medical, pd.DataFrame([new_med_row])], ignore_index=True)
                save_data(df_medical, MEDICAL_FILE)
                
                st.success(f"已成功記錄 {med_name} 的就醫資料！")
                if uploaded_file:
                    st.image(uploaded_file, caption="已上傳的照片", width=300)
                st.rerun()
            else:
                st.error("請填寫診斷結果。")

    # ---- 歷史就醫紀錄摘要檢視 ----
    st.divider()
    st.subheader("📋 歷史就醫紀錄檢視")
    if not df_medical.empty:
        st.dataframe(df_medical, use_container_width=True)
    else:
        st.info("目前沒有就醫紀錄。")