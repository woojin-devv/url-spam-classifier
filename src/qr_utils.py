from PIL import Image, ImageDraw
from pyzbar.pyzbar import decode
import requests
import streamlit as st

def handle_qr_image(file):
    """
    QR 이미지에서 텍스트를 읽고, URL이면 리디렉션 URL까지 따라가서
    Streamlit에 출력해 주는 함수. + QR bounding box 시각화
    return: (qr_text, final_url)
    """

    img = Image.open(file).convert("RGB")
    decoded_list = decode(img)

    if not decoded_list:
        st.error("QR 코드를 인식하지 못했습니다. 다시 시도 해주세요.")
        return None, None
    
    # 첫 번째 QR만 사용
    d = decoded_list[0]

    # 텍스트 읽기
    qr_text = d.data.decode("utf-8")
    final_url = None

    # URL 리디렉션 체크
    if qr_text.startswith(("http://", "https://")):
        try:
            req = requests.get(qr_text, allow_redirects=True, timeout=3)
            final_url = req.url
        except Exception:
            st.error("리디렉션 URL을 가져오는 데 실패했습니다.")

    # 출력
    st.success(f"QR 코드 내용: {qr_text}")

    return qr_text, final_url


def follow_redirect(url: str):
    """
    사용자가 직접 입력한 URL에 대해 리디렉션 최종 URL을 반환.
    ex) www.google.com 처럼 scheme이 없는 경우 http:// 붙여줌.
    """
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    try:
        req = requests.get(url, allow_redirects=True, timeout=3)
        final_url = req.url
        return final_url
    except Exception:
        st.error("리디렉션 URL을 가져오는 데 실패했습니다.")
        return None
