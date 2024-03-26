from rest_framework import serializers
from .models import VideoItem

class VideoItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = VideoItem
    fields = ['id', 'title', 'url', 'processed_date', 'status', 'path', 'result_makes_attemps']

  def update(self, instance, validated_data):
      instance.title = validated_data.get('title', instance.title)
      instance.url = validated_data.get('url', instance.url)
      instance.processed_date = validated_data.get('processed_date', instance.processed_date)
      instance.status = validated_data.get('status', instance.status)
      instance.path = validated_data.get('path', instance.path)
      instance.result_makes_attemps = validated_data.get('result_makes_attemps', instance.result_makes_attemps)
      instance.save()
      return instance