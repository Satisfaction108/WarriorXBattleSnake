#!/usr/bin/env python3
"""Simulate a real game to verify snake doesn't get stuck going up"""

import json
from main import move, start

print("="*80)
print("GAME SIMULATION: Verify snake makes intelligent varied moves")
print("="*80)

# Initialize game
game_state = {
    "game": {"id": "simulation-1", "timeout": 500},
    "turn": 0,
    "board": {
        "height": 11,
        "width": 11,
        "food": [{"x": 5, "y": 5}, {"x": 8, "y": 8}],
        "snakes": [
            {
                "id": "you",
                "name": "WarriorX",
                "health": 100,
                "body": [{"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 1, "y": 3}],
                "head": {"x": 1, "y": 1}
            },
            {
                "id": "opponent",
                "name": "Enemy",
                "health": 100,
                "body": [{"x": 9, "y": 9}, {"x": 9, "y": 8}, {"x": 9, "y": 7}],
                "head": {"x": 9, "y": 9}
            }
        ]
    },
    "you": {
        "id": "you",
        "name": "WarriorX",
        "health": 100,
        "body": [{"x": 1, "y": 1}, {"x": 1, "y": 2}, {"x": 1, "y": 3}],
        "head": {"x": 1, "y": 1}
    }
}

start(game_state)

moves_made = []
positions = [(1, 1)]

print("\nSimulating 10 turns...")
print("-" * 80)

for turn in range(10):
    game_state["turn"] = turn
    
    # Make move
    result = move(game_state)
    move_direction = result["move"]
    moves_made.append(move_direction)
    
    # Update position based on move
    current_pos = positions[-1]
    new_pos = list(current_pos)
    
    if move_direction == "up":
        new_pos[1] += 1
    elif move_direction == "down":
        new_pos[1] -= 1
    elif move_direction == "left":
        new_pos[0] -= 1
    elif move_direction == "right":
        new_pos[0] += 1
    
    positions.append(tuple(new_pos))
    
    # Update game state for next turn
    game_state["you"]["head"] = {"x": new_pos[0], "y": new_pos[1]}
    game_state["you"]["body"][0] = {"x": new_pos[0], "y": new_pos[1]}
    game_state["you"]["health"] -= 1
    
    print(f"Turn {turn}: {move_direction.upper():5s} -> Position: ({new_pos[0]}, {new_pos[1]})")

print("-" * 80)
print("\nSUMMARY:")
print(f"Moves made: {moves_made}")
print(f"Unique moves: {set(moves_made)}")
print(f"Move counts:")
for direction in ["up", "down", "left", "right"]:
    count = moves_made.count(direction)
    percentage = (count / len(moves_made)) * 100
    print(f"  {direction.upper():5s}: {count:2d} ({percentage:5.1f}%)")

print(f"\nPath taken: {positions}")

# Check if stuck in pattern
if len(set(moves_made)) == 1:
    print("\n❌ FAILED: Snake is stuck making only one move!")
elif moves_made.count("up") == len(moves_made):
    print("\n❌ FAILED: Snake is only going UP!")
else:
    print("\n✅ SUCCESS: Snake is making varied moves!")

print("="*80)

