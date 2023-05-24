#!/usr/bin/bash

LOG_BASE="$HOME/data_eval"

pytest test_video_ids.py::test_has_480p_video 2>&1 | tee "$LOG_BASE/480p.log"
pytest test_video_ids.py::test_has_720p_video 2>&1 | tee "$LOG_BASE/720p.log"
pytest test_video_ids.py::test_has_transcript 2>&1 | tee "$LOG_BASE/transcript.log"
pytest test_video_ids.py::test_has_keyframes 2>&1 | tee "$LOG_BASE/keyframes.log"
