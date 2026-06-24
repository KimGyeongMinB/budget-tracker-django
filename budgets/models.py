from django.conf import settings
from django.db import models
from django.db.models import Q


class TransactionType(models.TextChoices):
    # 카테고리와 거래 기록에서 공통으로 사용하는 수입/지출 구분값
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class Category(models.Model):
    # 수입과 지출을 분류하기 위한 기본 또는 사용자 지정 카테고리
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="categories",
    )
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "type"],
                name="unique_user_category_name_type",
            )
        ]
        ordering = ["type", "name"]

    def __str__(self):
        owner = "Default" if self.is_default else self.user
        return f"{self.name} ({self.get_type_display()}, {owner})"


class TransactionRecord(models.Model):
    # 사용자가 입력한 하나의 수입 또는 지출 거래 기록
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transaction_records",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transaction_records",
    )
    type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    transaction_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="transaction_amount_gt_0",
            )
        ]
        ordering = ["-transaction_date", "-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} - {self.category.name}"


class Budget(models.Model):
    # 사용자가 설정한 월별 예산 금액
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
    )
    year = models.PositiveIntegerField()
    month = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "year", "month"],
                name="unique_user_budget_year_month",
            ),
            models.CheckConstraint(
                condition=Q(month__gte=1) & Q(month__lte=12),
                name="budget_month_between_1_and_12",
            ),
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="budget_amount_gt_0",
            ),
        ]
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.user} - {self.year}-{self.month:02d}: {self.amount}"


class MLCategoryTrainingData(models.Model):
    # 카테고리 추천 모델 학습에 사용하는 텍스트 라벨 데이터
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ml_category_training_data",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="ml_training_data",
    )
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.description} -> {self.category.name}"


class ExpensePrediction(models.Model):
    # 사용자의 미래 월별 지출 예측 결과
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expense_predictions",
    )
    target_year = models.PositiveIntegerField()
    target_month = models.PositiveSmallIntegerField()
    predicted_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "target_year", "target_month"],
                name="unique_user_prediction_target_year_month",
            ),
            models.CheckConstraint(
                condition=Q(target_month__gte=1) & Q(target_month__lte=12),
                name="prediction_month_between_1_and_12",
            ),
            models.CheckConstraint(
                condition=Q(predicted_amount__gte=0),
                name="prediction_amount_gte_0",
            ),
        ]
        ordering = ["-target_year", "-target_month", "-created_at"]

    def __str__(self):
        return (
            f"{self.user} - {self.target_year}-{self.target_month:02d}: "
            f"{self.predicted_amount}"
        )
