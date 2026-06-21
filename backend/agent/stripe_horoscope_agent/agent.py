import os

import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from config import get_env_var  # This implicitly loads .env

from uagents import Agent

from chat_proto import build_chat_proto
from payment_proto import build_payment_proto

# Load dotenv before importing modules that read env vars.
from handlers import on_chat, on_commit, on_reject  # noqa: E402

agent = Agent(
    name="stripe-horoscope-agent",
    seed=os.getenv("AGENT_SEED", "datalogfusion-stripe-horoscope-seed-unique"),
    port=int(os.getenv("AGENT_PORT", "8012")),
    mailbox=True,
    publish_agent_details=True,
)

agent.include(build_chat_proto(on_chat), publish_manifest=True)
agent.include(build_payment_proto(on_commit, on_reject), publish_manifest=True)

if __name__ == "__main__":
    agent.run()

