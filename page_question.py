import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import time
from utils import *
s = os.path.dirname(os.path.abspath(__file__))

OFFLINE_RANGE_NAME = "offline!A1:D"
INPUT_RANGE_NAME = "input!A1:B"
OUTPUT_RANGE_NAME = "output!A1:F"
USER_RANGE_NAME = "user!A1:A"

def btn_continue(page, id):
    if st.button("Continue", key=f"continue_{id}"):
        with open(os.path.join(s ,"temp.json"), "w") as f:
            json.dump(dict(st.session_state), f, ensure_ascii=False)
        st.switch_page(page)

        
def btn_reset(id):
    if st.button("Reset", key=f"reset_{id}"):
        for i in st.session_state.keys():
            if i != "index" and i != "new_index":
                del st.session_state[i]
            else:
                st.session_state[i] = 0
        with open(os.path.join(s ,"temp.json"), "w") as f:
            json.dump(dict(st.session_state), f, ensure_ascii=False)
        st.switch_page("page_question.py")
        st.rerun()
        
def btn_submit(id):
    with open(os.path.join(s ,"Data","output.csv"),"rb") as f:
        st.download_button(
            label="Submit",
            data = f ,
            file_name=os.path.join(s ,"Data","output.csv"),
            mime='text/csv',
        )
    st.toast('Dữ liệu đã được ghi lại') 
    # if st.button("Submit", key=f"submit_{id}"):
    #     output_data = read_output_file(os.path.join(s ,"Data","output.csv"))
    #     if not output_data.empty:
    #         indexes = [int(i.split("_")[0]) for i in output_data["id"].to_list()]
    #         input_data = pd.read_csv(os.path.join(s ,"Data","input.csv"))
    #         input_data = update_input_file(input_data, indexes, os.path.join(s ,"Data","input.csv"))     
    #         update_input_data(input_data, INPUT_RANGE_NAME)
    #         update_output_data(output_data, OUTPUT_RANGE_NAME)
    #         os.remove(os.path.join(s ,"Data","output.csv"))  
    #         os.remove(os.path.join(s ,"Data","input.csv"))  
    #         os.remove(os.path.join(s ,"Data","user.csv"))  
    #     st.toast('Dữ liệu đã được ghi lại')    
    #     time.sleep(1)

def read_output_file(path):
    if os.path.exists(path):
        data = pd.read_csv(path)
    else:
        data = pd.DataFrame()
    return data

def update_input_file(data, index, input_path):
    data = data.drop(index, axis=0)
    data.to_csv(input_path, index=False)
    return data
           
        
def btn_footer(next_page, id):
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([1,1,1,9])
    with col1: btn_reset(id)
    with col2: btn_submit(id)
    with col3: btn_continue(next_page, id)
    
def btn_random(index):
    btn_random = st.button("Lấy câu hỏi từ cơ sở dữ liệu")
    if btn_random:
        st.session_state.index = random.choice(index)
        st.session_state.self_fill = False
        st.session_state.question = get_question(data, st.session_state.index)
        st.rerun()
    

st.set_page_config(
    layout="wide",  
)

def text_input():
    st.session_state.question = st.session_state.text
    st.session_state.new_index += 1
    st.session_state.self_fill = True
    st.session_state.text = ""
    return


if __name__ == "__main__":
    with open(os.path.join(s,"temp.json"), "r") as f:
        temp = json.load(f)
    
    if "question"not in st.session_state:
        st.session_state.question = ""

    if "self_fill"not in st.session_state:
        st.session_state.self_fill = False
    if "text"not in st.session_state:
        st.session_state.text = ""

    col1, col2 = st.columns([9,1])
    with col1: st.title('Phần 1: Chọn câu hỏi mà bạn muốn đánh nhãn')
    with col2: st.toggle("Online", False, key="toggle")
    st.markdown("---") 
    if st.session_state.toggle == False:
        data = pd.read_csv(os.path.join(s ,"Data","offline_input.csv"))

        if "index"not in st.session_state:
            st.session_state.index = data["id"].to_list()[0]
        if "new_index"not in st.session_state:
            st.session_state.new_index = 0
        if "context"not in st.session_state:
            st.session_state.context = ""
        st.session_state.context = str(data[data["id"] == st.session_state.index ]["context"].to_list()[0] \
            if (len(data[data["id"] == st.session_state.index ]["context"].to_list()) > 0) else "")
        st.session_state.disabled = True     
        page = "pages/page_answer.py"
    else:
        data = get_and_save_data(INPUT_RANGE_NAME, os.path.join(s ,"Data","input.csv"))
        if "index"not in st.session_state:
            st.session_state.index = temp["index"]
        if "new_index"not in st.session_state:
            st.session_state.new_index = temp["new_index"]
        st.session_state.disabled = False
        page = "pages/page_context.py"
    


    user = get_and_save_data(USER_RANGE_NAME, os.path.join(s ,"Data","user.csv"))
    st.header("Câu hỏi: "+ st.session_state.question)
    users = user["user"].dropna().unique().tolist()
    option = st.selectbox(
        "Bạn là:",
        users,
        index=None,
        key="user"
    )
    st.text_input("Bạn có thể nhập câu hỏi vào ô bên dưới", value="", max_chars=None, key="text", type="default", 
                    help="Nhập câu hỏi ví dụ sinh viên có thể hỏi", on_change=text_input, 
                    placeholder="Nhập câu hỏi", disabled=st.session_state.disabled, label_visibility="visible")
                    
    st.write("Hoặc")
    btn_random(data["id"].to_list())
    btn_footer(page, "question_page")

        

        
    


