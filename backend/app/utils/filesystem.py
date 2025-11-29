"""
Filesystem utilities for directory and file management.

Provides functions for creating directories, validating files,
and managing file operations.
"""

from pathlib import Path
from typing import List
import logging

from ..config import settings

logger = logging.getLogger(__name__)


def ensure_directories() -> None:
    """
    Ensure all required directories exist.

    Creates directories if they don't exist. Safe to call multiple times.
    """
    directories = [
        settings.upload_dir,
        settings.scripts_dir,
        settings.vectordb_path,
        settings.log_dir,
    ]

    for dir_path in directories:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            raise


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Name of the file

    Returns:
        str: File extension without the dot (e.g., 'pdf', 'md')
    """
    return Path(filename).suffix.lstrip('.').lower()


def is_allowed_file_type(filename: str) -> bool:
    """
    Check if file type is allowed for upload.

    Args:
        filename: Name of the file to check

    Returns:
        bool: True if file type is allowed
    """
    extension = get_file_extension(filename)
    return extension in settings.allowed_document_types


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size against maximum allowed size.

    Args:
        file_size: Size of file in bytes

    Returns:
        bool: True if file size is within limits
    """
    return file_size <= settings.max_upload_size


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to remove potentially dangerous characters.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Remove any characters that aren't alphanumeric, underscore, hyphen, or dot
    import re
    filename = re.sub(r'[^a-zA-Z0-9_\-.]', '', filename)

    return filename


def get_unique_filename(directory: str, filename: str) -> str:
    """
    Generate a unique filename in the given directory.

    If filename exists, appends a number to make it unique.

    Args:
        directory: Directory to check
        filename: Desired filename

    Returns:
        str: Unique filename
    """
    base_path = Path(directory)
    file_path = base_path / filename

    if not file_path.exists():
        return filename

    # File exists, append number
    name_stem = file_path.stem
    extension = file_path.suffix
    counter = 1

    while True:
        new_filename = f"{name_stem}_{counter}{extension}"
        new_path = base_path / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1


def save_uploaded_file(content: bytes, filename: str, directory: str = None) -> Path:
    """
    Save uploaded file to disk.

    Args:
        content: File content as bytes
        filename: Name for the file
        directory: Directory to save to (defaults to upload_dir)

    Returns:
        Path: Path to saved file

    Raises:
        ValueError: If file type not allowed
        IOError: If save fails
    """
    if directory is None:
        directory = settings.upload_dir

    # Sanitize filename
    filename = sanitize_filename(filename)

    # Check file type
    if not is_allowed_file_type(filename):
        raise ValueError(
            f"File type not allowed. Allowed types: {settings.allowed_document_types}"
        )

    # Get unique filename
    unique_filename = get_unique_filename(directory, filename)

    # Save file
    file_path = Path(directory) / unique_filename

    try:
        file_path.write_bytes(content)
        logger.info(f"Saved file: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Failed to save file {file_path}: {e}")
        raise IOError(f"Failed to save file: {e}")


def list_files_in_directory(directory: str, extension: str = None) -> List[Path]:
    """
    List all files in a directory.

    Args:
        directory: Directory to list
        extension: Optional file extension filter (e.g., '.py')

    Returns:
        List[Path]: List of file paths
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        return []

    if extension:
        if not extension.startswith('.'):
            extension = f'.{extension}'
        return list(dir_path.glob(f'*{extension}'))
    else:
        return [f for f in dir_path.iterdir() if f.is_file()]


def delete_file(file_path: str) -> bool:
    """
    Delete a file.

    Args:
        file_path: Path to file to delete

    Returns:
        bool: True if deleted successfully
    """
    try:
        Path(file_path).unlink()
        logger.info(f"Deleted file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete file {file_path}: {e}")
        return False
