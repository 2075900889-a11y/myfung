import streamlit as st
import requests
import re
import json

st.set_page_config(page_title="估值助手", layout="wide")
st.title("🍎 我的基金实时估值")

# 输入框，手机端默认显示两个示例
codes_input = st.text_input("输入代码(逗号隔开):", "000001,005827")

if codes_input:
    codes = codes_input.replace("，", ",").split(",")
    for code in codes:
        code = code.strip()
        url = f"https://fundgz.1234567.com.cn/js/{code}.js"
        try:
            res = requests.get(url, timeout=5)
            data = json.loads(re.findall(r"\((.*)\)", res.text)[0])
            # 这里的 gszzl 是估算涨跌幅
            color = "red" if float(data['gszzl']) > 0 else "green"
            st.metric(label=f"{data['name']} ({code})", 
                      value=data['gsz'], 
                      delta=f"{data['gszzl']}%")
        except:
            st.error(f"代码 {code} 没找到")

if st.button('点击刷新'):
    st.rerun()
