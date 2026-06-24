from django.contrib import admin

from .models import (
    Budget,
    Category,
    ExpensePrediction,
    MLCategoryTrainingData,
    TransactionRecord,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # 관리자 페이지에서 카테고리 기본 정보를 빠르게 확인하기 위한 설정
    list_display = ("name", "type", "user", "is_default", "created_at")
    list_filter = ("type", "is_default")
    search_fields = ("name", "user__username")


@admin.register(TransactionRecord)
class TransactionRecordAdmin(admin.ModelAdmin):
    # 수입/지출 거래 기록을 날짜, 유형, 카테고리 기준으로 관리하기 위한 설정
    list_display = (
        "transaction_date",
        "user",
        "type",
        "category",
        "amount",
        "description",
    )
    list_filter = ("type", "category", "transaction_date")
    search_fields = ("description", "user__username", "category__name")
    date_hierarchy = "transaction_date"


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    # 사용자별 월 예산을 연도와 월 기준으로 확인하기 위한 설정
    list_display = ("user", "year", "month", "amount", "updated_at")
    list_filter = ("year", "month")
    search_fields = ("user__username",)


@admin.register(MLCategoryTrainingData)
class MLCategoryTrainingDataAdmin(admin.ModelAdmin):
    # 카테고리 추천 모델 학습용 텍스트 데이터를 확인하기 위한 설정
    list_display = ("description", "category", "user", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("description", "category__name", "user__username")


@admin.register(ExpensePrediction)
class ExpensePredictionAdmin(admin.ModelAdmin):
    # 월별 지출 예측 결과를 사용자와 예측 대상 월 기준으로 확인하기 위한 설정
    list_display = (
        "user",
        "target_year",
        "target_month",
        "predicted_amount",
        "created_at",
    )
    list_filter = ("target_year", "target_month")
    search_fields = ("user__username",)
