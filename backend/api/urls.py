from django.urls import path
from .views import UploadView, BatchView

urlpatterns = [
    path('upload/', UploadView.as_view(), name='upload'),
    path('batch/', BatchView.as_view(), name='batch'),
]
