import asyncio
import uuid
import sys
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from chat_proto import ChatMessage

# Create a local client agent
client_agent = Agent(
    name="chat-client",
    port=8013,
    endpoint=["http://127.0.0.1:8013/submit"],
)

# Replace this with the exact address printed when you run agent.py
TARGET_AGENT_ADDRESS = sys.argv[1] if len(sys.argv) > 1 else "agent1qv2cggq3w06ndg9swdvu66ku9vn9w7mt838xr25e4dcycff7ulce63277kt"

@client_agent.on_event("startup")
async def start_chat(ctx: Context):
    print("\n--- Horoscope Chat Client Started ---")
    print("Type your message below (or 'quit' to exit):")
    # Prompt for initial message in the background
    asyncio.create_task(prompt_user(ctx))

async def prompt_user(ctx: Context):
    # Short sleep to ensure print formatting
    await asyncio.sleep(0.5)
    msg = await asyncio.to_thread(input, "\nYou: ")
    if msg.lower() in ("quit", "exit"):
        print("Goodbye!")
        import os
        os._exit(0)
        
    await ctx.send(
        TARGET_AGENT_ADDRESS,
        ChatMessage(message=msg, session_id=str(uuid.uuid4()))
    )

@client_agent.on_message(model=ChatMessage)
async def handle_reply(ctx: Context, sender: str, msg: ChatMessage):
    print(f"\nHoroscope Agent: {msg.message}")
    # Prompt for the next reply
    asyncio.create_task(prompt_user(ctx))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <TARGET_AGENT_ADDRESS>")
        print(f"Using default address: {TARGET_AGENT_ADDRESS}")
    client_agent.run()
