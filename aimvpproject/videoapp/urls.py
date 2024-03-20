from django.urls import path
from . import views

urlpatterns = [
  path('videos/', views.video_list),
  path('videos/process', views.video_process),
]