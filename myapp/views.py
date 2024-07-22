import json
import os
import yt_dlp
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from googleapiclient.discovery import build
from django.conf import settings

def index(request):
    return render(request, 'myapp/index.html')

def youtube_video_details(video_id):
    youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
    request = youtube.videos().list(part='snippet,contentDetails', id=video_id)
    response = request.execute()
    return response['items'][0] if response['items'] else None

@csrf_exempt
def fetch_audio(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            youtube_url = data.get('url')
            
            if not youtube_url:
                return JsonResponse({'error': 'No URL provided'}, status=400)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_audio.%(ext)s',
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                audio_file = 'downloaded_audio.' + info_dict.get('ext', 'mp4')
                
                if not os.path.exists(audio_file):
                    return JsonResponse({'error': 'Audio file not found'}, status=404)
                
                response = HttpResponse(open(audio_file, 'rb'), content_type='audio/mp4')
                response['Content-Disposition'] = f'attachment; filename="{info_dict["title"]}.mp4"'
                os.remove(audio_file)
                return response
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
