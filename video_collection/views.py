from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower
from .forms import VideoForm, SearchForm
from .models import Video


def home(request):
    app_name = 'Video Game Trailers'
    return render(request, 'video_collection/home.html', {'app_name': app_name})


# adds the video if it meets all criteria
def add(request):
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                return redirect('video_list')   # go to video list if save is successful
            except ValidationError:
                messages.warning(request, 'Invalid YouTube URL')
            except IntegrityError:
                messages.warning(request, 'You already added that video')
        messages.warning(request, 'Please check the data entered')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

    new_video_form = VideoForm()
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})


def video_list(request):
    search_form = SearchForm(request.GET)

    # sorts videos by title and lets user search their list
    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))
    else:
        search_form = SearchForm()
        videos = Video.objects.order_by(Lower('name'))
    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})


def video_detail(request, video_pk):
    video = get_object_or_404(Video, pk=video_pk)
    return render(request, 'video_collection/video_detail.html', {'video': video})
