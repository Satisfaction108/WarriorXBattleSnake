#!/usr/bin/env python3
"""
Test constrictor mode functionality
"""

import sys
sys.path.insert(0, '.')

from main import is_constrictor_mode, evaluate_move_constrictor, calculate_reachable_space_constrictor

def test_constrictor_detection():
    """Test that constrictor mode is detected correctly"""
    
    # Constrictor mode game state (no food, full health)
    constrictor_state = {
        "game": {"id": "test"},
        "turn": 10,
        "board": {
            "height": 11,
            "width": 11,
            "food": [],  # NO FOOD in constrictor mode
            "snakes": [
                {
                    "id": "me",
                    "body": [
                        {"x": 5, "y": 5},
                        {"x": 5, "y": 4},
                        {"x": 5, "y": 3}
                    ],
                    "health": 100
                }
            ]
        },
        "you": {
            "id": "me",
            "body": [
                {"x": 5, "y": 5},
                {"x": 5, "y": 4},
                {"x": 5, "y": 3}
            ],
            "health": 100
        }
    }
    
    # Standard mode game state (has food, varying health)
    standard_state = {
        "game": {"id": "test"},
        "turn": 10,
        "board": {
            "height": 11,
            "width": 11,
            "food": [{"x": 1, "y": 1}, {"x": 9, "y": 9}],  # HAS FOOD
            "snakes": [
                {
                    "id": "me",
                    "body": [
                        {"x": 5, "y": 5},
                        {"x": 5, "y": 4},
                        {"x": 5, "y": 3}
                    ],
                    "health": 75
                }
            ]
        },
        "you": {
            "id": "me",
            "body": [
                {"x": 5, "y": 5},
                {"x": 5, "y": 4},
                {"x": 5, "y": 3}
            ],
            "health": 75
        }
    }
    
    print("Testing constrictor mode detection...")
    
    is_constrictor = is_constrictor_mode(constrictor_state)
    is_standard = is_constrictor_mode(standard_state)
    
    print(f"  Constrictor state detected as constrictor: {is_constrictor} (expected: True)")
    print(f"  Standard state detected as constrictor: {is_standard} (expected: False)")
    
    assert is_constrictor == True, "Failed to detect constrictor mode!"
    assert is_standard == False, "Incorrectly detected standard mode as constrictor!"
    
    print("✅ Constrictor detection test PASSED!\n")


def test_constrictor_evaluation():
    """Test that constrictor mode evaluation works"""
    
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
                        {"x": 5, "y": 4},
                        {"x": 5, "y": 3},
                        {"x": 5, "y": 2}
                    ],
                    "health": 100
                },
                {
                    "id": "opponent",
                    "body": [
                        {"x": 8, "y": 8},
                        {"x": 8, "y": 7},
                        {"x": 8, "y": 6}
                    ],
                    "health": 100
                }
            ]
        },
        "you": {
            "id": "me",
            "body": [
                {"x": 5, "y": 5},
                {"x": 5, "y": 4},
                {"x": 5, "y": 3},
                {"x": 5, "y": 2}
            ],
            "health": 100
        }
    }
    
    print("Testing constrictor mode evaluation...")
    
    # Evaluate all 4 directions
    directions = ["up", "down", "left", "right"]
    results = []
    
    for direction in directions:
        eval_result = evaluate_move_constrictor(direction, game_state)
        results.append(eval_result)
        print(f"  {direction.upper()}: Score = {eval_result['score']}")
        print(f"    Top reasons: {eval_result['reasons'][:3]}")
    
    # Check that we got valid scores
    for result in results:
        assert "score" in result, "Missing score in evaluation!"
        assert "reasons" in result, "Missing reasons in evaluation!"
        assert "direction" in result, "Missing direction in evaluation!"
    
    # Check that wall moves are heavily penalized
    # Down would hit our own body at (5, 4)
    down_result = [r for r in results if r["direction"] == "down"][0]
    assert down_result["score"] < -1000000, "Self-collision not penalized enough!"
    
    print("✅ Constrictor evaluation test PASSED!\n")


def test_space_calculation():
    """Test space calculation in constrictor mode"""
    
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
                        {"x": 5, "y": 4}
                    ],
                    "health": 100
                }
            ]
        },
        "you": {
            "id": "me",
            "body": [
                {"x": 5, "y": 5},
                {"x": 5, "y": 4}
            ],
            "health": 100
        }
    }
    
    print("Testing space calculation...")
    
    # Calculate space from center position
    center_pos = {"x": 5, "y": 5}
    space_result = calculate_reachable_space_constrictor(center_pos, game_state, max_depth=50)
    
    print(f"  Reachable cells from center: {space_result['reachable_cells']}")
    print(f"  Max distance: {space_result['max_distance']}")
    print(f"  Is isolated: {space_result['is_isolated']}")
    
    # Should have lots of space from center
    assert space_result['reachable_cells'] > 50, "Not enough reachable space calculated!"
    assert not space_result['is_isolated'], "Center position incorrectly marked as isolated!"
    
    print("✅ Space calculation test PASSED!\n")


if __name__ == "__main__":
    print("="*80)
    print("🐍 CONSTRICTOR MODE TESTS")
    print("="*80)
    print()
    
    try:
        test_constrictor_detection()
        test_constrictor_evaluation()
        test_space_calculation()
        
        print("="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

