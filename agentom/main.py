import asyncio
import sys
from pathlib import Path

# Add the parent directory to sys.path to ensure agentom package is resolvable
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

from agentom.factory import AgentFactory
from agentom.logging_utils import CustomLoggingPlugin, logger
from agentom.settings import settings
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agentom.utils import clear_temp_dir, clear_workspace

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
    logger.info(f"User Query: {query}")
    
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
    logger.info(f"Agent Response: {final_response_text}")
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
    print(f"Initializing {settings.APP_NAME} (Google ADK)")
    print("=" * 70)
    
    # Ensure directories exist
    settings.ensure_directories()

    # --- Session Management ---
    # SessionService stores conversation history & state
    # InMemorySessionService is simple, non-persistent storage
    session_service = InMemorySessionService()
    
    # Define initial state with user preferences (example for future enhancement)
    initial_state = {
        "workspace_path": str(settings.WORKSPACE_DIR),
        "interaction_count": 0,
    }
    
    # Create the session for this interaction
    session = await session_service.create_session(
        app_name=settings.APP_NAME,
        user_id=settings.USER_ID,
        session_id=settings.SESSION_ID,
        state=initial_state,
    )
    print(f"✅ Session created: App='{settings.APP_NAME}', User='{settings.USER_ID}', Session='{settings.SESSION_ID}'")
    
    # --- Create Coordinator Agent (Root Agent) ---
    coordinator = AgentFactory.create_coordinator_agent()
    print(f"✅ Coordinator Agent '{coordinator.name}' initialized with {len(coordinator.sub_agents)} sub-agents:")
    for sub_agent in coordinator.sub_agents:
        print(f"   - {sub_agent.name}: {sub_agent.description}")
    
    # --- Runner ---
    # Runner orchestrates agent execution
    runner = Runner(
        agent=coordinator,
        app_name=settings.APP_NAME,
        session_service=session_service,
        plugins=[CustomLoggingPlugin()]  # Optional: add logging plugin if available
    )
    print(f"✅ Runner created for agent '{runner.agent.name}'")
    
    print("\n" + "=" * 70)
    print("Agent Team Ready! Available agents:")
    print("  • mp_agent - Materials Project search & download")
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
                user_id=settings.USER_ID,
                session_id=settings.SESSION_ID,
            )
            
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("   Please try again or type 'exit' to quit.\n")
    
    # Clean up temporary files after the session
    clear_temp_dir()
    clear_workspace()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        # Ensure temporary files and workspace are cleaned up on exit
        try:
            from agentom.utils import clear_temp_dir, clear_workspace
            clear_temp_dir()
            clear_workspace()
        except Exception as _:
            # Avoid masking original exceptions; log to stderr
            import traceback, sys
            traceback.print_exc(file=sys.stderr)

