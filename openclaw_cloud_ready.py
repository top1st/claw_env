from cmdop import AsyncCMDOPClient
import asyncio

async def main():
    async with AsyncCMDOPClient.remote(api_key="cmdop_RIOHcQt4LT3xPvlMTxQq51Sj6o3nbUaRG01h6hicELQ") as client:
        await client.terminal.set_machine("healthcare-server")
        output, code = await client.terminal.execute("python3 extract.py")
        print(output)

asyncio.run(main())