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
import requests
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.conf import settings

# Create your views here.

def process(url, video_id, disp = False, save_vid = False, debug = False):
  shot_det = ShotDetector()
  ret = False
  
  video = VideoItem.objects.get(pk = video_id)
  serializer = VideoItemSerializer(instance = video)
  data = serializer.data
  data['status'] = VideoItem.VideoStatus.UPLOADING
  serializer.update(video, data)
  
  path = download_file_to_server(url, str(video_id))

  data['status'] = VideoItem.VideoStatus.PROCESSING
  serializer.update(video, data)
  
  if os.path.isdir(path):
    print(f"[INFO]: Processing videos in {path}(same directory as executable)")
    video_files = []
    for filename in os.listdir(path):
      if filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.flv')):  # Add other video formats if needed
        vid_path = os.path.join(path, filename)
        video_files.append(vid_path)
    for vid_path in tqdm(video_files, desc=f" || Processing {vid_path} ||"):
      print(f"Processing {os.path.basename(vid_path)}")
      result_path = shot_det.process_vid(vid_path, disp, save_vid=True)
      shot_det.reset()
    ret = True
  elif os.path.isfile(path):
    vid_path = path
    result_path = shot_det.process_vid(vid_path, disp, save_vid, debug)
    ret = True
  else:
    print("[ERROR] Given path is neither Video Nor Directory!")
    ret = False

  if ret:
    data['status'] = VideoItem.VideoStatus.PROCESSED
    data['path'] = result_path
    serializer.update(video, data)

def download_file_to_server(url, video_id):
    dest_folder = os.path.join(settings.MEDIA_ROOT, video_id)
    if not os.path.exists(dest_folder):
      os.makedirs(dest_folder)

    filename = url.split('/')[-1].replace(" ", "_")
    file_path = os.path.join(dest_folder, filename)

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024*8):
                file.write(chunk)
        print("file_down_path", file_path)        
        return file_path
    else:
        response.raise_for_status()

@api_view(['GET'])
def download_video_to_local(request, pk):
  video = VideoItem.objects.get(pk=pk)
  try:
    video = VideoItem.objects.get(pk=pk)
    video_path = video.path
    file_name = video_path.split('/')[-1]

    print(file_name)

    FilePointer = open(video_path, "rb")
    response = HttpResponse(FilePointer, content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name

    return response
  
  except:
    return Response(status=status.HTTP_404_NOT_FOUND)

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
    url = request.data['url']

    validated_data = serializer.validated_data
    validated_data['status'] = VideoItem.VideoStatus.PROCESSING    
    serializer.save()

    video_id = serializer.data['id']

    t = Thread(target=process, args=(url, video_id), kwargs={'save_vid': True})
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
