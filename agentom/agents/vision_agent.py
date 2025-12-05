from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from agentom.tools.structure_tools import generate_structure_image
from agentom.tools.vision_tools import get_image_content
from agentom.tools.common_tools import list_all_files
from agentom.settings import settings

agent_description = "Vision specialist for analyzing atomic structures. Inspects and interprets structure images."
agent_instruction = """
You are a Vision Checking Agent specialized in analyzing atomic structures from images. Your ONLY tasks are: 
1. Generate images of atomic structures. 
2. Visually inspect and analyze structure images. 
3. Answer questions about structural properties based on visual inspection. 
Always explain what you see in the image to justify your analysis. 
Do not perform simulations or data lookups - that's for other agents.
"""


def create_vision_agent():
    """
    Creates a Vision specialist agent for structure analysis.
    
    This agent uses vision/multimodal capabilities to inspect
    and analyze atomic structure images.
    """
    return Agent(
        model=LiteLlm(settings.VISION_MODEL),
        name="vision_agent",
        description=agent_description,
        instruction=agent_instruction,
        tools=[generate_structure_image, get_image_content, list_all_files],
        output_key="last_vision_result",  # Auto-save agent's response
    )
