"""Player identity — who is 'me' in the demos.

Configure for your own account. PLAYER_STEAMID is the 64-bit Steam ID of the
player to analyze; PLAYER_NAME is the display name shown in reports. Both can
be set via environment variables so no personal data lives in the code.
"""
import os

PLAYER_STEAMID = os.environ.get("CS2_PLAYER_STEAMID", "0000000000000000")
PLAYER_NAME = os.environ.get("CS2_PLAYER_NAME", "Player")

# Aliases kept for backwards compatibility with the analyzer modules.
JOHN_STEAMID = PLAYER_STEAMID
JOHN_NAME = PLAYER_NAME
