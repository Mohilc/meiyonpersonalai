"""Training configuration and hyperparameter specifications for Unsloth AI fine-tuning."""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
TRAINING_DIR = DATA_DIR / "training"
TRAINING_DIR.mkdir(parents=True, exist_ok=True)

# Recommended Base Models for Unsloth Fine-Tuning
SUPPORTED_BASE_MODELS = {
    "llama-3.2-3b": "unsloth/Llama-3.2-3B-Instruct",
    "llama-3.2-1b": "unsloth/Llama-3.2-1B-Instruct",
    "llama-3.1-8b": "unsloth/meta-llama-3.1-8b-instruct-bnb-4bit",
    "mistral-7b": "unsloth/mistral-7b-instruct-v0.3-bnb-4bit",
    "qwen-2.5-7b": "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"
}

DEFAULT_BASE_MODEL = "unsloth/Llama-3.2-3B-Instruct"

@dataclass
class UnslothTrainingConfig:
    """Hyperparameters and configuration for fine-tuning Meiyon with Unsloth."""
    # Model parameters
    base_model_name: str = DEFAULT_BASE_MODEL
    max_seq_length: int = 2048
    dtype: str = "None"  # None for auto-detection (Float16 / Bfloat16)
    load_in_4bit: bool = True  # 4-bit QLoRA reduces VRAM by up to 70%

    # LoRA Adapter parameters
    lora_r: int = 16
    lora_alpha: int = 16
    lora_dropout: float = 0.0  # Unsloth supports optimized 0 dropout
    bias: str = "none"
    use_gradient_checkpointing: str = "unsloth"  # 60% less VRAM
    random_state: int = 3407
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"
    ])

    # SFT Trainer parameters
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 10
    max_steps: int = 80  # ~15-20 minutes on free T4 GPU
    learning_rate: float = 2e-4
    logging_steps: int = 5
    optim: str = "adamw_8bit"
    weight_decay: float = 0.01
    lr_scheduler_type: str = "linear"
    seed: int = 3407
    output_dir: str = "outputs"

    # Export formats
    export_gguf_quantization: str = "q4_k_m"  # Recommended for fast CPU/Ollama inference
    hub_model_id: str = "mohilc/meiyon-llama-3.2-3b"

    def to_dict(self) -> Dict[str, Any]:
        """Converts configuration to dictionary."""
        return {
            "base_model_name": self.base_model_name,
            "max_seq_length": self.max_seq_length,
            "load_in_4bit": self.load_in_4bit,
            "lora_r": self.lora_r,
            "lora_alpha": self.lora_alpha,
            "target_modules": self.target_modules,
            "learning_rate": self.learning_rate,
            "max_steps": self.max_steps,
            "batch_size": self.per_device_train_batch_size,
            "gradient_accumulation_steps": self.gradient_accumulation_steps,
            "export_gguf_quantization": self.export_gguf_quantization,
            "hub_model_id": self.hub_model_id
        }
