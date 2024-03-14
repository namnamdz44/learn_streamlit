import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from page_question import btn_footer
from utils import get_context

s = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# def get_context(question):
#     return ["Hello there", "General Kenobi"]

def get_offline_context(question):
    data = pd.read_csv(os.path.join(s, "Data/offline_input.csv"))
    return eval(data[data["question"]==question]["context"].to_list()[0]) + ["Các ngữ cảnh trên đều không thể trả lời được câu hỏi"]

if __name__ == "__main__":
    # print(get_offline_context("Em muốn xin lại bảng điểm thi tốt nghiệp THPT 2021 có được không ạ ?"))
    with open(os.path.join(s,"temp.json"), "r") as f:
        temp = json.load(f)

    for key in temp.keys():
        try:
            st.session_state[key] = temp[key]
        except:
            continue
        

    st.title('Phần 2: Chọn ngữ cảnh có thể có thể trả lời được câu hỏi')
    st.markdown("---") 

    st.header("Câu hỏi: "+ st.session_state.question)
    if st.session_state.toggle == True:
        context_list = get_context(st.session_state.question)
    else:
        context_list = get_offline_context(st.session_state.question)
        
    if "context_list" not in st.session_state:
        st.session_state.context_list = context_list
    if "context_tags" not in st.session_state:
        st.session_state.context_tags = []
    if "context" not in st.session_state:
        st.session_state.context = ""
    context_tags = []    
    st.write("Chọn ngữ cảnh có thể dùng để trả lời câu hỏi")
    for e,i in enumerate(st.session_state.context_list):
        a = st.checkbox(i, False, key=f"context_{e}")
        context_tags.append(st.session_state[f"context_{e}"])
    st.session_state.context_tags = context_tags
    st.session_state.context = "\n".join([i for e,i in enumerate(st.session_state.context_list) if st.session_state.context_tags[e] == True])
    
    # context_chose = st.radio(
    # "Chọn ngữ cảnh có thể dùng để trả lời câu hỏi",
    # context_list,
    # index=None, 
    # key="context")

    btn_footer("pages/page_answer.py", "context_page")
