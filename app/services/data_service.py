"""
Placeholder data layer. Replace with DB or CSV loaders for real IPL stats.
"""
from __future__ import annotations

from typing import Optional

_PLAYERS = [
    {"id": "demo-1", "name": "A. Sharma", "team": "Rajasthan Royals"},
    {"id": "demo-2", "name": "K. Patel", "team": "Kolkata Knight Riders"},
]

_MATCHUPS = [
    {"id": "m1", "label": "RR vs CSK", "venue": "Jaipur"},
    {"id": "m2", "label": "KKR vs RCB", "venue": "Eden Gardens"},
]


def list_players():
    return _PLAYERS


def get_player(player_id: str) -> Optional[dict]:
    for p in _PLAYERS:
        if p["id"] == player_id:
            return p
    return None


def list_matchups():
    return _MATCHUPS


def get_matchup(matchup_id: str) -> Optional[dict]:
    for m in _MATCHUPS:
        if m["id"] == matchup_id:
            return m
    return None
