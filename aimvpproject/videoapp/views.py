from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import VideoItem
from .serializers import VideoItemSerializer
from .aiutility.shotdetector import ShotDetector
import os
from tqdm import tqdm
from django.core.files.storage import FileSystemStorage
from threading import Thread
import time

# Create your views here.

def process(path, serializer, disp = False, save_vid = False, debug = False):
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
      # serialize = VideoItemSerializer(data = serializer)
      if serializer.is_valid():
        validated_data = serializer.validated_data
        validated_data['status'] = "processed"
        serializer.save()
      time.sleep(2)
  elif os.path.isfile(path):
    vid_path = path
    # shot_det.process_vid(vid_path, disp, save_vid, debug)
    if serializer.is_valid():
      print("aaaaaaaaaaaaa", serializer.validated_data.get('status'))
      validated_data = serializer.validated_data
      validated_data['status'] = "processed"
      serializer.save()
    time.sleep(2)
  else:
    print("[ERROR] Given path is neither Video Nor Directory!")
    time.sleep(2)


@api_view(['GET'])
def video_list(request):
  videos = VideoItem.objects.filter(id=request.query_params['id'])
  serializer = VideoItemSerializer(videos, many=True)
  return Response(serializer.data)
  # return Response({"message":f"The video {request.query_params['id']} is {serializer.data['status']}."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def video_process(request):
  serializer = VideoItemSerializer(data=request.data)
  if serializer.is_valid():
    path = request.data['url']
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = current_directory + r"/data/demo.mp4"
    vid_path = current_directory + path
    validated_data = serializer.validated_data
    validated_data['status'] = "processing" 
    serializer.save()
    t = Thread(target=process, args=(vid_path, serializer), kwargs={'save_vid': True})
    t.start()
    return Response(
      {
        "video_id": serializer.data['id']
      },
      status=status.HTTP_200_OK)
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def video_upload(request):
  if request.FILES['FILES']:
    myfile = request.FILES['FILES']
    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    return Response({"message": "Video uploading is success!", "url": uploaded_file_url})
  