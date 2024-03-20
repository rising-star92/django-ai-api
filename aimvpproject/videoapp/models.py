from django.db import models

# Create your models here.
class VideoItem(models.Model):
  title = models.CharField(max_length=200)
  url = models.TextField()
  processed_date = models.DateTimeField(auto_now_add=True)

  def __str__(self) -> str:
    return self.title