from cmdop import CMDOPClient, AsyncCMDOPClient
import asyncio

def use_cmdop_directly():
    print("=" * 50)
    print("USING CMDOP DIRECTLY")
    print("=" * 50)
    try:
        client = CMDOPClient.local()
        print("✓ Connected via CMDOP directly")
        result = client.terminal.execute("echo 'Healthcare automation ready'")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Start local agent: cmdop agent start")

async def use_async_cmdop():
    API_KEY = "cmdop_live_xxx"
    try:
        async with AsyncCMDOPClient.remote(api_key=API_KEY) as client:
            await client.terminal.set_machine("my-server")
            output, code = await client.terminal.execute("uptime")
            print(f"Server: {output}")
    except Exception as e:
        print(f"Cloud connection failed: {e}")

def healthcare_workflow_pattern():
    print("\n" + "=" * 50)
    print("HEALTHCARE WORKFLOW WITH CMDOP")
    print("=" * 50)
    print("""
async def healthcare_workflow():
    async with AsyncCMDOPClient.remote(api_key="cmdop_live_xxx") as client:
        await client.terminal.set_machine("healthcare-server")
        output, code = await client.terminal.execute("python3 process_patients.py")
        print(f"Processing output: {output}")
        
        files = await client.files.list("/data/processed/")
        for f in files:
            print(f"Found: {f}")
""")

if __name__ == "__main__":
    use_cmdop_directly()
    healthcare_workflow_pattern()
