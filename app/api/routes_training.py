"""FastAPI routes for Unsloth AI Model Training, dataset management, and fine-tuning exports."""
import os
import json
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import JSONResponse, FileResponse

from app.services.training import (
    get_dataset_statistics,
    export_dataset_files,
    generate_full_dataset,
    convert_to_alpaca,
    convert_to_sharegpt,
    convert_to_llama3_text,
    SUPPORTED_BASE_MODELS,
    DEFAULT_BASE_MODEL
)
from app.config import settings

router = APIRouter(prefix="/api/training", tags=["model-training"])


@router.get("/status")
def get_training_status():
    """Returns dataset metrics, supported base models, and fine-tuning recommendations."""
    stats = get_dataset_statistics()
    fine_tuned_active = getattr(settings, "FINE_TUNED_MODEL_ENABLED", False)
    fine_tuned_url = getattr(settings, "FINE_TUNED_MODEL_URL", "http://localhost:11434/v1")
    fine_tuned_name = getattr(settings, "FINE_TUNED_MODEL_NAME", "meiyon:latest")

    return {
        "status": "ready",
        "dataset_statistics": stats,
        "supported_base_models": SUPPORTED_BASE_MODELS,
        "default_base_model": DEFAULT_BASE_MODEL,
        "fine_tuned_runtime": {
            "enabled": fine_tuned_active,
            "endpoint_url": fine_tuned_url,
            "model_name": fine_tuned_name
        },
        "colab_notebook_path": "notebooks/meiyon_unsloth_finetuning.ipynb",
        "quick_links": {
            "colab_badge": "https://colab.research.google.com/github/Mohilc/meiyonpersonalai/blob/main/notebooks/meiyon_unsloth_finetuning.ipynb",
            "unsloth_repo": "https://github.com/unslothai/unsloth"
        }
    }


@router.post("/export")
def trigger_dataset_export():
    """Generates fresh Alpaca, ShareGPT, and Llama-3 instruction datasets from live database."""
    try:
        results = export_dataset_files()
        stats = get_dataset_statistics()
        return {
            "success": True,
            "message": f"Successfully exported {stats['total_samples']} training samples.",
            "exported_files": results,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export training dataset: {str(e)}")


@router.get("/dataset")
def download_dataset(format: str = Query("alpaca", enum=["alpaca", "sharegpt", "llama3"])):
    """Downloads or previews the generated training dataset in requested format."""
    samples = generate_full_dataset()
    if format == "alpaca":
        data = convert_to_alpaca(samples)
        return JSONResponse(content=data)
    elif format == "sharegpt":
        data = convert_to_sharegpt(samples)
        return JSONResponse(content=data)
    else:
        data = convert_to_llama3_text(samples)
        return JSONResponse(content=data)
