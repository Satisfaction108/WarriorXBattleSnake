# WarriorX Battlesnake

## Overview
This is an advanced Battlesnake AI built with Python and Flask. The snake uses sophisticated algorithms including:
- BFS pathfinding for shortest paths
- Flood fill for space evaluation
- Voronoi space control calculations
- Predictive collision avoidance
- Strategic gameplay with health and food management

## Project Structure
- `main.py` - Core Battlesnake logic and AI algorithms
- `server.py` - Flask server that handles Battlesnake API endpoints
- `requirements.txt` - Python dependencies (Flask 2.3.2)

## Technologies
- **Language**: Python 3.11
- **Framework**: Flask 2.3.2
- **API**: Battlesnake API v1

## API Endpoints
- `GET /` - Returns snake info (color, head, tail)
- `POST /start` - Called when game starts
- `POST /move` - Called each turn to get next move
- `POST /end` - Called when game ends

## Running Locally
The server runs on port 5000 and is accessible at the Replit webview URL.

## Deployment
This Battlesnake is ready to be published and registered at [play.battlesnake.com](https://play.battlesnake.com). The public URL from Replit deployment can be used as the Battlesnake endpoint.

## Recent Changes
- **Nov 9, 2025 (Latest Update)**: Critical bug fixes and strategy rebalancing
  - **Bug Fixes**: Fixed crashes caused by comparing direction strings with coordinates, fixed Voronoi calculation parameter mismatch
  - **Balanced Food Strategy**: Food-seeking now conditional on safety - only pursues risky food when desperate (health < 30)
  - **Enhanced Trap Avoidance**: Increased edge/corner penalties (corners -30k, edges -12k), better escape route evaluation
  - **Improved Center Control**: Dynamic center scoring that scales with snake size, rewards center dominance
  - **Safety-First Growth**: Snake will grow aggressively but only when safe - won't suicide for food anymore
  
- **Nov 9, 2025 (Earlier)**: Major AI improvements for dominance
  - **Opportunistic Food Eating**: Bot now grabs safe food even when healthy to grow larger
  - **Head-to-Head Mastery**: Threat mapping prevents collisions with larger/equal snakes, pursues smaller snakes aggressively
  - **Size Dominance Strategy**: When bigger, bot chases smaller snakes (up to +900 bonus), denies them food (+250 bonus)
  - **Advanced Food Prioritization**: Composite scoring considers safety, distance, growth benefit, opponent competition, and escape space
  
- **Nov 9, 2025**: Initial Replit setup
  - Configured Python 3.11 environment
  - Installed Flask dependencies
  - Set up workflow to run on port 5000
  - Updated .gitignore for Python project

## Snake Appearance
- **Color**: Black (#1a1a1a)
- **Head**: Skull (dead)
- **Tail**: Lightning bolt (bolt)
- **Name**: WarriorX

## Strategy
The AI uses an advanced multi-layered decision-making approach:

### Core Systems
1. **Safety First**: Avoids walls, bodies, and dangerous head-to-head collisions with larger/equal snakes
2. **Space Evaluation**: Flood fill ensures adequate room, requires 3x snake length for safety
3. **Predictive Analysis**: Minimax with alpha-beta pruning simulates 6-8 moves ahead
4. **Voronoi Territory Control**: Calculates space dominance for strategic positioning

### Food Strategy (Balanced Growth & Safety)
- **Conditional Food Pursuit**: Only chases food when it's safe OR health is critical (< 30)
- **Composite Value Scoring**: Evaluates each food by safety, distance, growth benefit, opponent competition, and escape space
- **Smart Eating**: Prioritizes safe food; only takes risky food when desperate
- **Health-Based Urgency**: Critical at < 15 health, high urgency at < 30, balanced otherwise
- **Safe Escape**: Validates escape routes and available space before committing to food

### Size Dominance (When Bigger)
- **Aggressive Pursuit**: Chases smaller snakes with distance-based bonuses (up to +900 points)
- **Food Denial**: Cuts off smaller opponents from food (+250 bonus per denial)
- **Head-to-Head Dominance**: Actively seeks head-to-head with smaller snakes (+2000 bonus)

### Defensive Play (When Smaller/Equal)
- **Threat Zone Avoidance**: Identifies dangerous tiles near larger/equal snake heads (-4000 penalty)
- **Distance Maintenance**: Stays away from larger opponents with scaled penalties
- **Space Maximization**: Prioritizes open areas when threatened

### Advanced Features
- **Anti-Predictability**: Randomizes moves with similar scores, penalizes repetitive patterns
- **Enhanced Edge Avoidance**: Strong penalties for corners (-30k) and edges (-12k), warns when near boundaries
- **Future Mobility**: Evaluates escape routes after each move (needs 3+ safe exits)
- **Center Control**: Dynamic scoring favoring center positions, scales with snake size for dominance
- **Desperation Mode**: When all moves look fatal, finds longest survival path
