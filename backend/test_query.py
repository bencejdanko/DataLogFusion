import asyncio
from uagents.resolver import get_resolver
from uagents.network import get_almanac_contract

async def query():
    almanac = get_almanac_contract("testnet")
    endpoints = almanac.query_endpoints("agent1q0sfkv77ye39d8ctsj6rxgzapmulas4lx0ygd8ek2lxuw2ks3p3659kj04g")
    print("Endpoints:", endpoints)

asyncio.run(query())
