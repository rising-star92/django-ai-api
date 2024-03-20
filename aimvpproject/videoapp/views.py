from rest_framework import viewsets
from .models import VideoItem
from .serializers import VideoItemSerializer

# Create your views here.
class VideoItemViewSet(viewsets.ModelViewSet):
  queryset = VideoItem.objects.all()
  serializer_class = VideoItemSerializer
