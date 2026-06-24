from decimal import Decimal

import numpy as np
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from sklearn.linear_model import LinearRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, StratifiedKFold

from .models import (
    ExpensePrediction,
    MLCategoryTrainingData,
    TransactionRecord,
    TransactionType,
)

# 유저별 학습된 파이프라인 캐시 {user_id: {"pipeline": ..., "data_count": ...}}
_pipeline_cache: dict = {}


def _build_pipeline() -> Pipeline:
    """TF-IDF + LinearSVC 파이프라인 생성."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(1, 4),
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", CalibratedClassifierCV(
            LinearSVC(max_iter=2000, C=1.0, class_weight="balanced"),
            cv=3,
        )),
    ])


def get_category_recommendation(description: str, user) -> dict:
    """
    거래 설명 텍스트를 기반으로 카테고리를 추천한다.
    학습된 파이프라인을 메모리에 캐시하여 재학습 비용 제거.
    """
    training_data = (
        MLCategoryTrainingData.objects.filter(user=user)
        .select_related("category")
    )

    data_count = training_data.count()
    if data_count < 3:
        return {"success": False, "message": "학습 데이터가 부족합니다."}

    cached = _pipeline_cache.get(user.id)

    # 캐시 미스 or 데이터 추가됐을 때만 재학습
    if cached is None or cached["data_count"] != data_count:
        texts = [d.description for d in training_data]
        label_ids = [d.category.id for d in training_data]
        category_map = {d.category.id: d.category for d in training_data}

        pipeline = _build_pipeline()
        pipeline.fit(texts, label_ids)

        # cross-validation 정확도 측정
        cv_accuracy = None
        if len(texts) >= 5 and len(set(label_ids)) >= 2:
            n_splits = min(5, len(texts) // len(set(label_ids)))
            if n_splits >= 2:
                cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
                scores = cross_val_score(pipeline, texts, label_ids, cv=cv, scoring="accuracy")
                cv_accuracy = round(float(scores.mean()) * 100, 1)

        _pipeline_cache[user.id] = {
            "pipeline": pipeline,
            "category_map": category_map,
            "data_count": data_count,
            "cv_accuracy": cv_accuracy,
        }

    cached = _pipeline_cache[user.id]
    pipeline = cached["pipeline"]
    category_map = cached["category_map"]
    cv_accuracy = cached["cv_accuracy"]

    try:
        predicted_id = pipeline.predict([description])[0]
        confidence = round(max(pipeline.predict_proba([description])[0]) * 100, 1)

        category = category_map.get(predicted_id)
        if category:
            return {
                "success": True,
                "category_id": category.id,
                "category_name": category.name,
                "category_type": category.type,
                "confidence": confidence,
                "cv_accuracy": cv_accuracy,
            }
    except Exception as e:
        return {"success": False, "message": str(e)}

    return {"success": False, "message": "추천 실패"}


def predict_next_month_expense(user) -> dict:
    """
    과거 월별 지출 합계를 단순 선형 회귀로 학습해 다음 달 지출을 예측한다.
    x = 월 인덱스 (0, 1, 2 ...), y = 해당 월 총 지출
    """
    monthly_qs = (
        TransactionRecord.objects.filter(
            user=user,
            type=TransactionType.EXPENSE,
        )
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    data = list(monthly_qs)

    if len(data) < 3:
        return {
            "success": False,
            "message": f"예측을 위해 최소 3개월치 데이터가 필요합니다. (현재 {len(data)}개월)",
        }

    x = np.array(range(len(data))).reshape(-1, 1)
    y = np.array([float(d["total"]) for d in data])

    model = LinearRegression()
    model.fit(x, y)

    next_x = np.array([[len(data)]])
    predicted = float(model.predict(next_x)[0])
    predicted = max(0, predicted)  # 음수 방지

    # 다음 달 계산
    last_month = data[-1]["month"]
    if last_month.month == 12:
        next_year, next_month = last_month.year + 1, 1
    else:
        next_year, next_month = last_month.year, last_month.month + 1

    # 결과 저장 (같은 달 예측이 있으면 업데이트)
    ExpensePrediction.objects.update_or_create(
        user=user,
        target_year=next_year,
        target_month=next_month,
        defaults={"predicted_amount": Decimal(str(round(predicted)))},
    )

    return {
        "success": True,
        "target_year": next_year,
        "target_month": next_month,
        "predicted_amount": round(predicted),
        "months_used": len(data),
    }
