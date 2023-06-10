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

### Citation

```
@inproceedings{Qiu2023MultiSumAD,
    title={MultiSum: A Dataset for Multimodal Summarization and Thumbnail Generation of Videos},
    author={Jielin Qiu and Jiacheng Zhu and William Han and Aditesh Kumar and Karthik Mittal
            and Claire Jin and Zhengyuan Yang and Linjie Li and Jianfeng Wang
            and Bo Li and Ding Zhao and Lijuan Wang},
    journal={arXiv preprint arXiv:2306.04216},
    year={2023}
```

## License

This project is licensed under the CC BY-NC-SA License.
