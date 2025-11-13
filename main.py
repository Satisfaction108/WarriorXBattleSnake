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
from itertools import product

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


def validate_path_safety(path_directions: list, start_pos: dict, game_state: dict,
                         min_escape_routes: int = 2, min_space: typing.Optional[int] = None) -> tuple:
    """
    Validates if following a path maintains safety at each step.
    Returns (is_safe, first_unsafe_step, reason).

    Args:
        path_directions: List of directions to follow
        start_pos: Starting position
        game_state: Current game state
        min_escape_routes: Minimum number of escape routes required at each step
        min_space: Minimum flood fill space required at each step (defaults to snake length * 2)

    Returns:
        (True, -1, "") if path is safe
        (False, step_number, reason) if path becomes unsafe
    """
    if not path_directions:
        return (True, -1, "")

    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    my_length = len(game_state["you"]["body"])

    if min_space is None:
        min_space = my_length * 2

    # Simulate following the path
    current_pos = {"x": start_pos["x"], "y": start_pos["y"]}

    for step, direction in enumerate(path_directions):
        # Move to next position
        if direction == "up":
            current_pos["y"] += 1
        elif direction == "down":
            current_pos["y"] -= 1
        elif direction == "left":
            current_pos["x"] -= 1
        elif direction == "right":
            current_pos["x"] += 1

        # Check escape routes from this position
        escape_count = 0
        for test_dir in ["up", "down", "left", "right"]:
            test_pos = {"x": current_pos["x"], "y": current_pos["y"]}
            if test_dir == "up":
                test_pos["y"] += 1
            elif test_dir == "down":
                test_pos["y"] -= 1
            elif test_dir == "left":
                test_pos["x"] -= 1
            elif test_dir == "right":
                test_pos["x"] += 1

            if is_safe_move(test_pos, game_state, my_length):
                escape_count += 1

        if escape_count < min_escape_routes:
            return (False, step, f"Only {escape_count} escape routes at step {step}")

        # Check available space from this position
        obstacles = get_all_obstacles(game_state, include_tail=False)
        available_space = flood_fill(current_pos, board_width, board_height, obstacles)

        if available_space < min_space:
            return (False, step, f"Only {available_space} space at step {step} (need {min_space})")

    return (True, -1, "")


def detect_dead_end(position: dict, game_state: dict, max_depth: int = 5) -> tuple:
    """
    Detects if a position leads to a dead end within max_depth moves.
    Uses recursive exploration to find if all paths from this position lead to traps.

    Returns (is_dead_end, depth_to_trap, escape_routes_at_trap).
    """
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    my_length = len(game_state["you"]["body"])
    obstacles = get_all_obstacles(game_state, include_tail=False)

    def explore(pos: dict, depth: int, visited: set) -> tuple:
        """Recursively explore from position. Returns (min_escape_routes, depth_found)."""
        if depth >= max_depth:
            return (4, depth)  # Assume safe if we can survive max_depth moves

        pos_tuple = (pos["x"], pos["y"])
        if pos_tuple in visited:
            return (4, depth)  # Already explored, assume safe

        visited.add(pos_tuple)

        # Count safe moves from this position
        safe_moves = []
        for direction in ["up", "down", "left", "right"]:
            next_pos = {"x": pos["x"], "y": pos["y"]}
            if direction == "up":
                next_pos["y"] += 1
            elif direction == "down":
                next_pos["y"] -= 1
            elif direction == "left":
                next_pos["x"] -= 1
            elif direction == "right":
                next_pos["x"] += 1

            if is_safe_move(next_pos, game_state, my_length):
                safe_moves.append(next_pos)

        if len(safe_moves) == 0:
            return (0, depth)  # Dead end found!
        elif len(safe_moves) == 1:
            return (1, depth)  # Only one escape - very dangerous

        # Recursively check all safe moves
        min_future_escapes = 4
        min_depth = max_depth
        for next_pos in safe_moves:
            future_escapes, future_depth = explore(next_pos, depth + 1, visited.copy())
            if future_escapes < min_future_escapes:
                min_future_escapes = future_escapes
                min_depth = future_depth

        return (min_future_escapes, min_depth)

    min_escapes, depth_found = explore(position, 0, set())
    is_dead_end = min_escapes == 0

    return (is_dead_end, depth_found, min_escapes)


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


def get_opponent_threat_tiles(game_state: dict, my_length: int) -> tuple:
    """
    Build threat map of tiles that opponents can reach in one move.
    Returns (threat_tiles, pursue_tiles):
    - threat_tiles: set of (x,y) dangerous to move into (larger/equal opponents)
    - pursue_tiles: set of (x,y) we should pursue (smaller opponents we can dominate)
    """
    threat_tiles = set()
    pursue_tiles = set()
    
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue
        
        opponent_head = snake["body"][0]
        opponent_length = len(snake["body"])
        
        # Get all tiles opponent could move to
        opponent_neighbors = get_neighbors(opponent_head,
                                          game_state["board"]["width"],
                                          game_state["board"]["height"])
        
        for neighbor in opponent_neighbors:
            tile = (neighbor["x"], neighbor["y"])
            
            if opponent_length >= my_length:
                # Opponent is bigger or equal - this tile is dangerous
                threat_tiles.add(tile)
            else:
                # Opponent is smaller - we can pursue them!
                pursue_tiles.add(tile)
    
    return (threat_tiles, pursue_tiles)


# ============================================================================
# SNAKE APPEARANCE
# ============================================================================

def info() -> typing.Dict:
    """Battlesnake appearance and metadata"""
    print("INFO")

    return {
        "apiversion": "1",
        "author": "WarriorX",
        "color": "#FF6600",      # TIGER ORANGE - Bold and fierce 🐯
        "head": "tiger-king",    # TIGER KING HEAD - Majestic predator 👑�
        "tail": "tiger-tail",    # TIGER TAIL - Powerful and sleek 🐅
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
                    neighbor_pos = {"x": neighbor["x"], "y": neighbor["y"]}
                    queue.append((neighbor_pos, dist + 1))

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
    Advanced food prioritization with opportunistic eating.
    Returns (should_seek_food, best_food, urgency_score, food_value_score).
    
    Now considers:
    - Health urgency
    - Size advantage (grow to dominate)
    - Safety of eating (escape space after eating)
    - Opponent competition
    - Travel cost vs benefit
    """
    my_snake = game_state["you"]
    my_health = my_snake["health"]
    my_length = len(my_snake["body"])
    food_list = game_state["board"]["food"]

    if not food_list:
        return (False, None, 0, 0)

    # Calculate urgency based on health - EXTREMELY AGGRESSIVE THRESHOLDS
    # Always seek food to grow fast like top players
    if my_health < 15:
        urgency = 10  # CRITICAL - will die very soon
    elif my_health < 30:
        urgency = 8   # VERY HIGH - need food urgently
    elif my_health < 50:
        urgency = 6   # HIGH - should seek food
    elif my_health < 70:
        urgency = 5   # MEDIUM-HIGH - actively seek food
    elif my_health < 90:
        urgency = 4   # MEDIUM - seek food to grow
    else:
        urgency = 3   # Even at full health, seek food to grow!

    # Calculate size advantage/disadvantage
    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != my_snake["id"]]
    if opponents:
        max_opponent_length = max(len(s["body"]) for s in opponents)
        size_deficit = max_opponent_length - my_length
    else:
        size_deficit = 0

    # Find best food considering multiple factors
    obstacles = get_all_obstacles(game_state, include_tail=False)
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    best_food = None
    best_value = float('-inf')

    for food in food_list:
        # Calculate actual path distance (not just Manhattan)
        obstacles_with_tail = get_all_obstacles(game_state, include_tail=True)
        path_to_food = bfs_path(position, food, board_width, board_height, obstacles_with_tail)

        if not path_to_food:
            continue  # Unreachable

        path_dist = len(path_to_food)

        # SAFETY CHECK: Only validate path when we have VERY good health
        # When health is lower, take risks to get food and grow!
        if my_health > 70:
            is_path_safe, unsafe_step, safety_reason = validate_path_safety(
                path_to_food, position, game_state,
                min_escape_routes=1,  # Only need 1 escape route
                min_space=int(my_length * 1.2)  # Very lenient - just need a bit of space
            )

            if not is_path_safe:
                # Path is unsafe - skip this food only if we have plenty of health
                continue
        # If health <= 70, skip path validation and go for food!

        # SAFETY CHECK: After eating, do we have escape space?
        # Simulate being at food position with +1 length
        test_obstacles = obstacles.copy()
        escape_space = flood_fill(food, board_width, board_height, test_obstacles)

        # Check opponent competition for this food
        opponent_threat = 0
        we_are_closest = True
        for snake in game_state["board"]["snakes"]:
            if snake["id"] == my_snake["id"]:
                continue

            opp_dist = manhattan_distance(snake["body"][0], food)
            if opp_dist < path_dist:
                opponent_threat += 1
                we_are_closest = False
            elif opp_dist == path_dist:
                # Tie - consider snake length
                if len(snake["body"]) >= my_length:
                    opponent_threat += 0.5
                    we_are_closest = False

        # COMPOSITE VALUE CALCULATION
        # Positive factors (benefits)
        growth_value = 100  # Base growth value
        if size_deficit > 0:
            growth_value += size_deficit * 50  # Extra value if we're smaller
        
        urgency_value = urgency * 80  # Health urgency
        
        proximity_value = max(0, 50 - path_dist * 5)  # Closer is better
        
        escape_value = min(escape_space * 2, 100)  # Safe escape space
        
        uncontested_bonus = 100 if we_are_closest else 0  # No competition
        
        # Negative factors (costs)
        travel_cost = path_dist * 10  # Cost of travel
        
        threat_penalty = opponent_threat * 80  # Competition penalty
        
        danger_penalty = 200 if escape_space < 10 else 0  # Trapped after eating
        
        # TOTAL VALUE = Benefits - Costs
        food_value = (growth_value + urgency_value + proximity_value + 
                     escape_value + uncontested_bonus - 
                     travel_cost - threat_penalty - danger_penalty)

        if food_value > best_value:
            best_value = food_value
            best_food = food

    # BALANCED SEEKING: Seek food when it's valuable and safe
    # Don't pursue food recklessly - balance growth with survival
    if best_food is None:
        # No reachable food - don't seek
        should_seek = False
    else:
        # Only seek food if it's worth it OR we're desperate
        # Positive value means benefits outweigh risks
        if best_value > 0 or urgency >= 8:
            should_seek = True
        else:
            # Food exists but is too risky/far - focus on positioning
            should_seek = False

    return (should_seek, best_food, urgency, best_value)


# ============================================================================
# ADVANCED MOVE LOGIC WITH PREDICTION
# ============================================================================

def generate_all_opponent_move_combinations(game_state: dict) -> list:
    """
    Generate ALL possible combinations of opponent moves.
    Returns list of dictionaries mapping snake_id -> move.

    Example: With 2 opponents each having 3 moves, returns 9 combinations.
    """
    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != game_state["you"]["id"]]

    if not opponents:
        return [{}]

    # Get all possible moves for each opponent
    opponent_move_options = {}
    opponent_ids = []

    for snake in opponents:
        moves = get_possible_moves(snake, game_state["board"]["width"], game_state["board"]["height"])
        if not moves:
            moves = ["up"]  # Fallback
        opponent_move_options[snake["id"]] = moves
        opponent_ids.append(snake["id"])

    # Generate all combinations using itertools.product
    move_lists = [opponent_move_options[snake_id] for snake_id in opponent_ids]
    all_combinations = list(product(*move_lists))

    # Convert to list of dictionaries
    result = []
    for combination in all_combinations:
        move_dict = {}
        for i, snake_id in enumerate(opponent_ids):
            move_dict[snake_id] = combination[i]
        result.append(move_dict)

    return result


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


def comprehensive_minimax(game_state: dict, my_id: str, depth: int, alpha: float, beta: float,
                         is_maximizing: bool, original_move: typing.Optional[str] = None,
                         log_depth: int = 0) -> tuple:
    """
    Comprehensive minimax with alpha-beta pruning that considers ALL opponent move combinations.
    Uses sequential thinking to evaluate every possible scenario.

    Returns (score, best_move, scenarios_evaluated).
    """
    # Base case: max depth or game over
    if depth == 0 or game_state["you"] is None:
        score = evaluate_game_state(game_state, my_id)
        return (score, original_move, 1)

    # Check if we're dead
    if game_state["you"] is None:
        return (-1000000.0, None, 1)

    scenarios_evaluated = 0

    # Our turn - try each of our moves and consider ALL opponent responses
    my_possible_moves = get_possible_moves(game_state["you"],
                                           game_state["board"]["width"],
                                           game_state["board"]["height"])

    if not my_possible_moves:
        return (-1000000.0, None, 1)

    max_eval = float('-inf')
    best_move = my_possible_moves[0]

    for move in my_possible_moves:
        # For this move, consider ALL possible opponent responses
        opponent_combinations = generate_all_opponent_move_combinations(game_state)

        # Find the worst-case scenario (assume opponents play optimally against us)
        worst_case_score = float('inf')

        for opponent_moves in opponent_combinations:
            # Simulate this scenario
            new_state = simulate_game_state(game_state, move, opponent_moves)

            scenarios_evaluated += 1

            # Recursively evaluate the next turn
            if depth > 1 and new_state["you"] is not None:
                eval_score, _, sub_scenarios = comprehensive_minimax(
                    new_state, my_id, depth - 1, alpha, beta, True,
                    original_move if original_move else move, log_depth + 1
                )
                scenarios_evaluated += sub_scenarios
            else:
                # At leaf node or we died, just evaluate
                eval_score = evaluate_game_state(new_state, my_id)

            # Track worst case for this move
            if eval_score < worst_case_score:
                worst_case_score = eval_score

            # Alpha-beta pruning at opponent level
            if worst_case_score <= alpha:
                break  # This move is already worse than what we have

        # Log scenario at top level
        if log_depth == 0 and len(opponent_combinations) > 1:
            print(f"   🤔 Move {move.upper()}: Evaluated {len(opponent_combinations)} opponent combinations, worst-case score: {worst_case_score:.0f}")

        # Update best move based on worst-case scenario
        if worst_case_score > max_eval:
            max_eval = worst_case_score
            best_move = move

        # Alpha-beta pruning
        alpha = max(alpha, worst_case_score)
        if beta <= alpha:
            break  # Beta cutoff

    return (max_eval, best_move, scenarios_evaluated)


def minimax_alpha_beta(game_state: dict, my_id: str, depth: int, alpha: float, beta: float,
                       maximizing: bool, my_move: typing.Optional[str] = None) -> tuple:
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


def simulate_future_turns(start_pos: dict, game_state: dict, num_turns: int = 3) -> dict:
    """
    Simulate the next N turns to see if this move leads to inevitable death.
    Returns analysis of future danger.

    This catches scenarios where a move seems safe NOW but leads to a trap in 2-3 turns.
    """
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]
    my_length = len(game_state["you"]["body"])

    # Simulate each future turn
    current_pos = start_pos
    min_future_escapes = 4  # Track the minimum escape routes we'll have
    future_trap_detected = False
    trap_turn = -1

    for turn in range(1, num_turns + 1):
        # Get obstacles for this future turn (bodies will have moved)
        obstacles = get_all_obstacles(game_state, include_tail=False)

        # Count escape routes from this future position
        escape_count = 0
        best_next_pos = None

        for test_dir in ["up", "down", "left", "right"]:
            test_pos = {"x": current_pos["x"], "y": current_pos["y"]}
            if test_dir == "up":
                test_pos["y"] += 1
            elif test_dir == "down":
                test_pos["y"] -= 1
            elif test_dir == "left":
                test_pos["x"] -= 1
            elif test_dir == "right":
                test_pos["x"] += 1

            # Check if this future move is valid
            if (0 <= test_pos["x"] < board_width and
                0 <= test_pos["y"] < board_height and
                (test_pos["x"], test_pos["y"]) not in obstacles):
                escape_count += 1
                if best_next_pos is None:
                    best_next_pos = test_pos

        # Track minimum escapes
        if escape_count < min_future_escapes:
            min_future_escapes = escape_count

        # Check if we're trapped in the future
        if escape_count == 0:
            future_trap_detected = True
            trap_turn = turn
            break

        # Move to best next position for next iteration
        if best_next_pos:
            current_pos = best_next_pos
        else:
            break

    return {
        "future_trap_detected": future_trap_detected,
        "trap_turn": trap_turn,
        "min_future_escapes": min_future_escapes,
        "is_future_dangerous": min_future_escapes <= 1
    }


def comprehensive_trap_detection(position: dict, game_state: dict, depth: int = 4) -> dict:
    """
    COMPREHENSIVE trap detection using multiple algorithms.
    Returns detailed trap analysis.
    """
    my_length = len(game_state["you"]["body"])
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Algorithm 1: Flood fill space analysis
    obstacles = get_all_obstacles(game_state, include_tail=False)
    available_space = flood_fill(position, board_width, board_height, obstacles)

    # Algorithm 2: Escape route counting
    escape_routes = 0
    for test_dir in ["up", "down", "left", "right"]:
        test_pos = {"x": position["x"], "y": position["y"]}
        if test_dir == "up":
            test_pos["y"] += 1
        elif test_dir == "down":
            test_pos["y"] -= 1
        elif test_dir == "left":
            test_pos["x"] -= 1
        elif test_dir == "right":
            test_pos["x"] += 1

        if is_safe_move(test_pos, game_state, my_length):
            escape_routes += 1

    # Algorithm 3: Recursive dead-end detection
    is_dead_end, trap_depth, min_escapes = detect_dead_end(position, game_state, max_depth=depth)

    # Algorithm 4: Corridor detection
    is_corridor = False
    corridor_length = 0
    if escape_routes <= 2:
        # Check if we're in a narrow corridor
        for test_dir in ["up", "down", "left", "right"]:
            test_pos = {"x": position["x"], "y": position["y"]}
            if test_dir == "up":
                test_pos["y"] += 1
            elif test_dir == "down":
                test_pos["y"] -= 1
            elif test_dir == "left":
                test_pos["x"] -= 1
            elif test_dir == "right":
                test_pos["x"] += 1

            if is_safe_move(test_pos, game_state, my_length):
                # Check if this continues as a corridor
                next_escapes = 0
                for next_dir in ["up", "down", "left", "right"]:
                    next_pos = {"x": test_pos["x"], "y": test_pos["y"]}
                    if next_dir == "up":
                        next_pos["y"] += 1
                    elif next_dir == "down":
                        next_pos["y"] -= 1
                    elif next_dir == "left":
                        next_pos["x"] -= 1
                    elif next_dir == "right":
                        next_pos["x"] += 1

                    if is_safe_move(next_pos, game_state, my_length):
                        next_escapes += 1

                if next_escapes <= 2:
                    is_corridor = True
                    corridor_length += 1

    return {
        "available_space": available_space,
        "escape_routes": escape_routes,
        "is_dead_end": is_dead_end,
        "trap_depth": trap_depth,
        "min_escapes_ahead": min_escapes,
        "is_corridor": is_corridor,
        "corridor_length": corridor_length,
        "is_trapped": escape_routes == 0 or available_space < my_length,
        "is_dangerous": escape_routes <= 1 or available_space < my_length * 2 or is_dead_end
    }


def detect_opponent_trap_opportunity(opponent_snake: dict, my_head: dict, my_length: int, game_state: dict) -> dict:
    """
    Detect if an opponent is in a vulnerable position that we can exploit.
    Returns analysis of trapping opportunity.
    """
    opponent_head = opponent_snake["body"][0]
    opponent_length = len(opponent_snake["body"])
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Get opponent's current trap status
    obstacles = get_all_obstacles(game_state, include_tail=False)
    opponent_space = flood_fill(opponent_head, board_width, board_height, obstacles)

    # Count opponent's escape routes
    opponent_escapes = 0
    escape_positions = []
    for test_dir in ["up", "down", "left", "right"]:
        test_pos = {"x": opponent_head["x"], "y": opponent_head["y"]}
        if test_dir == "up":
            test_pos["y"] += 1
        elif test_dir == "down":
            test_pos["y"] -= 1
        elif test_dir == "left":
            test_pos["x"] -= 1
        elif test_dir == "right":
            test_pos["x"] += 1

        if is_safe_move(test_pos, game_state, opponent_length):
            opponent_escapes += 1
            escape_positions.append(test_pos)

    # Check if opponent is near edge/corner (more vulnerable)
    is_edge = (opponent_head["x"] == 0 or opponent_head["x"] == board_width - 1 or
               opponent_head["y"] == 0 or opponent_head["y"] == board_height - 1)
    is_corner = (opponent_head["x"] == 0 or opponent_head["x"] == board_width - 1) and \
                (opponent_head["y"] == 0 or opponent_head["y"] == board_height - 1)

    # Calculate distance to opponent
    distance = manhattan_distance(my_head, opponent_head)

    # Determine if we can trap them
    can_trap = False
    trap_value = 0

    if opponent_escapes <= 2 and distance <= 3:
        # Opponent has limited escapes and we're close enough to cut them off
        can_trap = True
        trap_value = (3 - opponent_escapes) * 50000  # More valuable if fewer escapes

        if is_corner:
            trap_value += 30000  # Extra value for cornered opponent
        elif is_edge:
            trap_value += 15000  # Extra value for edge-trapped opponent

        if opponent_space < opponent_length * 2:
            trap_value += 40000  # They're in limited space

    # Check if we can block their escape routes
    can_block_escapes = 0
    for escape_pos in escape_positions:
        if manhattan_distance(my_head, escape_pos) <= 2:
            can_block_escapes += 1

    return {
        "opponent_id": opponent_snake["id"],
        "opponent_length": opponent_length,
        "opponent_escapes": opponent_escapes,
        "opponent_space": opponent_space,
        "distance": distance,
        "is_edge": is_edge,
        "is_corner": is_corner,
        "can_trap": can_trap,
        "trap_value": trap_value,
        "can_block_escapes": can_block_escapes,
        "escape_positions": escape_positions,
        "is_vulnerable": opponent_escapes <= 2 or opponent_space < opponent_length * 3
    }


def analyze_food_safety(food: dict, game_state: dict) -> dict:
    """
    COMPREHENSIVE food safety analysis.
    Checks if eating this food is safe.
    """
    my_snake = game_state["you"]
    my_length = len(my_snake["body"])
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Check 1: Space after eating
    obstacles = get_all_obstacles(game_state, include_tail=False)
    space_after_eating = flood_fill(food, board_width, board_height, obstacles)

    # Check 2: Escape routes from food
    escape_routes = 0
    for test_dir in ["up", "down", "left", "right"]:
        test_pos = {"x": food["x"], "y": food["y"]}
        if test_dir == "up":
            test_pos["y"] += 1
        elif test_dir == "down":
            test_pos["y"] -= 1
        elif test_dir == "left":
            test_pos["x"] -= 1
        elif test_dir == "right":
            test_pos["x"] += 1

        if is_safe_move(test_pos, game_state, my_length):
            escape_routes += 1

    # Check 3: Opponent competition
    opponents_nearby = 0
    larger_opponents_nearby = 0
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == my_snake["id"]:
            continue

        snake_head = snake["body"][0]
        dist = manhattan_distance(snake_head, food)

        if dist <= 3:
            opponents_nearby += 1
            if len(snake["body"]) >= my_length:
                larger_opponents_nearby += 1

    # Check 4: Is food in a corner or against wall?
    is_corner = (food["x"] == 0 or food["x"] == board_width - 1) and \
                (food["y"] == 0 or food["y"] == board_height - 1)
    is_edge = food["x"] == 0 or food["x"] == board_width - 1 or \
              food["y"] == 0 or food["y"] == board_height - 1

    return {
        "space_after": space_after_eating,
        "escape_routes": escape_routes,
        "opponents_nearby": opponents_nearby,
        "larger_opponents_nearby": larger_opponents_nearby,
        "is_corner": is_corner,
        "is_edge": is_edge,
        "is_safe": escape_routes >= 2 and space_after_eating >= my_length * 2 and larger_opponents_nearby == 0,
        "is_risky": escape_routes == 1 or space_after_eating < my_length * 2 or larger_opponents_nearby > 0,
        "is_deadly": escape_routes == 0 or space_after_eating < my_length or larger_opponents_nearby >= 2
    }


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

    score = 0  # Start from 0 for clear scoring
    reasons = []

    # ========================================================================
    # PHASE 1: IMMEDIATE SURVIVAL - Don't die this turn!
    # ========================================================================

    # Check 1: Wall collision
    if new_head["x"] < 0 or new_head["x"] >= board_width or new_head["y"] < 0 or new_head["y"] >= board_height:
        return {"score": -1000000, "reasons": ["💀 WALL COLLISION"], "direction": direction}

    # Check 2: Self collision
    for segment in my_body[:-1]:  # Exclude tail (it moves)
        if coords_equal(new_head, segment):
            return {"score": -1000000, "reasons": ["💀 SELF COLLISION"], "direction": direction}

    # Check 3: Other snake body collision
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue
        for segment in snake["body"][:-1]:  # Exclude tail
            if coords_equal(new_head, segment):
                return {"score": -1000000, "reasons": ["💀 SNAKE BODY COLLISION"], "direction": direction}

    # Check 4: Head-to-head collision danger
    head_to_head_danger = False
    head_to_head_with_equal = False
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        snake_head = snake["body"][0]
        snake_length = len(snake["body"])

        # Check if opponent could move to same position
        if manhattan_distance(new_head, snake_head) == 1:
            if snake_length >= my_length:
                head_to_head_danger = True
                if snake_length == my_length:
                    head_to_head_with_equal = True

    # Passed immediate survival checks
    score += 100000
    reasons.append("✅ IMMEDIATE SURVIVAL: Safe from instant death")

    # ========================================================================
    # PHASE 1.5: PREDICTIVE OPPONENT MOVEMENT - Avoid where opponents might move
    # ========================================================================

    # Predict where opponents might move and avoid those cells
    # This is CRITICAL in 4-player games to avoid collisions!
    opponent_threat_cells = set()

    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        snake_head = snake["body"][0]
        snake_length = len(snake["body"])

        # Predict opponent's possible moves
        possible_opponent_moves = [
            {"x": snake_head["x"], "y": snake_head["y"] + 1},  # up
            {"x": snake_head["x"], "y": snake_head["y"] - 1},  # down
            {"x": snake_head["x"] - 1, "y": snake_head["y"]},  # left
            {"x": snake_head["x"] + 1, "y": snake_head["y"]},  # right
        ]

        for opp_move in possible_opponent_moves:
            # Check if opponent move is valid
            if (opp_move["x"] >= 0 and opp_move["x"] < board_width and
                opp_move["y"] >= 0 and opp_move["y"] < board_height):

                # If opponent is same size or larger, avoid their possible moves
                if snake_length >= my_length:
                    opponent_threat_cells.add((opp_move["x"], opp_move["y"]))

    # Penalize moving into cells where opponents might move
    if (new_head["x"], new_head["y"]) in opponent_threat_cells:
        # Check if this is a head-to-head situation
        for snake in game_state["board"]["snakes"]:
            if snake["id"] == game_state["you"]["id"]:
                continue
            snake_head = snake["body"][0]
            if manhattan_distance(new_head, snake_head) == 1:
                snake_length = len(snake["body"])
                if snake_length > my_length:
                    # Larger opponent might move here - DANGER!
                    score -= 40000
                    reasons.append(f"⚠️  OPPONENT THREAT: Larger snake might move here (-40000)")
                elif snake_length == my_length:
                    # Equal opponent might move here - risky
                    score -= 15000
                    reasons.append(f"⚠️  COLLISION RISK: Equal snake nearby (-15000)")

    # ========================================================================
    # PHASE 2: COMPREHENSIVE TRAP ANALYSIS
    # ========================================================================

    trap_analysis = comprehensive_trap_detection(new_head, game_state, depth=4)

    # CRITICAL: If this move leads to guaranteed trap, reject it!
    if trap_analysis["is_trapped"]:
        score -= 500000
        reasons.append(f"💀 GUARANTEED TRAP: {trap_analysis['escape_routes']} escapes, {trap_analysis['available_space']} space")
        return {"score": score, "reasons": reasons, "direction": direction}

    # NEW: Multi-turn lookahead to catch future traps!
    # This prevents scenarios where we walk into a trap 2-3 turns later
    future_analysis = simulate_future_turns(new_head, game_state, num_turns=3)

    if future_analysis["future_trap_detected"]:
        # This move leads to INEVITABLE DEATH in the future!
        future_trap_penalty = 400000
        score -= future_trap_penalty
        reasons.append(f"💀 FUTURE TRAP: Death in {future_analysis['trap_turn']} turns! (-{future_trap_penalty})")
        # Don't return yet - might still be best option if all moves are bad

    elif future_analysis["is_future_dangerous"]:
        # This move leads to dangerous position in future (1 escape or less)
        future_danger_penalty = 150000
        score -= future_danger_penalty
        reasons.append(f"⚠️  FUTURE DANGER: Only {future_analysis['min_future_escapes']} escapes ahead (-{future_danger_penalty})")

    elif future_analysis["min_future_escapes"] >= 3:
        # This move maintains good escape routes in the future!
        future_safety_bonus = 20000
        score += future_safety_bonus
        reasons.append(f"✅ FUTURE SAFE: {future_analysis['min_future_escapes']}+ escapes ahead (+{future_safety_bonus})")

    # Penalize dangerous situations more heavily
    if trap_analysis["is_dangerous"]:
        # Scale penalty based on how dangerous it is
        danger_penalty = 80000 + (3 - trap_analysis['escape_routes']) * 20000
        score -= danger_penalty
        reasons.append(f"⚠️  DANGEROUS: {trap_analysis['escape_routes']} escapes, {trap_analysis['available_space']} space (-{danger_penalty})")

    # Reward safe positions with multiple escape routes
    if trap_analysis["escape_routes"] >= 3:
        safety_bonus = 15000
        score += safety_bonus
        reasons.append(f"✅ SAFE POSITION: {trap_analysis['escape_routes']} escape routes (+{safety_bonus})")
    elif trap_analysis["escape_routes"] == 2:
        # Two escapes is okay but not ideal
        score += 5000
        reasons.append(f"✓ ADEQUATE: {trap_analysis['escape_routes']} escape routes")

    # Extra reward for having lots of available space
    if trap_analysis["available_space"] >= my_length * 3:
        score += 10000
        reasons.append(f"🌊 PLENTY OF SPACE: {trap_analysis['available_space']} cells available")

    # ========================================================================
    # PHASE 3: FOOD ACQUISITION - Eat or seek food
    # ========================================================================

    # Determine health urgency - OPTIMIZED FOR 4-PLAYER
    # In 4-player games, space control > food unless health is critical!
    if my_health < 15:
        urgency = 10  # CRITICAL - must eat NOW!
    elif my_health < 25:
        urgency = 8   # VERY HIGH - eat soon
    elif my_health < 40:
        urgency = 5   # MEDIUM - eat when safe
    elif my_health < 60:
        urgency = 3   # LOW - only if convenient
    else:
        urgency = 1   # MINIMAL - focus on space control, not food!

    # Check if we're eating food THIS turn
    eating_food = False
    if food_list:
        for food in food_list:
            if coords_equal(new_head, food):
                eating_food = True

                # Analyze if eating this food is safe
                food_safety = analyze_food_safety(food, game_state)

                # CRITICAL: Check if we're eating food on an EDGE!
                # This is EXTREMELY dangerous - user's Turn 53 scenario
                is_edge = (new_head["x"] == 0 or new_head["x"] == board_width - 1 or
                          new_head["y"] == 0 or new_head["y"] == board_height - 1)
                is_corner = (new_head["x"] == 0 or new_head["x"] == board_width - 1) and \
                           (new_head["y"] == 0 or new_head["y"] == board_height - 1)

                if is_corner and urgency < 10:
                    # Eating food in a CORNER is almost always death!
                    score -= 300000
                    reasons.append(f"🚫 CORNER FOOD TRAP: Eating here = death! (-300000)")
                elif is_edge and urgency < 8:
                    # Eating food on an EDGE is very dangerous
                    edge_food_penalty = 150000
                    score -= edge_food_penalty
                    reasons.append(f"⚠️  EDGE FOOD DANGER: Eating on edge = trap risk! (-{edge_food_penalty})")

                if food_safety["is_deadly"]:
                    # Food is in a death trap!
                    score -= 200000
                    reasons.append(f"💀 DEADLY FOOD: {food_safety['escape_routes']} escapes after eating")
                elif food_safety["is_risky"]:
                    # Food is risky but might be worth it if desperate
                    if urgency >= 8:
                        # Desperate - take the risk!
                        score += 200000
                        reasons.append(f"🍎 DESPERATE EAT: Health {my_health}, risky but necessary!")
                    else:
                        # Not desperate - avoid risky food
                        score -= 50000
                        reasons.append(f"⚠️  RISKY FOOD: {food_safety['escape_routes']} escapes, avoiding")
                else:
                    # Food is safe - EAT IT!
                    # Balanced bonus that scales with urgency
                    food_bonus = 350000 + (urgency * 20000)
                    score += food_bonus
                    reasons.append(f"🍎🍎🍎 SAFE FOOD! Health:{my_health}, Urgency:{urgency} (+{food_bonus})")
                break

    # If not eating, check if we should seek food
    if not eating_food and food_list:
        # Find nearest safe food
        best_food = None
        best_food_score = float('-inf')

        obstacles_with_tail = get_all_obstacles(game_state, include_tail=True)

        for food in food_list:
            # Check food safety
            food_safety = analyze_food_safety(food, game_state)

            # Skip deadly food
            if food_safety["is_deadly"]:
                continue

            # Find path to food
            path = bfs_path(new_head, food, board_width, board_height, obstacles_with_tail)

            if path:
                # Calculate food value - balanced approach
                distance = len(path)
                safety_bonus = 2000 if food_safety["is_safe"] else 0  # Only pursue safe food when not urgent
                urgency_bonus = urgency * 800
                proximity_bonus = max(0, 150 - distance * 12)
                
                # Only add growth bonus if food is safe OR we're desperate
                growth_bonus = 500 if (food_safety["is_safe"] or urgency >= 8) else 0

                food_score = safety_bonus + urgency_bonus + proximity_bonus + growth_bonus

                if food_score > best_food_score:
                    best_food_score = food_score
                    best_food = (food, path, food_safety)

        if best_food:
            food, path, food_safety = best_food

            # Check if this move is on the path to food
            # path[0] is a direction string like "up", "down", etc.
            if len(path) > 0 and path[0] == direction:
                # We're moving toward food - balance urgency with safety
                # Only give big bonus if safe OR desperate
                if food_safety["is_safe"] or urgency >= 8:
                    path_bonus = 120000 + (urgency * 12000) + best_food_score
                    score += path_bonus
                    reasons.append(f"🍎 SEEKING FOOD: {len(path)} moves away (+{path_bonus})")
                else:
                    # Food path exists but not safe - smaller bonus
                    path_bonus = 40000 + (urgency * 8000)
                    score += path_bonus
                    reasons.append(f"🍎 FOOD NEARBY: {len(path)} moves, risky (+{path_bonus})")
            else:
                # Not on optimal path, adjust based on distance change
                current_dist = manhattan_distance(my_head, food)
                new_dist = manhattan_distance(new_head, food)
                if new_dist < current_dist:
                    # Moving closer to best food
                    score += 50000 + (urgency * 6000)
                    reasons.append(f"🍎 MOVING TOWARD FOOD: {new_dist} away")
                elif new_dist > current_dist and urgency >= 5:
                    # Moving away from best food while somewhat hungry - penalize
                    drift_penalty = 20000 + (urgency * 7000)
                    score -= drift_penalty
                    reasons.append(f"⚠️  DRIFTING FROM FOOD: {new_dist} away, urgency {urgency} (-{drift_penalty})")

    # CRITICAL: If health is critical and we're not eating/seeking, HUGE penalty
    if urgency >= 8 and not eating_food:
        score -= 100000
        reasons.append(f"💀 CRITICAL HEALTH: {my_health} HP, need food urgently!")

    # ========================================================================
    # PHASE 4: HEAD-TO-HEAD COLLISION HANDLING & MUTUAL KILL LOGIC
    # ========================================================================

    if head_to_head_danger:
        if head_to_head_with_equal:
            # Equal size - both die
            # Check if we're already in a bad position (trapped or about to die)
            # If so, taking them down with us is better than dying alone!
            if trap_analysis["is_dangerous"] or trap_analysis["escape_routes"] <= 1:
                # We're in trouble anyway - mutual kill is acceptable!
                score += 50000
                reasons.append("⚔️  MUTUAL KILL: We're trapped anyway, take them with us!")
            else:
                # We're in good position - avoid mutual kill
                score -= 80000
                reasons.append("⚠️  HEAD-TO-HEAD WITH EQUAL: Mutual destruction risk")
        else:
            # Larger opponent - we die, they live. AVOID!
            # UNLESS we're already doomed and can deny them the win
            if trap_analysis["is_trapped"] or trap_analysis["escape_routes"] == 0:
                # We're dead anyway - might as well try to take them down
                score += 20000
                reasons.append("⚔️  KAMIKAZE: Already doomed, attempting mutual kill!")
            else:
                score -= 200000
                reasons.append("💀 HEAD-TO-HEAD WITH LARGER: We die!")

    # ========================================================================
    # PHASE 5: POSITIONING & TERRITORY CONTROL
    # ========================================================================

    # TAIL CHASING - Following our own tail is SAFE (it moves away each turn)
    # This is a key strategy for advanced snakes!
    my_tail = my_body[-1]
    dist_to_tail = manhattan_distance(new_head, my_tail)

    # Strong bonus for moving toward tail (safe space!)
    if dist_to_tail == 1:
        # Adjacent to tail - very safe move!
        score += 20000
        reasons.append(f"🔄 TAIL CHASE: Following safe tail (+20000)")
    elif dist_to_tail == 2:
        # Near tail - safe direction
        score += 10000
        reasons.append(f"🔄 NEAR TAIL: Moving toward safety (+10000)")
    elif dist_to_tail <= 4 and my_length > 6:
        # Tail is nearby - good option for longer snakes
        score += 4000
        reasons.append(f"🔄 TAIL NEARBY: Safe area available (+4000)")

    # Center control - being in center gives more options and board dominance
    center_x = board_width // 2
    center_y = board_height // 2
    center = {"x": center_x, "y": center_y}
    dist_to_center = manhattan_distance(new_head, center)
    
    # Center control becomes more important when we're bigger (can dominate)
    center_importance = min(my_length, 15) * 400  # Scales with snake length
    
    # Reward being close to center - center control is crucial
    if dist_to_center == 0:
        # Perfect center position
        center_bonus = 12000 + center_importance
        score += center_bonus
        reasons.append(f"🎯🎯 CENTER CONTROL: Perfect position (+{center_bonus})")
    elif dist_to_center <= 2:
        # Very close to center
        center_bonus = 8000 + center_importance // 2
        score += center_bonus
        reasons.append(f"🎯 NEAR CENTER: Excellent positioning (+{center_bonus})")
    elif dist_to_center <= 4:
        # Reasonably close
        score += 4000
        reasons.append("🎯 CENTER AREA: Good positioning")
    elif dist_to_center > board_width // 2 + 1:
        # Too far from center - penalize
        distance_penalty = 6000 + (dist_to_center * 500)
        score -= distance_penalty
        reasons.append(f"⚠️  FAR FROM CENTER: Poor positioning (-{distance_penalty})")
    
    # Extra bonus for moving toward center when far away (unless chasing food)
    if not eating_food and dist_to_center > 4:
        current_center_dist = manhattan_distance(my_head, center)
        if dist_to_center < current_center_dist:
            score += 3000
            reasons.append("➡️  MOVING TO CENTER: Improving position")

    # Avoid edges and corners more aggressively - they reduce options and increase trap risk
    is_edge = (new_head["x"] == 0 or new_head["x"] == board_width - 1 or
               new_head["y"] == 0 or new_head["y"] == board_height - 1)
    is_corner = (new_head["x"] == 0 or new_head["x"] == board_width - 1) and \
                (new_head["y"] == 0 or new_head["y"] == board_height - 1)

    # Near edge/corner detection for better avoidance
    near_edge = (new_head["x"] <= 1 or new_head["x"] >= board_width - 2 or
                 new_head["y"] <= 1 or new_head["y"] >= board_height - 2)

    # Calculate edge penalty based on game state
    # Dynamically scale edge fear based on opponents, length, and health
    num_opponents = len([s for s in game_state["board"]["snakes"] if s["id"] != game_state["you"]["id"]])

    # Base: more opponents = more dangerous edges (1.5–2.4 range for 0–3 opponents)
    base_edge_multiplier = 1.5 + 0.3 * min(num_opponents, 3)

    # Smaller snakes are more agile and can escape edges more easily
    length_factor = 0.7 if my_length <= 6 else 1.0

    edge_multiplier = base_edge_multiplier * length_factor

    # If health is critical (urgency high), don't over-penalize edges that lead to food/survival
    if urgency >= 8:
        edge_multiplier *= 0.6

    if is_corner:
        corner_penalty = int(60000 * edge_multiplier)  # MASSIVE penalty for corners
        score -= corner_penalty
        reasons.append(f"🚫 CORNER: Very dangerous in multi-snake games (-{corner_penalty})")
    elif is_edge:
        edge_penalty = int(30000 * edge_multiplier)  # Strong edge penalty
        score -= edge_penalty
        reasons.append(f"⚠️  EDGE: Risky near wall with opponents (-{edge_penalty})")
    elif near_edge and my_length > 5:
        # When we're bigger, be more careful near edges
        near_edge_penalty = int(12000 * edge_multiplier)
        score -= near_edge_penalty
        reasons.append(f"⚠️  NEAR EDGE: Reduced flexibility near wall (-{near_edge_penalty})")

    # ========================================================================
    # PHASE 6: OPPONENT INTERACTION & TRAPPING
    # ========================================================================

    # Analyze each opponent for trapping opportunities
    best_trap_opportunity = None
    best_trap_value = 0

    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        snake_head = snake["body"][0]
        snake_length = len(snake["body"])
        dist_to_opponent = manhattan_distance(new_head, snake_head)

        # Detect trapping opportunity
        trap_analysis = detect_opponent_trap_opportunity(snake, new_head, my_length, game_state)

        # Debug: Log trap analysis for first move only
        # print(f"DEBUG {direction}: Opponent at {snake_head}, escapes={trap_analysis['opponent_escapes']}, can_trap={trap_analysis['can_trap']}, dist={dist_to_opponent}, vulnerable={trap_analysis['is_vulnerable']}")

        # Check if this move helps trap the opponent
        if trap_analysis["can_trap"]:
            # Calculate how much this move cuts off opponent's escapes
            cutoff_value = 0

            # If opponent has escape routes, reward blocking them
            if len(trap_analysis["escape_positions"]) > 0:
                for escape_pos in trap_analysis["escape_positions"]:
                    # Check if our new position blocks or threatens this escape
                    dist_to_escape = manhattan_distance(new_head, escape_pos)
                    if dist_to_escape == 1:
                        # We're adjacent to their escape route - blocking it!
                        cutoff_value += 60000
                    elif dist_to_escape == 2:
                        # We're close to their escape route - threatening it
                        cutoff_value += 25000
            else:
                # Opponent is already trapped (0 escapes)!
                # Reward being close to finish them off
                if dist_to_opponent == 1:
                    cutoff_value += 80000  # Adjacent to trapped opponent - go for the kill!
                elif dist_to_opponent == 2:
                    cutoff_value += 40000  # Close to trapped opponent

            total_trap_value = trap_analysis["trap_value"] + cutoff_value

            if total_trap_value > best_trap_value:
                best_trap_value = total_trap_value
                best_trap_opportunity = trap_analysis

            if cutoff_value > 0:
                if trap_analysis["opponent_escapes"] == 0:
                    score += cutoff_value
                    reasons.append(f"🎯🎯 OPPONENT TRAPPED: Finishing them off! (+{cutoff_value})")
                else:
                    score += cutoff_value
                    reasons.append(f"🎯 TRAPPING OPPONENT: Cutting off {trap_analysis['opponent_escapes']} escapes (+{cutoff_value})")

        # Standard opponent interaction
        if snake_length < my_length:
            # We're bigger - we can be aggressive
            if dist_to_opponent == 1:
                # Adjacent to smaller snake - we win head-to-head!
                score += 20000
                reasons.append(f"⚔️  DOMINATE: Adjacent to smaller snake (len {snake_length})")
            elif dist_to_opponent <= 3:
                # Near smaller snake - good positioning
                score += 5000
                reasons.append(f"⚔️  HUNTING: Near smaller snake")

                # If they're vulnerable, be more aggressive
                if trap_analysis["is_vulnerable"]:
                    score += 15000
                    reasons.append(f"🎯 VULNERABLE TARGET: {trap_analysis['opponent_escapes']} escapes")

        elif snake_length >= my_length:
            # Equal or larger - be cautious
            if dist_to_opponent <= 2:
                # Too close to dangerous snake
                score -= 10000
                reasons.append(f"⚠️  DANGER: Too close to larger/equal snake (len {snake_length})")

    # Give extra bonus if we found a great trapping opportunity
    if best_trap_opportunity and best_trap_value > 50000:
        score += 40000
        reasons.append(f"🎯🎯 EXCELLENT TRAP: Opponent has {best_trap_opportunity['opponent_escapes']} escapes!")

    # ========================================================================
    # PHASE 7: SPACE CONTROL & VORONOI - CRITICAL IN 4-PLAYER!
    # ========================================================================

    # Calculate Voronoi space control for all snakes
    # In 4-player games, space control is EVERYTHING!
    voronoi_spaces = calculate_voronoi_space(game_state)
    my_id = game_state["you"]["id"]

    if my_id in voronoi_spaces:
        my_voronoi = voronoi_spaces[my_id]

        # MUCH higher bonus for space control in 4-player games
        # Space = survival in competitive play
        voronoi_bonus = min(my_voronoi * 200, 30000)  # Up to 30k bonus!
        score += voronoi_bonus

        # Check if we're dominating space
        total_cells = board_width * board_height
        space_percentage = (my_voronoi / total_cells) * 100

        if space_percentage > 40:
            # Dominating the board!
            score += 15000
            reasons.append(f"👑 SPACE DOMINANCE: Controlling {my_voronoi} cells ({space_percentage:.0f}%) (+{voronoi_bonus + 15000})")
        elif space_percentage > 30:
            # Strong position
            score += 8000
            reasons.append(f"🗺️  STRONG TERRITORY: {my_voronoi} cells ({space_percentage:.0f}%) (+{voronoi_bonus + 8000})")
        elif space_percentage > 20:
            # Decent position
            reasons.append(f"🗺️  TERRITORY: Controlling {my_voronoi} cells (+{voronoi_bonus})")
        else:
            # Losing space control - WARNING!
            score -= 5000
            reasons.append(f"⚠️  LOW SPACE: Only {my_voronoi} cells ({space_percentage:.0f}%) - need more! (+{voronoi_bonus - 5000})")

    # CONSTRICTOR MODE - When we're the largest, use our body to control space!
    snakes_by_length = sorted(game_state["board"]["snakes"], key=lambda s: len(s["body"]), reverse=True)
    if snakes_by_length and snakes_by_length[0]["id"] == my_id:
        # We're the largest snake!
        length_advantage = my_length - len(snakes_by_length[1]["body"]) if len(snakes_by_length) > 1 else 0

        if length_advantage >= 3:
            # Significant size advantage - be aggressive!
            score += 12000
            reasons.append(f"🐍 CONSTRICTOR MODE: Largest snake (+{length_advantage} length) - DOMINATE! (+12000)")
        elif length_advantage >= 1:
            # Small advantage - maintain control
            score += 6000
            reasons.append(f"🐍 SIZE ADVANTAGE: +{length_advantage} length - control space (+6000)")

    # ========================================================================
    # PHASE 8: PREDICTIVE SIMULATION (Late game only)
    # ========================================================================

    if use_prediction and my_length >= 10 and my_health > 30:
        num_opponents = len([s for s in game_state["board"]["snakes"] if s["id"] != game_state["you"]["id"]])

        if num_opponents == 1:
            prediction_depth = 8
        elif num_opponents <= 2:
            prediction_depth = 6
        else:
            prediction_depth = 4

        # Simulate opponent moves
        opponent_moves = {}
        for snake in game_state["board"]["snakes"]:
            if snake["id"] == game_state["you"]["id"]:
                continue
            snake_moves = get_possible_moves(snake, board_width, board_height)
            if snake_moves:
                opponent_moves[snake["id"]] = snake_moves[0]

        test_state = simulate_game_state(game_state, direction, opponent_moves)

        if test_state["you"] is None:
            score -= 50000
            reasons.append("💀 MINIMAX: Immediate death predicted")
        else:
            future_score, _ = minimax_alpha_beta(test_state, game_state["you"]["id"],
                                                prediction_depth, float('-inf'), float('inf'), True, direction)

            if future_score < -500000:
                score -= 30000
                reasons.append(f"⚠️  MINIMAX: Danger ahead (depth {prediction_depth})")
            else:
                prediction_bonus = min(int(future_score // 20), 5000)
                score += prediction_bonus
                reasons.append(f"✓ MINIMAX: Future looks good (+{prediction_bonus})")

    # ========================================================================
    # FINAL SCORE RETURN
    # ========================================================================

    return {"score": score, "reasons": reasons, "direction": direction}


# ============================================================================
# CONSTRICTOR MODE - SPECIALIZED FUNCTIONS
# ============================================================================
# In constrictor mode: NO FOOD, always growing, can't revisit cells
# Strategy: Maximize space, avoid self-collision, cut off opponents

def is_constrictor_mode(game_state: dict) -> bool:
    """
    Detect if this is constrictor mode.
    In constrictor mode: no food on board, snakes grow every turn.
    """
    # Check if there's no food
    has_no_food = len(game_state["board"].get("food", [])) == 0

    # In constrictor mode, snakes grow every turn
    # We can detect this by checking if health is always 100 (doesn't decrease)
    my_health = game_state["you"]["health"]
    is_full_health = my_health == 100

    return has_no_food and is_full_health


def calculate_reachable_space_constrictor(pos: dict, game_state: dict, max_depth: int = 100) -> dict:
    """
    Calculate how much space is reachable from a position in constrictor mode.
    Returns detailed analysis of the reachable area.
    """
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Get all occupied cells (all snake bodies)
    occupied = set()
    for snake in game_state["board"]["snakes"]:
        for segment in snake["body"]:
            occupied.add((segment["x"], segment["y"]))

    # BFS to find all reachable cells
    visited = set()
    queue = deque([pos])
    visited.add((pos["x"], pos["y"]))

    cells_explored = 0
    max_distance = 0

    while queue and cells_explored < max_depth:
        current = queue.popleft()
        cells_explored += 1

        # Check all neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = current["x"] + dx, current["y"] + dy

            # Check bounds
            if not (0 <= nx < board_width and 0 <= ny < board_height):
                continue

            # Check if already visited or occupied
            if (nx, ny) in visited or (nx, ny) in occupied:
                continue

            visited.add((nx, ny))
            queue.append({"x": nx, "y": ny})
            max_distance = max(max_distance, abs(nx - pos["x"]) + abs(ny - pos["y"]))

    return {
        "reachable_cells": len(visited),
        "max_distance": max_distance,
        "is_isolated": len(visited) < 10,  # Less than 10 cells = isolated
        "cells": visited
    }


def detect_self_trap_constrictor(new_head: dict, game_state: dict, lookahead: int = 5) -> dict:
    """
    Detect if moving to new_head will trap us in constrictor mode.
    In constrictor mode, we grow every turn, so we need MORE space than standard mode.
    """
    my_length = len(game_state["you"]["body"])

    # Calculate space after this move
    space_analysis = calculate_reachable_space_constrictor(new_head, game_state)
    reachable = space_analysis["reachable_cells"]

    # In constrictor mode, we need space for our GROWING body
    # We grow 1 cell per turn, so we need at least (current_length + lookahead) cells
    min_required_space = my_length + lookahead

    is_trapped = reachable < min_required_space
    is_dangerous = reachable < min_required_space * 1.5

    return {
        "is_trapped": is_trapped,
        "is_dangerous": is_dangerous,
        "reachable_space": reachable,
        "required_space": min_required_space,
        "space_margin": reachable - min_required_space,
        "is_isolated": space_analysis["is_isolated"]
    }


def calculate_opponent_cutoff_value_constrictor(my_pos: dict, opponent: dict, game_state: dict) -> dict:
    """
    Calculate the value of cutting off an opponent's space in constrictor mode.
    This is CRITICAL - if we can trap them in a small space, they'll die!
    """
    opponent_head = opponent["body"][0]
    opponent_length = len(opponent["body"])

    # Calculate opponent's reachable space
    opponent_space = calculate_reachable_space_constrictor(opponent_head, game_state)
    opponent_reachable = opponent_space["reachable_cells"]

    # Calculate our reachable space
    my_space = calculate_reachable_space_constrictor(my_pos, game_state)
    my_reachable = my_space["reachable_cells"]

    # Check if we can cut them off
    cutoff_value = 0
    can_cutoff = False

    # If opponent has limited space relative to their length
    if opponent_reachable < opponent_length * 2:
        # They're in trouble!
        can_cutoff = True
        cutoff_value = 200000 + (opponent_length * 2 - opponent_reachable) * 10000

    # If we have significantly more space than them
    space_advantage = my_reachable - opponent_reachable
    if space_advantage > 20:
        cutoff_value += space_advantage * 1000

    # Check if we're blocking their path to larger spaces
    dist_to_opponent = manhattan_distance(my_pos, opponent_head)
    if dist_to_opponent <= 3 and my_reachable > opponent_reachable:
        # We're between them and freedom!
        cutoff_value += 100000
        can_cutoff = True

    return {
        "can_cutoff": can_cutoff,
        "cutoff_value": cutoff_value,
        "opponent_space": opponent_reachable,
        "my_space": my_reachable,
        "space_advantage": space_advantage,
        "opponent_is_trapped": opponent_reachable < opponent_length * 1.5
    }


def find_center_control_value(pos: dict, board_width: int, board_height: int) -> int:
    """
    Calculate value of controlling the center in constrictor mode.
    Center control is CRITICAL - it gives maximum options.
    """
    center_x = board_width / 2.0
    center_y = board_height / 2.0

    # Distance from center
    dist_from_center = abs(pos["x"] - center_x) + abs(pos["y"] - center_y)
    max_dist = center_x + center_y

    # Closer to center = higher value
    center_score = int((1.0 - (dist_from_center / max_dist)) * 100000)

    return center_score


def predict_opponent_moves_constrictor(opponent: dict, game_state: dict) -> list:
    """
    Predict where an opponent is likely to move in constrictor mode.
    Returns list of likely positions.
    """
    opponent_head = opponent["body"][0]
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    # Get all occupied cells
    occupied = set()
    for snake in game_state["board"]["snakes"]:
        for segment in snake["body"]:
            occupied.add((segment["x"], segment["y"]))

    # Evaluate each possible opponent move
    possible_positions = []

    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        new_x = opponent_head["x"] + dx
        new_y = opponent_head["y"] + dy

        # Check bounds
        if not (0 <= new_x < board_width and 0 <= new_y < board_height):
            continue

        # Check if occupied
        if (new_x, new_y) in occupied:
            continue

        # This is a valid move for the opponent
        new_pos = {"x": new_x, "y": new_y}

        # Calculate how good this move is for the opponent
        space_analysis = calculate_reachable_space_constrictor(new_pos, game_state, max_depth=30)

        possible_positions.append({
            "pos": new_pos,
            "space": space_analysis["reachable_cells"],
            "priority": space_analysis["reachable_cells"]  # Opponents will prefer moves with more space
        })

    # Sort by priority (most space first)
    possible_positions.sort(key=lambda x: x["priority"], reverse=True)

    return possible_positions


def calculate_blocking_value_constrictor(my_pos: dict, opponent: dict, game_state: dict) -> int:
    """
    Calculate the value of blocking an opponent's best moves.
    Returns bonus points for moves that cut off opponent's options.
    """
    # Predict where opponent wants to go
    opponent_moves = predict_opponent_moves_constrictor(opponent, game_state)

    if not opponent_moves:
        return 0  # Opponent has no moves (already dead)

    blocking_value = 0

    # Check if we're blocking their best moves
    for i, opp_move in enumerate(opponent_moves[:3]):  # Check top 3 opponent moves
        opp_pos = opp_move["pos"]
        dist = manhattan_distance(my_pos, opp_pos)

        if dist == 0:
            # We're moving to their best position!
            blocking_value += 150000 - (i * 30000)  # More value for blocking their #1 choice
        elif dist == 1:
            # We're adjacent to their best position - threatening it
            blocking_value += 80000 - (i * 20000)
        elif dist == 2:
            # We're close to their best position
            blocking_value += 40000 - (i * 10000)

    return blocking_value


def evaluate_move_constrictor(direction: str, game_state: dict) -> dict:
    """
    CONSTRICTOR MODE EVALUATION - Completely different strategy!

    In constrictor mode:
    - NO FOOD (ignore all food logic)
    - Always growing (every move adds a segment)
    - Can't revisit cells (they're "painted")
    - Space management is EVERYTHING
    - Self-collision is the main danger

    Strategy:
    1. Maximize reachable space
    2. Avoid self-trapping
    3. Cut off opponents
    4. Control center
    5. Create efficient patterns
    """
    my_head = game_state["you"]["body"][0]
    my_body = game_state["you"]["body"]
    my_length = len(my_body)
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

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

    score = 0
    reasons = []

    # ========================================================================
    # PHASE 1: IMMEDIATE SURVIVAL - CRITICAL!
    # ========================================================================

    # Check 1: Wall collision
    if new_head["x"] < 0 or new_head["x"] >= board_width or new_head["y"] < 0 or new_head["y"] >= board_height:
        return {"score": -10000000, "reasons": ["💀 WALL COLLISION"], "direction": direction}

    # Check 2: Self collision (CRITICAL in constrictor mode!)
    # In constrictor mode, we DON'T exclude the tail because we're always growing!
    for segment in my_body:  # Check ALL segments including tail!
        if coords_equal(new_head, segment):
            return {"score": -10000000, "reasons": ["💀 SELF COLLISION - CONSTRICTOR MODE"], "direction": direction}

    # Check 3: Opponent body collision
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue
        for segment in snake["body"]:
            if coords_equal(new_head, segment):
                return {"score": -10000000, "reasons": ["💀 OPPONENT BODY COLLISION"], "direction": direction}

    # Check 4: Head-to-head collision in constrictor mode
    # In constrictor mode, we need to avoid head-to-head with equal/longer snakes
    for snake in game_state["board"]["snakes"]:
        if snake["id"] == game_state["you"]["id"]:
            continue

        opponent_head = snake["body"][0]
        opponent_length = len(snake["body"])

        # Check if opponent could move to the same position
        dist_to_opponent_head = manhattan_distance(new_head, opponent_head)
        if dist_to_opponent_head == 1:
            # We're moving adjacent to opponent's head - possible head-to-head!
            if opponent_length >= my_length:
                # They're equal or longer - we lose or tie (both die)
                # CRITICAL: Avoid this!
                return {"score": -10000000, "reasons": [f"💀 HEAD-TO-HEAD: Opponent is equal/longer ({opponent_length} vs {my_length})"], "direction": direction}

    reasons.append("✅ IMMEDIATE SURVIVAL: Safe from instant death")

    # ========================================================================
    # PHASE 2: SPACE ANALYSIS - MOST CRITICAL IN CONSTRICTOR MODE!
    # ========================================================================

    # Detect if this move will trap us
    trap_analysis = detect_self_trap_constrictor(new_head, game_state, lookahead=10)

    if trap_analysis["is_trapped"]:
        # This move will trap us - REJECT!
        score -= 5000000
        reasons.append(f"💀 SELF-TRAP: Only {trap_analysis['reachable_space']} cells, need {trap_analysis['required_space']}!")
        return {"score": score, "reasons": reasons, "direction": direction}

    if trap_analysis["is_dangerous"]:
        # Risky move - limited space
        danger_penalty = 2000000
        score -= danger_penalty
        reasons.append(f"⚠️  DANGEROUS SPACE: Only {trap_analysis['reachable_space']} cells available (-{danger_penalty})")
    else:
        # Good space!
        space_bonus = min(trap_analysis["reachable_space"] * 5000, 500000)
        score += space_bonus
        reasons.append(f"🌊 GOOD SPACE: {trap_analysis['reachable_space']} cells reachable (+{space_bonus})")

    # Bonus for space margin (how much extra space we have)
    if trap_analysis["space_margin"] > 20:
        margin_bonus = min(trap_analysis["space_margin"] * 2000, 200000)
        score += margin_bonus
        reasons.append(f"✅ SPACE MARGIN: +{trap_analysis['space_margin']} extra cells (+{margin_bonus})")

    # ========================================================================
    # PHASE 3: OPPONENT CUTOFF & PREDICTIVE BLOCKING - KILL THEM!
    # ========================================================================

    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != game_state["you"]["id"]]

    total_cutoff_value = 0
    total_blocking_value = 0

    for opponent in opponents:
        # Calculate cutoff value (trapping them in small space)
        cutoff_analysis = calculate_opponent_cutoff_value_constrictor(new_head, opponent, game_state)

        if cutoff_analysis["can_cutoff"]:
            score += cutoff_analysis["cutoff_value"]
            total_cutoff_value += cutoff_analysis["cutoff_value"]

            if cutoff_analysis["opponent_is_trapped"]:
                reasons.append(f"🎯🎯 OPPONENT TRAPPED: {cutoff_analysis['opponent_space']} cells! (+{cutoff_analysis['cutoff_value']})")
            else:
                reasons.append(f"✂️  CUTTING OFF OPPONENT: Space advantage {cutoff_analysis['space_advantage']} (+{cutoff_analysis['cutoff_value']})")

        # Calculate predictive blocking value (blocking their best moves)
        blocking_value = calculate_blocking_value_constrictor(new_head, opponent, game_state)
        if blocking_value > 0:
            score += blocking_value
            total_blocking_value += blocking_value
            reasons.append(f"🚧 BLOCKING OPPONENT: Cutting off their best moves (+{blocking_value})")

    # ========================================================================
    # PHASE 4: CENTER CONTROL - MAXIMIZE OPTIONS
    # ========================================================================

    center_value = find_center_control_value(new_head, board_width, board_height)
    score += center_value

    if center_value > 70000:
        reasons.append(f"👑 CENTER CONTROL: Dominating center (+{center_value})")
    elif center_value > 40000:
        reasons.append(f"📍 GOOD POSITION: Near center (+{center_value})")

    # ========================================================================
    # PHASE 5: AVOID EDGES - EDGES ARE DEATH IN CONSTRICTOR MODE!
    # ========================================================================

    is_edge = (new_head["x"] == 0 or new_head["x"] == board_width - 1 or
               new_head["y"] == 0 or new_head["y"] == board_height - 1)
    is_corner = (new_head["x"] == 0 or new_head["x"] == board_width - 1) and \
                (new_head["y"] == 0 or new_head["y"] == board_height - 1)

    if is_corner:
        corner_penalty = 800000
        score -= corner_penalty
        reasons.append(f"🚫 CORNER: DEATH TRAP in constrictor! (-{corner_penalty})")
    elif is_edge:
        edge_penalty = 400000
        score -= edge_penalty
        reasons.append(f"⚠️  EDGE: Very dangerous in constrictor (-{edge_penalty})")

    # ========================================================================
    # PHASE 6: SPACE EFFICIENCY - PREFER MOVES THAT DON'T WASTE SPACE
    # ========================================================================

    # Count how many adjacent cells are already occupied
    adjacent_occupied = 0
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        check_x, check_y = new_head["x"] + dx, new_head["y"] + dy
        if not (0 <= check_x < board_width and 0 <= check_y < board_height):
            continue

        # Check if this cell is occupied by any snake
        for snake in game_state["board"]["snakes"]:
            for segment in snake["body"]:
                if segment["x"] == check_x and segment["y"] == check_y:
                    adjacent_occupied += 1
                    break

    # Prefer moves that don't create isolated pockets
    if adjacent_occupied >= 3:
        # This move creates a dead-end or pocket - BAD!
        pocket_penalty = 300000
        score -= pocket_penalty
        reasons.append(f"⚠️  CREATING POCKET: {adjacent_occupied} sides blocked (-{pocket_penalty})")

    return {"score": score, "reasons": reasons, "direction": direction}


# Global variable to track recent moves (for anti-pattern detection)
recent_moves = []

def move(game_state: typing.Dict) -> typing.Dict:
    """
    Main move function with fast, reliable move evaluation.
    Optimized for sub-500ms response time.
    """
    global recent_moves

    import time
    start_time = time.time()

    # Get all possible moves (using helper function for consistency)
    my_head = game_state["you"]["body"][0]
    my_id = game_state["you"]["id"]
    my_health = game_state["you"]["health"]
    my_length = len(game_state["you"]["body"])
    board_width = game_state["board"]["width"]
    board_height = game_state["board"]["height"]

    opponents = [s for s in game_state["board"]["snakes"] if s["id"] != my_id]
    num_opponents = len(opponents)

    turn = game_state["turn"]

    # ========================================================================
    # DETECT GAME MODE - CONSTRICTOR VS STANDARD
    # ========================================================================

    constrictor_mode = is_constrictor_mode(game_state)

    print(f"\n{'='*80}")
    if constrictor_mode:
        print(f"🐍 WARRIORX CONSTRICTOR MODE - TURN {turn}")
        print(f"{'='*80}")
        print(f"⚡ CONSTRICTOR RULES: No food, always growing, can't revisit cells!")
    else:
        print(f"🧠 WARRIORX BATTLESNAKE - TURN {turn}")
        print(f"{'='*80}")
    print(f"📍 Position: ({my_head['x']}, {my_head['y']}) | Health: {my_health} | Length: {my_length}")
    print(f"🎮 Opponents: {num_opponents} | Board: {board_width}x{board_height}")

    possible_moves = get_possible_moves(game_state["you"], board_width, board_height)

    print(f"🎯 Valid moves from get_possible_moves(): {possible_moves}")

    if not possible_moves:
        # CRITICAL: No valid moves means we're completely trapped!
        # Don't try wall moves - just pick the "least bad" option
        print("🚨 CRITICAL: No valid moves found! Snake is completely trapped!")
        print("   This means all 4 directions are either walls or backwards.")
        print("   Choosing a random direction as last resort (will likely die).")
        import random
        possible_moves = [random.choice(["up", "down", "left", "right"])]

    # Log current position details
    print(f"\n📊 Current State:")
    print(f"   Head: ({my_head['x']}, {my_head['y']})")
    if len(game_state["you"]["body"]) > 1:
        neck = game_state["you"]["body"][1]
        print(f"   Neck: ({neck['x']}, {neck['y']})")
    print(f"   Body length: {my_length}")
    print(f"   Recent moves: {recent_moves[-5:] if recent_moves else 'None'}")

    # ========================================================================
    # COMPREHENSIVE GAME TREE SEARCH
    # ========================================================================

    # ========================================================================
    # FAST EVALUATION: Use evaluate_move() for speed and reliability
    # ========================================================================
    # The comprehensive minimax is too slow for 500ms timeout
    # Using the faster evaluate_move() function instead

    if constrictor_mode:
        print(f"\n🐍 CONSTRICTOR MODE EVALUATION")
        print(f"   Strategy: Maximize space, avoid self-trap, cut off opponents!")
        print(f"{'='*80}")
    else:
        print(f"\n🔍 FAST MOVE EVALUATION")
        print(f"   Using optimized evaluation for sub-500ms response time...")
        print(f"{'='*80}")

    # Evaluate all possible moves with prediction
    move_evaluations = []
    for direction in possible_moves:
        # Use constrictor evaluation if in constrictor mode
        if constrictor_mode:
            evaluation = evaluate_move_constrictor(direction, game_state)
        else:
            evaluation = evaluate_move(direction, game_state, use_prediction=True)

        # ANTI-PATTERN: Penalize repeating the same direction too many times
        # (Less important in constrictor mode since we can't revisit cells anyway)
        if not constrictor_mode and len(recent_moves) >= 3:
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
    # OR prefer head-to-head with equal snake over solo death!
    if best_move["score"] <= -5000:
        print("⚠️  DESPERATION MODE: All moves look fatal! Finding best death option...")

        # Re-evaluate each move focusing on survival or taking opponent with us
        survival_evaluations = []
        my_length = len(game_state["you"]["body"])

        # CRITICAL FIX: Only evaluate VALID moves, not all 4 directions!
        # This prevents choosing wall moves in desperation
        for direction in possible_moves:
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
                death_type = "wall"
            else:
                # Check if this is a head-to-head collision with equal snake
                is_equal_head_to_head = False
                for snake in game_state["board"]["snakes"]:
                    if snake["id"] == game_state["you"]["id"]:
                        continue
                    snake_head = snake["body"][0]
                    snake_length = len(snake["body"])

                    # Check if opponent could move to same position
                    if abs(snake_head["x"] - new_head["x"]) + abs(snake_head["y"] - new_head["y"]) == 1:
                        if snake_length == my_length:
                            is_equal_head_to_head = True
                            break

                if is_equal_head_to_head:
                    # PREFER THIS! Take the opponent with us!
                    survival_score = -10000  # Bad, but better than solo death
                    death_type = "mutual_destruction"
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
                        death_type = "survival"
                    else:
                        survival_score = -50000
                        death_type = "immediate_death"

            survival_evaluations.append({
                "direction": direction,
                "score": survival_score,
                "reasons": [f"{death_type}: {survival_score}"]
            })

        # Pick the move with best survival (or mutual destruction over solo death)
        survival_evaluations.sort(key=lambda x: x["score"], reverse=True)
        best_move = survival_evaluations[0]
        print(f"   Desperation choice: {best_move['direction'].upper()} ({best_move['reasons'][0]})")

    print(f"\n{'='*60}")
    print(f"MOVE {turn} | Health: {game_state['you']['health']} | Length: {len(game_state['you']['body'])}")
    print(f"{'='*60}")
    print(f"\nMove Evaluations:")
    for eval in move_evaluations:
        # Show more reasons to see trapping logic
        reasons_str = ', '.join(eval['reasons'][:5]) if eval['reasons'] else "No reasons"
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
            print(f"   ⚠️  WARNING: Returning unsafe move as last resort!")
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
    elapsed_time = time.time() - start_time
    print(f"\n🚀 RETURNING JSON RESPONSE: {json.dumps(response)}")
    print(f"🚀 MOVE BEING SENT TO GAME: {chosen_direction.upper()}")
    print(f"⏱️  Total time: {elapsed_time*1000:.1f}ms\n")

    return response


# Start server when `python main.py` is run
if __name__ == "__main__":
    from server import run_server

    run_server({"info": info, "start": start, "move": move, "end": end})

