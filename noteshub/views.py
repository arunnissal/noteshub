from django.shortcuts import render
from django.http import HttpResponse
import os

def serve_frontend(request, path=''):
    """
    Serve the frontend React app for any non-API routes
    """
    try:
        # Get the path to the frontend index.html
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'index.html')
        
        with open(frontend_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return HttpResponse(content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Frontend not found. Please build the frontend files.", status=404) 