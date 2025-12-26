"""
Utility functions for the agentom package.

Note: The agent entrypoint (``agentom.agent``) registers
``clear_temp_dir`` as a shutdown hook so temporary files are
automatically removed on normal process exit or user-initiated
interrupts (e.g. Ctrl+C).
"""
import shutil
import traceback
from .settings import settings
from agentom.logging_utils import logger

# All the below logics are moved to middleware package's config and utils,
# but kept here for backward compatibility and reference.

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

def clear_input_dir():
    """
    Clear all files and subdirectories in the input directory.
    This is useful for cleaning up inputs from previous runs.
    """
    if settings.INPUT_DIR.exists():
        for item in settings.INPUT_DIR.iterdir():
            try:
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception:
                logger.exception("Failed to remove '%s'", item)
        logger.info("Cleared input directory: %s", settings.INPUT_DIR)

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


def transfer_outputs_to_target_dir(target_dir: str):
    """
    Transfer all files from the output directory to a specified target directory.

    Args:
        target_dir: The directory to which output files should be transferred. Should be later set by user in UI/CLI.
    """
    datetime_folder_name = settings.RUN_DATETIME.strftime("%Y%m%d_%H%M%S")
    target_path = settings.WORKSPACE_DIR / target_dir / datetime_folder_name
    target_path.mkdir(parents=True, exist_ok=True)

    if settings.OUTPUT_DIR.exists():
        for item in settings.OUTPUT_DIR.iterdir():
            try:
                dest = target_path / item.name
                if item.is_file():
                    shutil.move(str(item), str(dest))
                elif item.is_dir():
                    shutil.move(str(item), str(dest))
            except Exception:
                logger.exception("Failed to transfer '%s' to '%s'", item, target_path)
        logger.info("Transferred outputs to target directory: %s", target_path)