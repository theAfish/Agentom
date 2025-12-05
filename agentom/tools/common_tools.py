import os
import ast
from pathlib import Path
# from RestrictedPython import compile_restricted, safe_globals, limited_builtins, utility_builtins
import subprocess
import sys

from agentom.settings import settings


def safe_path(rel_path: str) -> Path:
    """Resolve relative path to absolute within workspace and prevent escapes."""
    full_path = (settings.WORKSPACE_DIR / rel_path).resolve()
    if not full_path.is_relative_to(settings.WORKSPACE_DIR):
        raise ValueError("Access denied: Path outside workspace")
    return full_path

def safe_open(filepath: str, mode: str = 'r', *args, **kwargs):
    """Custom open confined to workspace."""
    path = safe_path(filepath)
    return open(path, mode, *args, **kwargs)

def safe_makedirs(dirpath: str, *args, **kwargs):
    """Custom makedirs confined to workspace."""
    path = safe_path(dirpath)
    os.makedirs(path, *args, **kwargs)


def read_file(filepath: str) -> str:
    """Read contents of a file within the workspace.
    
    Args:
        filepath: Relative path to file to read
    """
    try:
        path = safe_path(filepath)
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"


def write_file(
    filepath: str,
    content: str
) -> str:
    """Write content to a file within the workspace.
    
    Args:
        filepath: Relative path to file to write
        content: Content to write to file
    """
    try:
        path = safe_path(filepath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error: {e}"


def list_files(directory: str) -> str:
    """List files in a directory within the workspace.
    
    Args:
        directory: Relative directory path to list
    """
    try:
        path = safe_path(directory)
        # If the path is inside the logs directory, ignore it and return an empty listing
        try:
            if path.is_relative_to(settings.LOGS_DIR):
                return {"files": ''}
        except Exception:
            # If is_relative_to isn't available for some reason, fall back to string comparison
            if str(settings.LOGS_DIR) in str(path):
                return {"files": ''}
        if not path.is_dir():
            return {"error": f"{directory} is not a directory"}
        files = [f.name for f in path.iterdir() if f.is_file()]
        return {"files": '\n'.join(files)}
    except Exception as e:
        return {"error": str(e)}


def list_all_files():
    """Lists all files available in the workspace directory, in a tree-like structure, with their relative subfolder paths as keys."""
    if not settings.WORKSPACE_DIR.exists():
        return {"files": []}
    files = {}
    for path in settings.WORKSPACE_DIR.rglob("*"):
        if path.is_file():
            # Skip anything under the logs directory so logs are not listed
            try:
                if path.is_relative_to(settings.LOGS_DIR):
                    continue
            except Exception:
                if str(settings.LOGS_DIR) in str(path):
                    continue

            try:
                subfolder = path.parent.relative_to(settings.WORKSPACE_DIR)
                files.setdefault(str(subfolder), []).append(path.name)
            except ValueError:
                # Handle case where path is not relative to WORKSPACE_DIR (should not happen with rglob)
                pass
    return {"files": files}


class CodeValidator(ast.NodeVisitor):
    """AST visitor to block dangerous patterns."""
    
    def __init__(self):
        self.prohibited_names = {'eval', 'exec', 'compile', '__import__', 'input'}
        self.prohibited_modules = {'subprocess', 'shutil', 'importlib'}
        self.prohibited_os_attrs = {
            'system', 'popen', 'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 
            'spawnv', 'spawnve', 'spawnvp', 'spawnvpe', 'execl', 'execle', 
            'execlp', 'execlpe', 'execv', 'execve', 'execvp', 'execvpe', 
            'fork', 'kill'
        }

    def visit_Call(self, node):
        # Check function calls like eval(...)
        if isinstance(node.func, ast.Name):
            if node.func.id in self.prohibited_names:
                raise ValueError(f"Prohibited function call: {node.func.id}")
        
        # Check method calls like os.system(...)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == 'os':
                if node.func.attr in self.prohibited_os_attrs:
                    raise ValueError(f"Prohibited os function call: os.{node.func.attr}")
        
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.name.split('.')[0]
            if name in self.prohibited_modules:
                raise ValueError(f"Prohibited module import: {name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            name = node.module.split('.')[0]
            if name in self.prohibited_modules:
                raise ValueError(f"Prohibited module import: {name}")
            if name == 'os':
                for alias in node.names:
                    if alias.name in self.prohibited_os_attrs:
                        raise ValueError(f"Prohibited import from os: {alias.name}")
        self.generic_visit(node)

def run_python_script(script_name: str) -> dict:
    """Runs a Python script in the workspace directly."""
    
    # script_name should be relative to WORKSPACE_DIR
    script_path = settings.WORKSPACE_DIR / script_name
    
    # Resolve the path to handle symlinks, relative components, etc.
    try:
        resolved_path = script_path.resolve()
    except Exception as e:
        return {"error": f"Failed to resolve script path: {str(e)}"}
    
    # Ensure the script is within the workspace to prevent path traversal
    if not resolved_path.is_relative_to(settings.WORKSPACE_DIR):
        return {"error": "Script path is outside the workspace"}
    
    if not resolved_path.exists():
        return {"error": f"File not found: {resolved_path}"}
    
    # Validate code safety
    try:
        with open(resolved_path, 'r') as f:
            code_content = f.read()
        tree = ast.parse(code_content)
        validator = CodeValidator()
        validator.visit(tree)
    except Exception as e:
        return {"error": f"Security check failed: {str(e)}"}
    
    try:
        # Run the script directly
        result = subprocess.run(
            [sys.executable, str(resolved_path)],
            cwd=settings.WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=120
        )
        return {
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"error": str(e)}
