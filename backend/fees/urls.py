from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    BillingRunViewSet,
    FeeHeadViewSet,
    FeeStructureViewSet,
    FeeSummaryView,
    FonepayConfirmView,
    LateFeePolicyViewSet,
    OnlinePaymentInitView,
    PaymentViewSet,
    RefundRequestViewSet,
    ScholarshipViewSet,
    StudentFeeAssignmentViewSet,
)

router = DefaultRouter()
router.register('heads', FeeHeadViewSet, basename='fee-head')
router.register('late-fee-policies', LateFeePolicyViewSet, basename='late-fee-policy')
router.register('scholarships', ScholarshipViewSet, basename='scholarship')
router.register('structures', FeeStructureViewSet, basename='fee-structure')
router.register('billing-runs', BillingRunViewSet, basename='billing-run')
router.register('assignments', StudentFeeAssignmentViewSet, basename='fee-assignment')
router.register('payments', PaymentViewSet, basename='payment')
router.register('refunds', RefundRequestViewSet, basename='refund')
urlpatterns = [
    path('summary/', FeeSummaryView.as_view(), name='fee-summary'),
    path('online/initiate/', OnlinePaymentInitView.as_view(), name='online-payment'),
    path('fonepay/confirm/', FonepayConfirmView.as_view(), name='fonepay-confirm'),
    path('', include(router.urls)),
]
