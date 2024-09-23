from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'gravity_app/index.html', context)