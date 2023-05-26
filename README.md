# MultiSum Data Collection Tool

Codebase for multimodal video data collection. 


## Build Dataset

```python
conda activate msmo
python3 build_msmo.py --video-ids ./keys --dataset-dir {dataset-dir} 2>&1 | tee "$HOME/build$(($(ls $HOME | wc -l)-3)).log"
```

## License

This project is licensed under the Apache-2.0 License.
