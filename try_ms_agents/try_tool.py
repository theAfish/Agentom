from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
import asyncio
from agent_framework.openai import OpenAIChatClient  
from agent_framework import ChatMessage, Role



@ai_function(name="weather_tool", description="Retrieves weather information for any location", approval_mode="always_require")
def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    return f"The weather in {location} is cloudy with a high of 15°C."


class WeatherTools:
    def __init__(self):
        self.last_location = None

    @ai_function(name="weather_tool", description="Retrieves weather information for any location", approval_mode="always_require")
    def get_weather(
        self,
        location: Annotated[str, Field(description="The location to get the weather for.")],
    ) -> str:
        """Get the weather for a given location."""
        return f"The weather in {location} is cloudy with a high of 15°C."

    def get_weather_details(self) -> int:
        """Get the detailed weather for the last requested location."""
        if self.last_location is None:
            return "No location specified yet."
        return f"The detailed weather in {self.last_location} is cloudy with a high of 15°C, low of 7°C, and 60% humidity."


tools = WeatherTools()
agent = OpenAIChatClient(  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model_id="qwen-turbo",
    env_file_path=".env"
).create_agent(
    instructions="You are a helpful assistant",
    name="WeatherReporter",
    tools=[tools.get_weather, tools.get_weather_details]
)


async def main():
    result = await agent.run("What is the detailed weather like in Amsterdam?")

    if result.user_input_requests:
        for user_input_needed in result.user_input_requests:
            print(f"Function: {user_input_needed.function_call.name}")
            print(f"Arguments: {user_input_needed.function_call.arguments}")
    # Get user approval (in a real application, this would be interactive)
    user_approval = True  # or False to reject

    # Create the approval response
    approval_message = ChatMessage(
        role=Role.USER, 
        contents=[user_input_needed.create_response(user_approval)]
    )

    # Continue the conversation with the approval
    final_result = await agent.run([
        "What is the detailed weather like in Amsterdam?",
        ChatMessage(role=Role.ASSISTANT, contents=[user_input_needed]),
        approval_message
    ])
    print(final_result.text)

asyncio.run(main())