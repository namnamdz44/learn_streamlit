import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import random
from utils import *
from page_question import btn_footer


# def get_answer(question, context, model="/media/namln/home3/all_model/gpt2"):
#     return ["Hello there"]

def get_offline_answer(index):
    data = pd.read_csv(os.path.join(s, "Data/offline_input.csv"))
    return eval(data[data["id"] == index]["all_answer"].to_list()[0])

if __name__ == "__main__":
    s = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    with open(os.path.join(s,"temp.json"), "r") as f:
        temp = json.load(f)

    for key in temp.keys():
        try:
            st.session_state[key] = temp[key]
        except:
            continue

    if "answers"not in st.session_state:
        st.session_state.answers = []
    if "answer_tags"not in st.session_state:
        st.session_state.answer_tags = []
        
    st.title('Phần 3: Chọn câu trả lời phù hợp với câu hỏi')
    st.markdown("---") 
    st.header("Câu hỏi: "+ st.session_state.question)
    st.write("Ngữ cảnh: "+ st.session_state.context)
    criteria_md = os.path.join(s, "hf_instruction" , "criteria.md")
    answers = []
    answer_tags = []
    model_list = ["vinallama_b1_ft_b2_fix"]
        
    if st.session_state.toggle == True:
        if len(st.session_state.answers) == 0:
            for model in model_list:
                answers += get_answer(temp["question"], temp["context"], model, nums=7, temperature=0.7)
            st.session_state.answers = answers
    else:
        if len(st.session_state.answers) == 0:
            st.session_state.answers = get_offline_answer(st.session_state.index)



    criteria, answer_col = st.columns([4,6])
    with criteria:
        with open(criteria_md, "r", encoding="utf-8") as file:
            md_content = file.read()
        st.markdown(md_content, unsafe_allow_html=True)
    with answer_col:
        for e,i in enumerate(st.session_state.answers):
            a = st.checkbox(i, False, key=f"answer_{e}")
            answer_tags.append(st.session_state[f"answer_{e}"])
    st.session_state.answer_tags = answer_tags
    
    btn_footer("pages/page_ranking.py", "answer_page")
