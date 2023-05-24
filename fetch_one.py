from typing import List, Dict
from xml.etree import ElementTree

import pytube

from lib import utils
from lib import data
from lib.fetch import Video


def get_video(video_id: str) -> pytube.YouTube:
    """Fetch metadata for a YouTube video by its id."""
    return pytube.YouTube(utils.short_yt_url(video_id))


def parse_transcripts_from_xml(xml_captions: str) -> List[Dict[str, str]]:
    """(DEPRECATED) Given an XML object for the video captions, construct a transcript for the video.

    We now use `youtube_transcript_api` to retrieve the captions, so this function is no longer needed.
    """
    transcripts = []
    root = ElementTree.fromstring(xml_captions)
    for child in root.find('body'):
        if child.tag != 'p':
            continue
        caption = ''.join(seg.text for seg in child)
        try:
            duration = float(child.attrib["d"])
        except KeyError:
            duration = 0.0
        start = float(child.attrib["t"])
        end = start + duration
        transcripts.append(
            {
                'index': len(transcripts),
                'start_time': utils.float_to_timestamp(start),
                'end_time': utils.float_to_timestamp(end),
                'length': utils.float_to_timestamp(end - start),
                'transcript': caption,
            }
        )
    return transcripts


if __name__ == '__main__':
    vid = Video(
        data.MSMOEntry(
            category='education',
            subcategory='presentation',
            index=0,
            youtube_id='xnZzXckB5TU',
            root_dir='./scratch/d',
        )
    )
    vid.download()

    # yt = get_video('3awIjbIzPhk')
    # captions_en = yt.captions['a.en']
    # with open('scratch/captions.txt', 'w') as fp:
    #     transcripts = parse_transcripts_from_xml(captions_en.xml_captions)
    #     fp.write(json.dumps(transcripts))
