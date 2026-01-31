import streamlit as st
import requests
import re
import json

st.set_page_config(page_title="估值助手", layout="wide")
st.title("🍎 我的基金实时估值")

# 默认展示的基金代码
codes_input = st.text_input("输入基金代码(多个用逗号隔开):", "011043,005827")

if codes_input:
    codes = codes_input.replace("，", ",").split(",")
    for code in codes:
        code = code.strip()
        if not code: continue
        url = f"https://fundgz.1234567.com.cn/js/{code}.js"
        try:
            res = requests.get(url, timeout=5)
            data = json.loads(re.findall(r"\((.*)\)", res.text)[0])
            val_change = float(data['gszzl'])
            # 这里的指标展示
            st.metric(label=f"{data['name']} ({code})", 
                      value=f"估值: {data['gsz']}", 
                      delta=f"{data['gszzl']}%")
            st.write(f"更新时间: {data['gztime']}")
            st.divider()
        except:
            st.error(f"代码 {code} 查询失败，请检查输入是否正确")

if st.button('🔄 刷新数据'):
    st.rerun()
