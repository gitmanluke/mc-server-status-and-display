"""
Mock data scenarios for visual display testing.
Each scenario matches the shape of app.current_data exactly.
"""

# Real Minecraft player names and UUIDs (publicly known)
_PLAYERS = [
    {"name": "Technoblade", "uuid": "b876ec32-e396-476b-a115-8438d83c67d4"},
    {"name": "Notch",       "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"},
    {"name": "jeb_",        "uuid": "853c80ef-3c37-49fd-aa49-938b674adae6"},
    {"name": "Dinnerbone",  "uuid": "61699b2e-d327-4a01-9f1e-0ea8c3f06bc6"},
    {"name": "Ph1LzA",      "uuid": "e8b8d8c4-0a8e-4f6d-9e6e-4d5c5a4b3a2e"},
    {"name": "Grumm",       "uuid": "e6b5c088-0680-44df-9e1b-9bf11792291b"},
    {"name": "Dream",       "uuid": "ec70bcaf-702f-4bb8-b48d-276fa52a780c"},
    {"name": "Skeppy",      "uuid": "d0e05de7-6067-4ebe-9103-99686b5a63d5"},
    {"name": "BadBoyHalo",  "uuid": "0d29f671-5247-4393-8a66-5bf2a3f44cc0"},
    {"name": "GeorgeNotFound", "uuid": "7428a6d7-01fe-4e2b-b43c-9d5e0e7b7b7b"},
]

# Players missing a UUID (head falls back to name-based lookup)
_PLAYERS_NO_UUID = [
    {"name": "MissingUUID_1"},
    {"name": "MissingUUID_2"},
    {"name": "MissingUUID_3"},
]

# Player dict missing both keys entirely
_PLAYERS_NO_DATA = [
    {},
    {"name": "ValidPlayer", "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"},
]


def _heads(players):
    heads = {}
    for p in players:
        name = p.get("name")
        uuid = p.get("uuid")
        if not name:
            continue
        heads[name] = f"https://mc-heads.net/avatar/{uuid or name}/24"
    return heads


SCENARIOS = {
    # Server online, 10 players — backend caps display at 5, count shows real total
    "normal": {
        "address": "lukeserver.net",
        "online": True,
        "players": _PLAYERS[:5],
        "player_count": len(_PLAYERS),
        "heads": _heads(_PLAYERS[:5]),
    },

    # 50 players on the server — only 5 heads shown, count shows 50
    "large_player_list": {
        "address": "lukeserver.net",
        "online": True,
        "players": _PLAYERS[:5],
        "player_count": 50,
        "heads": _heads(_PLAYERS[:5]),
    },

    # Some players have no UUID — head falls back to name-based URL
    "missing_heads": {
        "address": "lukeserver.net",
        "online": True,
        "players": (_PLAYERS[:2] + _PLAYERS_NO_UUID)[:5],
        "player_count": 5,
        "heads": _heads((_PLAYERS[:2] + _PLAYERS_NO_UUID)[:5]),
    },

    # API returned a nameless player dict — backend filters it, only valid player shown
    "malformed_players": {
        "address": "lukeserver.net",
        "online": True,
        "players": [{"name": "ValidPlayer", "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"}],
        "player_count": 2,
        "heads": _heads([{"name": "ValidPlayer", "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"}]),
    },

    # Server online but no one is playing
    "no_players": {
        "address": "lukeserver.net",
        "online": True,
        "players": [],
        "player_count": 0,
        "heads": {},
    },

    # Server offline
    "offline": {
        "address": "lukeserver.net",
        "online": False,
        "players": [],
        "player_count": 0,
        "heads": {},
    },
}
