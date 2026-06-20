import asyncio
import redis.asyncio as aioredis
from config import REDIS_HOST, REDIS_PORT, REDIS_USERNAME, REDIS_PASSWORD, STREAM_KEY

async def test():
    r = aioredis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, username=REDIS_USERNAME, password=REDIS_PASSWORD, decode_responses=True
    )
    print("Fetching count=6...")
    entries = await r.xrevrange(STREAM_KEY, count=6)
    print(f"Got {len(entries)} entries")
    await r.aclose()

if __name__ == "__main__":
    asyncio.run(test())
