# Atom Coding Multi-Agent System

This project implements a multi-agent system for atomic simulations and materials data access.

## Structure

- **agents/**: Contains the agent definitions.
  - `coordinator.py`: The main orchestrator agent.
  - `data_access.py`: Agent for interacting with Materials Project (MP-API).
  - `ase_agent.py`: Agent for performing ASE calculations and manipulations.
- **tools/**: Contains the tools used by agents.
  - `common_tools.py`: File I/O and code execution tools.
  - `data_tools.py`: Tools for MP-API.
  - `ase_tools.py`: Tools for ASE.
- **workspace/**: The working directory for agents. All file operations are confined here.
- **main.py**: The entry point to run the system.

## Usage

1.  Ensure you have the required dependencies installed.
2.  Set up your `.env` file with necessary API keys (e.g., `DASHSCOPE_API_KEY` or OpenAI keys).
3.  Run the main script:

```bash
python main.py
```

4.  Interact with the coordinator agent via the command line.

## Agents

- **Coordinator Agent**: Receives user requests and delegates to Data or ASE agents.
- **Data Access Agent**: Can search and download structures.
- **ASE Agent**: Can read structures, calculate distances, create slabs, etc.
