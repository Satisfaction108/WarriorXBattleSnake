#!/usr/bin/env python3
"""Quick test to verify snake makes different moves"""

import json
from main import move, start

# Test 1: Snake in middle of board
print("="*80)
print("TEST 1: Snake in middle - should have multiple move options")
print("="*80)

game_state_1 = {
    "game": {"id": "test-1", "timeout": 500},
    "turn": 5,
    "board": {
        "height": 11,
        "width": 11,
        "food": [{"x": 5, "y": 5}],
        "snakes": [{
            "id": "you",
            "name": "WarriorX",
            "health": 80,
            "body": [{"x": 3, "y": 3}, {"x": 3, "y": 4}, {"x": 3, "y": 5}],
            "head": {"x": 3, "y": 3}
        }]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 80,
        "body": [{"x": 3, "y": 3}, {"x": 3, "y": 4}, {"x": 3, "y": 5}],
        "head": {"x": 3, "y": 3}
    }
}

start(game_state_1)
result_1 = move(game_state_1)
print(f"\n✅ Result: {json.dumps(result_1, indent=2)}\n")

# Test 2: Snake in corner
print("="*80)
print("TEST 2: Snake in corner - should avoid walls")
print("="*80)

game_state_2 = {
    "game": {"id": "test-2", "timeout": 500},
    "turn": 1,
    "board": {
        "height": 11,
        "width": 11,
        "food": [{"x": 5, "y": 5}],
        "snakes": [{
            "id": "you",
            "name": "WarriorX",
            "health": 100,
            "body": [{"x": 0, "y": 0}, {"x": 0, "y": 1}],
            "head": {"x": 0, "y": 0}
        }]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 100,
        "body": [{"x": 0, "y": 0}, {"x": 0, "y": 1}],
        "head": {"x": 0, "y": 0}
    }
}

start(game_state_2)
result_2 = move(game_state_2)
print(f"\n✅ Result: {json.dumps(result_2, indent=2)}\n")

# Test 3: Multiple moves in sequence
print("="*80)
print("TEST 3: Multiple sequential moves - should vary")
print("="*80)

moves = []
for i in range(5):
    game_state_3 = {
        "game": {"id": "test-3", "timeout": 500},
        "turn": i,
        "board": {
            "height": 11,
            "width": 11,
            "food": [{"x": 5, "y": 5}],
            "snakes": [{
                "id": "you",
                "name": "WarriorX",
                "health": 90 - i*5,
                "body": [{"x": 5, "y": 5}, {"x": 5, "y": 6}, {"x": 5, "y": 7}],
                "head": {"x": 5, "y": 5}
            }]
        },
        "you": {
            "id": "you",
            "name": "WarriorX",
            "health": 90 - i*5,
            "body": [{"x": 5, "y": 5}, {"x": 5, "y": 6}, {"x": 5, "y": 7}],
            "head": {"x": 5, "y": 5}
        }
    }
    
    result = move(game_state_3)
    moves.append(result["move"])
    print(f"Turn {i}: {result['move']}")

print(f"\nMoves made: {moves}")
print(f"Unique moves: {set(moves)}")
print(f"\n✅ All tests completed!\n")

