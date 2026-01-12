# Agentom

An agent-based system for materials science powered by google-adk.

## Features

- Multi-agent system for materials science workflows
- Integration with ASE (Atomic Simulation Environment) and Pymatgen
- Materials Project API integration
- Structure manipulation and interface creation
- Vision capabilities for structure visualization

## Installation

### Prerequisites

- Python 3.10 or higher
- pip

### Install in Development Mode

For development and easy testing, install in editable mode:

```bash
pip install -e .
```


## Configuration

1. Create a `.env` file in the root directory with your API keys:
   ```
   MP_API_KEY=your_mp_api_key
   OPENAI_API_KEY=your_openai_key
   OPENAI_API_BASE=your_openai_api_base_url
   ```

2. Configure settings in `agentom/settings.py` as needed

