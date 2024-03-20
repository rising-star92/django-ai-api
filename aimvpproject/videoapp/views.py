from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VideoItem
from .serializers import VideoItemSerializer
from .aiutility.shotdetector import ShotDetector
import os
from tqdm import tqdm

# Create your views here.

def process(path, disp = False, save_vid = False, debug = False):
  shot_det = ShotDetector()
  if os.path.isdir(path):
    print(f"[INFO]: Processing videos in {path}(same directory as executable)")
    video_files = []
    for filename in os.listdir(path):
      if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):  # Add other video formats if needed
        vid_path = os.path.join(path, filename)
        video_files.append(vid_path)
    for vid_path in tqdm(video_files, desc=f" || Processing {vid_path} ||"):
      print(f"Processing {os.path.basename(vid_path)}")
      shot_det.process_vid(vid_path, disp, save_vid=True)
      shot_det.reset()
  elif os.path.isfile(path):
    vid_path = path
    shot_det.process_vid(vid_path, disp, save_vid, debug)
  else:
    print("[ERROR] Given path is neither Video Nor Directory!")


@api_view(['GET'])
def video_list(request):
  videos = VideoItem.objects.all()
  serializer = VideoItemSerializer(videos, many=True)
  return Response(serializer.data)

@api_view(['POST'])
def video_process(request):
  serializer = VideoItemSerializer(data=request.data)
  if serializer.is_valid():
    path = request.data['url']
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = current_directory + r"/data/demo.mp4"
    # process(default_path, save_vid = True)
    serializer.save()
    return Response(
      {
        "message": "Video processing is success!",
        "url": "path",
      },
      status=status.HTTP_200_OK)
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

