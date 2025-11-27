from agent_framework import ai_function
from litellm import completion
import base64
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
ENV_PATH = BASE_DIR / ".env"

def load_env(env_path):
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value

# Load environment variables
load_env(ENV_PATH)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

@ai_function(name="get_image_content", description="Reads an image file and returns its content as a data URL.")
def get_image_content(image_path: str) -> str:
    """Reads an image file and returns its content as a data URL.
    image_path: relative path to the image in the workspace.
    """
    full_path = WORKSPACE_DIR / image_path
    if not full_path.exists():
        return f"Error: Image file not found at {full_path}"
    
    try:
        base64_image = encode_image(full_path)
        return f"data:image/png;base64,{base64_image}"
    except Exception as e:
        return f"Error reading image: {str(e)}"
