# Testing Guide for WarriorX Battlesnake

## Quick Start

### 1. Run the Server
```bash
python3 main.py
```

You should see:
```
Running Battlesnake at http://0.0.0.0:5000
```

### 2. Test the Snake is Working

#### Option A: Quick Test (Recommended)
```bash
python3 test_quick.py
```

Expected output:
- ✅ Multiple different moves (not just "up")
- ✅ Response times under 10ms
- ✅ No errors

#### Option B: Game Simulation
```bash
python3 test_game_simulation.py
```

Expected output:
- ✅ Snake makes varied moves over 10 turns
- ✅ Snake navigates toward food
- ✅ "SUCCESS: Snake is making varied moves!"

#### Option C: Manual curl Test
```bash
curl -X POST http://localhost:5000/move \
  -H "Content-Type: application/json" \
  -d '{
    "game": {"id": "test", "timeout": 500},
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
  }'
```

Expected response:
```json
{"move": "right", "shout": "Feeling good!"}
```
(or "up", "down", "left" - should vary)

### 3. Play on Battlesnake.com

1. Go to https://play.battlesnake.com
2. Create/login to your account
3. Create a new Battlesnake
4. Enter your server URL (e.g., `https://your-server.com` or use ngrok for local testing)
5. Start a game!

## What to Look For

### ✅ Good Signs
- Snake makes different moves (up, down, left, right)
- Response times are 1-10ms
- Snake navigates toward food
- Snake avoids walls and its own body
- No error messages in logs

### ❌ Bad Signs
- Snake only goes "up"
- Response times >100ms
- Snake crashes into walls immediately
- Lots of error messages
- "Empty reply from server" errors

## Troubleshooting

### Problem: Snake still going only "up"

**Check 1**: Is the server actually running?
```bash
curl http://localhost:5000/
```
Should return snake info (color, head, tail)

**Check 2**: Are there errors in the logs?
Look for:
```
🚨🚨🚨 EXCEPTION IN MOVE HANDLER
```

**Check 3**: Is the game state valid?
The game engine should send proper JSON with:
- `game`, `turn`, `board`, `you` fields
- Valid snake positions
- Valid board dimensions

### Problem: Server crashes or times out

**Check 1**: Python version
```bash
python3 --version
```
Should be Python 3.7+

**Check 2**: Dependencies installed
```bash
python3 -m pip install -r requirements.txt
```

**Check 3**: Port already in use
```bash
lsof -i :5000
```
Kill any existing process on port 5000

### Problem: Snake makes bad decisions

**Check 1**: Review the logs
The snake logs its decision-making process:
```
Move Evaluations:
  right: 202000 - ✅ IMMEDIATE SURVIVAL: Safe from instant death, ...
  down: 130000 - ✅ IMMEDIATE SURVIVAL: Safe from instant death, ...
```

**Check 2**: Adjust scoring weights
Edit `main.py` in the `evaluate_move()` function to tune:
- Food seeking behavior
- Space preference
- Corner avoidance
- etc.

## Understanding the Logs

### Normal Move Log
```
🎯 MOVE REQUEST - Game: abc123, Turn: 5
🧠 WARRIORX BATTLESNAKE - TURN 5
📍 Position: (3, 3) | Health: 80 | Length: 3
🎮 Opponents: 1 | Board: 11x11
🎯 Valid moves from get_possible_moves(): ['up', 'down', 'left', 'right']

📊 Current State:
   Head: (3, 3)
   Neck: (3, 4)
   Body length: 3
   Recent moves: ['right', 'up']

Move Evaluations:
  right: 202000 - ✅ IMMEDIATE SURVIVAL, ✅ SAFE POSITION: 3 escape routes
  down: 130000 - ✅ IMMEDIATE SURVIVAL, ✅ SAFE POSITION: 3 escape routes
  left: 130000 - ✅ IMMEDIATE SURVIVAL, ✅ SAFE POSITION: 3 escape routes
  up: -1000000 - 💀 SELF COLLISION

>>> CHOSEN: RIGHT (score: 202000)

🚀 MOVE BEING SENT TO GAME: RIGHT
⏱️  Total time: 3.2ms
```

### What Each Section Means

- **🎯 MOVE REQUEST**: Incoming request from game engine
- **📍 Position**: Current snake location and stats
- **🎯 Valid moves**: Moves that don't go backwards or into walls
- **📊 Current State**: Detailed position info
- **Move Evaluations**: Score for each possible move
  - Higher score = better move
  - Negative scores = dangerous/deadly moves
- **>>> CHOSEN**: Final decision
- **⏱️ Total time**: How long the decision took

## Performance Benchmarks

### Expected Performance
- **Response time**: 1-10ms (well under 500ms limit)
- **Move variety**: Should use all 4 directions
- **Survival rate**: Should survive >10 turns in most games
- **Food seeking**: Should navigate toward food when health <70

### Test Results
```
Test 1 (Middle): RIGHT (3.3ms) ✅
Test 2 (Corner): RIGHT (1.0ms) ✅
Test 3 (Sequence): LEFT, RIGHT, LEFT, RIGHT, LEFT (varied) ✅
Simulation: 10 turns, 3 unique moves (up, right, left) ✅
```

## Next Steps

1. ✅ **Verify fixes work**: Run `python3 test_quick.py`
2. ✅ **Test locally**: Start server and test with curl
3. 🎮 **Play games**: Test on play.battlesnake.com
4. 🔧 **Tune behavior**: Adjust scoring in `evaluate_move()` if needed
5. 📊 **Monitor performance**: Watch logs for any issues

## Files Changed

- `main.py`: Disabled slow minimax, added logging, improved move selection
- `server.py`: Better error handling, added request logging
- `test_quick.py`: Quick test suite (NEW)
- `test_game_simulation.py`: Game simulation test (NEW)
- `FIXES_APPLIED.md`: Detailed explanation of fixes (NEW)
- `TESTING_GUIDE.md`: This file (NEW)

## Support

If you encounter issues:
1. Check the logs for error messages
2. Run the test files to verify basic functionality
3. Review `FIXES_APPLIED.md` for technical details
4. Check that all dependencies are installed
5. Verify Python version is 3.7+

Good luck and happy snake battling! 🐍⚔️

