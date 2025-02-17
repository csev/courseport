from django.urls import path
from . import views

app_name = 'upload'  # Namespace for the application

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_files, name='upload_files'),
] 