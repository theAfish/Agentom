from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools.ase_tools import generate_structure_image
from tools.vision_tools import get_image_content


def create_vision_agent():
    """
    Creates a Vision specialist agent for structure analysis.
    
    This agent uses vision/multimodal capabilities to inspect
    and analyze atomic structure images.
    """
    return Agent(
        model=LiteLlm("openai/qwen3-omni-flash"),
        name="vision_agent",
        description="Vision specialist for analyzing atomic structures. Inspects and interprets structure images.",
        instruction=(
            "You are a Vision Checking Agent specialized in analyzing atomic structures from images. "
            "Your ONLY tasks are: "
            "1. Generate images of atomic structures. "
            "2. Visually inspect and analyze structure images. "
            "3. Answer questions about structural properties based on visual inspection. "
            "Always explain what you see in the image to justify your analysis. "
            "Do not perform simulations or data lookups - that's for other agents."
        ),
        tools=[generate_structure_image, get_image_content],
        output_key="last_vision_result",  # Auto-save agent's response
    )
