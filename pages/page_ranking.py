import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import random
import subprocess
import time
from utils import *

def btn_finish(id):
    if not has_warning:
        if st.button("Finish", key=f"finish_{id}"):
            ranking = [st.session_state[f"ranking_{i+1}"] for i in range(len(chosen_answer))]
            if st.session_state.best_answer != "":
                chosen_answer.append(st.session_state.best_answer)
                ranking.append(5)
            data = {"id":f"{st.session_state.index}_{st.session_state.new_index}",
                    "question": st.session_state.question,	
                    "context":  st.session_state.context,	
                    "answers": 	chosen_answer,
                    "scores": 	ranking,
                    "user": st.session_state.user}

            if os.path.exists(os.path.join(s ,"Data","output.csv")):
                output_data = pd.read_csv(os.path.join(s ,"Data","output.csv"))
            else:
                output_data = pd.DataFrame(columns=["id","question","context", "answers", "scores", "user"])
            output_data = output_data._append(data, ignore_index=True)
            output_data.to_csv(os.path.join(s ,"Data","output.csv"), index=False)
            if st.session_state.self_fill==False:
                if st.session_state.toggle==False:
                    input_data = pd.read_csv(os.path.join(s ,"Data","offline_input.csv"))
                    input_data = input_data.drop(input_data[input_data["id"]==st.session_state.index].index, axis='index')
                    input_data.to_csv(os.path.join(s ,"Data","offline_input.csv"), index=False)
                else:
                    input_data = pd.read_csv(os.path.join(s ,"Data","input.csv"))
                    input_data = input_data.drop(input_data[input_data["id"]==st.session_state.index].index, axis='index')
                    input_data.to_csv(os.path.join(s ,"Data","input.csv"), index=False)
            for key in st.session_state.keys():
                if key != "index" and key != "new_index":
                    del st.session_state[key]
                else:
                    st.session_state[i] = 0
            with open(os.path.join(s ,"temp.json"), "w") as f:
                json.dump(dict(st.session_state), f, ensure_ascii=False)
            subprocess.run("git add .", shell=True)
            subprocess.run("git commit -m 'update'", shell=True)
            subprocess.run("git push", shell=True)
            st.switch_page("page_question.py")
        
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
    if st.button("Submit", key=f"submit_{id}"):
        output_data = read_output_file(os.path.join(s ,"Data","output.csv"))
        if not output_data.empty:
            indexes = [int(i.split("_")[0]) for i in output_data["id"].to_list()]
            input_data = pd.read_csv(os.path.join(s ,"Data","input.csv"))
            input_data = update_input_file(input_data, indexes, os.path.join(s ,"Data","input.csv"))     
            update_input_data(input_data, INPUT_RANGE_NAME)
            update_output_data(output_data, OUTPUT_RANGE_NAME)
            os.remove(os.path.join(s ,"Data","output.csv"))  
            os.remove(os.path.join(s ,"Data","input.csv"))  
            os.remove(os.path.join(s ,"Data","user.csv"))  
        st.toast('Dữ liệu đã được ghi lại')    
        time.sleep(1)
        # st.rerun()

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
           
        
def btn_footer(id):
    st.markdown("---")
    col1, col2, col3, col4 = st.columns([1,1,1,9])
    with col1: btn_reset(id)
    with col2: btn_submit(id)
    with col3: btn_finish(id)

if __name__ == "__main__":
    s = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    chosen_answer = [i for e,i in enumerate(st.session_state.answers) if st.session_state.answer_tags[e] == True]
    with open(os.path.join(s,"temp.json"), "r") as f:
        temp = json.load(f)

    for key in temp.keys():
        try:
            st.session_state[key] = temp[key]
        except:
            continue
    guilding_md = os.path.join(s, "hf_instruction" , "guilding.md")
    st.title("Phần 4: Xếp hạng các câu trả lời")
    st.markdown("---")
    st.header("Câu hỏi: "+ st.session_state.question)
    st.write("Ngữ cảnh: "+ st.session_state.context)
    
    scores = {sentence: 3 for sentence in chosen_answer} 

    score_counts = {i: 0 for i in range(1, 6)}
    duplicate_score = set()
    
    # Biến cờ để theo dõi trạng thái cảnh báo
    has_warning = False
    max_occurrences = 2
    col1, col2, col3 = st.columns([6,6,4])
    with col1: 
        with open(guilding_md, "r", encoding="utf-8") as file:
            md_content = file.read()
        st.markdown(md_content, unsafe_allow_html=True)
    with col2:
        st.subheader("To be ranked (1 = best, 5 = worst)")
        for i, sentence in enumerate(chosen_answer):
            score = st.slider(f"{sentence}", 1, 5,  st.session_state[f"ranking_{i+1}"] if f"ranking_{i+1}" in st.session_state.keys() else 0, key=f"ranking_{i+1}")
                
            if score != 0:
                # Kiểm tra nếu có điểm giống nhau
                if score_counts[score] >= max_occurrences:
                    duplicate_score.add(score)
                    has_warning = True

                score_counts[score] += 1
            scores[sentence] = score
        if has_warning:
            st.warning(f"Các câu có cùng điểm {duplicate_score} đã vượt quá {max_occurrences} lần xuất hiện. Số lần xuất hiện của từng điểm là {score_counts}.")
    with col3:
        st.text_input("Nếu bạn không hài lòng với câu trả lời của chúng tôi, hãy nhập câu trả lời mà bạn mong muốn", 
                      value="", max_chars=None, key="best_answer", type="default", help="Nhập câu trả lời tốt nhất", 
                      placeholder="Nhập câu trả lời", disabled=False, label_visibility="visible")
    btn_footer("ranking_page")
