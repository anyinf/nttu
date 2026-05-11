# Streamlit 基礎教學模板
# 用途：展示側邊欄篩選器、資料展示、多欄位佈局、圖表繪製

import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 頁面基本設定
# ==========================================
st.set_page_config(page_title="NTTU運動數據分析專題", layout="wide")

st.title("🏫 NTTU運動數據分析專題研究")      # 主標題
st.divider()
st.markdown("### 運動資源的投入真的會帶來優勢嗎？")          # 次標題
st.markdown("---")                       # 分隔線


# ==========================================
# 2. 載入資料
# ==========================================
df = pd.read_csv("practice_8_1.csv")

# 用 st.write() 顯示資料說明（最通用的顯示方式）
st.write("📁 **資料檔案**：practice_8_1.csv")
st.write("📊 **資料筆數**：", len(df), "筆")

# 顯示前5筆資料
st.subheader("📋 資料預覽（前5筆）")
st.dataframe(df)   # 或使用 st.write(df.head(5))

# ==========================================
# 3. 側邊欄篩選器（常見寫法）
# ==========================================
st.sidebar.header("🔧 篩選控制區")

# ---------- 篩選器 1：多選框（最常見）----------
st.sidebar.subheader("方式一：多選框")
sport_options = df["sport"].unique()                    # 取出所有運動項目
selected_sports = st.sidebar.multiselect(
    "選擇要顯示的運動項目（可多選）",
    options=sport_options,
    default=sport_options                                # 預設全選
)

# ---------- 篩選器 2：滑桿（數值範圍）----------
st.sidebar.subheader("方式二：滑桿")
grade_min, grade_max = st.sidebar.slider(
    "選擇年級範圍",
    min_value=1, max_value=4, value=(1, 4)
)

# ---------- 其他寫法（用註解教學，使用者可自行更換）----------
# 方式三：單選下拉選單（只能選一個）
# selected_sport = st.sidebar.selectbox("選擇一個運動項目", df["sport"].unique())

# 方式四：單選按鈕（適合選項少的時候）
# selected_gender = st.sidebar.radio("性別", ["全部", "M", "F"])

# 方式五：核取方塊（開關）
# show_injured = st.sidebar.checkbox("只顯示受傷學生")

# 方式六：數字輸入框
# min_hours = st.sidebar.number_input("最低訓練時數", min_value=0, max_value=10, value=0)

# ==========================================
# 4. 根據篩選條件過濾資料
# ==========================================
filtered_df = df[
    (df["sport"].isin(selected_sports)) &
    (df["grade"] >= grade_min) &
    (df["grade"] <= grade_max)
]

# 在側邊欄顯示篩選結果
st.sidebar.markdown("---")
st.sidebar.metric("📊 篩選後筆數", len(filtered_df))
st.sidebar.metric("📋 原始總筆數", len(df))

# ==========================================
# 5. 使用 st.expander（可收合區塊）
# ==========================================
with st.expander("ℹ️ 點我展開：篩選條件說明"):
    st.write("這裡可以放教學說明或註解")
    st.write("- 多選框：可以同時選多個運動項目")
    st.write("- 滑桿：可以調整年級範圍")
    st.write("- 篩選後的資料會自動更新下方的圖表")

# ==========================================
# 6. 多欄位佈局（columns）
# ==========================================
st.subheader("📊 圖表展示區")

# 建立兩欄（比例 1:1）
col1, col2 = st.columns(2)

# ----- 左欄：長條圖 -----
with col1:
    st.write("**圖表一：各運動項目平均體能分數**")
    
    # 計算各運動項目的平均值
    chart_data = filtered_df.groupby("sport")["fitness_score"].mean().reset_index()
    chart_data = chart_data.sort_values("fitness_score", ascending=False)
    
    # 繪製長條圖
    fig1 = px.bar(
        chart_data,
        x="sport",
        y="fitness_score",
        title="平均體能分數比較",
        text="fitness_score"
    )
    fig1.update_traces(textposition="outside")
    st.plotly_chart(fig1, use_container_width=True)

# ----- 右欄：散布圖 -----
with col2:
    st.write("**圖表二：訓練時數 vs 體能分數**")
    
    fig2 = px.scatter(
        filtered_df,
        x="weekly_training_hours",
        y="fitness_score",
        color="sport",
        title="訓練越多體能越好嗎？"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 7. 第三個圖表（單獨佔一整列）
# ==========================================
st.subheader("圖表三：滿意度分布（箱形圖）")

fig3 = px.box(
    filtered_df,
    x="sport",
    y="satisfaction",
    color="sport",
    title="各運動項目滿意度比較",
    points="all"
)
st.plotly_chart(fig3, use_container_width=True)

# ==========================================
# 8. 結論與教學提示
# ==========================================
st.markdown("---")
st.subheader("📝 學習重點整理")

# 使用 st.write() 做各種輸出示範
st.write("✅ **st應用重要功能**：")
st.write("1. `st.title()` / `st.markdown()` - 設定標題")
st.write("2. `st.sidebar.multiselect()` / `st.sidebar.slider()` - 建立篩選器")
st.write("3. `st.dataframe()` / `st.write()` - 顯示資料")
st.write("4. `st.expander()` - 建立可收合區塊")
st.write("5. `st.columns()` - 多欄位排版")
st.write("6. `st.metric()` - 顯示指標數字")

# 加上提示框
st.success("🎉 恭喜！你已經具備使用 Streamlit 的基礎功能！")

