from django.urls import path
from .views import CSVFileUploadView

urlpatterns = [
    path('', CSVFileUploadView.as_view(), name='csv-file-upload'),
]