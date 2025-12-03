import os
import asyncio
from agents.coordinator import create_coordinator_agent
from logging_utils import CustomLoggingPlugin
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Ensure workspace exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.join(BASE_DIR, 'workspace')
os.makedirs(WORKSPACE, exist_ok=True)

# Constants for session management
APP_NAME = "agentom_materials_science"
USER_ID = "materials_scientist"
SESSION_ID = "session_001"


async def call_agent_async(query: str, runner: Runner, user_id: str, session_id: str) -> str:
    """
    Sends a query to the agent team and returns the final response.
    
    This function demonstrates the ADK async interaction pattern:
    1. Package the user query into ADK Content format
    2. Call runner.run_async() which yields events
    3. Process events until final response is found
    4. Return the final agent response
    
    Args:
        query: User's input query
        runner: The Runner orchestrating agent execution
        user_id: User identifier for session
        session_id: Session identifier for conversation history
        
    Returns:
        The agent's final response text
    """
    print(f"\n>>> User: {query}")
    
    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])
    
    final_response_text = "Agent did not produce a final response."
    
    # Key Concept: run_async executes the agent logic and yields Events
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}")
        
        # Key Concept: is_final_response() marks the concluding message for the turn
        if event.is_final_response():
            if event.content and event.content.parts:
                # Extract text response
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break  # Stop processing events once the final response is found
    
    print(f"<<< Agent: {final_response_text}")
    return final_response_text


async def main():
    """
    Main entry point for the multi-agent materials science system.
    
    This function demonstrates the proper ADK agent team setup pattern:
    1. Initialize SessionService for managing conversation state
    2. Create a session with initial state
    3. Create a Runner with the root agent and session service
    4. Interact with the agent team using async patterns
    """
    print("=" * 70)
    print("Initializing Multi-Agent Materials Science System (Google ADK)")
    print("=" * 70)
    
    # --- Session Management ---
    # SessionService stores conversation history & state
    # InMemorySessionService is simple, non-persistent storage
    session_service = InMemorySessionService()
    
    # Define initial state with user preferences (example for future enhancement)
    initial_state = {
        "workspace_path": WORKSPACE,
        "interaction_count": 0,
    }
    
    # Create the session for this interaction
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    print(f"✅ Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")
    
    # --- Create Coordinator Agent (Root Agent) ---
    coordinator = create_coordinator_agent()
    print(f"✅ Coordinator Agent '{coordinator.name}' initialized with {len(coordinator.sub_agents)} sub-agents:")
    for sub_agent in coordinator.sub_agents:
        print(f"   - {sub_agent.name}: {sub_agent.description}")
    
    # --- Runner ---
    # Runner orchestrates agent execution
    runner = Runner(
        agent=coordinator,
        app_name=APP_NAME,
        session_service=session_service,
        # plugins=[CustomLoggingPlugin()]  # Optional: add logging plugin if available
    )
    print(f"✅ Runner created for agent '{runner.agent.name}'")
    
    print("\n" + "=" * 70)
    print("Agent Team Ready! Available agents:")
    print("  • data_access_agent - Materials Project search & download")
    print("  • ase_agent - Atomic simulations & structure manipulation")
    print("  • vision_agent - Structure visualization & analysis")
    print("  • wiki_agent - Materials science information")
    print("\nType 'exit' or 'quit' to stop.\n")
    print("=" * 70)
    
    # --- Interactive Loop ---
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print("\nThank you for using the Materials Science Agent Team. Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Call the agent team asynchronously
            await call_agent_async(
                query=user_input,
                runner=runner,
                user_id=USER_ID,
                session_id=SESSION_ID,
            )
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("   Please try again or type 'exit' to quit.\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}")

