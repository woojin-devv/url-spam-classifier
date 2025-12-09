from src.model_utils import explain_url_with_shap
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

def generate_explanation(url, pred, prob, shap_dict):
    from openai import AzureOpenAI
    import os
    from dotenv import load_dotenv

    load_dotenv()

    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OAI_KEY"),
        api_version="2025-01-01-preview"
    )

    sorted_features = sorted(
        shap_dict.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    top_features = "\n".join(
        [f"- {k}: {v:+.4f}" for k, v in sorted_features[:7]]
    )

    user_prompt = f"""
        당신은 URL 분석 보안 전문가입니다.  
        다음의 URL 분석 결과를 일반 사용자가 쉽게 이해할 수 있도록 **간결한 위험도 설명문**으로 정리해 주세요.

        입력 정보:
        • URL: {url}
        • 예측 결과: {"스팸" if pred == 1 else "정상"}
        • 스팸 확률: {prob:.4f}
        • 주요 특징 기여도(모델의 판단 근거): {top_features}

        요구사항:
        - 결과는 bullet list 형식으로 작성하세요.
        - 문장은 최대 6문장 이내로 구성합니다.
        - 다음 요소를 반드시 포함하세요:
        1. **첫 문장**: 최종 예측 결과와 위험도 등급(매우 높음/ 중간 / 낮음)을 명확히 표시합니다.  
            (예: “이 URL은 스팸일 가능성이 높으며, 위험도는 ‘매우 높음’으로 평가됩니다.”)
        2. **중간 문장들**: 모델이 그 판단을 내린 이유를 `top_features`의 정보를 활용해 **일반인도 이해할 수 있는 설명**으로 표현합니다.  
            (예: “도메인 이름이 복잡하거나 불필요한 숫자가 많습니다.”, “짧은 기간 전에 만들어진 사이트입니다.” 등)
        3. **마지막 문장**: 사용자가 취해야 할 간단한 안전 행동을 제시합니다.  
            (예: “이 링크를 클릭하지 말고, 공식 사이트를 직접 검색해 접속하세요.”)

        추가 지시:
        - 기술적인 통계 용어나 SHAP 같은 알고리즘 용어는 **절대 노출하지 말 것.**
        - 분석 이유는 “사람의 언어”로 풀어서 설명할 것.
        - 전체 결과는 사용자 안내 메시지처럼 자연스럽고 친근한 어조로 작성할 것.
        """

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "당신은 URL 분석 보안 전문가입니다."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
