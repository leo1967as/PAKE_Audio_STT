import torch
import faster_whisper
import pyannote.audio
import numpy as np
import sys

print(f"Python Version: {sys.version}")
print(f"NumPy Version: {np.__version__} (Should be 1.26.4)")
print(f"PyTorch Version: {torch.__version__} (Should be 2.1.2)")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU Device: {torch.cuda.get_device_name(0)}")
else:
    print("⚠️  Running on CPU mode")

try:
    import scipy
    print(f"SciPy Version: {scipy.__version__} (Should be 1.11.4)")
except ImportError:
    print("❌ SciPy not installed")

print("✅ Stack check finished.")
