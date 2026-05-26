from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    ExamViewSet,
    MarkEntryViewSet,
    MarkSheetView,
    MarksheetPDFView,
    ResultAnalysisView,
    ResultApprovalViewSet,
)

router = DefaultRouter()
router.register('exams', ExamViewSet, basename='exam')
router.register('marks', MarkEntryViewSet, basename='mark')
router.register('approvals', ResultApprovalViewSet, basename='approval')
urlpatterns = [
    path('mark-sheet/', MarkSheetView.as_view(), name='mark-sheet'),
    path('analysis/', ResultAnalysisView.as_view(), name='result-analysis'),
    path('marksheet/<int:student_id>/<int:exam_id>/', MarksheetPDFView.as_view(), name='marksheet-pdf'),
    path('', include(router.urls)),
]
