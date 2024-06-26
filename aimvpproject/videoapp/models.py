from django.db import models

# Create your models here.
class VideoItem(models.Model):
  class VideoStatus(models.TextChoices):
    PROCESSING = 'processing'
    PROCESSED = 'processed'
    UPLOADING = 'uploading'

  title = models.CharField(max_length=200)
  url = models.TextField()
  processed_date = models.DateTimeField(auto_now_add=True)
  status = models.CharField(max_length = 20, choices = VideoStatus.choices, default = VideoStatus.PROCESSING)
  path = models.TextField(default="")
  result_makes_attemps = models.TextField(default="0/0")

  def __str__(self) -> str:
    return self.title