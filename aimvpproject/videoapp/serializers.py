from rest_framework import serializers
from .models import VideoItem

class VideoItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = VideoItem
    fields = ['id', 'title', 'url', 'processed_date']