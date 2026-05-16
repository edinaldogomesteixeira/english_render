from pathlib import Path

import yt_dlp

from django.conf import settings


def video_youtube_download(url):

    download_dir = Path(
        settings.MEDIA_ROOT
    ) / 'videos'

    thumbnail_dir = Path(
        settings.MEDIA_ROOT
    ) / 'thumbnails'

    download_dir.mkdir(
        exist_ok=True
    )

    thumbnail_dir.mkdir(
        exist_ok=True
    )

    ydl_opts = {

        # VIDEO MP4
        "format": (
            "best[ext=mp4][height<=360]"
            "[acodec!=none][vcodec!=none]"
        ),

        # LOCAL DO VIDEO
        "outtmpl": str(
            download_dir / "%(title)s.%(ext)s"
        ),

        # BAIXA THUMBNAIL
        "writethumbnail": True,

        # EMBUTE THUMBNAIL NO MP4
        "embedthumbnail": True,

        # CONVERTE THUMBNAIL PARA JPG
        "postprocessors": [

            {

                "key": "FFmpegThumbnailsConvertor",

                "format": "jpg"

            }

        ],

        "noplaylist": True,

        "sleep_interval": 3,

        "max_sleep_interval": 8,

        "http_headers": {

            "User-Agent": (

                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"

            )

        }

    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(
            info
        )

        title = info.get(
            'title'
        )

        # THUMBNAIL JPG
        thumbnail_filename = (
            f'{title}.jpg'
        )

        thumbnail_path = (
            thumbnail_dir
            / thumbnail_filename
        )

    return {

        'title': title,

        'filepath': filename,

        'thumbnail_path': str(
            thumbnail_path
        ),

        'thumbnail_filename': (
            thumbnail_filename
        ),

        'youtube_id': info.get('id'),

        'description': info.get(
            'description',
            ''
        )

    }