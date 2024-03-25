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
import requests
import mimetypes
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.conf import settings

# Create your views here.

def process(vid_name, video_id, disp = False, save_vid = False, debug = False):
  shot_det = ShotDetector()
  ret = False
  path = download_file_to_server(vid_name)
  print("vvvvvvvvvvvvvv", path)
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

def download_file_to_server(vid_id):

    # fill these variables with real values   vid_id = 10tQGaAD_9c2am4_Yo6qVjf4YMBj5s6Fn
    url = f"https://api.1upstats.com/public/uploads/{vid_id}"

    # Make a request to the URL to get the file content
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(settings.MEDIA_ROOT, vid_id)
        
        # Stream the content and write it to a file in chunks
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1048576):
                file.write(chunk)
                
        return file_path
    else:
        response.raise_for_status()

@api_view(['GET'])
def download_video_to_local(request, name):
  print("downdowndown", name)
  url = 'http://198.22.162.34/home/don/Work/django-ai-api/aimvpproject/data/'
  root, ext = os.path.splitext(name)
  output_name = root + "_processed.mp4"
  with requests.get(url, stream=True) as r:
        r.raise_for_status()  # Raises an HTTPError if the response status code is 4XX/5XX
        with open(output_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1048576): 
                f.write(chunk)
  return HttpResponse(f"File has been downloaded and saved as: {output_name}") 

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
    path = request.data['title']
    current_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    default_path = current_directory + r"/data/demo.mp4"
    vid_path = current_directory + path
    print("vvvvvvvvvvvvvv", default_path)
    validated_data = serializer.validated_data
    validated_data['status'] = VideoItem.VideoStatus.PROCESSING
    serializer.save()
    video_id = serializer.data['id']
    t = Thread(target=process, args=(path, video_id), kwargs={'save_vid': True})
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
