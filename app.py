import streamlit as st
import requests
import os

from PIL import Image
from pyzbar.pyzbar import decode
from qr_utils import handle_qr_image, follow_redirect


def load_css(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(
    page_title="큐싱 예방",
    page_icon="🫆",
    layout="centered"
)

load_css("src/styles.css")

st.markdown("<h1 class='neon-title'> 🔐 SpamMayo</h1>", unsafe_allow_html=True)

st.caption("큐싱을 방지하기 위한 URL Detection입니다. ")
options = ["QR 코드 인식",  "QR 이미지 업로드", "URL 직접 입력",]

selection = st.segmented_control(
    "", options, width="stretch"
) 

# Selection button 클릭 > QR 코드 인식 
if selection == "QR 코드 인식":
    with st.container(border=True):
        enable = st.checkbox("카메라 허용")
        picture = st.camera_input("QR 코드를 찍어주세요", disabled=not enable)

        if picture:
            handle_qr_image(picture)

# Selection button 클릭 > QR 이미지 업로드
elif selection == "QR 이미지 업로드":
    uploaded_files = st.file_uploader(
        "QR 이미지 업로드",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.image(uploaded_file)
            handle_qr_image(uploaded_file)

# Selection button 클릭 > URL 직접 입력
elif selection == "URL 직접 입력": 
    with st.form(key="button_form"): 
        st.text_input(":gray-background[:gray[예 : www.google.com 과 같은 url을 입력하세요.]]") 
        st.form_submit_button("검사하기", width="stretch")
        written_url = None
