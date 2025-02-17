from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name='upload'
urlpatterns = [
    path('', TemplateView.as_view(template_name='upload/index.html'), name='index'),
    path('upload', views.UploadView.as_view(), name='upload_files'),
]
