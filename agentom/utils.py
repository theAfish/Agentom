"""
Utility functions for the agentom package.
"""
import shutil
import traceback
from .settings import settings
from agentom.logging_utils import logger


def clear_temp_dir():
    """
    Clear all files and subdirectories in the temporary directory.
    This is useful for cleaning up after a run to free up space.
    """
    if settings.TEMP_DIR.exists():
        for item in settings.TEMP_DIR.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception:
                logger.exception("Failed to remove '%s'", item)
        logger.info("Cleared temporary directory: %s", settings.TEMP_DIR)

def clear_output_dir():
    """
    Clear all files and subdirectories in the output directory.
    This is useful for cleaning up outputs from previous runs.
    """
    if settings.OUTPUT_DIR.exists():
        for item in settings.OUTPUT_DIR.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception:
                logger.exception("Failed to remove '%s'", item)
        logger.info("Cleared output directory: %s", settings.OUTPUT_DIR)


def clear_workspace():
    """
    Clear all files and subdirectories in the workspace directory.
    """
    if settings.WORKSPACE_DIR.exists():
        # Remove all files and subdirectories inside the workspace
        for item in settings.WORKSPACE_DIR.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
            except Exception:
                logger.exception("Failed to remove '%s'", item)
        logger.info("Cleared workspace directory: %s", settings.WORKSPACE_DIR)