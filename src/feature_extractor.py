import re
import pandas as pd
from urllib.parse import urlparse
from sklearn.base import BaseEstimator, TransformerMixin

class URLFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self, domain_counts=None):
        self.domain_counts = domain_counts

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for url in X:
            url = str(url).strip()
            has_https = int(url.lower().startswith("https"))
            cleaned = re.sub(r"^https?://", "", url, flags=re.IGNORECASE)
            cleaned = cleaned.rstrip("/")
            cleaned = cleaned.split("?", 1)[0]

            length = len(cleaned)
            digit_ratio = sum(c.isdigit() for c in cleaned) / length if length else 0
            special_char_count = sum(not c.isalnum() for c in cleaned)

            parsed = urlparse("http://" + cleaned)
            domain = parsed.netloc or ""
            parts = domain.split(".") if domain else []
            subdomain_count = max(len(parts) - 1, 0)
            tld = parts[-1] if parts else ""
            is_ip = int(bool(re.fullmatch(r"\d+\.\d+\.\d+\.\d+", domain)))

            if self.domain_counts is not None:
                domain_freq = float(self.domain_counts.get(domain, 1))
            else:
                domain_freq = 1

            features.append({
                "length": length,
                "digit_ratio": digit_ratio,
                "special_char_count": special_char_count,
                "subdomain_count": subdomain_count,
                "domain_freq": domain_freq,
                "has_https": has_https,
                "is_ip": is_ip,
                "tld": tld
            })

        return pd.DataFrame(features)
