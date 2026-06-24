from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.db.models import Q

from .models import Budget, Category, TransactionRecord

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="이메일",
        help_text="유효한 이메일 주소를 입력하세요.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "아이디"
        self.fields["username"].help_text = (
            "150자 이하, 영문·숫자·@·.·+·-·_ 만 사용 가능합니다."
        )
        self.fields["password1"].label = "비밀번호"
        self.fields["password1"].help_text = (
            "비밀번호는 8자 이상이며, 아이디·이메일과 유사하거나 너무 단순한 비밀번호는 사용할 수 없습니다."
        )
        self.fields["password2"].label = "비밀번호 확인"
        self.fields["password2"].help_text = "위와 동일한 비밀번호를 입력하세요."

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        # 형식 검사 (EmailField가 기본으로 하지만 명시적으로 재확인)
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError("올바른 이메일 형식이 아닙니다.")

        # 중복 검사
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")

        return email


class TransactionRecordForm(forms.ModelForm):
    # 수입/지출 거래 기록 등록 및 수정 폼
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).order_by("type", "name")

    class Meta:
        model = TransactionRecord
        fields = [
            "type",
            "category",
            "amount",
            "description",
            "transaction_date",
        ]
        labels = {
            "type": "유형",
            "category": "카테고리",
            "amount": "금액",
            "description": "내용",
            "transaction_date": "거래 날짜",
        }
        widgets = {
            "transaction_date": forms.DateInput(attrs={"type": "date"}),
        }


class CategoryForm(forms.ModelForm):
    # 사용자 지정 카테고리 등록 및 수정 폼
    class Meta:
        model = Category
        fields = [
            "name",
            "type",
        ]
        labels = {
            "name": "카테고리명",
            "type": "유형",
        }


class BudgetForm(forms.ModelForm):
    # 월별 예산 등록 및 수정 폼
    class Meta:
        model = Budget
        fields = [
            "year",
            "month",
            "amount",
        ]
        labels = {
            "year": "연도",
            "month": "월",
            "amount": "예산 금액",
        }
