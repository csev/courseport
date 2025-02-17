from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import os

def index(request):
    return render(request, 'uploads/index.html')

@csrf_exempt
def upload_files(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files[]')
        uploaded_files = []
        
        for file in files:
            # Save file to MEDIA_ROOT/uploads directory
            file_path = default_storage.save(f'uploads/{file.name}', file)
            uploaded_files.append(file_path)
            
        return JsonResponse({
            'message': 'Files uploaded successfully',
            'files': uploaded_files
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400) 