import streamlit as st
import pandas as pd
import data_loader
import logic
import red
from qingx import qingxu

# --- Page Configuration ---
st.set_page_config(
    page_title="Sector Alpha Hunter",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed" # Collapsed to save space for "one page" feel
)

# --- Custom CSS (The "Linear" Look) ---
st.markdown("""
<style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    .stApp { background-color: #FFFFFF; }
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1F2937;
    }

    /* Layout */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
        max-width: 1200px;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-weight: 600 !important;
        color: #0F172A !important;
        letter-spacing: -0.025em;
    }
    h1 { font-size: 1.875rem !important; margin-bottom: 0.75rem !important; }
    h2 { font-size: 1.25rem !important; margin-top: 2rem !important; }
    h3 { font-size: 1.125rem !important; }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.25s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #EF4444;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 0.875rem; 
        color: #64748B; 
        font-weight: 500; 
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] { 
        font-size: 2rem; 
        font-weight: 700; 
        color: #EF4444 !important;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        background: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2.5rem;
        border-bottom: 1px solid #E2E8F0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        color: #94A3B8;
        font-weight: 500;
        transition: color 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover { color: #64748B; }
    .stTabs [aria-selected="true"] {
        color: #EF4444 !important;
        border-bottom: 2px solid #EF4444 !important;
    }

    /* All Buttons - Base Style */
    .stButton > button,
    div.stDownloadButton > button {
        border-radius: 12px !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.9375rem !important;
        transition: all 0.2s ease !important;
        min-height: 42px !important;
    }

    /* Red Buttons (Primary + Download) */
    button[kind="primary"],
    div.stDownloadButton > button {
        background-color: #EF4444 !important;
        border: 1px solid #EF4444 !important;
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover,
    div.stDownloadButton > button:hover {
        background-color: #DC2626 !important;
        border-color: #DC2626 !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.25) !important;
        transform: translateY(-1px);
    }
    
    /* Force white text on all red button children */
    button[kind="primary"] *,
    div.stDownloadButton > button * {
        color: #FFFFFF !important;
    }

    /* Secondary Buttons */
    button[kind="secondary"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        color: #475569 !important;
    }
    button[kind="secondary"]:hover {
        background-color: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFA;
        border-right: 1px solid #E2E8F0;
    }

    /* Utils */
    .text-red { color: #EF4444; font-weight: 600; }
    .text-subtle { color: #94A3B8; font-size: 0.8125rem; }
</style>
""", unsafe_allow_html=True)

def main():
    # --- Header (Compact) ---
    col_title, col_settings = st.columns([6, 1])
    with col_title:
        st.markdown("<h1>📈 A股板块轮动猎手</h1>", unsafe_allow_html=True)
        st.markdown("<h3>追踪A股最强风口，锁定龙头与补涨机会</h3>", unsafe_allow_html=True)
    with col_settings:
        if st.button("刷新数据", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


    # --- Sidebar (Hidden by default, clean params) ---
    with st.sidebar:
        st.subheader("功能")
        
        # --- Export Feature ---
        if st.toggle("使用历史日期"):
             selected_date = st.date_input(
                "选择日期",
                value=pd.Timestamp.now().date(),
                max_value=pd.Timestamp.now().date()
            )
             date_str = selected_date.strftime("%Y%m%d")
             export_label = f"⬇️ 导出 {selected_date} 涨停数据"
        else:
             date_str = None # Defaults to "latest" in data_loader
             export_label = "⬇️ 导出今日涨停数据"

        if st.button(export_label, type="primary", use_container_width=True):
             with st.spinner("正在获取涨停数据..."):
                zt_df = data_loader.get_limit_up_pool(date=date_str)
                if not zt_df.empty:
                    export_df = logic.format_limit_up_export(zt_df)
                    
                    # Generate filename
                    final_date_str = date_str if date_str else pd.Timestamp.now().strftime('%Y%m%d')
                    
                    csv = export_df.to_csv(index=False).encode('gbk', errors='ignore') # GBK for Excel/WPS
                    st.download_button(
                        label="点击下载 CSV",
                        data=csv,
                        file_name=f"limit_up_{final_date_str}.csv",
                        mime='text/csv',
                        type='primary' 
                    )
                else:
                    st.error(f"暂无数据 ({date_str if date_str else '今日'}), 可能是非交易日")
        st.divider()
        st.subheader("设置")
        top_n = st.slider("展现板块数", 1, 10,9)
        max_mkt_cap_yi = st.number_input("补涨市值上限 (亿)", 10, 500, 200, 10)
        
        # --- Signal Lab ---
        with st.expander("🎯 信号工坊 (Signal Lab)", expanded=True):
            st.caption("选择叠加因子 (严格与逻辑)")
            
            # Dynamic Checkboxes based on Registry
            # Hardcoded for now based on known Phase 1 signals to ensure order/naming
            # In future, can iterate logic.SIGNAL_REGISTRY
            
            sig_vol = st.checkbox("量比爆发 (>1.5)", value=True, key="sig_vol_ratio")
            sig_div = st.checkbox("板块背离 (滞涨)", value=False, key="sig_sector_divergence")
            sig_cap = st.checkbox("市值下沉 (Bottom 20%)", value=False, key="sig_small_cap")
            
            selected_signal_ids = []
            if sig_vol: selected_signal_ids.append('vol_ratio')
            if sig_div: selected_signal_ids.append('sector_divergence')
            if sig_cap: selected_signal_ids.append('small_cap')
       # 创建主容器
    with st.empty():
        # 创建三个标签页
        tab1, tab2, tab3= st.tabs([ "🏢 龙头股分析","💹 成交量与情绪", "📊 龙股"])
        # --- Step 1: Metrics Row (The "Market Heat" Bar) ---
        # Fetch Data
    with tab1:
        with st.spinner("Analyzing Market..."):
            # 1. Get Ranking
            sector_df = data_loader.get_sector_ranking(top_n=top_n)

            if sector_df.empty:
                st.error("无法获取板块排名，请稍后重试")
                return

            # 2. Parallel Fetching: Global Data + Sector Constituents
            # We do this here so the user waits once, then interactions are instant
            status_text = st.empty()
            status_text.text("正在拉取全市场实时数据...")
            spot_data = data_loader.get_all_market_spot_data()
            status_text.text(f"正在并行扫描 Top {top_n} 板块成分股...")
            sector_names = sector_df['板块名称'].tolist()
            cons_map = data_loader.get_multiple_sector_cons(sector_names)
            status_text.empty() # Clear status

        # Display Top Sectors as a horizontal bar of cards
        cols = st.columns(top_n)
        for i, (index, row) in enumerate(sector_df.iterrows()):
            with cols[i]:
                st.metric(
                    label=row['板块名称'],
                    value=f"{row['涨跌幅']:.2f}%",
                    delta=None # Custom red color handled by CSS
                )

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # --- Step 2: Main Content (Tabs) ---
        # Use tabs to keep it single-page, no scrolling down for other sectors
        tab_names = [f"{row['板块名称']}" for _, row in sector_df.iterrows()]
        tabs = st.tabs(tab_names)

        for i, tab in enumerate(tabs):
            sector_name = sector_df.iloc[i]['板块名称']
            sector_gain = sector_df.iloc[i]['涨跌幅'] # Grab Sector Gain

            with tab:
                # Data Processing: Merge On-Demand (Fast in-memory)
                # Retrieve cons from map
                sector_cons = cons_map.get(sector_name, None)

                if sector_cons is None or spot_data.empty:
                    st.warning("暂无数据 (可能是API限制或网络波动)")
                    continue

                # Inject Sector Gain
                raw_df = data_loader.merge_stock_data(sector_cons, spot_data, sector_gain=sector_gain)

                clean_df = logic.clean_data(raw_df)

                # 2-Column Layout for "Dragons" vs "Laggards"
                # This allows seeing Leaders and Followers side-by-side (One Page concept)
                c1, c2 ,c3= st.columns([1, 1.4,1])

                # --- Column 1: Leaders ---
                with c1:
                    st.markdown("### 🐲龙头梯队")
                    st.markdown("<p class='text-subtle'>高标 / 涨停</p>", unsafe_allow_html=True)

                    dragons = logic.filter_dragons(clean_df)
                    if not dragons.empty:
                        dragons_disp = dragons.copy()
                        dragons_disp['总市值'] = dragons_disp['总市值'] / 100_000_000

                        st.dataframe(
                            dragons_disp[['名称', '最新价', '涨跌幅', '总市值']],
                            height=400, # Fixed height to align
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "涨跌幅": st.column_config.NumberColumn(format="%.2f%%"),
                                "总市值": st.column_config.NumberColumn(label="市值(亿)", format="%.1f"),
                                "最新价": st.column_config.NumberColumn(format="%.2f"),
                            }
                        )
                    else:
                        st.caption("无")

                # --- Column 2: Details & Laggards ---
                with c2:
                    st.markdown("### 🚀补涨挖掘")
                    st.markdown("<p class='text-subtle'>低位 / 活跃 / 资金异动</p>", unsafe_allow_html=True)

                    laggards = logic.filter_laggards(clean_df, max_cap_billion=max_mkt_cap_yi)

                    # Apply Validated Signals (Filtering)
                    if not laggards.empty:
                        laggards = logic.apply_signals(laggards, selected_signal_ids)

                    if not laggards.empty:
                        laggards_disp = laggards.copy()
                        laggards_disp['总市值'] = laggards_disp['总市值'] / 100_000_000

                        # Sort by Volume Ratio descending as specific signal sort is removed
                        laggards_disp = laggards_disp.sort_values(by='量比', ascending=False)

                        st.dataframe(
                            laggards_disp[['名称', '最新价', '涨跌幅', '量比', '换手率', '总市值']],
                            height=400,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "涨跌幅": st.column_config.NumberColumn(format="%.2f%%"),
                                "总市值": st.column_config.NumberColumn(label="市值", format="%.0f"),
                                "量比": st.column_config.NumberColumn(format="%.1f"),
                                "换手率": st.column_config.NumberColumn(label="换手", format="%.0f%%"),
                            }
                        )

                        # CSV Export (Minimal text link style)
                        csv = laggards_disp.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            label="下载 CSV",
                            data=csv,
                            file_name=f"{sector_name}_alpha.csv",
                            mime='text/csv',
                            key=f"dl_{i}"
                        )
                    else:
                        st.info("暂无符合条件标的")

    with tab2:
        # 第一个tab显示成交额和情绪指标
        with st.spinner("Analyzing Market..."):
            # 1. Get Ranking
            k1 = red.xiangt()

            if k1.empty:
                st.error("无法获取板块排名，请稍后重试")
                return

            # 2. Parallel Fetching: Global Data + Sector Constituents
            # We do this here so the user waits once, then interactions are instant
            status_text = st.empty()
            status_text.text("正在拉取全市场实时数据...")
            k2 = data_loader.get_all_market_spot_data()
            status_text.text(f"正在并行扫描 Top {top_n} 板块成分股...")
            k3 = k1['板块名称'].tolist()
            k4 = data_loader.get_multiple_sector_cons(k3)
            status_text.empty()  # Clear status

        # Display Top Sectors as a horizontal bar of cards
        cols = st.columns(top_n)
        for i, (index, row) in enumerate(k1.iterrows()):
            with cols[i]:
                st.metric(
                    label=row['板块名称'],
                    value=f"代码：{row['代码']}",
                    delta=None  # Custom red color handled by CSS
                )

        st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

        # --- Step 2: Main Content (Tabs) ---
        # Use tabs to keep it single-page, no scrolling down for other sectors
        k5 = [f"{row['板块名称']}" for _, row in k1.iterrows()]
        k6 = st.tabs(k5)

        for i, tab in enumerate(k6):
            k7 = k1.iloc[i]['板块名称']

            with tab:
                # Data Processing: Merge On-Demand (Fast in-memory)
                # Retrieve cons from map
                k9 = k4.get(k7, None)

                if k9 is None or k2.empty:
                    st.warning("暂无数据 (可能是API限制或网络波动)")
                    continue

                # Inject Sector Gain
                k10 = data_loader.merge_stock_data(k9, k2, sector_gain=None)

                k11 = logic.clean_data(k10)
                # 2-Column Layout for "Dragons" vs "Laggards"
                # This allows seeing Leaders and Followers side-by-side (One Page concept)
                c1, c2, c3 = st.columns([1, 1.4, 1])
                # --- Column 1: Leaders ---
                with c1:
                    st.markdown("### 🐲龙头梯队")
                    st.markdown("<p class='text-subtle'>高标 / 涨停</p>", unsafe_allow_html=True)

                    k13 = logic.tidui(k11)
                    if not k13.empty:
                        dragons_disp = k13.copy()
                        dragons_disp['总市值'] = dragons_disp['总市值'] / 100_000_000

                        st.dataframe(
                            dragons_disp[['名称', '最新价', '涨跌幅', '总市值']],
                            height=400,  # Fixed height to align
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "涨跌幅": st.column_config.NumberColumn(format="%.2f%%"),
                                "总市值": st.column_config.NumberColumn(label="市值(亿)", format="%.1f"),
                                "最新价": st.column_config.NumberColumn(format="%.2f"),
                            }
                        )
                    else:
                        st.caption("无")

                        # --- Column 2: Details & Laggards ---
                        with c2:
                            st.markdown("### 🚀补涨挖掘")
                            st.markdown("<p class='text-subtle'>低位 / 活跃 / 资金异动</p>", unsafe_allow_html=True)

                            laggards = logic.tidui(k11, max_cap_billion=max_mkt_cap_yi)

                            # Apply Validated Signals (Filtering)
                            if not laggards.empty:
                                laggards = logic.apply_signals(laggards, selected_signal_ids)

                            if not laggards.empty:
                                laggards_disp = laggards.copy()
                                laggards_disp['总市值'] = laggards_disp['总市值'] / 100_000_000

                                # Sort by Volume Ratio descending as specific signal sort is removed
                                laggards_disp = laggards_disp.sort_values(by='量比', ascending=False)

                                st.dataframe(
                                    laggards_disp[['名称', '最新价', '涨跌幅', '量比', '换手率', '总市值']],
                                    height=400,
                                    use_container_width=True,
                                    hide_index=True,
                                    column_config={
                                        "涨跌幅": st.column_config.NumberColumn(format="%.2f%%"),
                                        "总市值": st.column_config.NumberColumn(label="市值", format="%.0f"),
                                        "量比": st.column_config.NumberColumn(format="%.1f"),
                                        "换手率": st.column_config.NumberColumn(label="换手", format="%.0f%%"),
                                    }
                                )

                                # CSV Export (Minimal text link style)
                                csv = laggards_disp.to_csv(index=False).encode('utf-8-sig')
                                st.download_button(
                                    label="下载 CSV",
                                    data=csv,
                                    file_name=f"{k3}_alpha.csv",
                                    mime='text/csv',
                                    key=f"dl_{i}"
                                )
                            else:
                                st.info("暂无符合条件标的")
    with tab3:
        # 第一个tab显示成交额和情绪指标
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 🎯 市场成交与情绪分析")

        try:
            data = qingxu.get_market_heat()
        except Exception:
            st.error("开盘期间，无法获取数据，请稍后刷新。")
            return

        # 使用多列布局显示主要指标
        metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)

        with metrics_col1:
            avg_amount = data["数值"][9]  # 5日均值（亿）
            pred_amount = data["数值"][8]  # 预估成交额（亿）

            # 预估成交额指标
            if pred_amount is not None:
                delta_vs_avg = pred_amount - avg_amount
                delta_color = "normal" if delta_vs_avg > 0 else "inverse"
                st.metric(
                    "预估成交额",
                    f"{pred_amount:,}亿",
                    delta=f"{delta_vs_avg:+,}亿 vs 5日均值",
                    delta_color=delta_color,
                )

        with metrics_col2:
            up_ratio = data["数值"][14]  # 上涨占比（%）
            st.metric("上涨占比", f"{up_ratio:.1f}%")

        with metrics_col3:
            limit_up = data["数值"][15]  # 涨停数量
            limit_down = data["数值"][16]  # 跌停数量
            st.metric(
                "涨停数量",
                str(limit_up),
                delta=f"-跌停 {limit_down}",
                delta_color="inverse",
            )

        with metrics_col4:
            middle_change = data["数值"][11]  # 中位数涨幅（%）
            st.metric(
                "中位数涨幅",
                f"{middle_change:.2f}%",
                delta=None,
                delta_color="inverse" if middle_change > 0 else "normal",
            )

        # 分两列显示详细数据
        col1, col2 = st.columns(2)

        with col1:

            def get_progress_html(value_pct):
                """根据百分比返回进度条HTML"""

                def get_color(pct):
                    if pct <= 20:
                        return "#90d4a2"  # 绿色
                    elif pct <= 40:
                        return "#27ae60"  # 深绿色
                    elif pct <= 60:
                        return "#f1c40f"  # 黄色
                    elif pct <= 80:
                        return "#e67e22"  # 橙色
                    else:
                        return "#e74c3c"  # 红色

                color = get_color(value_pct)
                width = value_pct  # percentage已经是百分比值，不需要再乘100
                return f"""
                                   <div style="
                                       width: 100%;
                                       background-color: #eee;
                                       border-radius: 3px;
                                       padding: 3px;
                                       box-sizing: border-box;
                                   ">
                                       <div style="
                                           width: {width}%;
                                           height: 20px;
                                           background-color: {color};
                                           border-radius: 2px;
                                           transition: width 0.3s ease;
                                       "></div>
                                   </div>
                               """

            st.markdown(
                """
            <style>
            .index-progress {
                margin-bottom: 1rem;
            }
            .index-progress .label {
                margin-bottom: 0.5rem;
                font-weight: 500;
                color: #333;
            }
            .index-progress .value {
                font-size: 0.9rem;
                color: #666;
                margin-top: 0.3rem;
                text-align: right;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            st.markdown("#### 💰 指数成交占比")

            # 总成交额（亿）
            total = data["数值"][3]

            # 定义指数数据
            indices = [
                ("上证指数", data["数值"][0]),
                ("深证指数", data["数值"][1]),
                ("创业板", data["数值"][2]),
                ("中证1000", data["数值"][5] * total / 100),  # 转换百分比为实际值
                ("中证2000", data["数值"][6] * total / 100),  # 转换百分比为实际值
                ("沪深300", data["数值"][7] * total / 100),  # 转换百分比为实际值
            ]

            # 显示各指数进度条
            for name, amount in indices:
                st.markdown('<div class="index-progress">', unsafe_allow_html=True)
                cols = st.columns([2, 8])
                with cols[0]:
                    st.markdown(
                        f'<div class="label">{name}</div>', unsafe_allow_html=True
                    )
                with cols[1]:
                    percentage = (amount / total) * 100  # 转换为百分比
                    progress_html = get_progress_html(percentage)
                    st.markdown(progress_html, unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="value">{percentage:.1f}%</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            # 显示总成交额和5日均值
            cols = st.columns(2)
            with cols[0]:
                st.info(f"**总成交额**: {data['数值'][3]} 亿")
            with cols[1]:
                st.info(f"**5日均值**: {data['数值'][9]} 亿")

        with col2:
            st.markdown("#### 💡 情绪指标")
            for item, value in zip(data["指标"][10:17], data["数值"][10:17]):
                # 处理带颜色标记的值
                output = f"**{item}**: {value}"
                # More Pythonic way to check for specific substrings
                if any(keyword in item for keyword in ["百分比", "涨幅"]):
                    output = output + "%"
                if value > 0:
                    st.success(output)
                else:
                    st.error(output)


if __name__ == "__main__":
    main()
