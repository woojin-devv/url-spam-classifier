from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_explanation(url, pred, prob, shap_dict):
    """
    SHAP 값 기반 자연어 설명 생성
    """
    client = AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OAI_KEY"),
        api_version="2025-01-01-preview"
    )

    sorted_features = sorted(
        shap_dict.items(), key=lambda x: abs(x[1]), reverse=True
    )
    top_features = "\n".join([f"- {k}: {v:+.4f}" for k, v in sorted_features[:7]])

    user_prompt = f"""
URL 분석 결과는 다음과 같습니다.

- 예측 결과: {"스팸" if pred == 1 else "정상"}
- 스팸 확률: {prob:.4f}

[SHAP 주요 기여도 Top Features]
{top_features}

위 내용을 기반으로 일반 사용자가 이해하기 쉽게 
"이 URL이 왜 위험/안전한지" 자연어로 설명해줘.
"""

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": "당신은 URL 보안 분석 설명 전문가입니다."},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4
    )

    return response.choices[0].message.content
