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

def process(path, video_id, disp = False, save_vid = False, debug = False):
  shot_det = ShotDetector()
  ret = False

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
    ret = True
  elif os.path.isfile(path):
    vid_path = path
    shot_det.process_vid(vid_path, disp, save_vid, debug)
    ret = True
  else:
    print("[ERROR] Given path is neither Video Nor Directory!")
    ret = False

  if ret:
    video = VideoItem.objects.get(pk = video_id)    
    serializer = VideoItemSerializer(instance = video)
    data = serializer.data
    data['status'] = VideoItem.VideoStatus.PROCESSED
    serializer.update(video, data)


@api_view(['GET', 'POST'])
def video_list(request):
  if request.method == 'GET':
    videos = VideoItem.objects.all()
    serializer = VideoItemSerializer(videos, many=True)
    return Response(serializer.data)
  
  elif request.method == 'POST':
    serializer = VideoItemSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def video_details(request, pk):
  try:
    video = VideoItem.objects.get(pk=pk)
  except VideoItem.DoesNotExist:
    return Response(status=status.HTTP_404_NOT_FOUND)
  
  if request.method == 'GET':
    serializer = VideoItemSerializer(video)
    return Response(serializer.data)
  
  elif request.method == 'PUT':
    serializer = VideoItemSerializer(instance=video, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    else:
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  elif request.method == 'DELETE':
    video.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
  
@api_view(['POST'])
def video_process(request):
  serializer = VideoItemSerializer(data=request.data)
  if serializer.is_valid():
    path = request.data['url']
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_path = current_directory + r"/data/demo.mp4"
    vid_path = current_directory + path
    validated_data = serializer.validated_data
    validated_data['status'] = VideoItem.VideoStatus.PROCESSING
    serializer.save()
    video_id = serializer.data['id']
    t = Thread(target=process, args=(vid_path, video_id), kwargs={'save_vid': True})
    t.start()
    return Response(serializer.data)
  return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def video_upload(request):
  if request.FILES['FILES']:
    myfile = request.FILES['FILES']
    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)
    uploaded_file_url = fs.url(filename)
    return Response({"message": "Video uploading is success!", "url": uploaded_file_url})
  