"""Unit tests for Unsloth AI Model Training, dataset generation, and fine-tuning endpoints."""
import os
import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.services.training import (
    generate_full_dataset,
    convert_to_alpaca,
    convert_to_sharegpt,
    convert_to_llama3_text,
    export_dataset_files,
    get_dataset_statistics,
    UnslothTrainingConfig,
    SUPPORTED_BASE_MODELS
)
from scripts.training.train_unsloth import check_gpu_environment, run_training_pipeline

client = TestClient(app)


def test_training_config_defaults():
    """Verify default hyperparameters for Unsloth training."""
    cfg = UnslothTrainingConfig()
    assert "Llama-3.2-3B" in cfg.base_model_name
    assert cfg.load_in_4bit is True
    assert cfg.lora_r == 16
    assert cfg.lora_alpha == 16
    assert "q_proj" in cfg.target_modules
    assert cfg.export_gguf_quantization == "q4_k_m"

    d = cfg.to_dict()
    assert d["base_model_name"] == cfg.base_model_name
    assert d["lora_r"] == 16


def test_generate_full_dataset():
    """Verify full dataset contains required golden scenarios and structure."""
    samples = generate_full_dataset()
    assert len(samples) >= 8

    categories = {s["category"] for s in samples}
    assert "persona" in categories
    assert "tool_calling" in categories
    assert "verification_rag" in categories

    for s in samples:
        assert "instruction" in s
        assert "output" in s
        assert len(s["output"]) > 20


def test_dataset_converters():
    """Verify conversion to Alpaca, ShareGPT, and Llama-3 formats."""
    samples = generate_full_dataset()

    # Alpaca
    alpaca = convert_to_alpaca(samples)
    assert len(alpaca) == len(samples)
    assert "instruction" in alpaca[0]
    assert "input" in alpaca[0]
    assert "output" in alpaca[0]

    # ShareGPT
    sharegpt = convert_to_sharegpt(samples)
    assert len(sharegpt) == len(samples)
    convs = sharegpt[0]["conversations"]
    assert len(convs) == 3
    assert convs[0]["from"] == "system"
    assert convs[1]["from"] == "human"
    assert convs[2]["from"] == "gpt"

    # Llama-3
    llama3 = convert_to_llama3_text(samples)
    assert len(llama3) == len(samples)
    assert "<|begin_of_text|>" in llama3[0]["text"]
    assert "<|start_header_id|>assistant<|end_header_id|>" in llama3[0]["text"]


def test_export_dataset_files(tmp_path):
    """Verify export_dataset_files creates valid JSON and JSONL files."""
    results = export_dataset_files(target_dir=tmp_path)
    assert Path(results["alpaca"]).exists()
    assert Path(results["sharegpt"]).exists()
    assert Path(results["llama3"]).exists()

    with open(results["alpaca"], "r", encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert len(data) > 0

    with open(results["sharegpt"], "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
        assert len(lines) == len(data)


def test_get_dataset_statistics():
    """Verify dataset statistics computation."""
    stats = get_dataset_statistics()
    assert stats["total_samples"] >= 8
    assert stats["curated_samples"] >= 8
    assert "tool_calling" in stats["categories"]
    assert len(stats["supported_formats"]) >= 3


def test_routes_training_status():
    """Verify GET /api/training/status endpoint."""
    resp = client.get("/api/training/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert "dataset_statistics" in data
    assert "supported_base_models" in data
    assert "fine_tuned_runtime" in data
    assert "llama-3.2-3b" in data["supported_base_models"]


def test_routes_training_export():
    """Verify POST /api/training/export endpoint."""
    resp = client.post("/api/training/export")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "exported_files" in data
    assert "alpaca" in data["exported_files"]


def test_routes_training_download():
    """Verify GET /api/training/dataset endpoint."""
    resp = client.get("/api/training/dataset?format=alpaca")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    assert len(items) > 0
    assert "instruction" in items[0]

    resp_share = client.get("/api/training/dataset?format=sharegpt")
    assert resp_share.status_code == 200
    assert isinstance(resp_share.json(), list)


def test_gpu_environment_check():
    """Verify check_gpu_environment returns structured diagnostic dict."""
    env = check_gpu_environment()
    assert "cuda_available" in env
    assert "device_name" in env
    assert "unsloth_installed" in env


def test_training_pipeline_dry_run():
    """Verify run_training_pipeline executes cleanly in dry-run mode on non-GPU."""
    res = run_training_pipeline()
    assert res is not None
    assert "status" in res
    assert res["status"] in ("dry_run_passed", "success")
