"""
Run the app with a mock data scenario instead of polling a real server.

Usage:
    python run_mock.py <scenario>

Available scenarios:
    normal            10 players, all with valid heads
    large_player_list 50 players — tests scrolling
    missing_heads     mix of players with and without UUIDs
    malformed_players player dicts missing name/uuid fields
    no_players        server online but empty
    offline           server offline
"""

import sys
import asyncio
import signal
import subprocess
import uvicorn
import app
from mock_scenarios import SCENARIOS


def _free_port(port):
    result = subprocess.run(
        ["lsof", "-ti", f":{port}"],
        capture_output=True, text=True
    )
    pids = result.stdout.strip().split()
    for pid in pids:
        try:
            subprocess.run(["kill", "-9", pid], check=True)
        except subprocess.CalledProcessError:
            pass


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SCENARIOS:
        print(__doc__)
        print(f"Available scenarios: {', '.join(SCENARIOS)}")
        sys.exit(1)

    scenario_name = sys.argv[1]
    scenario = SCENARIOS[scenario_name]

    # Inject mock data and replace the fetch loop with a no-op
    app.current_data.update(scenario)

    async def mock_fetch_loop():
        # Broadcast the initial state once then sit idle
        await app.broadcast()
        while True:
            await asyncio.sleep(3600)

    app.fetch_data_loop = mock_fetch_loop

    _free_port(8000)

    print(f"\n  Scenario : {scenario_name}")
    print(f"  Players  : {scenario['player_count']}")
    print(f"  Online   : {scenario['online']}")
    print(f"  URL      : http://localhost:8000\n")

    uvicorn.run(app.app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
