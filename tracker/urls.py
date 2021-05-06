from django.urls import path
from .views import (
    TrackerCreateView,
    TrackerUpdateView,
    TrackerDeleteView,
    AssignFieldToMemberView,
    MealCreateView,
    MealUpdateView,
    MealUpdateAdminView,
    MealUpdateRequestView,
    meal_update_request_cancel,
    MealUpdateRequestConfirmView,
    meal_update_request_deny,
    ShoppingCreateView,
    ShoppingUpdateView,
    ShoppingDeleteView,
    MonthlyShoppingCreateView,
    MonthlyShoppingUpdateView,
    MonthlyShoppingDeleteView,
    CashDepositFieldCreateView,
    CashDepositFieldUpdateView,
    CashDepositFieldDeleteView,
    CostChartView,
    MealChartView,
    ShoppingChartView,
    DepositChartView,
    CashDepositFieldAssignView,
    AnalyticsView
    )

urlpatterns = [
    # cost-sector urls
    path('create/', TrackerCreateView.as_view(), name='tracker_create'),
    path('<slug>/update/', TrackerUpdateView.as_view(), name='tracker_update'),
    path('<slug>/delete/', TrackerDeleteView.as_view(), name='tracker_delete'),
    path('allocate-cost-to-/<slug>/', AssignFieldToMemberView.as_view(), name='assign_field_to_member'),
    # meal-urls
    path('meal/entry/', MealCreateView.as_view(), name='meal_create'),
    path('meal/<slug>/update/', MealUpdateView.as_view(), name='meal_update'),
    path('meal/<slug>/update/maintainer/', MealUpdateAdminView.as_view(), name='meal_update_admin'),
    path('meal/<slug>/update/request/', MealUpdateRequestView.as_view(), name='meal_update_request'),
    path('meal/<slug>/update/request/cancel/', meal_update_request_cancel, name='meal_update_request_cancel'),
    path('meal/<slug>/update/request/confirm/', MealUpdateRequestConfirmView.as_view(), name='meal_update_request_confirm'),
    path('meal/<slug>/update/request/deny/', meal_update_request_deny, name='meal_update_request_deny'),
    # shopping-urls
    path('shopping/entry/', ShoppingCreateView.as_view(), name='shopping_create'),
    path('shopping/<slug>/update/', ShoppingUpdateView.as_view(), name='shopping_update'),
    path('shopping/<slug>/delete/', ShoppingDeleteView.as_view(), name='shopping_delete'),
    path('shopping/monthly/entry/', MonthlyShoppingCreateView.as_view(), name='monthly_shopping_create'),
    path('shopping/monthly/<slug>/update/', MonthlyShoppingUpdateView.as_view(), name='monthly_shopping_update'),
    path('shopping/monthly/<slug>/delete/', MonthlyShoppingDeleteView.as_view(), name='monthly_shopping_delete'),
    # deposit-urls
    path('deposit/field/create/', CashDepositFieldCreateView.as_view(), name='deposit_field_create'),
    path('deposit/field/<slug>/update/', CashDepositFieldUpdateView.as_view(), name='deposit_field_update'),
    path('deposit/field/<slug>/delete/', CashDepositFieldDeleteView.as_view(), name='deposit_field_delete'),
    path('deposit/field/<slug>/assign/', CashDepositFieldAssignView.as_view(), name='deposit_field_assign'),
    # chart-analytics-urls
    path('cost/chart/', CostChartView.as_view(), name='cost_chart'),
    path('meal/chart/', MealChartView.as_view(), name='meal_chart'),
    path('shopping/chart/', ShoppingChartView.as_view(), name='shopping_chart'),
    path('deposit/chart/', DepositChartView.as_view(), name='deposit_chart'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]
