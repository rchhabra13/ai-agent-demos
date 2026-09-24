"""Llama 3.2 fine-tuning script using LoRA adapters and Unsloth.

This module fine-tunes Meta's Llama 3.2 3B Instruct model on the FineTome-100k
dataset using LoRA adapters and 4-bit quantization for memory-efficient training.
Optimized for Google Colab and consumer GPUs (8-12GB VRAM).
"""

import logging
from typing import Any

import torch
from datasets import DatasetDict
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template, standardize_sharegpt

# Configuration constants
MODEL_NAME: str = "unsloth/Llama-3.2-3B-Instruct"
MAX_SEQ_LENGTH: int = 2048
LORA_RANK: int = 16
BATCH_SIZE: int = 2
GRADIENT_ACCUMULATION_STEPS: int = 4
WARMUP_STEPS: int = 5
MAX_STEPS: int = 60
LEARNING_RATE: float = 2e-4
OUTPUT_DIR: str = "outputs"
MODEL_OUTPUT_DIR: str = "finetuned_model"

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

TARGET_MODULES: list[str] = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "gate_proj", "up_proj", "down_proj"
]


def load_model_and_tokenizer() -> tuple[Any, Any]:
    """Load Llama 3.2 model and tokenizer with 4-bit quantization.

    Returns:
        tuple[Any, Any]: Loaded model and tokenizer objects.

    Raises:
        RuntimeError: If model loading fails.
    """
    try:
        logger.info(f"Loading model: {MODEL_NAME}")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=MODEL_NAME,
            max_seq_length=MAX_SEQ_LENGTH,
            load_in_4bit=True,
        )
        logger.info("Model and tokenizer loaded successfully")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise RuntimeError(f"Model loading failed: {e}") from e


def apply_lora_adapters(model: Any) -> Any:
    """Apply LoRA adapters to the model.

    Args:
        model (Any): The loaded model.

    Returns:
        Any: Model with LoRA adapters applied.

    Raises:
        RuntimeError: If LoRA adapter application fails.
    """
    try:
        logger.info(f"Applying LoRA adapters (rank={LORA_RANK})")
        model = FastLanguageModel.get_peft_model(
            model,
            r=LORA_RANK,
            target_modules=TARGET_MODULES,
        )
        logger.info("LoRA adapters applied successfully")
        return model
    except Exception as e:
        logger.error(f"Failed to apply LoRA adapters: {e}")
        raise RuntimeError(f"LoRA adapter application failed: {e}") from e


def prepare_dataset(tokenizer: Any) -> DatasetDict:
    """Load and prepare the FineTome-100k dataset for training.

    Args:
        tokenizer (Any): The loaded tokenizer.

    Returns:
        DatasetDict: Processed dataset ready for training.

    Raises:
        RuntimeError: If dataset loading or processing fails.
    """
    try:
        logger.info("Loading FineTome-100k dataset")
        tokenizer = get_chat_template(tokenizer, chat_template="llama-3.1")
        dataset = load_dataset("mlabonne/FineTome-100k", split="train")
        dataset = standardize_sharegpt(dataset)

        logger.info("Formatting dataset with chat template")
        dataset = dataset.map(
            lambda examples: {
                "text": [
                    tokenizer.apply_chat_template(convo, tokenize=False)
                    for convo in examples["conversations"]
                ]
            },
            batched=True,
        )
        logger.info("Dataset prepared successfully")
        return dataset
    except Exception as e:
        logger.error(f"Failed to prepare dataset: {e}")
        raise RuntimeError(f"Dataset preparation failed: {e}") from e


def train_model(model: Any, dataset: DatasetDict) -> None:
    """Train the model using SFTTrainer.

    Args:
        model (Any): The model with LoRA adapters.
        dataset (DatasetDict): The prepared training dataset.

    Raises:
        RuntimeError: If training fails.
    """
    try:
        logger.info("Setting up trainer")
        training_args = TrainingArguments(
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            warmup_steps=WARMUP_STEPS,
            max_steps=MAX_STEPS,
            learning_rate=LEARNING_RATE,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            output_dir=OUTPUT_DIR,
        )

        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=MAX_SEQ_LENGTH,
            args=training_args,
        )

        logger.info("Starting training")
        trainer.train()
        logger.info("Training completed successfully")
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise RuntimeError(f"Model training failed: {e}") from e


def save_model(model: Any) -> None:
    """Save the fine-tuned model.

    Args:
        model (Any): The trained model.

    Raises:
        RuntimeError: If model saving fails.
    """
    try:
        logger.info(f"Saving model to {MODEL_OUTPUT_DIR}")
        model.save_pretrained(MODEL_OUTPUT_DIR)
        logger.info("Model saved successfully")
    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        raise RuntimeError(f"Model saving failed: {e}") from e


def main() -> None:
    """Main execution function for fine-tuning pipeline."""
    try:
        model, tokenizer = load_model_and_tokenizer()
        model = apply_lora_adapters(model)
        dataset = prepare_dataset(tokenizer)
        train_model(model, dataset)
        save_model(model)
        logger.info("Fine-tuning pipeline completed successfully")
    except RuntimeError as e:
        logger.error(f"Fine-tuning pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()