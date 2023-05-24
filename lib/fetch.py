import json
import math
import urllib

from pytube import YouTube, extract
from youtube_transcript_api import YouTubeTranscriptApi

from lib import constants
from lib import utils
from lib.data import MSMOEntry

logger = utils.get_logger()


class Video:
    def __init__(self, entry: MSMOEntry):
        self.entry = entry
        self.youtube_id = entry.youtube_id
        self.yt = YouTube(utils.short_yt_url(self.youtube_id))
        self.initial_data = extract.initial_data(self.yt.watch_html)

    def download(self):
        logger.info(f"Downloading {self.entry.video_id} ({self.youtube_id})")
        annotation = self.get_annotation()
        with open(self.entry.annotation_path(), 'w') as ann_file:
            ann_file.write(json.dumps(annotation, indent=2))
        video = self.yt.streams.filter(mime_type='video/mp4').get_highest_resolution()
        for attempt in range(5):
            try:
                video.download(filename=self.entry.video_path())
            except urllib.error.HTTPError as e:
                logger.warn(
                    f"Attempt {attempt}: Failed to download video for video `{self.youtube_id}` ({self.entry.video_id})"
                    + "\n" + str(e)
                )
            else:
                break
        else:
            logger.error(f"Failed to download video stream for `{self.youtube_id}`")

    def get_transcript(self):
        transcripts = []
        prev_start, prev_dur, prev_end = None, None, None
        for i, subtitle in enumerate(
            YouTubeTranscriptApi.get_transcript(self.youtube_id, languages=('en', 'en-US', 'en-GB'))
        ):
            # Clip previous transcript if it goes past the start of the currents transcript
            if i > 0 and prev_start + prev_dur >= math.floor(subtitle['start']):
                prev_end = math.floor(subtitle['start']) - 1
                # Merge transcripts if the clipped transcript would be less than 1 second long
                if prev_end - prev_start < 1:
                    prev_end = math.floor(subtitle['start'] + subtitle['duration'])
                    transcripts[-1]['end_time'] = utils.float_to_timestamp(prev_end)
                    transcripts[-1]['length'] = utils.float_to_timestamp(prev_end - prev_start)
                    transcripts[-1]['summary'] += ' ' + subtitle['text']
                    continue # Because we merged, we don't to skip to the next transcript
                transcripts[-1]['end_time'] = utils.float_to_timestamp(prev_end)
                transcripts[-1]['length'] = utils.float_to_timestamp(prev_end - prev_start)
            prev_start = math.floor(subtitle['start'])
            prev_end = math.floor(subtitle['start'] + subtitle['duration'])
            prev_dur = prev_end - prev_start
            transcripts.append(
                {
                    'index': i,
                    'start_time': utils.float_to_timestamp(prev_start),
                    'end_time': utils.float_to_timestamp(prev_end),
                    'length': utils.float_to_timestamp(prev_dur),
                    'summary': subtitle['text']
                }
            )
        return transcripts

    def _chapter_renderers_from_overlay(self):
        """Look for chapters in the video overlay.
        
        Generates an iterable of tuples (timestamp, renderer), each corresponding to a chapter.
        """
        markers = self.initial_data['playerOverlays']['playerOverlayRenderer']['decoratedPlayerBarRenderer'][
            'decoratedPlayerBarRenderer']['playerBar']['multiMarkersPlayerBarRenderer']['markersMap']
        chapters = markers[0]['value']['chapters']
        for chapter in chapters:
            renderer = chapter['chapterRenderer']
            assert len(
                renderer['thumbnail']['thumbnails']
            ) > 0, f"Chapter `{renderer['title']['simpleText']}` has no thumbnails"
            ts = renderer['timeRangeStartMillis'] / 1000
            yield ts, renderer

    def _chapter_renderers_from_engagement_panel(self):
        """Look for chapters in the engagement panel section.
        
        Generates an iterable of tuples (timestamp, renderer), each corresponding to a chapter.
        """
        panels = [
            p['engagementPanelSectionListRenderer'] for p in self.initial_data['engagementPanels']
            if p['engagementPanelSectionListRenderer'].get('panelIdentifier', None) ==
            'engagement-panel-macro-markers-auto-chapters'
        ]
        chapters = panels[0]['content']['macroMarkersListRenderer']['contents']
        for chapter in (c for c in chapters if 'macroMarkersListItemRenderer' in c):
            renderer = chapter['macroMarkersListItemRenderer']
            assert len(
                renderer['thumbnail']['thumbnails']
            ) > 0, f"Chapter `{renderer['title']['simpleText']}` has no thumbnails"
            ts = renderer['onTap']['watchEndpoint']['startTimeSeconds']
            yield ts, renderer

    def chapter_renderers(self, tries=5):
        """Try to extract the chapters from either the engagement panel or the overlay.
        
        Try each location twice, to account for a non-determinism issue with the `pytube` API.
        """
        errors = []
        for _ in range(tries):
            for gen in (self._chapter_renderers_from_engagement_panel, self._chapter_renderers_from_overlay):
                try:
                    return list(gen())
                except (KeyError, IndexError, AssertionError) as e:
                    errors.append(e)
        raise Exception(
            f"Unable to find chapters for video `{self.youtube_id} ({self.entry.video_id})`\n" +
            "\n".join("\t" + repr(e) for e in errors)
        )

    def get_summary(self):
        """"Create a list of chapters from the video.
        
        Each video is broken up to segments, labeled as either "Key Moments" or "Chapters".
        This function extracts the (start time, end time, length) for each segment, and also
        downloads the thumbnail for the segment.
        """
        summary = []
        prev_start = 0.
        for i, (ts, renderer) in enumerate(self.chapter_renderers()):
            if i > 0:
                summary[-1]['end_time'] = utils.float_to_timestamp(ts - 1)
                summary[-1]['length'] = utils.float_to_timestamp(ts - prev_start - 1)
            summary.append(
                {
                    'segment': i,
                    'start_time': utils.float_to_timestamp(ts),
                    'summary': renderer['title']['simpleText'],
                }
            )
            prev_start = ts
            # Extract keyframe with proper size from `thumbnails` and download
            keyframe = [
                frame for frame in renderer['thumbnail']['thumbnails']
                if frame['height'] == constants.KEYFRAME_HEIGHT and frame['width'] == constants.KEYFRAME_WIDTH
            ]
            assert len(keyframe) > 0, f"Frame `{summary[-1]['summary']}` of {self.youtube_id} has no thumbnail"
            utils.download_blob(keyframe[0]['url'], self.entry.keyframe_path(i))
        if summary:
            summary[-1]['end_time'] = utils.float_to_timestamp(self.yt.length * 1000)
            summary[-1]['length'] = utils.float_to_timestamp(self.yt.length - prev_start)
        return summary

    def get_annotation(self):
        summary = self.get_summary()
        info = {
            'video_id': self.entry.video_id,
            'youtube_id': self.youtube_id,
            'url': self.yt.watch_url,
            'author': self.yt.author,
            'title': self.yt.title,
            'num_of_segments': len(summary),
            'duration': utils.float_to_timestamp(self.yt.length),
            'category': self.entry.category,
            'sub_category': self.entry.subcategory,
        }
        return {
            'info': info,
            'summary': summary,
            'transcript': self.get_transcript(),
        }