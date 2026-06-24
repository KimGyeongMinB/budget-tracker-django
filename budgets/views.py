import json
import time
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.db.models import Q, Sum, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import TransactionRecordForm, CategoryForm, BudgetForm, SignUpForm
from .models import Budget, ExpensePrediction, MLCategoryTrainingData, TransactionRecord, TransactionType, Category


def _save_training_data(user, description: str, category):
    """거래 설명 + 카테고리를 ML 학습 데이터에 자동 저장."""
    description = description.strip()
    if description:
        MLCategoryTrainingData.objects.get_or_create(
            user=user,
            description=description,
            category=category,
        )

"""회원가입"""

def signup(request):
    # 이미 로그인된 사용자는 대시보드로
    if request.user.is_authenticated:
        return redirect("budgets:dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            # 비밀번호는 UserCreationForm이 자동으로 해싱 처리
            form.save()
            # 가입 완료 후 로그인 페이지로 이동
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "registration/signup.html", {"form": form})


"""대시보드"""

@login_required
def dashboard(request):
    # 로그인한 사용자의 이번 달 예산 현황과 최근 거래 기록을 보여주는 대시보드
    today = timezone.localdate()
    current_year = today.year
    current_month = today.month

    monthly_records = TransactionRecord.objects.filter(
        user=request.user,
        transaction_date__year=current_year,
        transaction_date__month=current_month,
    )

    # 수입/지출 합계를 단일 쿼리로 계산 (조건부 집계)
    totals = monthly_records.aggregate(
        total_income=Sum("amount", filter=Q(type=TransactionType.INCOME)),
        total_expense=Sum("amount", filter=Q(type=TransactionType.EXPENSE)),
    )
    total_income = totals["total_income"] or Decimal("0")
    total_expense = totals["total_expense"] or Decimal("0")

    balance = total_income - total_expense

    # 이번 달 수입 합계를 예산으로 사용
    budget_amount = total_income
    remaining_budget = budget_amount - total_expense if budget_amount > 0 else None
    budget_usage_rate = (
        round((total_expense / budget_amount) * 100, 1)
        if budget_amount > 0
        else 0
    )
    is_over_budget = remaining_budget is not None and remaining_budget < 0

    category_expenses = (
        monthly_records.filter(type=TransactionType.EXPENSE)
        .values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    recent_records = TransactionRecord.objects.filter(user=request.user).select_related(
        "category"
    )[:5]

    next_year = current_year + 1 if current_month == 12 else current_year
    next_month = 1 if current_month == 12 else current_month + 1
    next_prediction = ExpensePrediction.objects.filter(
        user=request.user,
        target_year=next_year,
        target_month=next_month,
    ).first()

    # 파이 차트: 카테고리별 지출 (JSON)
    pie_labels = json.dumps([item["category__name"] for item in category_expenses], ensure_ascii=False)
    pie_values = json.dumps([float(item["total"]) for item in category_expenses])

    # 월별 추세 차트: 최근 6개월 지출 (JSON)
    monthly_qs = (
        TransactionRecord.objects.filter(user=request.user, type=TransactionType.EXPENSE)
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    bar_labels = json.dumps(
        [f"{d['month'].year}.{d['month'].month:02d}" for d in monthly_qs],
        ensure_ascii=False,
    )
    bar_values = json.dumps([float(d["total"]) for d in monthly_qs])

    context = {
        "current_year": current_year,
        "current_month": current_month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "budget_amount": budget_amount,
        "remaining_budget": remaining_budget,
        "budget_usage_rate": budget_usage_rate,
        "is_over_budget": is_over_budget,
        "category_expenses": category_expenses,
        "recent_records": recent_records,
        "next_prediction": next_prediction,
        "pie_labels": pie_labels,
        "pie_values": pie_values,
        "bar_labels": bar_labels,
        "bar_values": bar_values,
    }

    return render(request, "budgets/dashboard.html", context)

"""거래기록 CRUD"""

# 거래기록 List
@login_required
def transaction_list(request):
    today = timezone.localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    records = (
        TransactionRecord.objects.filter(
            user=request.user,
            transaction_date__year=year,
            transaction_date__month=month,
        )
        .select_related("category")
        .order_by("-transaction_date", "-created_at")
    )

    total_income = records.filter(type=TransactionType.INCOME).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    total_expense = records.filter(type=TransactionType.EXPENSE).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0")

    # 드롭다운용: 거래가 존재하는 연월 목록
    months_qs = (
        TransactionRecord.objects.filter(user=request.user)
        .annotate(month=TruncMonth("transaction_date"))
        .values("month")
        .distinct()
        .order_by("-month")
    )
    available_months = [
        {"year": d["month"].year, "month": d["month"].month}
        for d in months_qs
    ]

    context = {
        "records": records,
        "selected_year": year,
        "selected_month": month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "available_months": available_months,
    }

    return render(request, "budgets/transaction_list.html", context)


# 거래기록 Create
@login_required
def transaction_create(request):
    # 로그인한 사용자의 거래 기록 생성
    if request.method == "POST":
        form = TransactionRecordForm(request.POST, user=request.user)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            _save_training_data(request.user, transaction.description, transaction.category)
            return redirect("budgets:transaction_list")
    else:
        form = TransactionRecordForm(user=request.user)

    context = {
        "form": form,
        "title": "거래 기록 등록",
        "button_text": "등록",
    }

    return render(request, "budgets/transaction_form.html", context)


# 거래기록 Update
@login_required
def transaction_update(request, pk):
    # 로그인한 사용자의 거래 기록 수정
    transaction = get_object_or_404(
        TransactionRecord,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        form = TransactionRecordForm(
            request.POST,
            instance=transaction,
            user=request.user,
        )

        if form.is_valid():
            transaction = form.save()
            _save_training_data(request.user, transaction.description, transaction.category)
            return redirect("budgets:transaction_list")
    else:
        form = TransactionRecordForm(instance=transaction, user=request.user)

    context = {
        "form": form,
        "title": "거래 기록 수정",
        "button_text": "수정",
    }

    return render(request, "budgets/transaction_form.html", context)


# 거래기록 Delete
@login_required
def transaction_delete(request, pk):
    # 로그인한 사용자의 거래 기록 삭제
    transaction = get_object_or_404(
        TransactionRecord,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        transaction.delete()
        return redirect("budgets:transaction_list")

    context = {
        "transaction": transaction,
    }

    return render(request, "budgets/transaction_confirm_delete.html", context)


"""카테고리 CRUD"""

@login_required
def category_list(request):
    # 공용 기본 카테고리와 로그인한 사용자의 카테고리 목록 + 지출 합계
    categories = Category.objects.filter(
        Q(user__isnull=True) | Q(user=request.user)
    ).order_by("type", "name")

    # 각 카테고리별로 현재 사용자의 거래 합계를 별도 dict로 계산
    totals_qs = (
        TransactionRecord.objects.filter(user=request.user)
        .values("category_id", "type")
        .annotate(total=Sum("amount"))
    )
    totals = {(r["category_id"], r["type"]): r["total"] for r in totals_qs}

    category_rows = []
    for cat in categories:
        total = totals.get((cat.pk, cat.type), None)
        category_rows.append({"category": cat, "total": total})

    context = {
        "category_rows": category_rows,
    }

    return render(request, "budgets/category_list.html", context)


@login_required
def category_detail(request, pk):
    # 특정 카테고리에 속하는 현재 사용자의 거래 내역 + 합계
    category = get_object_or_404(
        Category,
        pk=pk,
    )
    # 기본 카테고리(user=None)이거나 본인 카테고리만 접근 허용
    if category.user is not None and category.user != request.user:
        return redirect("budgets:category_list")

    records = (
        TransactionRecord.objects.filter(user=request.user, category=category)
        .order_by("-transaction_date", "-created_at")
    )

    total = records.aggregate(total=Sum("amount"))["total"] or Decimal("0")

    context = {
        "category": category,
        "records": records,
        "total": total,
    }

    return render(request, "budgets/category_detail.html", context)


@login_required
def category_create(request):
    # 로그인한 사용자의 사용자 지정 카테고리 생성
    if request.method == "POST":
        form = CategoryForm(request.POST)

        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.is_default = False
            category.save()
            return redirect("budgets:transaction_create")
    else:
        form = CategoryForm()

    context = {
        "form": form,
        "title": "카테고리 등록",
        "button_text": "등록",
    }

    return render(request, "budgets/category_form.html", context)


@login_required
def category_update(request, pk):
    # 로그인한 사용자의 카테고리 수정
    category = get_object_or_404(
        Category,
        pk=pk,
        user=request.user,
    )

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect("budgets:category_list")
    else:
        form = CategoryForm(instance=category)

    context = {
        "form": form,
        "title": "카테고리 수정",
        "button_text": "수정",
    }

    return render(request, "budgets/category_form.html", context)


"""예산 관리"""

@login_required
def budget_set(request):
    # 현재 월(또는 GET 파라미터로 지정한 월)의 예산을 설정하거나 수정
    today = timezone.localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    budget = Budget.objects.filter(
        user=request.user,
        year=year,
        month=month,
    ).first()

    if request.method == "POST":
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.save()
            return redirect("budgets:dashboard")
    else:
        form = BudgetForm(
            instance=budget,
            initial={"year": year, "month": month},
        )

    total_expense = (
        TransactionRecord.objects.filter(
            user=request.user,
            type=TransactionType.EXPENSE,
            transaction_date__year=year,
            transaction_date__month=month,
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0")
    )

    budget_amount = budget.amount if budget else Decimal("0")
    remaining = budget_amount - total_expense if budget else None
    is_over = remaining is not None and remaining < 0

    context = {
        "form": form,
        "year": year,
        "month": month,
        "budget": budget,
        "budget_amount": budget_amount,
        "total_expense": total_expense,
        "remaining": remaining,
        "is_over": is_over,
    }

    return render(request, "budgets/budget_form.html", context)


"""머신러닝"""

@login_required
@require_POST
def recommend_category(request):
    # 거래 설명 텍스트로 카테고리 추천 (AJAX) + 응답 시간 측정
    from .ml import get_category_recommendation
    description = request.POST.get("description", "").strip()
    if not description:
        return JsonResponse({"success": False, "message": "설명을 입력하세요."})
    start = time.time()
    result = get_category_recommendation(description, request.user)
    result["response_ms"] = round((time.time() - start) * 1000, 1)
    return JsonResponse(result)


@login_required
def run_prediction(request):
    # 선형 회귀로 다음 달 지출 예측 후 대시보드로 리다이렉트
    from .ml import predict_next_month_expense
    predict_next_month_expense(request.user)
    return redirect("budgets:dashboard")
