# Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization
Official implementation of paper:

> "Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization"
> Tiancheng Xing, Jerry Li, Yixuan Du, Xiyang Hu

<div align=center>
<img width=100% src="./img/raf.png"/>
</div>


## Run
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Create folder for each dataset, name unified file unified_dataset.json
huggingface-cli login #Login to HuggingFace
wandb login #Login to WandDB
python pipeline.py


## Citation
If you find our code useful for your research, please cite our paper.
```bibtex
@article{xing2025llms,
  title={Are LLMs Reliable Rankers? Rank Manipulation via Two-Stage Token Optimization},
  author={Xing, Tiancheng and Li, Jerry and Du, Yixuan and Hu, Xiyang},
  journal={arXiv preprint arXiv:2510.06732},
  year={2025}
}
```
