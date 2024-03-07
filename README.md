# MMSum Data Collection Tool

Codebase for multimodal video data collection. 

## Installation

```python
conda create -n mmsum python=3.8
conda activate mmsum
pip install -r requirements.txt
```

## Build Dataset

```python
python3 build_msmo.py --video-ids ./keys --dataset-dir {dataset-dir} 2>&1 | tee "$HOME/build$(($(ls $HOME | wc -l)-3)).log"
```

### Citation

```
@inproceedings{Qiu2023MultiSumAD,
    title={MMSum: A Dataset for Multimodal Summarization and Thumbnail Generation of Videos},
    author={Jielin Qiu and Jiacheng Zhu and William Han and Aditesh Kumar and Karthik Mittal
            and Claire Jin and Zhengyuan Yang and Linjie Li and Jianfeng Wang
            and Ding Zhao and Bo Li and Lijuan Wang},
    journal={CVPR},
    year={2024}
```

## License

This project is licensed under the CC BY-NC-SA License.
