# inspect_openclaw.py
import openclaw

print("OpenClaw version:", getattr(openclaw, '__version__', 'unknown'))
print("\nAvailable attributes:")
for attr in dir(openclaw):
    if not attr.startswith('_'):
        print(f"  - {attr}")