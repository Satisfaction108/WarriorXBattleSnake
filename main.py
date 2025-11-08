# Welcome to
# __________         __    __  .__                               __
# \______   \_____ _/  |__/  |_|  |   ____   ______ ____ _____  |  | __ ____
#  |    |  _/\__  \\   __\   __\  | _/ __ \ /  ___//    \\__  \ |  |/ // __ \
#  |    |   \ / __ \|  |  |  | |  |_\  ___/ \___ \|   |  \/ __ \|    <\  ___/
#  |________/(______/__|  |__| |____/\_____>______>___|__(______/__|__\\_____>
#
# WarriorX - Advanced Battlesnake AI
# Implements pathfinding, flood fill, predictive collision avoidance, and strategic gameplay

import random
import typing
from collections import deque

# ============================================================================
# HELPER FUNCTIONS AND DATA STRUCTURES
# ============================================================================

def get_neighbors(pos: dict, board_width: int, board_height: int) -> list:
    """Get all valid neighboring positions (up, down, left, right)"""
    neighbors = []
    directions = [
        {"x": pos["x"], "y": pos["y"] + 1, "dir": "up"},
        {"x": pos["x"], "y": pos["y"] - 1, "dir": "down"},
        {"x": pos["x"] - 1, "y": pos["y"], "dir": "left"},
        {"x": pos["x"] + 1, "y": pos["y"], "dir": "right"}
    ]

    for d in directions:
        if 0 <= d["x"] < board_width and 0 <= d["y"] < board_height:
            neighbors.append(d)

    return neighbors


def coords_equal(a: dict, b: dict) -> bool:
    """Check if two coordinates are equal"""
    return a["x"] == b["x"] and a["y"] == b["y"]


def manhattan_distance(a: dict, b: dict) -> int:
    """Calculate Manhattan distance between two points"""
    return abs(a["x"] - b["x"]) + abs(a["y"] - b["y"])


# ============================================================================
# PATHFINDING - BFS ALGORITHM
# ============================================================================

def bfs_path(start: dict, goal: dict, board_width: int, board_height: int, obstacles: set) -> list:
    """
    BFS pathfinding to find shortest path from start to goal.
    Returns list of directions to reach goal, or empty list if no path exists.
    """
    queue = deque([(start, [])])
    visited = {(start["x"], start["y"])}

    while queue:
        current, path = queue.popleft()

        if coords_equal(current, goal):
            return path

        for neighbor in get_neighbors(current, board_width, board_height):
            coord_tuple = (neighbor["x"], neighbor["y"])

            if coord_tuple not in visited and coord_tuple not in obstacles:
                visited.add(coord_tuple)
                queue.append((neighbor, path + [neighbor["dir"]]))

    return []  # No path found


def bfs_distance(start: dict, goal: dict, board_width: int, board_height: int, obstacles: set) -> int:
    """Calculate shortest distance using BFS. Returns -1 if unreachable."""
    path = bfs_path(start, goal, board_width, board_height, obstacles)
    return len(path) if path else -1


# ============================================================================
# FLOOD FILL - SPACE EVALUATION
# ============================================================================

def flood_fill(start: dict, board_width: int, board_height: int, obstacles: set) -> int:
    """
    Flood fill algorithm to count available space from a starting position.
    Returns the number of reachable cells.
    """
    if (start["x"], start["y"]) in obstacles:
        return 0

    visited = set()
    queue = deque([start])
    count = 0

    while queue:
        current = queue.popleft()
        coord_tuple = (current["x"], current["y"])

        if coord_tuple in visited or coord_tuple in obstacles:
            continue

        visited.add(coord_tuple)
        count += 1

        for neighbor in get_neighbors(current, board_width, board_height):
            neighbor_tuple = (neighbor["x"], neighbor["y"])
            if neighbor_tuple not in visited and neighbor_tuple not in obstacles:
                queue.append(neighbor)

    return count


# ============================================================================
# COLLISION DETECTION
# ============================================================================

def get_all_obstacles(game_state: dict, include_tail: bool = True) -> set:
    """
    Get all obstacle coordinates (snake bodies).
    If include_tail=False, excludes all snake tails (they'll move next turn).
    """
    obstacles = set()

    # Add all snake bodies
    for snake in game_state["board"]["snakes"]:
        body = snake["body"]
        end_idx = len(body) if include_tail else len(body) - 1
        for i in range(end_idx):
            obstacles.add((body[i]["x"], body[i]["y"]))

    return obstacles


def is_safe_move(pos: dict, game_state: dict, my_length: int) -> bool:
    """Check if a position is safe (no walls, no snake bodies)"""
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Check walls
    if pos["x"] < 0 or pos["x"] >= board_width or pos["y"] < 0 or pos["y"] >= board_height:
        return False

    # Check snake bodies (excluding tails that will move)
    obstacles = get_all_obstacles(game_state, include_tail=False)
    if (pos["x"], pos["y"]) in obstacles:
        return False

    return True


def avoid_head_collision(pos: dict, game_state: dict, my_length: int) -> bool:
    """
    Check if moving to pos could result in head-to-head collision with larger/equal snake.
    Returns True if safe, False if dangerous.
    """
    my_head = game_state["you"]["body"][0]

    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        opponent_head = snake["body"][0]
        opponent_length = len(snake["body"])

        # Check if opponent could move to same position or adjacent position
        opponent_neighbors = get_neighbors(opponent_head,
                                          game_state["board"]["width"],
                                          game_state["board"]["height"])

        for opp_move in opponent_neighbors:
            # Direct head-to-head collision
            if coords_equal(pos, opp_move):
                if opponent_length >= my_length:
                    return False  # Dangerous - opponent is bigger or equal

        # Check if we're moving next to opponent's head (they could collide with us)
        if manhattan_distance(pos, opponent_head) == 1:
            if opponent_length >= my_length:
                return False

    return True


# ============================================================================
# SNAKE APPEARANCE
# ============================================================================

def info() -> typing.Dict:
    """Battlesnake appearance and metadata"""
    print("INFO")

    return {
        "apiversion": "1",
        "author": "WarriorX",
        "color": "#FF0000",  # Bold red color
        "head": "evil",      # Intimidating head
        "tail": "sharp",     # Sharp tail
    }


# ============================================================================
# GAME LIFECYCLE FUNCTIONS
# ============================================================================

def start(game_state: typing.Dict):
    """Called when game starts"""
    print("GAME START")


def end(game_state: typing.Dict):
    """Called when game ends"""
    print("GAME OVER\n")


# ============================================================================
# ADVANCED MOVE LOGIC
# ============================================================================

def evaluate_move(direction: str, game_state: dict) -> dict:
    """
    Evaluate a move direction and return a score with reasoning.
    Higher score = better move.
    """
    my_head = game_state["you"]["body"][0]
    my_body = game_state["you"]["body"]
    my_length = len(my_body)
    my_health = game_state["you"]["health"]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    food_list = game_state["board"]["food"]

    # Calculate new head position
    new_head = {"x": my_head["x"], "y": my_head["y"]}
    if direction == "up":
        new_head["y"] += 1
    elif direction == "down":
        new_head["y"] -= 1
    elif direction == "left":
        new_head["x"] -= 1
    elif direction == "right":
        new_head["x"] += 1

    score = 100  # Base score
    reasons = []

    # CRITICAL: Check basic safety
    if not is_safe_move(new_head, game_state, my_length):
        return {"score": -1000, "reasons": ["UNSAFE: Wall or snake body collision"], "direction": direction}

    # CRITICAL: Avoid head-to-head collisions with larger/equal snakes
    if not avoid_head_collision(new_head, game_state, my_length):
        score -= 500
        reasons.append("DANGER: Potential head-to-head with larger snake")

    # Get obstacles for flood fill (excluding tails)
    obstacles = get_all_obstacles(game_state, include_tail=False)

    # IMPORTANT: Evaluate available space using flood fill
    available_space = flood_fill(new_head, board_width, board_height, obstacles)

    # If space is less than our body length, it's very dangerous (potential trap)
    if available_space < my_length:
        score -= 300
        reasons.append(f"TRAP: Only {available_space} spaces available (need {my_length})")
    elif available_space < my_length * 2:
        score -= 100
        reasons.append(f"TIGHT: Limited space ({available_space})")
    else:
        # Reward more space
        score += min(available_space, 50)
        reasons.append(f"SPACE: {available_space} cells available")

    # FOOD SEEKING: Prioritize food when health is low
    if food_list:
        nearest_food = min(food_list, key=lambda f: manhattan_distance(new_head, f))
        food_distance = manhattan_distance(new_head, nearest_food)

        # Calculate path to food
        obstacles_with_tail = get_all_obstacles(game_state, include_tail=True)
        path_to_food = bfs_path(new_head, nearest_food, board_width, board_height, obstacles_with_tail)

        if my_health < 50:
            # Low health - prioritize food heavily
            if path_to_food:
                score += 200 - len(path_to_food) * 10
                reasons.append(f"HUNGRY: Food in {len(path_to_food)} moves")
            else:
                score -= 50
                reasons.append("HUNGRY: No path to food")
        elif my_health < 80:
            # Medium health - consider food
            if path_to_food:
                score += 50 - len(path_to_food) * 5
                reasons.append(f"Food available in {len(path_to_food)} moves")
        else:
            # High health - food is less important, but still good
            if path_to_food and len(path_to_food) < 5:
                score += 20
                reasons.append("Opportunistic food grab")

    # TAIL CHASING: When healthy and no immediate food needed, follow tail
    if my_health > 60 and len(my_body) > 3:
        my_tail = my_body[-1]
        tail_distance = manhattan_distance(new_head, my_tail)
        if tail_distance <= 2:
            score += 30
            reasons.append("TAIL CHASE: Following tail for safety")

    # AGGRESSIVE BEHAVIOR: Cut off smaller snakes
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        opponent_head = snake["body"][0]
        opponent_length = len(snake["body"])

        if opponent_length < my_length:
            # We're bigger - be aggressive
            distance_to_opponent = manhattan_distance(new_head, opponent_head)
            if distance_to_opponent <= 3:
                score += 40
                reasons.append(f"AGGRESSIVE: Pressuring smaller snake")

    # CENTER CONTROL: Prefer center positions (more options)
    center_x = board_width // 2
    center_y = board_height // 2
    distance_from_center = manhattan_distance(new_head, {"x": center_x, "y": center_y})
    max_distance = board_width + board_height
    center_score = (max_distance - distance_from_center) * 2
    score += center_score

    return {"score": score, "reasons": reasons, "direction": direction}


def move(game_state: typing.Dict) -> typing.Dict:
    """
    Main move function - evaluates all possible moves and chooses the best one.
    Implements advanced AI with pathfinding, flood fill, and strategic decision making.
    """
    my_head = game_state["you"]["body"][0]
    my_neck = game_state["you"]["body"][1] if len(game_state["you"]["body"]) > 1 else my_head

    # Get all possible moves
    possible_moves = ["up", "down", "left", "right"]

    # Remove backwards move
    if my_neck["x"] < my_head["x"]:
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:
        possible_moves.remove("up")

    # Evaluate all possible moves
    move_evaluations = []
    for direction in possible_moves:
        evaluation = evaluate_move(direction, game_state)
        move_evaluations.append(evaluation)

    # Sort by score (highest first)
    move_evaluations.sort(key=lambda x: x["score"], reverse=True)

    # Log the decision
    turn = game_state["turn"]
    best_move = move_evaluations[0]

    print(f"\n=== MOVE {turn} ===")
    print(f"Health: {game_state['you']['health']}")
    print(f"Length: {len(game_state['you']['body'])}")
    print(f"\nMove Evaluations:")
    for eval in move_evaluations:
        print(f"  {eval['direction']}: {eval['score']} - {', '.join(eval['reasons'][:2])}")
    print(f"\nChosen: {best_move['direction']} (score: {best_move['score']})")

    # If best move is still unsafe, try any move as last resort
    if best_move["score"] < -500:
        print("WARNING: All moves are dangerous! Choosing least bad option.")

    return {
        "move": best_move["direction"],
        "shout": "WarriorX strikes!" if turn % 10 == 0 else ""
    }


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

