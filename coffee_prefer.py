import streamlit as st
import pandas as pd
import csv
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os


def cosine_similarity(my_scores, coffee_scores, features):
    v1 = np.array([float(my_scores[f]) for f in features])
    v2 = np.array([float(coffee_scores[f]) for f in features])

    cos_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    # print(f"餘弦相似度: {cos_sim:.3f}")
    return cos_sim

def find_best_coffee(my_scores,features):
    best_score = 0
    best_coffee = None
    best_row = None
    recommand_sort = []

    with open('coffee_item.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            coffee_name = row['coffee_name']

            # score 1
            # diff_score = 0
            # for feature in features:
            #     diff_score += abs(float(my_scores[feature])-float(row[feature]))
            
            # score 2 - cos
            suit_score = cosine_similarity(my_scores, row, features)
            recommand_sort.append({"coffee_name":coffee_name,"suit_score":suit_score})

            # if diff_score < best_score:
            if suit_score > best_score:
                best_score = suit_score
                best_coffee = coffee_name
                best_row = row

            
            # print(coffee_name, f"餘弦相似度: {suit_score:.3f}")

    recommand_sort = sorted(recommand_sort, key=lambda x: x['suit_score'], reverse=True)
    # print("row format", best_row)
    coffee_name = best_row.pop('coffee_name', None)
    return best_coffee, best_row, best_score, recommand_sort

st.markdown("<h1 style='text-align: center;'>橘時冰滴咖啡喜好測試</h1>", unsafe_allow_html=True)

#分類題目
features = ["香", "甜", "酸", "澀", "苦"]
scores = {}

#表單輸入
with st.form("score_form"):
    st.subheader("請對每項目根據喜好給予 1~5 分：")
    st.markdown("<h5>分數越高代表喜歡該風味越重</h5>", unsafe_allow_html=True)
    for feature in features:
        scores[feature] = st.slider(feature, min_value=1, max_value=5, value=3)
    submitted = st.form_submit_button("送出")

#若送出則處理邏輯與繪圖
if submitted:

    best_coffee, best_row, best_score, recommand_sort = find_best_coffee(scores,features)
    # 轉為 DataFrame
    my_df = pd.DataFrame(dict(
        r = list(scores.values()) + [list(scores.values())[0]],  # 雷達圖需首尾相接
        theta = features + [features[0]]
    )) 
    best_df = pd.DataFrame(dict(
        r = list(best_row.values()) + [list(best_row.values())[0]],  # 雷達圖需首尾相接
        theta = features + [features[0]]
    )) 

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=my_df['r'],
        theta=my_df['theta'],
        name='我的喜好',
        line=dict(shape='linear',color='red'),
        fill='none'
    ))

    fig.add_trace(go.Scatterpolar(
        r=best_df['r'],
        theta=best_df['theta'],
        name=best_coffee,
        line=dict(shape='linear'),
        fill='none'
    ))

    fig.update_layout(
    title=f'最適合你的咖啡：{best_coffee}（適合度{round(best_score*100,1)}%）<br>其他推薦：{recommand_sort[1]["coffee_name"]}（適合度{round(recommand_sort[1]["suit_score"]*100,1)}%）或 {recommand_sort[2]["coffee_name"]}（適合度{round(recommand_sort[2]["suit_score"]*100,1)}%）',
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 5]
        ),
        angularaxis=dict(
            rotation=90  # 這裡調整角度
        )
    ),
    showlegend=True
)
    st.plotly_chart(fig)

    image_filepath = "coffee_info"

    if os.path.exists(os.path.join(image_filepath,f"{best_coffee}.webp")):
        coffee_image_path = os.path.join(image_filepath,f"{best_coffee}.webp")
    elif os.path.exists(os.path.join(image_filepath,f"{best_coffee}.png")):
        coffee_image_path = os.path.join(image_filepath,f"{best_coffee}.png")
    else:
        coffee_image_path = None

    if coffee_image_path is not None:
        st.image(coffee_image_path, caption=f"{best_coffee}", use_container_width=True)

    
    

    st.success("✅ 歡迎到店試喝，Enjoy your day!")