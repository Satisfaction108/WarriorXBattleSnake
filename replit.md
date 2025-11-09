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
The AI uses a multi-layered decision-making approach:
1. Safety checks (avoid walls, bodies, head-to-head collisions)
2. Space evaluation (flood fill to ensure adequate room)
3. Food prioritization based on health urgency
4. Voronoi territory control for strategic positioning
5. Predictive opponent move simulation
