import streamlit as st
import requests
import re
import json
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="私人基金管家", layout="wide")

st.title("🍎 我的动态基金管家")
st.caption("直接在下方表格修改数据，页面会自动计算并更新图表")

# 1. 初始化持仓数据（如果想永久保存，下次改这里）
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame([
        {"代码": "011043", "名称": "沪港深价值", "份额": 1000.0, "成本价": 1.25},
        {"代码": "005827", "名称": "易方达蓝筹", "份额": 500.0, "成本价": 2.10}
    ])

# 2. 动态编辑表格
st.subheader("📝 我的持仓配置")
edited_df = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",  # 可以点击下方 (+) 号添加新行
    use_container_width=True,
    column_config={
        "代码": st.column_config.TextColumn("基金代码", help="输入6位代码"),
        "份额": st.column_config.NumberColumn("持有份额", min_value=0, format="%.2f"),
        "成本价": st.column_config.NumberColumn("买入成本", min_value=0, format="%.4f"),
    }
)

# 存储计算结果的列表
results = []
total_day_profit = 0
total_market_value = 0

# 3. 获取实时数据并计算
if st.button('🚀 开始计算并更新行情'):
    with st.spinner('正在调取实时行情...'):
        for index, row in edited_df.iterrows():
            code = row['代码']
            url = f"https://fundgz.1234567.com.cn/js/{code}.js"
            try:
                res = requests.get(url, timeout=5)
                data = json.loads(re.findall(r"\((.*)\)", res.text)[0])
                
                gsz = float(data['gsz'])      # 估值
                dwjz = float(data['dwjz'])    # 昨收净值
                
                curr_value = row['份额'] * gsz
                day_profit = row['份额'] * (gsz - dwjz)
                total_profit = row['份额'] * (gsz - row['成本价'])
                
                results.append({
                    "基金名称": data['name'],
                    "市值": curr_value,
                    "今日盈亏": day_profit,
                    "总盈亏": total_profit,
                    "涨跌幅": float(data['gszzl'])
                })
                total_day_profit += day_profit
                total_market_value += curr_value
            except:
                st.error(f"代码 {code} 好像不对哦，请检查")

    # 4. 展示看板
    if results:
        res_df = pd.DataFrame(results)
        
        # 顶部指标
        c1, c2, c3 = st.columns(3)
        c1.metric("今日总盈亏", f"¥{total_day_profit:.2f}")
        c2.metric("持仓总市值", f"¥{total_market_value:.2f}")
        c3.metric("整体涨跌", f"{(total_day_profit/(total_market_value-total_day_profit)*100):.2f}%" if total_market_value !=0 else "0%")

        # 5. 可视化图表
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.write("📈 各基金盈亏对比")
            st.bar_chart(res_df.set_index("基金名称")["今日盈亏"])
            
        with col_right:
            st.write("🍰 持仓分布图")
            fig = px.pie(res_df, values='市值', names='基金名称', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        # 详细列表
        st.write("📋 详细数据明细")
        st.table(res_df)

st.divider()
st.info("💡 提示：点击表格最下方的 (+) 可以添加新基金；选中行按 Delete 可以删除。")
