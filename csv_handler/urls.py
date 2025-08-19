from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CSVReconciliationViewSet

router = DefaultRouter()
router.register(r'', CSVReconciliationViewSet, basename='csv-reconciliation')

urlpatterns = [
    path('', include(router.urls)),
]