import asyncio  
from agent_framework import ChatAgent  
from agent_framework.openai import OpenAIChatClient  

# agent = ChatAgent(  
#     chat_client=OpenAIChatClient(  
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # Qwen endpoint  
#         model_id="qwen-turbo",  # or qwen-plus, qwen-max, etc.  
#         env_file_path=".env"
#     ),  
#     instructions="You are a helpful assistant."  
# )

agent = OpenAIChatClient(  
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model_id="qwen-turbo",
    env_file_path=".env"
).create_agent(
    instructions="You are good at telling jokes.",
    name="Joker"
)
  
# async def main():  
#     # Run the agent  
#     response = await agent.run("Hello! Tell me about yourself.")  
#     print(response.text)  

thread = agent.get_new_thread()  
async def main():
      
    while True:  
        user_input = input("\nUser (or 'exit' to quit): ")  
        if user_input.lower() == 'exit':  
            break  
              
        print("Agent: ", end="", flush=True)  
        async for update in agent.run_stream(user_input, thread=thread):  
            if update.text:  
                print(update.text, end="", flush=True)  
        print()  

  
asyncio.run(main())