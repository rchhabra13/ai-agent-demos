# Llama 3.2 Fine-Tuning with LoRA

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Fine-tune Meta's Llama 3.2 3B Instruct model using LoRA adapters and [Unsloth](https://github.com/unslothai/unsloth) for 2x faster training with 70% less memory. Trains on the FineTome-100k dataset with 4-bit quantization — runs on Google Colab free tier.

## How It Works

```
FineTome-100k Dataset → Chat Template Formatting → LoRA Adapters (rank 16) → SFTTrainer → Saved Model
```

The script loads the base model in 4-bit precision, attaches LoRA adapters to attention and MLP layers, formats the dataset into Llama 3.1 chat template, and trains with SFTTrainer from TRL.

## Features

- **4-bit quantization** via Unsloth — fits in 8-12GB VRAM
- **LoRA adaptation** on all attention + MLP projections (rank 16)
- **FineTome-100k** multi-turn conversation dataset (ShareGPT format)
- **bf16/fp16 auto-detection** based on GPU capabilities
- Saves LoRA weights for efficient inference

## Quick Start

```bash
git clone https://github.com/rchhabra13/llama3-2-finetuning.git
cd llama3-2-finetuning
pip install -r requirements.txt
python finetune_llama3.2.py
```

The fine-tuned model saves to `finetuned_model/`. Training logs print to stdout.

## Configuration

Edit constants at the top of `finetune_llama3.2.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL_NAME` | `unsloth/Llama-3.2-3B-Instruct` | Base model (also supports 1B) |
| `LORA_RANK` | `16` | LoRA rank (8 for smaller, 32 for more capacity) |
| `MAX_SEQ_LENGTH` | `2048` | Context window |
| `max_steps` | `60` | Training steps (increase for full training) |

## Tech Stack

Python, PyTorch, Unsloth, Transformers, TRL, Datasets

## License

MIT
