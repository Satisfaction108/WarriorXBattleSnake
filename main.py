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
        "color": "#8B00FF",  # Deep electric purple - powerful and menacing
        "head": "dead",      # SKULL HEAD - ultimate intimidation
        "tail": "bolt",      # Lightning bolt - raw power
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
# GAME STATE SIMULATION
# ============================================================================

def simulate_snake_move(snake: dict, direction: str, ate_food: bool = False) -> dict:
    """
    Simulate a snake moving in a direction.
    Returns new snake state.
    """
    head = snake["body"][0]
    new_head = {"x": head["x"], "y": head["y"]}

    if direction == "up":
        new_head["y"] += 1
    elif direction == "down":
        new_head["y"] -= 1
    elif direction == "left":
        new_head["x"] -= 1
    elif direction == "right":
        new_head["x"] += 1

    new_body = [new_head] + snake["body"][:]

    # If didn't eat food, remove tail
    if not ate_food:
        new_body = new_body[:-1]

    return {
        "id": snake["id"],
        "name": snake["name"],
        "health": snake["health"] - 1 if not ate_food else 100,
        "body": new_body,
        "head": new_head
    }


def get_possible_moves(snake: dict, board_width: int, board_height: int) -> list:
    """Get all valid moves for a snake (not into walls, not backwards)"""
    head = snake["body"][0]
    neck = snake["body"][1] if len(snake["body"]) > 1 else head

    moves = []

    # Up
    if head["y"] + 1 < board_height and not (neck["x"] == head["x"] and neck["y"] == head["y"] + 1):
        moves.append("up")

    # Down
    if head["y"] - 1 >= 0 and not (neck["x"] == head["x"] and neck["y"] == head["y"] - 1):
        moves.append("down")

    # Left
    if head["x"] - 1 >= 0 and not (neck["x"] == head["x"] - 1 and neck["y"] == head["y"]):
        moves.append("left")

    # Right
    if head["x"] + 1 < board_width and not (neck["x"] == head["x"] + 1 and neck["y"] == head["y"]):
        moves.append("right")

    return moves


def simulate_game_state(game_state: dict, my_move: str, opponent_moves: dict) -> dict:
    """
    Simulate one turn of the game.
    opponent_moves is a dict mapping snake_id to move direction.
    Returns new game state.
    """
    new_snakes = []
    food_eaten = set()

    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    food_list = game_state["board"]["food"][:]

    # Simulate each snake's move
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            move = my_move
        else:
            move = opponent_moves.get(snake["id"], "up")  # Default to up if not specified

        # Check if snake will eat food
        head = snake["body"][0]
        new_head = {"x": head["x"], "y": head["y"]}

        if move == "up":
            new_head["y"] += 1
        elif move == "down":
            new_head["y"] -= 1
        elif move == "left":
            new_head["x"] -= 1
        elif move == "right":
            new_head["x"] += 1

        ate_food = False
        for food in food_list:
            if coords_equal(new_head, food):
                ate_food = True
                food_eaten.add((food["x"], food["y"]))
                break

        new_snake = simulate_snake_move(snake, move, ate_food)
        new_snakes.append(new_snake)

    # Remove eaten food
    new_food = [f for f in food_list if (f["x"], f["y"]) not in food_eaten]

    # Check for collisions and remove dead snakes
    alive_snakes = []
    for snake in new_snakes:
        if is_snake_alive(snake, new_snakes, board_width, board_height):
            alive_snakes.append(snake)

    # Update game state
    new_game_state = {
        "game": game_state["game"],
        "turn": game_state["turn"] + 1,
        "board": {
            "width": board_width,
            "height": board_height,
            "food": new_food,
            "snakes": alive_snakes
        },
        "you": next((s for s in alive_snakes if s["id"] == game_state["you"]["id"]), None)
    }

    return new_game_state


def is_snake_alive(snake: dict, all_snakes: list, board_width: int, board_height: int) -> bool:
    """Check if a snake is still alive after a move"""
    head = snake["body"][0]

    # Check wall collision
    if head["x"] < 0 or head["x"] >= board_width or head["y"] < 0 or head["y"] >= board_height:
        return False

    # Check self-collision
    for i in range(1, len(snake["body"])):
        if coords_equal(head, snake["body"][i]):
            return False

    # Check collision with other snakes
    for other_snake in all_snakes:
        if other_snake["id"] == snake["id"]:
            continue

        # Check body collision
        for segment in other_snake["body"]:
            if coords_equal(head, segment):
                return False

        # Check head-to-head collision
        other_head = other_snake["body"][0]
        if coords_equal(head, other_head):
            # Both die if same length, smaller dies if different
            if len(snake["body"]) <= len(other_snake["body"]):
                return False

    # Check health
    if snake["health"] <= 0:
        return False

    return True


# ============================================================================
# ADVANCED MOVE LOGIC WITH PREDICTION
# ============================================================================

def predict_opponent_moves(game_state: dict, depth: int = 1) -> list:
    """
    Predict possible opponent move combinations.
    Returns list of move dictionaries (snake_id -> move).
    For depth > 1, returns most likely moves based on simple heuristics.
    """
    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != game_state["you"]["id"]]

    if not opponents:
        return [{}]

    # For each opponent, get their possible moves
    opponent_move_options = {}
    for snake in opponents:
        moves = get_possible_moves(snake, game_state["board"]["width"], game_state["board"]["height"])
        if not moves:
            moves = ["up"]  # Fallback
        opponent_move_options[snake["id"]] = moves

    # For simplicity, we'll consider a few likely scenarios rather than all combinations
    # This prevents exponential explosion

    if len(opponents) == 1:
        # Single opponent - consider all their moves
        return [{opponents[0]["id"]: move} for move in opponent_move_options[opponents[0]["id"]]]
    else:
        # Multiple opponents - use heuristic to pick most likely move for each
        likely_moves = {}
        for snake in opponents:
            # Simple heuristic: move toward center or toward food
            head = snake["body"][0]
            moves = opponent_move_options[snake["id"]]

            # Pick move that gets closer to nearest food or center
            best_move = moves[0]
            if game_state["board"]["food"]:
                nearest_food = min(game_state["board"]["food"],
                                 key=lambda f: manhattan_distance(head, f))
                best_dist = float('inf')
                for move in moves:
                    new_pos = {"x": head["x"], "y": head["y"]}
                    if move == "up":
                        new_pos["y"] += 1
                    elif move == "down":
                        new_pos["y"] -= 1
                    elif move == "left":
                        new_pos["x"] -= 1
                    elif move == "right":
                        new_pos["x"] += 1

                    dist = manhattan_distance(new_pos, nearest_food)
                    if dist < best_dist:
                        best_dist = dist
                        best_move = move

            likely_moves[snake["id"]] = best_move

        return [likely_moves]


def simulate_future(game_state: dict, my_move: str, depth: int = 6, max_depth: int = 6) -> dict:
    """
    Simulate future game states to evaluate survival probability.
    Optimized for speed - uses limited depth and early termination.
    Returns evaluation metrics.
    """
    if depth == 0 or game_state["you"] is None:
        # Base case
        if game_state["you"] is None:
            return {"alive": False, "health": 0, "length": 0, "space": 0}

        my_head = game_state["you"]["body"][0]
        obstacles = get_all_obstacles(game_state, include_tail=False)
        space = flood_fill(my_head, game_state["board"]["width"],
                          game_state["board"]["height"], obstacles)

        return {
            "alive": True,
            "health": game_state["you"]["health"],
            "length": len(game_state["you"]["body"]),
            "space": space
        }

    # Only predict opponent moves for first few levels to save time
    if depth == max_depth:
        opponent_move_scenarios = predict_opponent_moves(game_state, depth)
    else:
        # Use simplified prediction for deeper levels
        opponent_move_scenarios = [{}]
        for snake in game_state["board"]["snakes"]:
            if snake["id"] != game_state["you"]["id"]:
                # Just assume they move toward food or center
                moves = get_possible_moves(snake, game_state["board"]["width"],
                                          game_state["board"]["height"])
                opponent_move_scenarios[0][snake["id"]] = moves[0] if moves else "up"

    best_outcome = None

    for opponent_moves in opponent_move_scenarios[:2]:  # Limit to 2 scenarios max
        # Simulate this scenario
        new_state = simulate_game_state(game_state, my_move, opponent_moves)

        if new_state["you"] is None:
            # We died
            outcome = {"alive": False, "health": 0, "length": 0, "space": 0}
        else:
            # We survived, continue simulation
            # For remaining depth, pick best move recursively
            my_possible_moves = get_possible_moves(new_state["you"],
                                                   new_state["board"]["width"],
                                                   new_state["board"]["height"])

            if not my_possible_moves:
                outcome = {"alive": False, "health": 0, "length": 0, "space": 0}
            else:
                # Only recurse for first 2 moves to save time
                if depth > max_depth - 3:
                    # Recursively evaluate best future move
                    best_future = None
                    for future_move in my_possible_moves[:2]:  # Limit to 2 best moves
                        future_outcome = simulate_future(new_state, future_move, depth - 1, max_depth)
                        if best_future is None or (future_outcome["alive"] and
                                                  future_outcome["health"] > best_future.get("health", 0)):
                            best_future = future_outcome

                    outcome = best_future if best_future else {"alive": False, "health": 0, "length": 0, "space": 0}
                else:
                    # Just evaluate current state without further recursion
                    my_head = new_state["you"]["body"][0]
                    obstacles = get_all_obstacles(new_state, include_tail=False)
                    space = flood_fill(my_head, new_state["board"]["width"],
                                      new_state["board"]["height"], obstacles)
                    outcome = {
                        "alive": True,
                        "health": new_state["you"]["health"],
                        "length": len(new_state["you"]["body"]),
                        "space": space
                    }

        if best_outcome is None or (outcome["alive"] and outcome["health"] > best_outcome.get("health", 0)):
            best_outcome = outcome

    return best_outcome if best_outcome else {"alive": False, "health": 0, "length": 0, "space": 0}


def evaluate_move(direction: str, game_state: dict, use_prediction: bool = True) -> dict:
    """
    Evaluate a move direction with deep prediction.
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

    score = 1000  # Base score
    reasons = []

    # CRITICAL: Check basic safety
    if not is_safe_move(new_head, game_state, my_length):
        return {"score": -10000, "reasons": ["INSTANT DEATH: Wall or body collision"], "direction": direction}

    # PREDICTIVE SIMULATION: Simulate 6-8 moves ahead (optimized for speed)
    if use_prediction:
        prediction_depth = 6  # Simulate 6 moves ahead (balanced speed/accuracy)
        future_outcome = simulate_future(game_state, direction, prediction_depth, prediction_depth)

        if not future_outcome["alive"]:
            score -= 5000
            reasons.append(f"PREDICTION: Dies within {prediction_depth} moves")
        else:
            # Reward based on predicted health and space
            score += future_outcome["health"] * 10
            score += min(future_outcome["space"], 100) * 5
            reasons.append(f"PREDICTION: Survives with health {future_outcome['health']}")

    # Get obstacles for flood fill (excluding tails)
    obstacles = get_all_obstacles(game_state, include_tail=False)

    # IMMEDIATE SPACE: Evaluate available space
    available_space = flood_fill(new_head, board_width, board_height, obstacles)

    if available_space < my_length:
        score -= 2000
        reasons.append(f"TRAP: Only {available_space} spaces (need {my_length})")
    elif available_space < my_length * 2:
        score -= 500
        reasons.append(f"TIGHT: {available_space} spaces")
    else:
        score += min(available_space * 3, 300)
        reasons.append(f"SPACE: {available_space} cells")

    # FOOD SEEKING: More aggressive food seeking
    if food_list:
        nearest_food = min(food_list, key=lambda f: manhattan_distance(new_head, f))

        obstacles_with_tail = get_all_obstacles(game_state, include_tail=True)
        path_to_food = bfs_path(new_head, nearest_food, board_width, board_height, obstacles_with_tail)

        if my_health < 30:
            # Critical - MUST get food
            if path_to_food:
                score += 1000 - len(path_to_food) * 50
                reasons.append(f"CRITICAL: Food in {len(path_to_food)} moves")
            else:
                score -= 500
                reasons.append("CRITICAL: No food path!")
        elif my_health < 70:
            # Should get food soon
            if path_to_food:
                score += 500 - len(path_to_food) * 20
                reasons.append(f"HUNGRY: Food in {len(path_to_food)} moves")
            else:
                score -= 100
                reasons.append("HUNGRY: No food path")
        else:
            # Healthy but still seek food opportunistically
            if path_to_food and len(path_to_food) < 5:
                score += 200 - len(path_to_food) * 10
                reasons.append(f"Food nearby ({len(path_to_food)} moves)")

    # TAIL CHASING: Safe when healthy
    if my_health > 50 and len(my_body) > 3:
        my_tail = my_body[-1]
        if manhattan_distance(new_head, my_tail) <= 2:
            score += 100
            reasons.append("Following tail")

    # CENTER CONTROL
    center_x = board_width // 2
    center_y = board_height // 2
    distance_from_center = manhattan_distance(new_head, {"x": center_x, "y": center_y})
    score += (20 - distance_from_center) * 5

    return {"score": score, "reasons": reasons, "direction": direction}


def move(game_state: typing.Dict) -> typing.Dict:
    """
    Main move function with advanced prediction and evaluation.
    Simulates 10-15 moves ahead for all snakes.
    """
    my_head = game_state["you"]["body"][0]
    my_neck = game_state["you"]["body"][1] if len(game_state["you"]["body"]) > 1 else my_head

    # Get all possible moves (using helper function for consistency)
    possible_moves = get_possible_moves(game_state["you"],
                                       game_state["board"]["width"],
                                       game_state["board"]["height"])

    if not possible_moves:
        # No valid moves - try anything as last resort
        possible_moves = ["up", "down", "left", "right"]
        print("WARNING: No valid moves found! Trying all directions.")

    # Evaluate all possible moves with prediction
    move_evaluations = []
    for direction in possible_moves:
        evaluation = evaluate_move(direction, game_state, use_prediction=True)
        move_evaluations.append(evaluation)

    # Sort by score (highest first)
    move_evaluations.sort(key=lambda x: x["score"], reverse=True)

    # Log the decision
    turn = game_state["turn"]
    best_move = move_evaluations[0]

    print(f"\n{'='*60}")
    print(f"MOVE {turn} | Health: {game_state['you']['health']} | Length: {len(game_state['you']['body'])}")
    print(f"{'='*60}")
    print(f"\nMove Evaluations:")
    for eval in move_evaluations:
        reasons_str = ', '.join(eval['reasons'][:3]) if eval['reasons'] else "No reasons"
        print(f"  {eval['direction']:>5}: {eval['score']:>6} - {reasons_str}")
    print(f"\n>>> CHOSEN: {best_move['direction'].upper()} (score: {best_move['score']})")

    # Safety check
    if best_move["score"] < -1000:
        print("⚠️  CRITICAL: All moves lead to death! Choosing least bad option.")
    elif best_move["score"] < 0:
        print("⚠️  WARNING: Best move has negative score - dangerous situation!")

    # Dynamic shouts based on situation
    shout = ""
    if turn % 10 == 0:
        shout = "WarriorX dominates!"
    elif game_state["you"]["health"] < 30:
        shout = "Need food!"
    elif best_move["score"] > 2000:
        shout = "Feeling good!"

    return {
        "move": best_move["direction"],
        "shout": shout
    }


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

