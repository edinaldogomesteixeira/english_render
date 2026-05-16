import json
import os

import ffmpeg
from pathlib import Path
import eng_to_ipa as ipa

from django.conf import settings

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

#from .utils.youtube import extract_youtube_id
from django.core.paginator import Paginator

from django.shortcuts import (

    render,
    redirect,
    get_object_or_404,

)

from .models import (

    Video,
    Vocabulary,

)


from .services.thumbnails import (
    generate_thumbnail
)

from .services.word_counter import (
    count_words
)

from .services.video_processor import (
    process_video
)

from .services.video_youtube import (
    video_youtube_download
)

# ====================================
# HOME
# ====================================

def home(request):

    videos = Video.objects.all().order_by(
        '-created_at'
    )

    return render(

        request,

        'home.html',

        {
            'videos': videos
        }

    )


# ====================================
# VIDEO DETAIL
# ====================================

def video_detail(
    request,
    video_id
):

    video = get_object_or_404(

        Video,
        id=video_id

    )

    return render(

        request,

        'video_detail.html',

        {
            'video': video
        }

    )


# ====================================
# VOCABULARY
# ====================================

def vocabulary(request):

    words_list = Vocabulary.objects.all().order_by(
        '-created_at'
    )

    paginator = Paginator(
        words_list,
        10
    )

    page_number = request.GET.get(
        'page'
    )

    words = paginator.get_page(
        page_number
    )

    return render(

        request,

        'vocabulary.html',

        {
            'words': words
        }

    )
# ====================================
# STATISTICA
# ====================================

def statistics(request):

    total_videos = 120
    total_hours = 15
    current_level = "A1"
    daily_average = 27
    weekly_videos = 10

    context = {
        'current_level': current_level,
        'next_level_time': '34 hrs 46 mins',
        'total_hours': '15 hrs 14 mins',
        'weekly_hours': '1 hr 48 mins',
        'total_videos': total_videos,
        'weekly_videos': weekly_videos,
        'daily_average': 27,
        'level_a1_hours': 15,
        'level_a2_hours': 10,
        'level_b1_hours': 5,
        'level_b2_hours': 4,
        'level_c1_hours': 3,
        'level_c2_hours': 2,
    }

    return render(request, 'statistics.html', context)

# ====================================
# SAVE WORD
# ====================================

def save_word(request):

    if request.method == 'POST':

        word = (

            request.POST.get(
                'word',
                ''
            )

            .strip()

            .lower()

        )

        sentence = (

            request.POST.get(
                'sentence',
                ''
            )

            .strip()

        )

        if word:

            existing_word = Vocabulary.objects.filter(
                word=word
            ).first()

            if not existing_word:

                try:

                    ipa_text = ipa.convert(
                        word
                    )

                except:

                    ipa_text = '-'

                Vocabulary.objects.create(

                    word=word,

                    ipa=ipa_text,

                    original_sentence=sentence,

                )

            return JsonResponse({

                'status': 'success',

                'word': word,

                'sentence': sentence

            })

    return JsonResponse({

        'status': 'error'

    })

def delete_word(request, word_id):

    word = get_object_or_404(
        Vocabulary,
        id=word_id
    )

    word.delete()
    page = request.POST.get('page', 1)

    return redirect(
        f'/vocabulary/?page={page}'
    )

# ====================================
# VIDEO YOUTUBE+LOCAL
# ====================================
def upload_video(request):

    if request.method == 'POST':

        title = request.POST.get(
            'title'
        )

        description = request.POST.get(
            'description'
        )

        level = request.POST.get(
            'level'
        )

        youtube_url = request.POST.get(
            'youtube_url'
        )

        video_file = request.FILES.get(
            'video_file'
        )

        # =========================================
        # LOCAL VIDEO
        # =========================================

        if video_file:

            video = Video.objects.create(

                title=title or video_file.name,

                description=description,

                level=level,

                source_type='local',

                video_file=video_file,

                status='processing'
            )

            process_video(

                video.id,

                schedule=5

            )

        # =========================================
        # YOUTUBE VIDEO
        # =========================================

        elif youtube_url:

            video = Video.objects.create(

                title=title or 'YouTube Video',

                description=description or '',

                level=level,

                source_type='youtube',

                youtube_url=youtube_url,

                status='processing'
            )

            process_video(

                video.id,

                schedule=5

            )

    return redirect('home')

# =========================================================
# Delete CARD
# =========================================================
def delete_video(request, video_id):

    video = get_object_or_404(
        Video,
        id=video_id
    )

    if request.method == 'POST':

        video.delete()

    return redirect('home')



def video_status(request, video_id):

    try:

        video = Video.objects.get(
            id=video_id
        )

        return JsonResponse({

            'status': video.status,

            'thumbnail': (

                video.thumbnail.url

                if video.thumbnail

                else ''

            ),

            'duration': video.duration,

            'word_count': video.word_count

        })

    except Video.DoesNotExist:

        return JsonResponse({

            'status': 'deleted'

        }, status=404)