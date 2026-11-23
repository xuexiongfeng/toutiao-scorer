import streamlit as st
import requests
import json

API_KEY = st.secrets["DEEPSEEK_API_KEY"]

st.title("头条选题打分器")
st.write("输入标题和一句话简介，让 AI 按热度 / 相关性 / 冲突性打分，总分 4 分以上才写。")

topic = st.text_input("选题标题")
desc = st.text_area("一句话简介 / 内容要点")

if st.button("让 AI 打分"):
    if not topic:
        st.warning("先输一个选题标题")
    else:
        url = "https://api.deepseek.com/chat/completions"
        headers = {"Authorization": "Bearer " + API_KEY, "Content-Type": "application/json"}
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "你是一个头条选题编辑。按热度、相关性、冲突性各打 0、1 或 2 分，只返回 JSON，不要多余文字，格式：{\"heat\": 2, \"relevance\": 1, \"conflict\": 1, \"reason\": \"一句话理由\"}"},
                {"role": "user", "content": "选题标题：" + topic + "\n简介：" + desc},
            ],
        }
        resp = requests.post(url, headers=headers, json=data, timeout=60)
        reply = resp.json()["choices"][0]["message"]["content"]
        reply = reply.replace("```json", "").replace("```", "").strip()
        score = json.loads(reply)
        total = score["heat"] + score["relevance"] + score["conflict"]

        st.metric("总分", total)
        st.write("热度", score["heat"], "相关性", score["relevance"], "冲突性", score["conflict"])
        st.write(score["reason"])
        if total >= 4:
            st.success("总分 >= 4，可以写")
        else:
            st.warning("总分不到 4，先换角度，别硬写")

        with open("scores.txt", "a", encoding="utf-8") as f:
            f.write(f"{topic}，{total}分，{score['reason']}\n")
        st.write("已保存到 scores.txt")
