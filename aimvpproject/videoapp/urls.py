from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
  path('videos/', views.video_list),
  path('videos/<int:pk>/', views.video_details),
  path('videos/process', views.video_process),
  path('videos/upload', views.video_upload),
  path('videos/download/<int:pk>', views.download_video_to_local)
]
if settings.DEBUG:
    # urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)