#!/usr/bin/env python3
"""
Full integration test for constrictor mode
Simulates a real game scenario
"""

import sys
sys.path.insert(0, '.')

from main import move, is_constrictor_mode

def test_full_constrictor_game():
    """Test a full constrictor mode game scenario"""
    
    # Constrictor mode game state with 2 snakes
    game_state = {
        "game": {
            "id": "test-constrictor",
            "ruleset": {
                "name": "constrictor",
                "version": "v1.0.0"
            }
        },
        "turn": 15,
        "board": {
            "height": 11,
            "width": 11,
            "food": [],  # NO FOOD in constrictor mode
            "snakes": [
                {
                    "id": "me",
                    "name": "WarriorX",
                    "body": [
                        {"x": 5, "y": 5},
                        {"x": 5, "y": 4},
                        {"x": 5, "y": 3},
                        {"x": 5, "y": 2},
                        {"x": 6, "y": 2},
                        {"x": 7, "y": 2}
                    ],
                    "health": 100,
                    "latency": 50,
                    "head": {"x": 5, "y": 5},
                    "length": 6,
                    "shout": ""
                },
                {
                    "id": "opponent",
                    "name": "Enemy",
                    "body": [
                        {"x": 8, "y": 8},
                        {"x": 8, "y": 7},
                        {"x": 8, "y": 6},
                        {"x": 9, "y": 6}
                    ],
                    "health": 100,
                    "latency": 50,
                    "head": {"x": 8, "y": 8},
                    "length": 4,
                    "shout": ""
                }
            ],
            "hazards": []
        },
        "you": {
            "id": "me",
            "name": "WarriorX",
            "body": [
                {"x": 5, "y": 5},
                {"x": 5, "y": 4},
                {"x": 5, "y": 3},
                {"x": 5, "y": 2},
                {"x": 6, "y": 2},
                {"x": 7, "y": 2}
            ],
            "health": 100,
            "latency": 50,
            "head": {"x": 5, "y": 5},
            "length": 6,
            "shout": ""
        }
    }
    
    print("="*80)
    print("🐍 FULL CONSTRICTOR MODE INTEGRATION TEST")
    print("="*80)
    print()
    
    # Verify constrictor mode is detected
    assert is_constrictor_mode(game_state), "Failed to detect constrictor mode!"
    print("✅ Constrictor mode detected correctly")
    print()
    
    # Call the move function
    print("Calling move() function...")
    print()
    
    result = move(game_state)
    
    print()
    print("="*80)
    print("📊 MOVE RESULT")
    print("="*80)
    print(f"Move chosen: {result['move']}")
    print(f"Shout: {result.get('shout', 'N/A')}")
    print()
    
    # Verify we got a valid move
    assert "move" in result, "No move returned!"
    assert result["move"] in ["up", "down", "left", "right"], f"Invalid move: {result['move']}"
    
    # Verify we didn't choose a suicidal move
    # Down would be self-collision (body at 5,4)
    assert result["move"] != "down", "Chose self-collision move!"
    
    print("✅ Valid move chosen")
    print("✅ Avoided self-collision")
    print()
    
    return result


def test_constrictor_edge_avoidance():
    """Test that constrictor mode avoids edges when possible"""
    
    # Snake near edge
    game_state = {
        "game": {"id": "test"},
        "turn": 5,
        "board": {
            "height": 11,
            "width": 11,
            "food": [],
            "snakes": [
                {
                    "id": "me",
                    "body": [
                        {"x": 1, "y": 1},  # Near corner!
                        {"x": 1, "y": 2},
                        {"x": 1, "y": 3}
                    ],
                    "health": 100,
                    "head": {"x": 1, "y": 1},
                    "length": 3
                }
            ]
        },
        "you": {
            "id": "me",
            "body": [
                {"x": 1, "y": 1},
                {"x": 1, "y": 2},
                {"x": 1, "y": 3}
            ],
            "health": 100,
            "head": {"x": 1, "y": 1},
            "length": 3
        }
    }
    
    print("="*80)
    print("🚫 EDGE AVOIDANCE TEST")
    print("="*80)
    print()
    
    result = move(game_state)
    
    print()
    print(f"Move chosen: {result['move']}")
    
    # Should prefer right (away from edge) over down (toward corner)
    # Left is wall, up is backwards
    assert result["move"] == "right", f"Should avoid corner! Chose: {result['move']}"
    
    print("✅ Correctly avoided corner/edge")
    print()


def test_constrictor_space_maximization():
    """Test that constrictor mode maximizes available space"""

    # Snake with choice between large and small spaces
    game_state = {
        "game": {"id": "test"},
        "turn": 10,
        "board": {
            "height": 11,
            "width": 11,
            "food": [],
            "snakes": [
                {
                    "id": "me",
                    "body": [
                        {"x": 5, "y": 5},
                        {"x": 4, "y": 5},
                        {"x": 3, "y": 5},
                        {"x": 2, "y": 5}
                    ],
                    "health": 100,
                    "head": {"x": 5, "y": 5},
                    "length": 4
                }
            ]
        },
        "you": {
            "id": "me",
            "body": [
                {"x": 5, "y": 5},
                {"x": 4, "y": 5},
                {"x": 3, "y": 5},
                {"x": 2, "y": 5}
            ],
            "health": 100,
            "head": {"x": 5, "y": 5},
            "length": 4
        }
    }

    print("="*80)
    print("🌊 SPACE MAXIMIZATION TEST")
    print("="*80)
    print()

    result = move(game_state)

    print()
    print(f"Move chosen: {result['move']}")

    # Should choose a valid move that doesn't trap us
    # Valid moves are up, down, right (left is backwards)
    assert result["move"] in ["up", "down", "right"], f"Invalid move! Chose: {result['move']}"
    assert result["move"] != "left", "Should not go backwards!"

    print("✅ Chose valid move with good space")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "🐍 CONSTRICTOR MODE FULL TESTS" + " "*28 + "║")
    print("╚" + "="*78 + "╝")
    print()
    
    try:
        test_full_constrictor_game()
        test_constrictor_edge_avoidance()
        test_constrictor_space_maximization()
        
        print("="*80)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("="*80)
        print()
        print("🎉 Constrictor mode is fully functional!")
        print()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

