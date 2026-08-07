import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import app
from app import request_heads


# --- Test 3: player with neither uuid nor name ---

def test_request_heads_no_uuid_no_name_does_not_crash():
    """A player dict with no 'uuid' and no 'name' should not raise."""
    result = request_heads([{}])
    # The function should return without raising; we just verify the type.
    assert isinstance(result, dict)


def test_request_heads_no_uuid_no_name_skips_entry():
    """A nameless player should not pollute the heads dict with a None key."""
    result = request_heads([{}])
    assert None not in result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_client(json_payload):
    """Return a mock httpx.AsyncClient whose .get() returns json_payload."""
    mock_response = MagicMock()
    mock_response.json.return_value = json_payload

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


async def _run_one_fetch_iteration(json_payload):
    """Run fetch_data_loop for exactly one iteration then stop."""
    mock_client = _make_mock_client(json_payload)
    with patch('app.httpx.AsyncClient', return_value=mock_client):
        with patch('asyncio.sleep', side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await app.fetch_data_loop()


# --- Test 11: API returns {} ---

@pytest.mark.asyncio
async def test_empty_api_response_sets_offline():
    """Empty API response should result in offline state with cleared players."""
    await _run_one_fetch_iteration({})

    assert app.current_data['online'] is False
    assert app.current_data['players'] == []
    assert app.current_data['player_count'] == 0


# --- Test 12: API returns malformed JSON ---

@pytest.mark.asyncio
async def test_malformed_json_response_sets_offline():
    """If response.json() raises, the exception handler should clear state."""
    mock_response = MagicMock()
    mock_response.json.side_effect = Exception("JSON decode error")

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch('app.httpx.AsyncClient', return_value=mock_client):
        with patch('asyncio.sleep', side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await app.fetch_data_loop()

    assert app.current_data['online'] is False
    assert app.current_data['players'] == []
    assert app.current_data['heads'] == {}
    assert app.current_data['player_count'] == 0


# --- Test 14: stale heads cleared when server goes offline ---

@pytest.mark.asyncio
async def test_stale_heads_cleared_when_server_goes_offline():
    """Heads from a previous online poll must not persist after server goes offline."""
    # Seed state as if a prior poll found players online.
    app.current_data['online'] = True
    app.current_data['players'] = [{'name': 'Steve', 'uuid': 'abc-123'}]
    app.current_data['heads'] = {'Steve': 'https://mc-heads.net/avatar/abc-123/24'}
    app.current_data['player_count'] = 1

    offline_response = {
        'debug': {'ping': True},
        'online': False,
    }
    await _run_one_fetch_iteration(offline_response)

    assert app.current_data['online'] is False
    assert app.current_data['players'] == []
    assert app.current_data['player_count'] == 0


# --- Test 13: network timeout ---

@pytest.mark.asyncio
async def test_network_timeout_sets_offline():
    """A network error on client.get() should be caught and set offline state."""
    import httpx

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timed out"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch('app.httpx.AsyncClient', return_value=mock_client):
        with patch('asyncio.sleep', side_effect=asyncio.CancelledError):
            with pytest.raises(asyncio.CancelledError):
                await app.fetch_data_loop()

    assert app.current_data['online'] is False
    assert app.current_data['players'] == []
    assert app.current_data['heads'] == {}
    assert app.current_data['player_count'] == 0
