import streamlit as st
import os

from src.dummy_threshold_rf import ThresholdedRF
from src.qr_utils import handle_qr_image, follow_redirect
from src.url_analysis import render_url_analysis
from src.feature_extractor import URLFeatureExtractor  # (안 쓰면 삭제해도 됨)

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

# QR 코드 인식
if selection == "QR 코드 인식":
    with st.container(border=True):
        enable = st.checkbox("카메라 허용")
        picture = st.camera_input("QR 코드를 찍어주세요", disabled=not enable)

        if picture is not None:
            bytes_data = picture.getvalue()
            # 1) QR 인식
            qr_text, final_url = handle_qr_image(picture)

            if qr_text is None:
                st.stop()

            # 2) 최종 URL 결정
            target_url = final_url or qr_text

            # 3) 리디렉션 처리
            try:
                resolved_url = follow_redirect(target_url)
                st.info(f"최종 리디렉션 URL: {resolved_url}")
            except Exception as e:
                st.error(f"리디렉션 처리 중 오류 발생 : {e}")
                resolved_url = target_url

            # 4) 공통 분석 + UI 렌더링
            render_url_analysis(resolved_url)
        else:
            st.info("카메라 허용 후 QR 코드를 촬영하면 분석을 시작합니다.")

# QR 이미지 업로드
elif selection == "QR 이미지 업로드":
    uploaded_files = st.file_uploader(
        "QR 이미지 업로드",
        accept_multiple_files=True,
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.image(uploaded_file)
            qr_text, final_url = handle_qr_image(uploaded_file)

            if qr_text is None:
                continue

            target_url = final_url or qr_text

            try:
                resolved_url = follow_redirect(target_url)
                st.info(f"최종 리디렉션 URL: {resolved_url}")
            except Exception as e:
                st.error(f"리디렉션 처리 중 오류 발생 : {e}")
                resolved_url = target_url

            render_url_analysis(resolved_url)

# URL 직접 입력
elif selection == "URL 직접 입력": 
    with st.form(key="button_form"): 
        written_url = st.text_input(
            ":gray-background[:gray[예 : www.google.com 과 같은 url을 입력하세요.]]",
            placeholder="검사할 URL을 입력하세요."
        )
        submitted = st.form_submit_button("검사하기", width="stretch")

    if submitted:
        if not written_url:
            st.warning("URL을 입력해주세요.")
            st.stop()
        else:
            st.write("입력한 URL:", written_url)
        
        try:
            final_url = follow_redirect(written_url)
            st.info(f"최종 리디렉션 URL:{final_url}")
        except Exception as e:
            st.error(f"리디렉션 처리 중 오류 발생 : {e}")
            final_url = written_url
        
        render_url_analysis(final_url)
