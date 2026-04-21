import openclaw
from openclaw import OpenClaw, AsyncOpenClaw
import asyncio

def check_openclaw():
    print("=" * 50)
    print("OPENCLAW AVAILABLE FEATURES")
    print("=" * 50)
    print(f"OpenClaw version: {openclaw.__version__}")
    print("\nAvailable classes:")
    print("  - OpenClaw (sync client)")
    print("  - AsyncOpenClaw (async client)")
    print("\nConnection methods:")
    print("  - OpenClaw.local() - Connect to local agent")
    print("  - OpenClaw.remote(api_key='xxx') - Connect to cloud")

def test_local_connection():
    print("\n" + "=" * 50)
    print("TESTING LOCAL CONNECTION")
    print("=" * 50)
    try:
        client = OpenClaw.local()
        print("✓ Local OpenClaw agent is running!")
        return client
    except Exception as e:
        print(f"✗ Local agent not running: {e}")
        print("\nTo start local agent:")
        print("  cmdop agent start")
        return None

def cloud_connection_pattern():
    print("\n" + "=" * 50)
    print("CLOUD CONNECTION PATTERN")
    print("=" * 50)
    print("""
async def main():
    async with AsyncOpenClaw.remote(api_key="cmdop_live_xxx") as client:
        await client.terminal.set_machine("my-server")
        output, code = await client.terminal.execute("uptime")
        print(output)
""")

def healthcare_agent_pattern():
    print("\n" + "=" * 50)
    print("HEALTHCARE AGENT ORCHESTRATION PATTERN")
    print("=" * 50)
    print("""
async def healthcare_workflow():
    async with AsyncOpenClaw.remote(api_key="cmdop_live_xxx") as client:
        extractor = await client.agent.create(
            name="DataExtractor",
            instructions="Extract patient appointments"
        )
        validator = await client.agent.create(
            name="DataValidator",
            instructions="Check for missing fields"
        )
        reporter = await client.agent.create(
            name="ReportGenerator",
            instructions="Create summary report"
        )
        raw = await extractor.run("Get today's appointments")
        validated = await validator.run(f"Validate: {raw}")
        report = await reporter.run(f"Summarize: {validated}")
        return report
""")

async def main():
    print("\n" + "=" * 60)
    print("OPENCLAW HEALTHCARE AUTOMATION GUIDE")
    print("=" * 60)
    check_openclaw()
    test_local_connection()
    cloud_connection_pattern()
    healthcare_agent_pattern()

if __name__ == "__main__":
    asyncio.run(main())
