import os

from pathlib import Path

from background_task import background

from django.conf import settings

from videos.models import Video

from videos.services.transcription import (
    generate_srt
)

from videos.services.word_counter import (
    count_words
)

from videos.services.thumbnails import (
    generate_thumbnail
)

from videos.services.video_duration import (
    get_video_duration
)

from videos.services.video_youtube import (
    video_youtube_download
)


@background(schedule=5)
def process_video(video_id):

    print(
        'START PROCESS:',
        video_id
    )

    # ====================================
    # GET VIDEO
    # ====================================

    video = Video.objects.filter(
        id=video_id
    ).first()

    if not video:

        print(
            f'Video {video_id} not found'
        )

        return

    try:

        # ====================================
        # YOUTUBE DOWNLOAD
        # ====================================

        if (
            video.source_type == 'youtube'
            and video.youtube_url
        ):

            print(
                'DOWNLOADING YOUTUBE VIDEO...'
            )

            data = video_youtube_download(
                video.youtube_url
            )

            relative_path = (
                Path(data['filepath'])
                .relative_to(settings.MEDIA_ROOT)
            )

            video.video_file = str(
                relative_path
            )

            video.youtube_id = data.get(
                'youtube_id'
            )

            # Atualiza título automaticamente
            if (
                not video.title
                or video.title == 'YouTube Video'
            ):

                video.title = data.get(
                    'title'
                )

            video.save()

            print(
                'YOUTUBE DOWNLOAD FINISHED'
            )

        # ====================================
        # VIDEO PATH
        # ====================================

        video_path = video.video_file.path

        # ====================================
        # DURATION
        # ====================================

        video.duration = (

            get_video_duration(
                video_path
            )

        )

        # ====================================
        # THUMBNAIL
        # ====================================

        thumbnail_dir = os.path.join(

            settings.MEDIA_ROOT,

            'videos'

        )

        os.makedirs(

            thumbnail_dir,

            exist_ok=True

        )

        video_filename = os.path.basename(
            video_path
        )

        name, _ = os.path.splitext(
            video_filename
        )

        thumbnail_filename = (
            f'{name}.jpg'
        )

        thumbnail_path = os.path.join(

            thumbnail_dir,

            thumbnail_filename

        )

        # ====================================
        # YOUTUBE THUMBNAIL
        # ====================================

        if (
            video.source_type == 'youtube'
            and data
        ):

            print(
                'USING YOUTUBE THUMBNAIL...'
            )

            thumbnail_path = data[
                'thumbnail_path'
            ]

            thumbnail_filename = data[
                'thumbnail_filename'
            ]

        # ====================================
        # LOCAL VIDEO THUMBNAIL
        # ====================================

        else:

            print(
                'GENERATING LOCAL THUMBNAIL...'
            )

            generate_thumbnail(

                video_path,

                thumbnail_path

            )

        # ====================================
        # SAVE THUMBNAIL
        # ====================================

        video.thumbnail.name = (
            f'videos/{thumbnail_filename}'
        )


        # ====================================
        # SUBTITLE
        # ====================================

        subtitles_dir = os.path.join(

            settings.MEDIA_ROOT,

            'subtitles'

        )

        os.makedirs(

            subtitles_dir,

            exist_ok=True

        )

        srt_filename = (
            f'{video.id}.srt'
        )

        srt_path = os.path.join(

            subtitles_dir,

            srt_filename

        )

        # ====================================
        # GENERATE SRT + TRANSCRIPTION
        # ====================================

        transcription_text = generate_srt(

            video_path,

            srt_path

        )

        video.subtitle_file.name = (
            f'subtitles/{srt_filename}'
        )

        # ====================================
        # DESCRIPTION
        # ====================================

        # Salva somente frases limpas
        video.description = (
            transcription_text.strip()
        )

        # ====================================
        # WORD COUNT
        # ====================================

        video.word_count = count_words(
            transcription_text
        )

        # ====================================
        # STATUS
        # ====================================

        video.status = 'ready'

        # ====================================
        # SAVE
        # ====================================

        video.save()

        print(
            f'Video {video.id} processed'
        )

    except Exception as error:

        print(
            'PROCESS ERROR:'
        )

        print(error)

        if video:

            video.status = 'error'

            video.save()