# Gemma 3 Fine-Tuning with Unsloth

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Fine-tune Google's Gemma 3 models using [Unsloth](https://github.com/unslothai/unsloth) for 2x faster training with 4-bit LoRA. Supports multiple model sizes (1B, 4B, 12B, 27B) with automatic CUDA optimization. Runs on Google Colab free tier.

## Quick Start

```bash
git clone https://github.com/rchhabra13/gemma3-finetuning.git
cd gemma3-finetuning
pip install -r requirements.txt
python finetune_gemma3.py
```

## Configuration

Edit `finetune_gemma3.py` to customize:

| Parameter | Default | Options |
|-----------|---------|---------|
| `model_name` | `unsloth/gemma-3-4b-it` | 1b-it, 4b-it, 12b-it, 27b-it |
| `max_seq_length` | `2048` | Up to 8192 |
| `r` (LoRA rank) | `16` | 8, 16, 32, 64 |
| `max_steps` | `60` | Increase for full training |

## How It Works

1. Loads Gemma 3 in 4-bit precision via Unsloth
2. Attaches LoRA adapters to attention + MLP layers
3. Formats the Alpaca dataset with chat templates
4. Trains with TRL's SFTTrainer (bf16/fp16 auto-detected)
5. Saves LoRA weights to `finetuned_model/`

## Tech Stack

Python, PyTorch, Unsloth, Transformers, TRL, Datasets

## License

MIT
