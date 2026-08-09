"""
Mock data scenarios for visual display testing.
Each scenario matches the shape of app.current_data exactly.
"""

# Real Minecraft player names and UUIDs (publicly known)
_PLAYERS = [
    {"name": "Technoblade",    "uuid": "b876ec32-e396-476b-a115-8438d83c67d4"},
    {"name": "Notch",          "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"},
    {"name": "jeb_",           "uuid": "853c80ef-3c37-49fd-aa49-938b674adae6"},
    {"name": "CaptainSparklez","uuid": "5f820c39-5883-4392-b174-3125ac05e38c"},
    {"name": "Ph1LzA",         "uuid": "84555089-add1-49b1-a26d-8021270a40f0"},
    {"name": "Grumm",          "uuid": "e6b5c088-0680-44df-9e1b-9bf11792291b"},
    {"name": "Skeppy",         "uuid": "8e176c5a-c26d-4c14-8efe-77b598b8b3ea"},
    {"name": "BadBoyHalo",     "uuid": "26bdff37-fec8-48f1-980f-66bf69ee751c"},
    {"name": "MumboJumbo",     "uuid": "c7da90d5-6a05-4217-b94a-7d427cbbcad8"},
    {"name": "Grian",          "uuid": "5f8eb73b-25be-4c5a-a50f-d27d65e30ca0"},
    {"name": "xisumavoid",     "uuid": "8d86df19-fa5c-4939-ac7c-3b90b2b6abb6"},
    {"name": "impulseSV",      "uuid": "f6fe2200-609d-4fe6-88b6-529d59ee5b71"},
    {"name": "ibxtoycat",      "uuid": "f17709a2-566d-49fa-b75a-3df8561f78dc"},
    {"name": "mattbatwings",   "uuid": "92e38e65-5904-4217-8ba8-11382b9e83f1"},
    {"name": "EthosLab",       "uuid": "4f41dcda-449a-46b7-8635-88979061fdd2"},
]

# Players missing a UUID (head falls back to name-based lookup)
_PLAYERS_NO_UUID = [
    {"name": "MissingUUID_1"},
    {"name": "MissingUUID_2"},
    {"name": "MissingUUID_3"},
]

# 50 fake players for stress-testing the grid layout
_PLAYERS_50 = [
    {"name": "Technoblade",    "uuid": "b876ec32-e396-476b-a115-8438d83c67d4"},
    {"name": "Notch",          "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"},
    {"name": "jeb_",           "uuid": "853c80ef-3c37-49fd-aa49-938b674adae6"},
    {"name": "CaptainSparklez","uuid": "5f820c39-5883-4392-b174-3125ac05e38c"},
    {"name": "Ph1LzA",         "uuid": "84555089-add1-49b1-a26d-8021270a40f0"},
    {"name": "Grumm",          "uuid": "e6b5c088-0680-44df-9e1b-9bf11792291b"},
    {"name": "Skeppy",         "uuid": "8e176c5a-c26d-4c14-8efe-77b598b8b3ea"},
    {"name": "BadBoyHalo",     "uuid": "26bdff37-fec8-48f1-980f-66bf69ee751c"},
    {"name": "MumboJumbo",     "uuid": "c7da90d5-6a05-4217-b94a-7d427cbbcad8"},
    {"name": "Grian",          "uuid": "5f8eb73b-25be-4c5a-a50f-d27d65e30ca0"},
    {"name": "xisumavoid",     "uuid": "8d86df19-fa5c-4939-ac7c-3b90b2b6abb6"},
    {"name": "impulseSV",      "uuid": "f6fe2200-609d-4fe6-88b6-529d59ee5b71"},
    {"name": "ibxtoycat",      "uuid": "f17709a2-566d-49fa-b75a-3df8561f78dc"},
    {"name": "mattbatwings",   "uuid": "92e38e65-5904-4217-8ba8-11382b9e83f1"},
    {"name": "EthosLab",       "uuid": "4f41dcda-449a-46b7-8635-88979061fdd2"},
    {"name": "Steve"},
    {"name": "Alex"},
    {"name": "Herobrine"},
    {"name": "xX_D4rkS0ul_Xx"},
    {"name": "CreeperSlayer99"},
    {"name": "DiamondMiner42"},
    {"name": "NightOwl"},
    {"name": "PixelWarrior"},
    {"name": "RedstoneKing"},
    {"name": "EnderDragon99"},
    {"name": "SwordFish"},
    {"name": "BlockBreaker"},
    {"name": "LavaLord"},
    {"name": "IceDragon"},
    {"name": "StormRider"},
    {"name": "GhostBlade"},
    {"name": "TurtleMaster"},
    {"name": "ZombieHunter"},
    {"name": "SpiderMan404"},
    {"name": "WitchDoctor"},
    {"name": "SkeletonKing"},
    {"name": "NetherWalker"},
    {"name": "CloudSurfer"},
    {"name": "MoonStriker"},
    {"name": "ShadowFox"},
    {"name": "ThunderBolt"},
    {"name": "FrostByte"},
    {"name": "CobbleGoblin"},
    {"name": "PiglinTrader"},
    {"name": "VillagerBob"},
    {"name": "BlazeRunner"},
    {"name": "WarpedWolf"},
    {"name": "MossyMike"},
    {"name": "QuartzQueen"},
    {"name": "ObsidianOllie"},
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
    # Server online, all players shown
    "normal": {
        "address": "lukeserver.net",
        "online": True,
        "players": _PLAYERS,
        "player_count": len(_PLAYERS),
        "heads": _heads(_PLAYERS),
    },

    # 50 players on the server
    "large_player_list": {
        "address": "lukeserver.net",
        "online": True,
        "players": _PLAYERS_50,
        "player_count": 50,
        "heads": _heads(_PLAYERS_50),
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
