import zipfile
from pathlib import Path
from app_logging.logger import get_logger

logger = get_logger(__name__)

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def extract_zip(zip_path: Path, extract_to: Path) -> None:
    if not zip_path.exists():
        logger.error(f"File not found: {zip_path}")
        return
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        logger.info(f"Extracted {zip_path} to {extract_to}")
