import argparse
import os
import sys

from tqdm import tqdm

from lib import data
from lib.fetch import Video


def build_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='MSMO Builder', description='Retrieves and parses YouTube data to create the MSMO dataset'
    )
    parser.add_argument(
        '--video-ids',
        help='Path to a directory with .csv files of videos to use in the dataset',
        required=True,
        type=valid_dir
    )
    parser.add_argument(
        '-d', '--dataset-dir', help='Directory where the dataset will be created', required=True, type=valid_dir
    )
    parser.add_argument('-v', '--verbose', help='Displays additional logging while building the dataset', default=False)
    return parser


def valid_dir(arg: str):
    if not os.path.exists(arg) or not os.path.isdir(arg):
        raise ValueError(f"{arg} is not a valid directory")
    return arg


def main(args: argparse.Namespace):
    for entry in tqdm(data.read_entries(args.video_ids, args.dataset_dir)):
        if entry.exists():
            continue
        Video(entry).download()


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args(sys.argv[1:])
    main(args)
