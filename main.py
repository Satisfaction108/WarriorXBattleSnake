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
    """Check if a position is safe (no walls, no snake bodies, no head-to-head with larger snakes)"""
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Check walls
    if pos["x"] < 0 or pos["x"] >= board_width or pos["y"] < 0 or pos["y"] >= board_height:
        return False

    # Check snake bodies (excluding tails that will move)
    obstacles = get_all_obstacles(game_state, include_tail=False)
    if (pos["x"], pos["y"]) in obstacles:
        return False

    # EXTRA CHECK: Make sure we're not moving into our own body (even with tail excluded)
    my_body = game_state["you"]["body"]
    for i, segment in enumerate(my_body):
        # Skip the tail (it will move), but check all other segments
        if i == len(my_body) - 1:
            continue
        if coords_equal(pos, segment):
            return False

    # CRITICAL: Check head-to-head collision with larger/equal snakes
    if not avoid_head_collision(pos, game_state, my_length):
        return False

    return True


def avoid_head_collision(pos: dict, game_state: dict, my_length: int) -> bool:
    """
    Check if moving to pos could result in head-to-head collision with LARGER OR EQUAL snake.
    Returns True if safe, False if dangerous (instant death or mutual death).
    Blocks moves that would result in head-to-head with larger/equal snakes.
    """
    my_head = game_state["you"]["body"][0]

    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        opponent_head = snake["body"][0]
        opponent_length = len(snake["body"])

        # CRITICAL: Avoid head-to-head with LARGER OR EQUAL snakes
        # Equal length = both die = loss for us!
        if opponent_length < my_length:
            continue  # Only skip if we're BIGGER

        # Check if opponent could move to same position
        opponent_neighbors = get_neighbors(opponent_head,
                                          game_state["board"]["width"],
                                          game_state["board"]["height"])

        for opp_move in opponent_neighbors:
            # Direct head-to-head collision with LARGER/EQUAL snake = death!
            if coords_equal(pos, opp_move):
                return False  # Dangerous - opponent is bigger or equal

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
        "color": "#1a1a1a",  # PURE BLACK - Ultimate menace and fear
        "head": "dead",      # SKULL HEAD - Death incarnate 💀
        "tail": "bolt",      # LIGHTNING BOLT - Unstoppable power ⚡
    }


# ============================================================================
# GAME LIFECYCLE FUNCTIONS
# ============================================================================

def start(game_state: typing.Dict):
    """Called when game starts"""
    global recent_moves
    recent_moves = []  # Reset move history for new game
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
# VORONOI SPACE CONTROL - Calculate which areas each snake controls
# ============================================================================

def calculate_voronoi_space(game_state: dict) -> dict:
    """
    Calculate Voronoi space control for each snake.
    Returns dict mapping snake_id to number of cells they control.
    A cell is controlled by the snake that can reach it first.
    """
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    snakes = game_state["board"]["snakes"]

    if not snakes:
        return {}

    # Map each cell to (distance, snake_id) - which snake can reach it fastest
    cell_ownership = {}

    for snake in snakes:
        head = snake["body"][0]
        # BFS from each snake's head
        queue = deque([(head, 0)])
        visited = {(head["x"], head["y"])}

        while queue:
            pos, dist = queue.popleft()
            cell_key = (pos["x"], pos["y"])

            # Claim cell if we're first or tied (but we'll count ties as shared)
            if cell_key not in cell_ownership or dist < cell_ownership[cell_key][0]:
                cell_ownership[cell_key] = (dist, snake["id"])
            elif dist == cell_ownership[cell_key][0]:
                # Tie - mark as contested
                cell_ownership[cell_key] = (dist, "contested")

            # Explore neighbors
            for neighbor in get_neighbors(pos, board_width, board_height):
                neighbor_key = (neighbor["x"], neighbor["y"])
                if neighbor_key not in visited:
                    visited.add(neighbor_key)
                    queue.append((neighbor, dist + 1))

    # Count cells controlled by each snake
    control_count = {snake["id"]: 0 for snake in snakes}
    for (dist, owner) in cell_ownership.values():
        if owner != "contested" and owner in control_count:
            control_count[owner] += 1

    return control_count


def calculate_area_control_score(game_state: dict, my_id: str) -> float:
    """
    Calculate our area control advantage.
    Returns positive if we control more space, negative if opponents do.
    """
    control = calculate_voronoi_space(game_state)
    if not control:
        return 0.0

    my_control = control.get(my_id, 0)
    total_control = sum(control.values())

    if total_control == 0:
        return 0.0

    # Return our percentage of total control (0.0 to 1.0)
    return my_control / total_control


def should_play_aggressive(game_state: dict) -> bool:
    """
    Determine if we should play aggressively or defensively.
    Aggressive: We're bigger than average, high health, control more space
    Defensive: We're smaller, low health, less space control
    """
    my_snake = game_state["you"]
    my_length = len(my_snake["body"])
    my_health = my_snake["health"]

    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != my_snake["id"]]

    if not opponents:
        return True  # No opponents, play aggressive

    avg_opponent_length = sum(len(s["body"]) for s in opponents) / len(opponents)

    # Calculate area control
    area_control = calculate_area_control_score(game_state, my_snake["id"])

    # Aggressive if:
    # - We're bigger than average
    # - We have good health (>50)
    # - We control more than 40% of space
    is_bigger = my_length > avg_opponent_length
    is_healthy = my_health > 50
    controls_space = area_control > 0.4

    return is_bigger and (is_healthy or controls_space)


def prioritize_food(game_state: dict, position: dict) -> tuple:
    """
    Smart food prioritization.
    Returns (should_seek_food, best_food, urgency_score).
    """
    my_snake = game_state["you"]
    my_health = my_snake["health"]
    my_length = len(my_snake["body"])
    food_list = game_state["board"]["food"]

    if not food_list:
        return (False, None, 0)

    # Calculate urgency based on health
    if my_health < 15:
        urgency = 10  # CRITICAL
    elif my_health < 30:
        urgency = 7   # HIGH
    elif my_health < 50:
        urgency = 4   # MEDIUM
    elif my_health < 70:
        urgency = 2   # LOW
    else:
        urgency = 0   # Not urgent

    # Find nearest food
    obstacles = get_all_obstacles(game_state, include_tail=False)
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    best_food = None
    best_score = float('inf')

    for food in food_list:
        # Calculate actual path distance (not just Manhattan)
        path_dist = bfs_distance(position, food, board_width, board_height, obstacles)

        if path_dist == -1:
            continue  # Unreachable

        # Check if any opponent is closer to this food
        opponent_threat = 0
        for snake in game_state["board"]["snakes"]:
            if snake["id"] == my_snake["id"]:
                continue

            opp_dist = manhattan_distance(snake["body"][0], food)
            if opp_dist < path_dist:
                opponent_threat += 1  # Opponent is closer

        # Score: prefer closer food with less opponent threat
        food_score = path_dist * 10 + opponent_threat * 5

        if food_score < best_score:
            best_score = food_score
            best_food = food

    should_seek = urgency > 3 or (urgency > 0 and best_food is not None)

    return (should_seek, best_food, urgency)


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


def evaluate_game_state(game_state: dict, my_id: str) -> float:
    """
    Comprehensive evaluation of a game state.
    Returns a score where higher is better for us.
    """
    if game_state["you"] is None:
        return -1000000.0  # We're dead

    my_snake = game_state["you"]
    my_head = my_snake["body"][0]
    my_health = my_snake["health"]
    my_length = len(my_snake["body"])

    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Calculate available space
    obstacles = get_all_obstacles(game_state, include_tail=False)
    my_space = flood_fill(my_head, board_width, board_height, obstacles)

    # Calculate Voronoi control
    area_control = calculate_area_control_score(game_state, my_id)

    # Count opponents
    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != my_id]
    num_opponents = len(opponents)

    # Calculate relative size advantage
    size_advantage = 0.0
    if opponents:
        avg_opponent_length = sum(len(s["body"]) for s in opponents) / len(opponents)
        size_advantage = my_length - avg_opponent_length

    # Distance to nearest food
    food_score = 0.0
    if game_state["board"]["food"] and my_health < 70:
        nearest_food = min(game_state["board"]["food"],
                          key=lambda f: manhattan_distance(my_head, f))
        food_dist = manhattan_distance(my_head, nearest_food)
        food_score = max(0, 20 - food_dist)  # Closer food = higher score

    # Combine all factors
    score = (
        my_health * 10.0 +           # Health is important
        my_space * 5.0 +              # Space is critical
        my_length * 100.0 +           # Length gives advantage
        area_control * 1000.0 +       # Voronoi control is very important
        size_advantage * 50.0 +       # Being bigger is good
        food_score * 5.0 +            # Food when hungry
        -num_opponents * 50.0         # Fewer opponents is better
    )

    return score


def minimax_alpha_beta(game_state: dict, my_id: str, depth: int, alpha: float, beta: float,
                       maximizing: bool, my_move: str = None) -> tuple:
    """
    Minimax with alpha-beta pruning.
    Returns (score, best_move).
    """
    # Base case: max depth or game over
    if depth == 0 or game_state["you"] is None:
        return (evaluate_game_state(game_state, my_id), my_move)

    # Get our possible moves
    if game_state["you"] is None:
        return (-1000000.0, None)

    my_possible_moves = get_possible_moves(game_state["you"],
                                           game_state["board"]["width"],
                                           game_state["board"]["height"])

    if not my_possible_moves:
        return (-1000000.0, None)

    if maximizing:
        max_eval = float('-inf')
        best_move = my_possible_moves[0]

        for move in my_possible_moves:
            # Predict opponent moves (use heuristic for speed)
            opponent_moves = {}
            for snake in game_state["board"]["snakes"]:
                if snake["id"] == my_id:
                    continue
                snake_moves = get_possible_moves(snake, game_state["board"]["width"],
                                                game_state["board"]["height"])
                if snake_moves:
                    # Assume opponent moves toward food or center
                    opponent_moves[snake["id"]] = snake_moves[0]

            # Simulate
            new_state = simulate_game_state(game_state, move, opponent_moves)

            # Recurse
            eval_score, _ = minimax_alpha_beta(new_state, my_id, depth - 1, alpha, beta, False, move)

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff

        return (max_eval, best_move)
    else:
        # Minimizing (opponent's turn - but we simplify by just evaluating)
        # In real minimax, opponents would minimize our score
        # For speed, we just continue with our perspective
        return minimax_alpha_beta(game_state, my_id, depth - 1, alpha, beta, True, my_move)


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
        # Check specifically what's wrong
        if new_head["x"] < 0 or new_head["x"] >= board_width or new_head["y"] < 0 or new_head["y"] >= board_height:
            return {"score": -10000, "reasons": [f"INSTANT DEATH: WALL at ({new_head['x']}, {new_head['y']})"], "direction": direction}
        else:
            return {"score": -10000, "reasons": ["INSTANT DEATH: Body collision"], "direction": direction}

    # PREDICTIVE SIMULATION: Use minimax with alpha-beta pruning
    if use_prediction:
        # Adaptive depth: deeper search in critical situations
        num_opponents = len([s for s in game_state["board"]["snakes"] if s["id"] != game_state["you"]["id"]])

        if my_health < 20 or num_opponents == 1:
            prediction_depth = 8  # Deeper search when critical or 1v1
        elif num_opponents <= 2:
            prediction_depth = 7  # Medium depth for few opponents
        else:
            prediction_depth = 6  # Standard depth for many opponents

        # Simulate this move first with smart opponent prediction
        opponent_moves = {}
        for snake in game_state["board"]["snakes"]:
            if snake["id"] == game_state["you"]["id"]:
                continue
            snake_moves = get_possible_moves(snake, board_width, board_height)
            if snake_moves:
                # Predict opponent's most likely move (toward food or toward us)
                best_opp_move = snake_moves[0]
                if food_list and snake["health"] < 70:
                    # Opponent likely going for food
                    nearest_food = min(food_list, key=lambda f: manhattan_distance(snake["body"][0], f))
                    best_dist = float('inf')
                    for move in snake_moves:
                        test_pos = {"x": snake["body"][0]["x"], "y": snake["body"][0]["y"]}
                        if move == "up":
                            test_pos["y"] += 1
                        elif move == "down":
                            test_pos["y"] -= 1
                        elif move == "left":
                            test_pos["x"] -= 1
                        elif move == "right":
                            test_pos["x"] += 1
                        dist = manhattan_distance(test_pos, nearest_food)
                        if dist < best_dist:
                            best_dist = dist
                            best_opp_move = move
                opponent_moves[snake["id"]] = best_opp_move

        test_state = simulate_game_state(game_state, direction, opponent_moves)

        if test_state["you"] is None:
            # We die immediately
            score -= 15000
            reasons.append(f"💀💀💀 IMMEDIATE DEATH! (-15000)")
        else:
            # Run minimax from this position
            future_score, _ = minimax_alpha_beta(test_state, game_state["you"]["id"],
                                                prediction_depth, float('-inf'), float('inf'), True, direction)

            if future_score < -500000:
                score -= 15000
                reasons.append(f"💀💀💀 MINIMAX: DEATH predicted! (-15000)")
            else:
                prediction_bonus = min(int(future_score // 10), 3000)
                score += prediction_bonus
                reasons.append(f"✓ MINIMAX(d={prediction_depth}): Score {int(future_score)} (+{prediction_bonus})")

    # Get obstacles for flood fill (excluding tails)
    obstacles = get_all_obstacles(game_state, include_tail=False)

    # IMMEDIATE SPACE: Evaluate available space - BE CONSERVATIVE!
    available_space = flood_fill(new_head, board_width, board_height, obstacles)

    # Need MORE space than just our length to be safe
    safe_space_needed = my_length * 3  # Conservative: need 3x our length

    if available_space < my_length:
        # DEATH TRAP - not enough space to even fit!
        score -= 5000
        reasons.append(f"🚫 DEATH TRAP: Only {available_space} spaces (need {my_length})")
    elif available_space < my_length * 2:
        # Very tight - dangerous!
        score -= 2000
        reasons.append(f"⚠️  VERY TIGHT: {available_space} spaces (risky!)")
    elif available_space < safe_space_needed:
        # Somewhat tight - be careful
        score -= 800
        reasons.append(f"⚠️  TIGHT: {available_space} spaces (need {safe_space_needed})")
    else:
        # Good space - reward it
        score += min(available_space * 5, 500)
        reasons.append(f"✓ SPACE: {available_space} cells")

    # FUTURE MOBILITY: Check if we'll have escape routes after this move
    # Count how many safe moves we'll have from the new position
    future_safe_moves = 0
    for future_dir in ["up", "down", "left", "right"]:
        # Calculate future position
        future_pos = {"x": new_head["x"], "y": new_head["y"]}
        if future_dir == "up":
            future_pos["y"] += 1
        elif future_dir == "down":
            future_pos["y"] -= 1
        elif future_dir == "left":
            future_pos["x"] -= 1
        elif future_dir == "right":
            future_pos["x"] += 1

        if is_safe_move(future_pos, game_state, my_length):
            future_safe_moves += 1

    if future_safe_moves == 0:
        # NO ESCAPE ROUTES - this is a trap!
        score -= 6000
        reasons.append(f"🚫 TRAP: No escape routes! (-6000)")
    elif future_safe_moves == 1:
        # Only one escape route - very risky!
        score -= 2500
        reasons.append(f"⚠️  RISKY: Only 1 escape route (-2500)")
    elif future_safe_moves == 2:
        # Two escape routes - okay but not great
        score -= 500
        reasons.append(f"⚠️  Limited: 2 escape routes (-500)")
    else:
        # Multiple escape routes - good!
        score += 300
        reasons.append(f"✓ SAFE: {future_safe_moves} escape routes (+300)")

    # EDGE AWARENESS: Avoid getting trapped against walls, especially when opponents are nearby
    distance_to_left_wall = new_head["x"]
    distance_to_right_wall = board_width - 1 - new_head["x"]
    distance_to_bottom_wall = new_head["y"]
    distance_to_top_wall = board_height - 1 - new_head["y"]

    min_distance_to_wall = min(distance_to_left_wall, distance_to_right_wall,
                                distance_to_bottom_wall, distance_to_top_wall)

    # Check if any opponents are nearby (within 5 spaces)
    opponents_nearby = False
    closest_opponent_distance = float('inf')
    for snake in game_state["board"]["snakes"]:
        if snake["id"] != game_state["you"]["id"]:
            opponent_head = snake["body"][0]
            dist = manhattan_distance(new_head, opponent_head)
            closest_opponent_distance = min(closest_opponent_distance, dist)
            if dist <= 5:
                opponents_nearby = True
                break

    # Penalize being near walls when opponents are nearby
    if opponents_nearby:
        if min_distance_to_wall == 0:
            # Right against the wall with opponents nearby = VERY DANGEROUS
            score -= 3000
            reasons.append(f"🚫 WALL TRAP: Against wall with opponents nearby! (-3000)")
        elif min_distance_to_wall == 1:
            # One space from wall with opponents nearby = dangerous
            score -= 1500
            reasons.append(f"⚠️  WALL DANGER: 1 space from wall, opponents close (-1500)")
        elif min_distance_to_wall == 2:
            # Two spaces from wall with opponents nearby = risky
            score -= 800
            reasons.append(f"⚠️  Near wall with opponents close (-800)")

    # Check for corner positions (even more dangerous)
    in_corner = (distance_to_left_wall <= 1 and distance_to_bottom_wall <= 1) or \
                (distance_to_left_wall <= 1 and distance_to_top_wall <= 1) or \
                (distance_to_right_wall <= 1 and distance_to_bottom_wall <= 1) or \
                (distance_to_right_wall <= 1 and distance_to_top_wall <= 1)

    if in_corner:
        if opponents_nearby:
            score -= 4000
            reasons.append(f"🚫🚫 CORNER TRAP: In corner with opponents! (-4000)")
        else:
            score -= 1000
            reasons.append(f"⚠️  In corner (-1000)")

    # OPPONENT PROXIMITY: Avoid getting boxed in by other snakes
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        opponent_head = snake["body"][0]
        opponent_length = len(snake["body"])
        distance_to_opponent = manhattan_distance(new_head, opponent_head)

        # Check for potential head-to-head collision
        opponent_neighbors = get_neighbors(opponent_head, board_width, board_height)
        potential_head_to_head = any(coords_equal(new_head, opp_pos) for opp_pos in opponent_neighbors)

        if potential_head_to_head:
            if opponent_length > my_length:
                # Already blocked by avoid_head_collision in is_safe_move
                pass
            elif opponent_length == my_length:
                # Equal length - risky but not instant death
                score -= 3000
                reasons.append(f"💀 HEAD-TO-HEAD RISK: Equal length! (-3000)")
            else:
                # We're bigger - still risky but less penalty
                score -= 1000
                reasons.append(f"⚠️  Head-to-head with smaller snake (-1000)")

        # Penalize being too close to larger/equal snakes
        if opponent_length >= my_length:
            if distance_to_opponent == 1:
                penalty = 2000
                score -= penalty
                reasons.append(f"🚫 VERY CLOSE to larger/equal snake! (-{penalty})")
            elif distance_to_opponent == 2:
                penalty = 1000
                score -= penalty
                reasons.append(f"⚠️  CLOSE to larger/equal snake! (-{penalty})")
            elif distance_to_opponent <= 3:
                penalty = 400
                score -= penalty
                reasons.append(f"⚠️  Near larger/equal snake (-{penalty})")

        # Check if we're moving adjacent to opponent body segments
        for segment in snake["body"][:5]:  # Check first 5 segments
            if manhattan_distance(new_head, segment) == 1:
                score -= 2000
                reasons.append(f"🚫 DANGER: Adjacent to opponent body! (-2000)")
                break

    # FOOD SEEKING: Smart prioritization based on game state
    should_seek, best_food, urgency = prioritize_food(game_state, new_head)

    if food_list:
        # Check if we're moving ONTO food (this move eats it!)
        eating_food = False
        for food in food_list:
            if coords_equal(new_head, food):
                eating_food = True
                break

        if eating_food:
            # EATING FOOD THIS TURN = MASSIVE BONUS!
            # Scale bonus based on urgency
            food_bonus = 10000 + (urgency * 1000)
            score += food_bonus
            reasons.append(f"🍎🍎🍎 EATING FOOD NOW! Urgency:{urgency} (+{food_bonus})")
        elif should_seek and best_food:
            # Seeking food based on smart prioritization
            obstacles_with_tail = get_all_obstacles(game_state, include_tail=True)
            path_to_food = bfs_path(new_head, best_food, board_width, board_height, obstacles_with_tail)

            if path_to_food:
                # Calculate bonus based on urgency and distance
                base_bonus = urgency * 500
                distance_penalty = len(path_to_food) * 50
                food_bonus = max(base_bonus - distance_penalty, 100)
                score += food_bonus
                reasons.append(f"🍎 FOOD SEEK: {len(path_to_food)} moves, urgency:{urgency} (+{food_bonus})")
            else:
                # No path to prioritized food
                if urgency > 7:
                    score -= 3000
                    reasons.append("💀 CRITICAL: No food path!")
                elif urgency > 3:
                    score -= 1000
                    reasons.append("⚠️  URGENT: No food path!")

    # TAIL CHASING: Safe when healthy
    if my_health > 50 and len(my_body) > 3:
        my_tail = my_body[-1]
        if manhattan_distance(new_head, my_tail) <= 2:
            score += 100
            reasons.append("Following tail")

    # AGGRESSIVE/DEFENSIVE MODE
    is_aggressive = should_play_aggressive(game_state)

    if is_aggressive:
        # Aggressive mode: seek center, cut off opponents
        center_x = board_width // 2
        center_y = board_height // 2
        center = {"x": center_x, "y": center_y}
        dist_to_center = manhattan_distance(new_head, center)

        # Reward moving toward center
        if dist_to_center < manhattan_distance(my_head, center):
            score += 200
            reasons.append("⚔️  AGGRESSIVE: Moving to center (+200)")

        # Reward cutting off opponents
        for snake in game_state["board"]["snakes"]:
            if snake["id"] == game_state["you"]["id"]:
                continue

            opp_head = snake["body"][0]
            # If we're between opponent and food, bonus
            if food_list:
                nearest_food = min(food_list, key=lambda f: manhattan_distance(opp_head, f))
                our_dist_to_food = manhattan_distance(new_head, nearest_food)
                opp_dist_to_food = manhattan_distance(opp_head, nearest_food)

                if our_dist_to_food < opp_dist_to_food:
                    score += 150
                    reasons.append("⚔️  AGGRESSIVE: Cutting off opponent food (+150)")
                    break
    else:
        # Defensive mode: maximize space, avoid opponents
        score += available_space * 2  # Extra space bonus
        reasons.append(f"🛡️  DEFENSIVE: Space priority (+{available_space * 2})")

    # CENTER CONTROL (reduced to avoid predictable movement patterns)
    center_x = board_width // 2
    center_y = board_height // 2
    distance_from_center = manhattan_distance(new_head, {"x": center_x, "y": center_y})
    # Reduced from *5 to *2 to make movement less predictable
    score += (20 - distance_from_center) * 2

    return {"score": score, "reasons": reasons, "direction": direction}


# Global variable to track recent moves (for anti-pattern detection)
recent_moves = []

def move(game_state: typing.Dict) -> typing.Dict:
    """
    Main move function with advanced prediction and evaluation.
    Uses minimax search with 20-move lookahead.
    """
    global recent_moves

    # Get all possible moves (using helper function for consistency)
    my_head = game_state["you"]["body"][0]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    print(f"\n📍 Current Position: ({my_head['x']}, {my_head['y']}) on {board_width}x{board_height} board")
    print(f"   Walls at: x={board_width}, y={board_height}")

    possible_moves = get_possible_moves(game_state["you"], board_width, board_height)

    print(f"   Possible moves (wall-filtered): {possible_moves}")

    if not possible_moves:
        # No valid moves - try anything as last resort
        possible_moves = ["up", "down", "left", "right"]
        print("⚠️  WARNING: No valid moves found! Trying all directions as last resort.")

    # Evaluate all possible moves with prediction
    move_evaluations = []
    for direction in possible_moves:
        evaluation = evaluate_move(direction, game_state, use_prediction=True)

        # ANTI-PATTERN: Penalize repeating the same direction too many times
        if len(recent_moves) >= 3:
            last_3_moves = recent_moves[-3:]
            if last_3_moves.count(direction) >= 2:
                # Penalize if this direction was used 2+ times in last 3 moves
                pattern_penalty = -200
                evaluation["score"] += pattern_penalty
                evaluation["reasons"].append(f"⚠️  PATTERN: Repeated {direction} too much ({pattern_penalty})")

        move_evaluations.append(evaluation)

    # Sort by score (highest first)
    move_evaluations.sort(key=lambda x: x["score"], reverse=True)

    # ANTI-PREDICTABILITY: If top moves have similar scores, randomize to avoid patterns
    import random
    best_score = move_evaluations[0]["score"]
    similar_moves = [m for m in move_evaluations if abs(m["score"] - best_score) < 50]

    if len(similar_moves) > 1:
        print(f"🎲 Multiple good moves (within 50 points): {[m['direction'] for m in similar_moves]}")
        best_move = random.choice(similar_moves)
        print(f"   Randomly chose: {best_move['direction'].upper()}")
    else:
        best_move = move_evaluations[0]

    # Log the decision
    turn = game_state["turn"]

    # DESPERATION MODE: If all moves are terrible, try to find the one that survives longest
    if best_move["score"] <= -5000:
        print("⚠️  DESPERATION MODE: All moves look fatal! Finding longest survival...")

        # Re-evaluate each move focusing purely on survival time
        survival_evaluations = []
        for direction in ["up", "down", "left", "right"]:
            my_head = game_state["you"]["body"][0]
            new_head = {"x": my_head["x"], "y": my_head["y"]}
            if direction == "up":
                new_head["y"] += 1
            elif direction == "down":
                new_head["y"] -= 1
            elif direction == "left":
                new_head["x"] -= 1
            elif direction == "right":
                new_head["x"] += 1

            # Check basic validity (walls)
            board_width = game_state["board"]["width"]
            board_height = game_state["board"]["height"]
            if (new_head["x"] < 0 or new_head["x"] >= board_width or
                new_head["y"] < 0 or new_head["y"] >= board_height):
                survival_score = -100000  # Wall = definitely bad
            else:
                # Use minimax to evaluate survival time
                opponent_moves = {}
                for snake in game_state["board"]["snakes"]:
                    if snake["id"] == game_state["you"]["id"]:
                        continue
                    snake_moves = get_possible_moves(snake, game_state["board"]["width"],
                                                    game_state["board"]["height"])
                    if snake_moves:
                        opponent_moves[snake["id"]] = snake_moves[0]

                test_state = simulate_game_state(game_state, direction, opponent_moves)
                if test_state["you"] is not None:
                    future_score, _ = minimax_alpha_beta(test_state, game_state["you"]["id"],
                                                        6, float('-inf'), float('inf'), True, direction)
                    survival_score = 50000 + int(future_score)
                else:
                    survival_score = -50000

            survival_evaluations.append({
                "direction": direction,
                "score": survival_score,
                "reasons": [f"Survival score: {survival_score}"]
            })

        # Pick the move with best survival
        survival_evaluations.sort(key=lambda x: x["score"], reverse=True)
        best_move = survival_evaluations[0]
        print(f"   Desperation choice: {best_move['direction'].upper()} (survival: {best_move['score']})")

    print(f"\n{'='*60}")
    print(f"MOVE {turn} | Health: {game_state['you']['health']} | Length: {len(game_state['you']['body'])}")
    print(f"{'='*60}")
    print(f"\nMove Evaluations:")
    for eval in move_evaluations:
        reasons_str = ', '.join(eval['reasons'][:3]) if eval['reasons'] else "No reasons"
        print(f"  {eval['direction']:>5}: {eval['score']:>6} - {reasons_str}")
    print(f"\n>>> CHOSEN: {best_move['direction'].upper()} (score: {best_move['score']})")

    # FINAL SAFETY CHECK: Verify the chosen move won't cause immediate death
    chosen_direction = best_move["direction"]
    my_head = game_state["you"]["body"][0]
    my_length = len(game_state["you"]["body"])
    final_board_width = game_state["board"]["width"]
    final_board_height = game_state["board"]["height"]

    print(f"\n🎯 FINAL DECISION: {chosen_direction.upper()}")
    print(f"   From: ({my_head['x']}, {my_head['y']})")

    final_head = {"x": my_head["x"], "y": my_head["y"]}
    if chosen_direction == "up":
        final_head["y"] += 1
    elif chosen_direction == "down":
        final_head["y"] -= 1
    elif chosen_direction == "left":
        final_head["x"] -= 1
    elif chosen_direction == "right":
        final_head["x"] += 1

    print(f"   To: ({final_head['x']}, {final_head['y']})")

    # Check if this would go out of bounds - CRITICAL SAFETY CHECK
    if final_head["x"] < 0 or final_head["x"] >= final_board_width or final_head["y"] < 0 or final_head["y"] >= final_board_height:
        print(f"🚨🚨🚨 CRITICAL BUG: Chosen move {chosen_direction.upper()} would go OUT OF BOUNDS!")
        print(f"   Head: ({my_head['x']}, {my_head['y']}) -> ({final_head['x']}, {final_head['y']})")
        print(f"   Board: {final_board_width}x{final_board_height}")
        print(f"   THIS SHOULD NEVER HAPPEN!")

    # Double-check this move is actually safe
    if not is_safe_move(final_head, game_state, my_length):
        print(f"🚨 SAFETY OVERRIDE: {chosen_direction.upper()} is NOT SAFE!")
        print(f"   Attempting to move from ({my_head['x']}, {my_head['y']}) to ({final_head['x']}, {final_head['y']})")

        # Find first actually safe move
        safe_found = False
        for alt_direction in ["up", "down", "left", "right"]:
            alt_head = {"x": my_head["x"], "y": my_head["y"]}
            if alt_direction == "up":
                alt_head["y"] += 1
            elif alt_direction == "down":
                alt_head["y"] -= 1
            elif alt_direction == "left":
                alt_head["x"] -= 1
            elif alt_direction == "right":
                alt_head["x"] += 1

            if is_safe_move(alt_head, game_state, my_length):
                print(f"   ✅ Safety override: Choosing {alt_direction.upper()} instead -> ({alt_head['x']}, {alt_head['y']})")
                chosen_direction = alt_direction
                safe_found = True
                break

        if not safe_found:
            print(f"   💀 NO SAFE MOVES FOUND! Will die this turn.")
    else:
        print(f"   ✅ Move is safe!")

    print(f"\n>>> FINAL MOVE: {chosen_direction.upper()} <<<\n")
    print("=" * 60)

    # Safety check
    if best_move["score"] < -1000:
        print("⚠️  CRITICAL: All moves lead to death! Choosing least bad option.")
    elif best_move["score"] < 0:
        print("⚠️  WARNING: Best move has negative score - dangerous situation!")

    # Track recent moves for pattern detection (keep last 5 moves)
    recent_moves.append(chosen_direction)
    if len(recent_moves) > 5:
        recent_moves.pop(0)

    # Dynamic shouts based on situation
    shout = ""
    if turn % 10 == 0:
        shout = "WarriorX dominates!"
    elif game_state["you"]["health"] < 30:
        shout = "Need food!"
    elif best_move["score"] > 2000:
        shout = "Feeling good!"

    response = {
        "move": chosen_direction,
        "shout": shout
    }

    # CRITICAL: Log the exact JSON response being returned
    import json
    print(f"\n🚀 RETURNING JSON RESPONSE: {json.dumps(response)}")
    print(f"🚀 MOVE BEING SENT TO GAME: {chosen_direction.upper()}\n")

    return response


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

