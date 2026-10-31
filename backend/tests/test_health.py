"""Automated health and endpoint verification test."""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import asyncio
import httpx
from backend.app.main import app

async def run_tests():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Test Root Endpoint
        res_root = await client.get("/")
        print("Root Endpoint Test:")
        print("  Status:", res_root.status_code)
        print("  Data:", res_root.json())
        assert res_root.status_code == 200

        # Test Health Endpoint
        res_health = await client.get("/api/health")
        print("\nHealth Endpoint Test:")
        print("  Status:", res_health.status_code)
        print("  Data:", res_health.json())
        assert res_health.status_code == 200
        
        print("\nAll endpoint assertions passed!")

if __name__ == "__main__":
    asyncio.run(run_tests())
