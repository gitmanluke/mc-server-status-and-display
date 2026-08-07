"""
Run the static site (index.html) with a mock data scenario instead of hitting mcsrvstat.us.

Usage:
    python run_mock_index.py <scenario>

Available scenarios:
    normal            5 players shown, 10 total
    large_player_list 5 players shown, 50 total
    missing_heads     mix of players with and without UUIDs
    malformed_players player dict missing name field filtered out
    no_players        server online but empty
    offline           server offline
"""

import sys
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from mock_scenarios import SCENARIOS


def _to_api_format(scenario):
    """Convert a scenario dict to mcsrvstat.us v3 API shape."""
    if not scenario['online']:
        return {'debug': {'ping': True}, 'online': False}
    return {
        'debug': {'ping': True},
        'online': True,
        'players': {
            'online': scenario['player_count'],
            'list': scenario['players'],
        },
    }


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in SCENARIOS:
        print(__doc__)
        print(f"Available scenarios: {', '.join(SCENARIOS)}")
        sys.exit(1)

    scenario_name = sys.argv[1]
    scenario = SCENARIOS[scenario_name]
    api_response = _to_api_format(scenario)

    mock_app = FastAPI()
    mock_app.mount('/static', StaticFiles(directory='static'), name='static')

    @mock_app.get('/')
    def home():
        with open('index.html', encoding='utf-8') as f:
            return HTMLResponse(f.read())

    @mock_app.get('/3/{server_address}')
    def mock_api(server_address: str):
        return JSONResponse(api_response)

    print(f"\n  Scenario : {scenario_name}")
    print(f"  Players  : {scenario['player_count']}")
    print(f"  Online   : {scenario['online']}")
    print(f"  URL      : http://localhost:8000\n")

    uvicorn.run(mock_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
