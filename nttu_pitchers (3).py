import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 設定網頁標題
st.set_page_config(page_title="投手數據分析 Dashboard", layout="wide")
st.title("⚾ 投手春季聯賽數據分析儀表板")

# 📊 棒球專用局數進位轉換器
def convert_innings(val):
    try:
        val = float(val)
        integer_part = int(val)
        decimal_part = round(val - integer_part, 1)
        if decimal_part == 0.1:
            return integer_part + 0.3333
        elif decimal_part == 0.2:
            return integer_part + 0.6667
        else:
            return val
    except:
        return 0.0

# 📦 直接內嵌與圖片完全吻合的春季聯賽數據 (完美避開外部檔案讀取錯誤)
raw_data = {
    '出賽球員': [
        '李聖韓', '李冠中', '葉一鋐', '李振綸', '林誠恩', 
        '許少捷', '邱承華', '王弘彥', '張甯翔', '林張旭',
        '陳培安', '王弘彥', '董誥', '林承恩', '李振綸', '林誠恩', '董誥',
        '許少捷', '邱承華', '陳培安', '葉一鋐', '李冠中',
        '董誥', '李冠中', '葉一鋐', '李振綸', '林誠恩',
        '李聖韓', '林承恩', '林承恩'
    ],
    '局數': [1.2, 2.2, 1.0, 1.2, 2.0, 3.0, 3.0, 1.0, 5.0, 2.0, 4.1, 1.1, 1.1, 5.1, 2.1, 1.0, 0.1, 6.0, 3.0, 1.1, 5.2, 2.0, 4.0, 2.1, 1.0, 0.2, 1.0, 3.0, 2.2, 3.1],
    '最速': [138, 132, 139, 131, 142, 143, 135, 130, 134, 143, 134, 132, 143, 138, 133, 144, 137, 144, 136, 130, 138, 133, 144, 136, 137, 131, 146, 146, 133, 140],
    '總球數': [42, 53, 22, 17, 24, 62, 37, 10, 61, 23, 99, 36, 16, 88, 33, 23, 6, 72, 39, 38, 74, 27, 71, 41, 12, 7, 12, 52, 36, 47],
    '好球數': [21, 35, 12, 13, 15, 34, 26, 7, 46, 19, 52, 20, 10, 53, 21, 11, 4, 43, 30, 18, 45, 16, 42, 25, 4, 6, 11, 38, 24, 34],
    '壞球數': [21, 18, 10, 4, 9, 28, 11, 3, 15, 4, 47, 16, 6, 35, 12, 12, 2, 29, 9, 20, 29, 11, 29, 16, 8, 1, 1, 16, 12, 13],
    '自責分': [0, 2, 2, 0, 1, 3, 1, 0, 0, 0, 1, 2, 0, 0, 1, 1, 0, 1, 0, 5, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0],
    '被安打': [1, 4, 3, 0, 2, 4, 4, 0, 2, 1, 4, 2, 0, 4, 1, 1, 1, 3, 1, 4, 4, 1, 3, 5, 0, 0, 1, 0, 1, 2],
    '奪三振': [2, 2, 2, 0, 0, 4, 2, 1, 9, 3, 2, 4, 3, 4, 0, 1, 0, 4, 3, 1, 5, 2, 3, 1, 0, 1, 1, 6, 3, 4],
    '四死球': [3, 1, 0, 0, 1, 3, 0, 0, 0, 0, 5, 2, 0, 4, 1, 2, 0, 2, 0, 2, 2, 1, 3, 1, 1, 0, 0, 2, 1, 1]
}

df = pd.DataFrame(raw_data)
df['真實局數'] = df['局數'].apply(convert_innings)

# ==================== 側邊欄設計 ====================
st.sidebar.header("⚙️ 功能切換選單")
main_function = st.sidebar.radio(
    "請選擇您要查看的功能：",
    ["1. 投手的數據分析", "2. 投手春聯表現"]
)

all_pitchers = sorted(df['出賽球員'].unique())

# ==================== 功能一：投手的數據分析 ====================
if main_function == "1. 投手的數據分析":
    st.markdown("## 🎯 投手核心數據與指標比例")
    
    selected_pitcher_1 = st.sidebar.selectbox("請選擇要分析的投手：", all_pitchers)
    
    p_df = df[df['出賽球員'] == selected_pitcher_1]
    
    total_balls = p_df['總球數'].sum()
    total_strikes = p_df['好球數'].sum()
    total_bad_balls = p_df['壞球數'].sum()
    total_so = p_df['奪三振'].sum()
    total_bb = p_df['四死球'].sum()
    total_h = p_df['被安打'].sum()
    total_er = p_df['自責分'].sum()
    total_ip = p_df['真實局數'].sum()
    
    max_speed = p_df['最速'].max()
    
    # 計算防禦率、被上壘率 (WHIP)
    era = (total_er * 9 / total_ip) if total_ip > 0 else 0
    whip = ((total_h + total_bb) / total_ip) if total_ip > 0 else 0
    
    st.markdown(f"### 目前檢視選手：**{selected_pitcher_1}**")
    
    # 並排三大指標卡片
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("自責分率 (ERA)", f"{era:.2f}")
    col2.metric("每局被上壘率 (WHIP)", f"{whip:.2f}")
    col3.metric("最快球速 (MAX)", f"{int(max_speed)} km/h")
    col4.metric("累積投球局數", f"{total_ip:.1f} 局")
    
    st.write("---")
    
    # 好壞球事件比例圓餅圖
    pie_data = pd.DataFrame({
        '指標項目': ['好球數', '壞球數', '奪三振(個)', '四死球(個)', '被安打(支)'],
        '數量': [total_strikes, total_bad_balls, total_so, total_bb, total_h]
    })
    
    fig_pie = px.pie(
        pie_data, 
        values='數量', 
        names='指標項目', 
        title=f"【{selected_pitcher_1}】個人投球好壞球與事件比例分布",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    
# ==================== 功能二：投手春聯表現 ====================
elif main_function == "2. 投手春聯表現":
    st.markdown("## 📈 投手春聯個別壓制力評估")
    
    selected_pitcher_2 = st.sidebar.selectbox("請選擇要查看春聯表現的選手：", all_pitchers)
    
    pitcher_stats = []
    for pitcher, group in df.groupby('出賽球員'):
        t_balls = group['總球數'].sum()
        t_strikes = group['好球數'].sum()
        t_er = group['自責分'].sum()
        t_ip = group['真實局數'].sum()
        
        s_rate = (t_strikes / t_balls * 100) if t_balls > 0 else 0
        era = (t_er * 9 / t_ip) if t_ip > 0 else 0
        
        pitcher_stats.append({
            '投手': pitcher,
            '好球率 (%)': round(s_rate, 1),
            '防禦率 (ERA)': round(era, 2),
            '總球數': t_balls,
            '累積投球局數': round(t_ip, 1)
        })
    
    summary_df = pd.DataFrame(pitcher_stats)
    
    target_label = f"🎯 {selected_pitcher_2} (目前選手)"
    summary_df['焦點標記'] = summary_df['投手'].apply(
        lambda x: target_label if x == selected_pitcher_2 else '其他聯賽球員'
    )
    
    st.markdown(f"### 正在追蹤：**{selected_pitcher_2}** 在全隊的壓制力落點")
    
    fig_scatter = px.scatter(
        summary_df,
        x='好球率 (%)',
        y='防禦率 (ERA)',
        text='投手',
        size='總球數',
        color='焦點標記',
        title=f"春季聯賽全隊投手控球與壓制力分佈 (目前觀測: {selected_pitcher_2})",
        labels={
            '好球率 (%)': '好球率 (%) → 越高代表控球越好', 
            '防禦率 (ERA)': '防禦率 (ERA) ↓ 越低代表壓制力越強'
        },
        color_discrete_map={target_label: '#FF4B4B', '其他聯賽球員': '#1C83E1'},
        hover_data=['累積投球局數']
    )
    
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_yaxes(autorange="reversed")
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.info(f"💡 **圖表看點：** 紅色泡泡代表 **{selected_pitcher_2}**。泡泡位置越往**右上方**，代表壓制力與控球越好！")