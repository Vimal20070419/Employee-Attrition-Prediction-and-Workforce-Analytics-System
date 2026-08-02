"""AttritionIQ — File Handler Utility"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Tuple


def compute_file_hash(file_bytes: bytes) -> str:
    """Compute SHA-256 hash of file content."""
    return hashlib.sha256(file_bytes).hexdigest()


def save_upload_file(file_bytes: bytes, filename: str, target_dir: str) -> Tuple[str, int]:
    """Save bytes to target directory and return (filepath, file_size)."""
    dir_path = Path(target_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return str(file_path), len(file_bytes)
