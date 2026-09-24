"""Fine-tune Google Gemma 3 models using Unsloth with 4-bit LoRA.

This module demonstrates efficient fine-tuning of Gemma 3 language models
using Unsloth's optimized training pipeline with 4-bit quantization and LoRA.
"""

import logging
from typing import Any, Dict, Tuple

import torch
from datasets import Dataset, load_dataset
from transformers import TrainingArguments
from trl import SFTTrainer
from unsloth import FastModel
from unsloth.chat_templates import get_chat_template, standardize_sharegpt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration constants
MODEL_NAME = "unsloth/gemma-3-270m-it"
MAX_SEQ_LEN = 2048
LOAD_IN_4BIT = True
LOAD_IN_8BIT = False
FULL_FINETUNING = False
BATCH_SIZE = 2
GRADIENT_ACCUMULATION_STEPS = 4
WARMUP_STEPS = 5
MAX_STEPS = 60
LEARNING_RATE = 2e-4
OUTPUT_DIR = "outputs"
MODEL_OUTPUT_DIR = "finetuned_model"


def load_model_and_tokenizer() -> Tuple[Any, Any]:
    """Load Gemma 3 model and tokenizer with quantization and LoRA.

    Returns:
        Tuple[Any, Any]: Loaded model and tokenizer.

    Raises:
        Exception: If model loading fails.
    """
    logger.info(f"Loading model: {MODEL_NAME}")
    logger.info(f"Configuration: 4bit={LOAD_IN_4BIT}, LoRA={not FULL_FINETUNING}")

    try:
        model, tokenizer = FastModel.from_pretrained(
            model_name=MODEL_NAME,
            max_seq_length=MAX_SEQ_LEN,
            load_in_4bit=LOAD_IN_4BIT,
            load_in_8bit=LOAD_IN_8BIT,
            full_finetuning=FULL_FINETUNING,
        )

        if not FULL_FINETUNING:
            logger.info("Adding LoRA adapters to model")
            model = FastModel.get_peft_model(
                model,
                r=16,
                target_modules=[
                    "q_proj",
                    "k_proj",
                    "v_proj",
                    "o_proj",
                    "gate_proj",
                    "up_proj",
                    "down_proj",
                ],
            )

        logger.info("Applying Gemma 3 chat template")
        tokenizer = get_chat_template(tokenizer, chat_template="gemma-3")

        logger.info("Model and tokenizer loaded successfully")
        return model, tokenizer

    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def prepare_dataset(tokenizer: Any) -> Dataset:
    """Prepare training dataset with chat template formatting.

    Args:
        tokenizer (Any): The tokenizer to use for formatting.

    Returns:
        Dataset: Formatted training dataset.

    Raises:
        Exception: If dataset loading or processing fails.
    """
    logger.info("Loading FineTome-100k dataset")

    try:
        dataset = load_dataset("mlabonne/FineTome-100k", split="train")
        logger.info(f"Dataset loaded with {len(dataset)} examples")

        logger.info("Standardizing ShareGPT format")
        dataset = standardize_sharegpt(dataset)

        logger.info("Applying chat template to dataset")
        dataset = dataset.map(
            lambda ex: {
                "text": [
                    tokenizer.apply_chat_template(c, tokenize=False)
                    for c in ex["conversations"]
                ]
            },
            batched=True,
        )

        logger.info("Dataset prepared successfully")
        return dataset

    except Exception as e:
        logger.error(f"Error preparing dataset: {str(e)}")
        raise


def train(model: Any, dataset: Dataset) -> None:
    """Fine-tune the model on the prepared dataset.

    Args:
        model (Any): The model to fine-tune.
        dataset (Dataset): The training dataset.

    Raises:
        Exception: If training fails.
    """
    logger.info("Starting fine-tuning")

    # Determine training precision based on GPU capabilities
    use_bf16 = torch.cuda.is_available() and torch.cuda.is_bf16_supported()
    use_fp16 = torch.cuda.is_available() and not use_bf16

    logger.info(f"Training precision: bf16={use_bf16}, fp16={use_fp16}")
    logger.info(f"GPU available: {torch.cuda.is_available()}")

    try:
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=MAX_SEQ_LEN,
            args=TrainingArguments(
                per_device_train_batch_size=BATCH_SIZE,
                gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
                warmup_steps=WARMUP_STEPS,
                max_steps=MAX_STEPS,
                learning_rate=LEARNING_RATE,
                bf16=use_bf16,
                fp16=use_fp16,
                logging_steps=1,
                output_dir=OUTPUT_DIR,
            ),
        )

        logger.info("Beginning training loop")
        trainer.train()
        logger.info("Fine-tuning completed successfully")

    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise


def main() -> None:
    """Main function to orchestrate the fine-tuning process.

    Raises:
        Exception: If any step fails.
    """
    logger.info("Starting Gemma 3 fine-tuning pipeline")

    try:
        logger.info("Step 1: Loading model and tokenizer")
        model, tokenizer = load_model_and_tokenizer()

        logger.info("Step 2: Preparing dataset")
        dataset = prepare_dataset(tokenizer)

        logger.info("Step 3: Fine-tuning model")
        train(model, dataset)

        logger.info(f"Step 4: Saving model to {MODEL_OUTPUT_DIR}")
        model.save_pretrained(MODEL_OUTPUT_DIR)
        logger.info("Model saved successfully")

        logger.info("Fine-tuning pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error in fine-tuning pipeline: {str(e)}")
        raise


if __name__ == "__main__":
    main()
