# MSMO

Codebase for MSMO data collection


## Build Dataset

```python
conda activate msmo
python3 build_msmo.py --video-ids ./keys --dataset-dir /mnt/data1/jielin/msmo 2>&1 | tee "$HOME/build$(($(ls $HOME | wc -l)-3)).log"
```