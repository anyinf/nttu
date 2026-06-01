import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 設定網頁標題與寬度佈局
st.set_page_config(page_title="投手春季聯賽數據分析 Dashboard", layout="wide")
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

# ==================== 1. 側邊欄：手動檔案上傳 ====================
st.sidebar.header("📁 數據檔案輸入")
uploaded_file = st.sidebar.file_uploader("請上傳您的投手 Excel 檔案 (.xlsx)", type=["xlsx"])

# ==================== 2. 判斷檔案是否存在 ====================
if uploaded_file is None:
    st.info("👋 您好！請先在左側邊欄點擊或拖曳上傳您的 Excel 檔案。上傳後即可開始切換功能分析！")
else:
    try:
        # 讀取 Excel
        df = pd.read_excel(uploaded_file)
        
        # 【防呆機制 1】強制清除所有欄位名稱的前後空白字元
        df.columns = df.columns.astype(str).str.strip()
        
        # 計算棒球專用真實局數
        df['真實局數'] = df['局數'].apply(convert_innings)
        
        st.sidebar.success("🎉 檔案上傳成功！")
        st.sidebar.write("---")
        
        # ==================== 3. 側邊欄主要功能切換 ====================
        st.sidebar.header("⚙️ 功能切換選單")
        main_function = st.sidebar.radio(
            "請選擇您要查看的功能：",
            ["1. 投手的數據分析", "2. 投手春聯表現"]
        )
        
        # 撈取不重複的投手名單
        all_pitchers = sorted(df['出賽球員'].dropna().unique())
        
        # ==================== 功能一：投手的數據分析 ====================
        if main_function == "1. 投手的數據分析":
            st.markdown("## 🎯 投手核心數據與指標比例")
            
            # 側邊欄功能一：選投手
            selected_pitcher_1 = st.sidebar.selectbox("請選擇要分析的投手：", all_pitchers, key="func_1")
            
            # 篩選該投手的資料
            p_df = df[df['出賽球員'] == selected_pitcher_1]
            
            total_balls = p_df['總球數'].sum()
            total_strikes = p_df['好球數'].sum()
            total_bad_balls = p_df['壞球數'].sum()
            total_so = p_df['奪三振'].sum()
            total_bb = p_df['四死球'].sum()
            total_h = p_df['被安打'].sum()
            total_er = p_df['自責分'].sum()
            total_ip = p_df['真實局數'].sum()
            
            # 【防呆機制 2】智慧尋找「最快球速」欄位，防止 KeyError 當機
            speed_col = None
            for possible_name in ['最速', '最快球速', '球速', 'MAX', '最速球速']:
                if possible_name in p_df.columns:
                    speed_col = possible_name
                    break
            
            if speed_col and not p_df[speed_col].dropna().empty:
                max_speed = p_df[speed_col].max()
            else:
                max_speed = 0 # 若真的都找不到，設為 0 預備，不報錯
            
            # 計算防禦率與被上壘率
            era = (total_er * 9 / total_ip) if total_ip > 0 else 0
            whip = ((total_h + total_bb) / total_ip) if total_ip > 0 else 0
            
            st.markdown(f"### 目前檢視選手：**{selected_pitcher_1}**")
            
            # 版面：最上方並排放置數據
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("自責分率 (ERA)", f"{era:.2f}", help="越低代表壓制力越好")
            col2.metric("每局被上壘率 (WHIP)", f"{whip:.2f}", help="越低代表每局讓對手上壘人數越少")
            
            if max_speed > 0:
                col3.metric("最快球速 (MAX)", f"{int(max_speed)} km/h")
            else:
                col3.metric("最快球速 (MAX)", "無數據", help="Excel 內未找到『最速』或相符的欄位")
                
            col4.metric("累積投球局數", f"{total_ip:.1f} 局")
            
            st.write("---")
            
            # 下面放好壞球與事件組成的圓餅圖
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
            
            # 側邊欄功能二：選選手
            selected_pitcher_2 = st.sidebar.selectbox("請選擇要查看春聯表現的選手：", all_pitchers, key="func_2")
            
            # 計算全隊表現
            pitcher_stats = []
            for pitcher, group in df.groupby('出賽球員'):
                if pd.isna(pitcher): continue
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
            
            # 高亮標籤設定
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
            fig_scatter.update_yaxes(autorange="reversed")  # 反轉防禦率軸
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.info(f"💡 **圖表看點：** 紅色泡泡代表 **{selected_pitcher_2}**。泡泡位置越往**右上方**，代表他在春季聯賽中的控球越準、失分壓制力越強！")

    except Exception as e:
        st.error(f"❌ 讀取 Excel 檔案時發生錯誤。請確認您的檔案欄位名稱。錯誤訊息: {e}")