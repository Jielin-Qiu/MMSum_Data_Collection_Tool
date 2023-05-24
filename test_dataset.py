import os

import pytest

from lib.constants import DATASET_DIR


def test_has_each_annotation():
    for cat in os.listdir(video_dir := os.path.join(DATASET_DIR, 'annotation')):
        for subcat in os.listdir(cat_dir := os.path.join(video_dir, cat)):
            for i, ann_file in enumerate(sorted(os.listdir(subcat_dir := os.path.join(cat_dir, subcat)))):
                exp_filename = f"{cat[:3].upper()}{subcat[:3].upper()}{i:04}.json"
                assert ann_file == exp_filename, f"Expected `{exp_filename}`; Received `{ann_file}`"
                assert os.path.getsize(
                    os.path.join(subcat_dir, ann_file)
                ) > 0, f"Annotation file `{os.path.join(subcat_dir, ann_file)}` is empty"

def test_has_keyframes_in_order():
    errors = []
    for cat in os.listdir(keyframe_dir := os.path.join(DATASET_DIR, 'keyframe')):
        for subcat in os.listdir(cat_dir := os.path.join(keyframe_dir, cat)):
            for vid in os.listdir(subcat_dir := os.path.join(cat_dir, subcat)):
                vid_dir = os.path.join(subcat_dir, vid)
                # assert len(os.listdir(vid_dir)) > 0, f"No keyframes found in `{vid_dir}`"
                frames = set(os.listdir(vid_dir))
                for i in range(len(frames)):
                    if f"keyframe_{i}.jpg" not in frames:
                        errors.append(f"{vid_dir}: Expected `keyframe_{i}.jpg` in {frames}")
    if errors:
        print(*errors, sep='\n')
        raise AssertionError

def test_has_at_least_one_keyframe():
    errors = []
    for cat in os.listdir(keyframe_dir := os.path.join(DATASET_DIR, 'keyframe')):
        for subcat in os.listdir(cat_dir := os.path.join(keyframe_dir, cat)):
            for vid in os.listdir(subcat_dir := os.path.join(cat_dir, subcat)):
                vid_dir = os.path.join(subcat_dir, vid)
                # assert len(os.listdir(vid_dir)) > 0, f"No keyframes found in `{vid_dir}`"
                if len(os.listdir(vid_dir)) <= 0:
                    errors.append(f"No keyframes found in `{vid_dir}`")
                for keyframe in os.listdir(vid_dir):
                    img_file = os.path.join(vid_dir, keyframe)
                    # assert os.path.getsize(img_file) > 0, f"Keyframe `{img_file}` is empty"
                    if os.path.getsize(img_file) <= 0:
                        errors.append(f"Keyframe `{img_file}` is empty")
    if errors:
        print(*errors, sep='\n')
        raise AssertionError


def test_has_each_video():
    empty = []
    for cat in os.listdir(video_dir := os.path.join(DATASET_DIR, 'video')):
        for subcat in os.listdir(cat_dir := os.path.join(video_dir, cat)):
            for i, vid_file in enumerate(sorted(os.listdir(subcat_dir := os.path.join(cat_dir, subcat)))):
                exp_filename = f"{cat[:3].upper()}{subcat[:3].upper()}{i:04}.mp4"
                assert vid_file == exp_filename, f"Expected `{exp_filename}`; Received `{vid_file}`"
                # assert os.path.getsize(
                #     os.path.join(subcat_dir, vid_file)
                # ) > 0, f"Video file `{os.path.join(subcat_dir, vid_file)}` is empty"
                if os.path.getsize(os.path.join(subcat_dir, vid_file)) <= 0:
                    empty.append(f"Video file `{os.path.join(subcat_dir, vid_file)}` is empty")
    if empty:
        print(*empty, sep='\n')
        raise AssertionError


def test_has_complete_dir_structure():
    annot_dir = os.path.join(DATASET_DIR, 'annotation')
    video_dir = os.path.join(DATASET_DIR, 'video')
    keyframe_dir = os.path.join(DATASET_DIR, 'keyframe')

    def _validate_directory(dir):
        assert os.path.isdir(dir)
        assert len(os.listdir(dir)) == 17, f"Expected 17 categories in `{dir}`; Found {len(os.listdir(dir))}"
        for cat in os.listdir(dir):
            cat_dir = os.path.join(dir, cat)
            assert len(
                os.listdir(cat_dir)
            ) == 10, f"Expected 10 subcategories in `{cat_dir}`; Found {len(os.listdir(cat_dir))}"
            for subcat in os.listdir(cat_dir):
                subcat_dir = os.path.join(cat_dir, subcat)
                assert len(
                    os.listdir(subcat_dir)
                ) == 30, f"Expected 30 entries in `{subcat_dir}`; Found {len(os.listdir(subcat_dir))}"

    _validate_directory(annot_dir)
    _validate_directory(video_dir)
    _validate_directory(keyframe_dir)


if __name__ == '__main__':
    pytest.main()