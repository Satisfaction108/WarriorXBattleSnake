#!/usr/bin/env python3
"""Test trapping logic - verify snake can trap opponents"""

import json
from main import move, start

print("="*80)
print("TEST 1: Opponent in corner - should try to trap them")
print("="*80)

# Opponent is in bottom-left corner with limited escapes
game_state_1 = {
    "game": {"id": "trap-test-1", "timeout": 500},
    "turn": 10,
    "board": {
        "height": 11,
        "width": 11,
        "food": [{"x": 5, "y": 5}],
        "snakes": [
            {
                "id": "you",
                "name": "WarriorX",
                "health": 90,
                "body": [{"x": 2, "y": 2}, {"x": 2, "y": 3}, {"x": 2, "y": 4}],
                "head": {"x": 2, "y": 2}
            },
            {
                "id": "opponent",
                "name": "Enemy",
                "health": 80,
                "body": [{"x": 0, "y": 0}, {"x": 0, "y": 1}],  # In corner!
                "head": {"x": 0, "y": 0}
            }
        ]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 90,
        "body": [{"x": 2, "y": 2}, {"x": 2, "y": 3}, {"x": 2, "y": 4}],
        "head": {"x": 2, "y": 2}
    }
}

start(game_state_1)
result_1 = move(game_state_1)
print(f"\n✅ Result: {json.dumps(result_1, indent=2)}")
print(f"Expected: Should move toward opponent to cut off escapes (left or down)")
print()

print("="*80)
print("TEST 2: Opponent on edge with 2 escapes - should try to trap")
print("="*80)

# Opponent is on edge with only 2 escape routes
game_state_2 = {
    "game": {"id": "trap-test-2", "timeout": 500},
    "turn": 15,
    "board": {
        "height": 11,
        "width": 11,
        "food": [{"x": 8, "y": 8}],
        "snakes": [
            {
                "id": "you",
                "name": "WarriorX",
                "health": 85,
                "body": [{"x": 3, "y": 0}, {"x": 3, "y": 1}, {"x": 3, "y": 2}, {"x": 3, "y": 3}],
                "head": {"x": 3, "y": 0}
            },
            {
                "id": "opponent",
                "name": "Enemy",
                "health": 75,
                "body": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 0, "y": 2}],  # On edge
                "head": {"x": 0, "y": 0}
            }
        ]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 85,
        "body": [{"x": 3, "y": 0}, {"x": 3, "y": 1}, {"x": 3, "y": 2}, {"x": 3, "y": 3}],
        "head": {"x": 3, "y": 0}
    }
}

start(game_state_2)
result_2 = move(game_state_2)
print(f"\n✅ Result: {json.dumps(result_2, indent=2)}")
print(f"Expected: Should move left to cut off opponent's escape")
print()

print("="*80)
print("TEST 3: Mutual kill scenario - both trapped")
print("="*80)

# Both snakes are in bad positions, should prefer mutual kill
game_state_3 = {
    "game": {"id": "trap-test-3", "timeout": 500},
    "turn": 20,
    "board": {
        "height": 11,
        "width": 11,
        "food": [],
        "snakes": [
            {
                "id": "you",
                "name": "WarriorX",
                "health": 50,
                "body": [
                    {"x": 0, "y": 1}, {"x": 0, "y": 2}, {"x": 0, "y": 3},
                    {"x": 1, "y": 3}, {"x": 2, "y": 3}, {"x": 3, "y": 3}
                ],
                "head": {"x": 0, "y": 1}
            },
            {
                "id": "opponent",
                "name": "Enemy",
                "health": 50,
                "body": [
                    {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 3, "y": 0},
                    {"x": 4, "y": 0}, {"x": 5, "y": 0}, {"x": 6, "y": 0}
                ],
                "head": {"x": 1, "y": 0}
            }
        ]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 50,
        "body": [
            {"x": 0, "y": 1}, {"x": 0, "y": 2}, {"x": 0, "y": 3},
            {"x": 1, "y": 3}, {"x": 2, "y": 3}, {"x": 3, "y": 3}
        ],
        "head": {"x": 0, "y": 1}
    }
}

start(game_state_3)
result_3 = move(game_state_3)
print(f"\n✅ Result: {json.dumps(result_3, indent=2)}")
print(f"Expected: Should consider aggressive moves since we're trapped")
print()

print("="*80)
print("TEST 4: Edge avoidance - should avoid edges when possible")
print("="*80)

# Snake in middle with choice between center and edge
game_state_4 = {
    "game": {"id": "trap-test-4", "timeout": 500},
    "turn": 5,
    "board": {
        "height": 11,
        "width": 11,
        "food": [{"x": 5, "y": 5}],
        "snakes": [
            {
                "id": "you",
                "name": "WarriorX",
                "health": 95,
                "body": [{"x": 5, "y": 1}, {"x": 5, "y": 2}, {"x": 5, "y": 3}],
                "head": {"x": 5, "y": 1}
            },
            {
                "id": "opponent",
                "name": "Enemy",
                "health": 90,
                "body": [{"x": 8, "y": 8}, {"x": 8, "y": 9}, {"x": 8, "y": 10}],
                "head": {"x": 8, "y": 8}
            }
        ]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 95,
        "body": [{"x": 5, "y": 1}, {"x": 5, "y": 2}, {"x": 5, "y": 3}],
        "head": {"x": 5, "y": 1}
    }
}

start(game_state_4)
result_4 = move(game_state_4)
print(f"\n✅ Result: {json.dumps(result_4, indent=2)}")
print(f"Expected: Should prefer 'up' (toward center) over 'down' (toward edge)")
print()

print("="*80)
print("✅ All trapping tests completed!")
print("="*80)

