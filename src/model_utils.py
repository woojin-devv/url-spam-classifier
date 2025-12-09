import joblib
import shap
import numpy as np

from src.feature_extractor import URLFeatureExtractor
from src.dummy_threshold_rf import ThresholdedRF

# 모델을 global 캐시에 저장해서 Streamlit rerun 시 반복 로드 방지
_model_cache = None
_shap_cache = None

def load_model(model_path="rf_full_pipeline_v1.pkl"):
    global _model_cache
    if _model_cache is None:
        _model_cache = joblib.load(model_path)
    return _model_cache

def predict_url(url):
    """
    raw URL 입력 => full pipeline 모델이 자동 feature 추출 => 예측 반환
    """
    model = load_model()
    pred = model.predict([url])[0]
    prob = model.predict_proba([url])[0][1]
    return pred, prob


def explain_url_with_shap(url):
    """
    URL => 예측 및 SHAP feature contribution 반환
    """
    global _shap_cache
    _shap_cache = None

    model = load_model()
    extractor = model.named_steps["extract"]
    preprocess = model.named_steps["pre"]
    rf = model.named_steps["rf"]

    # 1) URL => features
    raw_feat = extractor.transform([url])
    processed = preprocess.transform(raw_feat)

    if hasattr(processed, "toarray"):
        processed = processed.toarray()

    processed = processed.astype("float64")

    # 2) SHAP explainer 캐싱
    if _shap_cache is None:
        # background data 생성
        background_urls = [
            "http://gtzt5.hnztu.beauty",
            "http://m04.x7hz.black",
            "http://dfse.oksn.miami",
            "http://wwmae.pmquu.com",
        ]
        raw_bg = extractor.transform(background_urls)
        bg_processed = preprocess.transform(raw_bg)
        if hasattr(bg_processed, "toarray"):
            bg_processed = bg_processed.toarray()

        bg_processed = bg_processed.astype("float64")
        _shap_cache = shap.TreeExplainer(rf, bg_processed)

    explainer = _shap_cache
    shap_values = explainer.shap_values(processed, check_additivity=False)

    # class=1 (SPAM)
    shap_vec = shap_values[1] if isinstance(shap_values, list) else shap_values
    shap_vec = np.array(shap_vec).reshape(-1)

    feature_names = preprocess.get_feature_names_out()

    shap_dict = {
        name: float(value)
        for name, value in zip(feature_names, shap_vec)
    }

    # 모델 예측
    pred = int(model.predict([url])[0])
    prob = float(model.predict_proba([url])[0][1])

    return pred, prob, shap_dict