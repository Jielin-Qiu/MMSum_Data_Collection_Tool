# MultiSum Data Collection Tool

Codebase for multimodal video data collection. 

## Installation

```python
conda create -n multisum python=3.8
conda activate multisum
pip install -r requirements.txt
```

## Build Dataset

```python
python3 build_msmo.py --video-ids ./keys --dataset-dir {dataset-dir} 2>&1 | tee "$HOME/build$(($(ls $HOME | wc -l)-3)).log"
```

## License

This project is licensed under the CC BY-NC-SA License.
