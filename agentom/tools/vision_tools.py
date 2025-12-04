from litellm import completion
import base64
import os
from pathlib import Path

from agentom.settings import settings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def get_image_content(image_path: str) -> str:
    """Reads an image file and returns its content as a data URL.
    image_path: relative path to the image in the workspace.
    """
    full_path = settings.WORKSPACE_DIR / image_path
    if not full_path.exists():
        return f"Error: Image file not found at {full_path}"
    
    try:
        base64_image = encode_image(full_path)
        return f"data:image/png;base64,{base64_image}"
    except Exception as e:
        return f"Error reading image: {str(e)}"
