from rest_framework import serializers
from .models import VideoItem

class VideoItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = VideoItem
    # fields = ['id', 'title', 'url', 'processed_date']
    fields = ['id', 'title', 'url', 'processed_date', 'status', 'path']
  def update(self, instance, validated_data):
      instance.title = validated_data.get('title', instance.title)
      instance.url = validated_data.get('url', instance.url)
      instance.processed_date = validated_data.get('processed_date', instance.processed_date)
      instance.status = validated_data.get('status', instance.status)
      instance.path = validated_data.get('path', instance.path)
      instance.save()
      return instance