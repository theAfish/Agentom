import asyncio
import os
from agents.coordinator import create_coordinator_agent

# Ensure workspace exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(BASE_DIR, 'workspace')
os.makedirs(WORKSPACE, exist_ok=True)

async def main():
    print('Initializing Multi-Agent System...')
    coordinator = create_coordinator_agent()
    
    print('\nCoordinator Agent is ready.')
    print('You can ask for tasks involving data access (Materials Project) or ASE simulations.')
    print('Type \'exit\' or \'quit\' to stop.\n')
    
    while True:
        try:
            user_input = input('User: ')
            if user_input.lower() in ['exit', 'quit']:
                break
            
            if not user_input.strip():
                continue
                
            print('\nProcessing request...\n')
            result = await coordinator.run(user_input)
            print(f'\nAgent: {result}\n')
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f'An error occurred: {e}')

if __name__ == '__main__':
    asyncio.run(main())
