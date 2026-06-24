from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/create/", views.transaction_create, name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.transaction_update, name="transaction_update"),
    path("transactions/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/create/", views.category_create, name="category_create"),
    path("categories/<int:pk>/", views.category_detail, name="category_detail"),
    path("categories/<int:pk>/edit/", views.category_update, name="category_update"),
    path("budget/set/", views.budget_set, name="budget_set"),
    path("ml/recommend/", views.recommend_category, name="recommend_category"),
    path("ml/predict/", views.run_prediction, name="run_prediction"),
]
