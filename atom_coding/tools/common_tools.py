import os
from typing import Annotated
from agent_framework import ai_function
import ast
from RestrictedPython import compile_restricted, safe_globals, limited_builtins, utility_builtins

# Define the workspace directory
# We assume this file is in atom_coding/tools/common_tools.py
# So workspace is ../../workspace relative to this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.join(BASE_DIR, "workspace")
os.makedirs(WORKSPACE, exist_ok=True)

def safe_path(rel_path: str) -> str:
    """Resolve relative path to absolute within workspace and prevent escapes."""
    full_path = os.path.normpath(os.path.join(WORKSPACE, rel_path))
    if not full_path.startswith(WORKSPACE):
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

@ai_function
def read_file(filepath: Annotated[str, "Relative path to file to read"]) -> str:
    """Read contents of a file within the workspace."""
    try:
        path = safe_path(filepath)
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

@ai_function
def write_file(
    filepath: Annotated[str, "Relative path to file to write"],
    content: Annotated[str, "Content to write to file"]
) -> str:
    """Write content to a file within the workspace."""
    try:
        path = safe_path(filepath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {filepath}"
    except Exception as e:
        return f"Error: {e}"

@ai_function
def list_files(directory: Annotated[str, "Relative directory path to list"]) -> str:
    """List files in a directory within the workspace."""
    try:
        path = safe_path(directory)
        files = os.listdir(path)
        return '\n'.join(files)
    except Exception as e:
        return f"Error: {e}"

class CodeValidator(ast.NodeVisitor):
    """AST visitor to block additional dangerous patterns (optional pre-check)."""
    prohibited_calls = {'eval', 'exec', 'compile', '__import__'}  # RestrictedPython handles most imports

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.prohibited_calls:
            raise ValueError(f"Prohibited call: {node.func.id}")
        self.generic_visit(node)

@ai_function
def execute_code(filepath: Annotated[str, "Relative path to Python file to execute"]) -> str:
    """Execute a Python file within the workspace after validation and in restricted mode. Returns output or error."""
    try:
        path = safe_path(filepath)
        with open(path, 'r') as f:
            code = f.read()

        # Optional: Pre-validate with AST
        tree = ast.parse(code)
        CodeValidator().visit(tree)

        # Prepare restricted globals
        restricted_globals = safe_globals.copy()
        restricted_globals['__builtins__'] = limited_builtins.copy()
        restricted_globals['__builtins__'].update(utility_builtins)
        restricted_globals['__builtins__']['open'] = safe_open  # Override with confined open
        restricted_globals['makedirs'] = safe_makedirs  # Provide for dir creation (code can call makedirs('subdir'))
        # Add more safe builtins/functions as needed (e.g., print, len, etc., are already in limited_builtins)

        local_ns = {}

        # Compile and exec with restrictions
        byte_code = compile_restricted(code, filename='<restricted_code>', mode='exec')
        exec(byte_code, restricted_globals, local_ns)

        return "Execution successful"  # Or capture output (e.g., via io.StringIO redirecting stdout)

    except Exception as e:
        return f"Error: {e}"
