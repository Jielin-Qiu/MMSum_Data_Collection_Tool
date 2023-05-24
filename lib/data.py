import csv
from dataclasses import dataclass
import os

from lib import utils


@dataclass
class MSMOEntry:
    """Class for tracking entries in the dataset."""
    category: str
    subcategory: str
    index: int
    youtube_id: str
    root_dir: str

    def keyframe_path(self, keyframe_id):
        return utils.make_path(self._subfolder('keyframe'), self.video_id, f"keyframe_{keyframe_id}.jpg")

    def annotation_path(self):
        return utils.make_path(self._subfolder('annotation'), f"{self.video_id}.json")

    def video_path(self):
        return utils.make_path(self._subfolder('video'), f"{self.video_id}.mp4")

    def _subfolder(self, attribute: str):
        return os.path.join(self.root_dir, attribute, self.category, self.subcategory)

    @staticmethod
    def _key(s: str):
        return s[:3].upper()

    @property
    def category_key(self) -> str:
        return self._key(self.category)

    @property
    def subcategory_key(self) -> str:
        return self._key(self.subcategory)

    @property
    def video_id(self) -> str:
        """Build the MSMO dataset key for a given video entry.
        
        The data set key consists of:
            - The first 3 letters of the category (capitalized).
            - The first 3 letters of the subcategory (capitalized).
            - The a 4 digit number representing the index.
        """
        return f"{self.category_key}{self.subcategory_key}{self.index:04d}"

    def exists(self) -> bool:
        """Whether the entry has already been downloaded."""
        return all(os.path.exists(p) for p in (self.annotation_path(), self.keyframe_path(0), self.video_path()))


def read_entries(key_dir, data_dir, categories=None):
    assert os.path.exists(key_dir) and os.path.isdir(key_dir)
    if categories:
        assert all(f"{cat}.csv" in os.listdir(key_dir) for cat in categories)
        files = [os.path.join(key_dir, f"{cat}.csv") for cat in categories]
    else:
        files = [os.path.join(key_dir, filename) for filename in os.listdir(key_dir)]
    for file in files:
        category = utils.sanitize(os.path.basename(file)[:-len('.csv')])
        with open(file, 'r') as csvfile:
            subcategory = None
            for line in csv.reader(csvfile):
                if line[0]:
                    subcategory = utils.sanitize(line[0])
                    idx = 0
                for vid in line[1:]:
                    if vid:
                        yield MSMOEntry(category, subcategory, idx, vid, data_dir)
                        idx += 1


if __name__ == '__main__':
    from collections import defaultdict
    length = len(tuple(read_entries('./keys')))
    assert length == 17 * 10 * 30, f"Length is {length}"
    cats = defaultdict(int)
    subcats = defaultdict(int)
    for entry in read_entries('./keys'):
        cats[entry.category] += 1
        subcats[entry.subcategory] += 1
    assert len(cats) == 17, f"Expected 17 categories, found {len(cats)}"
    assert all(count == 10 * 30 for _, count in cats.items())
    # These lines will fail because the `writing` subcategory exists in both the `hobbies` and `education` categories.
    # assert len(subcats) == 17 * 10, f"Expected 170 subcategories, found {len(subcats)}"
    # assert all(count == 30 for _, count in subcats.items())