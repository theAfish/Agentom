import sys
import os
import inspect
from typing import get_type_hints

# Add current directory to sys.path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'agentom'))

try:
    from agentom.agents.coordinator import ask_ase_agent
    print("Function:", ask_ase_agent)
    print("File:", inspect.getfile(ask_ase_agent))
    print("Signature:", inspect.signature(ask_ase_agent))
    print("Type hints:", get_type_hints(ask_ase_agent))
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
