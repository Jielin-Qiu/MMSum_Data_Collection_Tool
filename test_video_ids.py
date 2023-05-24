import pytest

import pytube
from youtube_transcript_api import YouTubeTranscriptApi

from lib import data
from lib import fetch
from lib import utils


ALL_VIDEO_IDS = [entry.youtube_id for entry in data.read_entries('./keys', '/mnt/MSMO')]

@pytest.mark.parametrize('youtube_id', ALL_VIDEO_IDS)
def test_has_480p_video(youtube_id):
    yt = pytube.YouTube(utils.short_yt_url(youtube_id))
    streams_480p = yt.streams.filter(file_extension='mp4', res='480p')
    assert len(streams_480p) > 0, f"{youtube_id} does not have a 480p stream"


@pytest.mark.parametrize('youtube_id', ALL_VIDEO_IDS)
def test_has_720p_video(youtube_id):
    yt = pytube.YouTube(utils.short_yt_url(youtube_id))
    streams_480p = yt.streams.filter(file_extension='mp4', res='720p')
    assert len(streams_480p) > 0, f"{youtube_id} does not have a 720p stream"


@pytest.mark.parametrize('youtube_id', ALL_VIDEO_IDS)
def test_has_transcript(youtube_id):
    transcript = YouTubeTranscriptApi.get_transcript(youtube_id, languages=('en', 'en-US', 'en-GB'))
    assert len(transcript) > 0, f"{youtube_id} does not have a transcript"


@pytest.mark.parametrize('youtube_id', ALL_VIDEO_IDS)
@pytest.mark.flaky
def test_has_keyframes(youtube_id):
    yt = pytube.YouTube(utils.short_yt_url(youtube_id))
    initial_data = pytube.extract.initial_data(yt.watch_html)

    errors = []
    try:
        panels = [
            p['engagementPanelSectionListRenderer'] for p in initial_data['engagementPanels']
            if p['engagementPanelSectionListRenderer'].get('panelIdentifier', None) ==
            'engagement-panel-macro-markers-auto-chapters'
        ]
        assert len(panels) > 0, f"{youtube_id} has no panel `engagement-panel-macro-markers-auto-chapters`"
        chapters = panels[0]['content']['macroMarkersListRenderer']['contents']
        assert len(chapters) > 0, f"{youtube_id} has no chapters"
        for chapter in (c for c in chapters if 'macroMarkersListItemRenderer' in c):
            renderer = chapter['macroMarkersListItemRenderer']
            assert len(
                renderer['thumbnail']['thumbnails']
            ) > 0, f"Chapter `{renderer['title']['simpleText']}` has no thumbnails"
    except (KeyError, AssertionError) as e:
        errors.append(e)
    else:
        return

    # Option B: use the markers on the video to get the keyframes.
    try:
        markers = initial_data['playerOverlays']['playerOverlayRenderer']['decoratedPlayerBarRenderer'][
            'decoratedPlayerBarRenderer']['playerBar']['multiMarkersPlayerBarRenderer']['markersMap']
        chapter_markers = [m for m in markers if m['key'] in ('AUTO_CHAPTERS', 'DESCRIPTION_CHAPTERS')]
        assert len(chapter_markers) > 0, f"{youtube_id} has no CHAPTER markers"
        chapter_markers = list(sorted(chapter_markers, key=lambda m: m['key'], reverse=True))
        chapters = chapter_markers[0]['value']['chapters']
        assert len(chapters) > 0, f"{youtube_id} has no keyframes"
    except (KeyError, AssertionError) as e:
        errors.append(e)
    else:
        return

    raise Exception(f"Video ID {youtube_id} has no keyframes\n" + \
                        "\n\n".join('\t' + str(e) for e in errors))


if __name__ == '__main__':
    pytest.main()