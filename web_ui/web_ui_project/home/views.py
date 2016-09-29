from django.shortcuts import render

from web_ui_project.project_settings import app_list

# Create your views here.


def index(request):
    return render(request, 'home/index.html', {'app_list': app_list})
