from django.urls import path
from .views import CSVFileUploadView

urlpatterns = [
    path('upload/', CSVFileUploadView.as_view(), name='csv-file-upload'),
]