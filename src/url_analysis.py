import streamlit as st

from src.model_utils import explain_url_with_shap
from src.explain_openai import generate_explanation

def render_url_analysis(final_url: str):
    """
    final_url을 입력받아
    1) ML + SHAP 분석
    2) 결과 카드 출력
    3) GPT 기반 위험도 설명 출력
    까지 한 번에 처리하는 함수
    """
    try:
        pred, prob, shap_dict = explain_url_with_shap(final_url)
    except Exception as e:
        st.error(f"SHAP 분석 중 오류 발생: {e}")
        return

    # === 결과 카드 출력 ===
    result_label = "스팸" if pred == 1 else "정상"
    prob_percent = f"{prob * 100:.2f}%"
    label_class = "result-danger" if pred == 1 else "result-safe"

    st.markdown("---")
    st.markdown(
        f"""
<div class="result-label {label_class}">
    {result_label}
</div>

<div class="result-body">
    <b>스팸일 확률은</b> {prob_percent} 입니다.<br>
    URL 분석이 완료되었으며, 위 결과는 ML 기반 RandomForest와 SHAP 해석을 통해 산출되었습니다.
</div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # GPT 위험도 설명
    if shap_dict:
        try:
            with st.spinner("위험 정도를 정확히 분석 중입니다..."):
                explanation = generate_explanation(final_url, pred, prob, shap_dict)
            with st.container(border=True):
                st.subheader("위험도 설명", divider="grey")
                st.write(explanation)
        except Exception as e:
            st.error(f"GPT 설명 생성 중 오류 발생: {e}")
