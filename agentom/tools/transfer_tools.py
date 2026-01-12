"""Tools for saving and sharing workspace files over A2A.

These utilities keep files on disk in the session-specific workspace while
exposing stable URLs via the Starlette static mount at ``/artifacts``.
"""

from pathlib import Path
from typing import List

from google.adk.tools.tool_context import ToolContext

from agentom.settings import settings
from agentom.tools.common_tools import safe_path


def _artifact_base_uri() -> str:
    """Return the base URL where artifacts are served."""
    return f"{settings.A2A_PROTOCOL}://{settings.A2A_HOST}:{settings.A2A_PORT}/artifacts/{settings.current_session_folder}"


async def select_workspace_files_for_transfer(
    files: List[str]
) -> dict:
    """Return public URLs for files in the workspace.
    
    Converts workspace file paths to downloadable URLs.
    Accepts paths relative to the workspace.

    Args:
        files: List of file paths to expose. Can be:
            - Relative to current session workspace (e.g., "outputs/file.cif")

    Returns:
        dict with:
            - result: Summary message
            - file_urls: List of downloadable HTTP URLs
            - missing: List of files that couldn't be found
    """
    if not files:
        return {"error": "No files provided"}

    uris = []
    missing = []

    for item in files:
        candidate = None
        
        if (settings.WORKSPACE_DIR / item).exists():
            candidate = settings.WORKSPACE_DIR / item
        
        if candidate:
            try:
                if not candidate.is_relative_to(settings.WORKSPACE_DIR):
                    missing.append(item)
                    continue
                rel_path = candidate.relative_to(settings.WORKSPACE_DIR).as_posix()
                uris.append(f"{_artifact_base_uri()}/{rel_path}")
            except (ValueError, Exception):
                missing.append(item)
        else:
            missing.append(item)

    return {
        "result": f"Prepared {len(uris)} file(s) for transfer",
        "file_uris": uris,
        "missing": missing if missing else None,
    }
