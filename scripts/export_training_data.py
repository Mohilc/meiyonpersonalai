"""CLI Script to generate and export training datasets for Unsloth AI fine-tuning."""
import os
import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.training import export_dataset_files, get_dataset_statistics

def main():
    print("=" * 65)
    print("🚀 Meiyon AI Dataset Exporter for Unsloth Fine-Tuning")
    print("=" * 65)

    stats = get_dataset_statistics()
    print(f"\n📊 Current Dataset Summary:")
    print(f"  • Total Training Samples: {stats['total_samples']}")
    print(f"  • Curated Scenarios:      {stats['curated_samples']}")
    print(f"  • Live Database Records:  {stats['database_samples']}")
    print(f"  • Categories:             {', '.join([f'{k}: {v}' for k, v in stats['categories'].items()])}")
    print(f"  • Recommended Model:      {stats['recommended_base_model']}")

    print("\n📦 Generating export files...")
    results = export_dataset_files()

    print("\n✅ Successfully exported:")
    print(f"  1. Alpaca Format:   {results['alpaca']}")
    print(f"  2. ShareGPT Format: {results['sharegpt']}")
    print(f"  3. Llama-3 Format:  {results['llama3']}")
    print("\n💡 You can now upload these files to Google Colab or train directly with:")
    print("   python scripts/training/train_unsloth.py")
    print("=" * 65)

if __name__ == "__main__":
    main()
