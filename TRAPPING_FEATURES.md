# Trapping & Aggressive Play Features

## New Features Added

### 1. **Enhanced Edge/Corner Avoidance**
**Location**: `main.py` lines 1608-1635

**What it does**:
- Penalizes moves that go to edges and corners
- Penalty scales with number of opponents (more opponents = avoid edges more)
- Corner penalty: 35,000 base (very dangerous)
- Edge penalty: 15,000 base (dangerous)
- Near-edge penalty: 6,000 (when snake is longer than 5)

**Why it matters**:
- Edges and corners are common trap locations
- With more opponents, edges become even more dangerous
- Helps snake stay in open space where it has more options

**Example**:
```
With 1 opponent:
- Corner penalty: -52,500
- Edge penalty: -22,500

With 2 opponents:
- Corner penalty: -70,000
- Edge penalty: -30,000
```

### 2. **Opponent Trap Detection**
**Location**: `main.py` lines 1190-1268 (`detect_opponent_trap_opportunity` function)

**What it does**:
- Analyzes each opponent to see if they're vulnerable to being trapped
- Checks:
  - Number of escape routes opponent has
  - Amount of space available to opponent
  - Whether opponent is near edge/corner
  - Distance from our snake to opponent
  - Which escape routes we can block

**Returns**:
- `can_trap`: Boolean - can we trap this opponent?
- `trap_value`: Score value for trapping opportunity
- `opponent_escapes`: How many escape routes they have
- `is_vulnerable`: Are they in a weak position?
- `escape_positions`: List of positions they can escape to

**Vulnerability criteria**:
- 2 or fewer escape routes
- Limited space (less than 3x their length)
- Near edge or corner
- We're close enough to cut them off (distance ≤ 3)

### 3. **Aggressive Trapping Behavior**
**Location**: `main.py` lines 1655-1729

**What it does**:
- When opponent is vulnerable, actively tries to trap them
- Rewards moves that:
  - Block opponent's escape routes (+60,000 if adjacent to escape)
  - Threaten opponent's escapes (+25,000 if 2 cells away)
  - Finish off already-trapped opponents (+80,000 if adjacent)
  - Get close to trapped opponents (+40,000 if 2 cells away)

**Special bonuses**:
- "EXCELLENT TRAP" bonus: +40,000 when trap value > 50,000
- "VULNERABLE TARGET" bonus: +15,000 when hunting smaller vulnerable snake
- "OPPONENT TRAPPED" bonus: +80,000 when adjacent to trapped opponent

**Example scenarios**:
```
Scenario 1: Opponent in corner with 1 escape
- Detect they have 1 escape route
- Move to block that escape: +60,000
- Total trap value: ~110,000

Scenario 2: Opponent already trapped (0 escapes)
- Detect they're trapped
- Move adjacent to finish them: +80,000
- Excellent trap bonus: +40,000
- Total bonus: +120,000
```

### 4. **Mutual Kill Logic**
**Location**: `main.py` lines 1553-1579

**What it does**:
- When we're in a bad position (trapped or about to die), prefer taking opponent down with us
- Recognizes when mutual destruction is better than dying alone

**Scenarios**:

**Equal-size head-to-head**:
- Normal situation: -80,000 (avoid mutual kill)
- We're trapped/dangerous: +50,000 (take them with us!)

**Larger opponent head-to-head**:
- Normal situation: -200,000 (we die, avoid!)
- We're already doomed: +20,000 (kamikaze attack!)

**Why it matters**:
- If we're going to die anyway, might as well deny opponent the win
- Better to draw than lose
- Can turn a loss into a tie

**Example**:
```
Situation: We're in a corner with 1 escape, opponent blocks it
- Without mutual kill logic: Try to escape (fail and die alone)
- With mutual kill logic: Go for head-to-head (both die, it's a draw)
```

## How It Works Together

### Example Game Scenario

**Turn 15**: Opponent is on edge with 2 escape routes
```
1. Detect opponent is vulnerable (2 escapes, on edge)
2. Calculate which moves block their escapes
3. Move toward their escape routes
4. Bonus: +60,000 for blocking escape
5. Result: Opponent gets trapped
```

**Turn 16**: Opponent now has 0 escapes (trapped!)
```
1. Detect opponent is trapped (0 escapes)
2. Move adjacent to finish them off
3. Bonus: +80,000 for finishing trapped opponent
4. Bonus: +40,000 for excellent trap
5. Result: Opponent dies, we win!
```

**Alternative Turn 16**: We're also trapped
```
1. Detect we're in dangerous position (1 escape)
2. Detect opponent is also trapped
3. Mutual kill logic activates
4. Bonus: +50,000 for mutual kill (better than dying alone)
5. Result: Both die, it's a draw (better than losing)
```

## Testing

Run the trapping tests:
```bash
python3 test_trapping.py
```

Expected behaviors:
1. ✅ Moves toward cornered opponents to trap them
2. ✅ Avoids edges and corners when possible
3. ✅ Prefers mutual kill when already trapped
4. ✅ Actively blocks opponent escape routes

## Configuration

### Tuning Trap Aggression

To make snake MORE aggressive at trapping:
- Increase `cutoff_value` bonuses (lines 1684-1691)
- Increase `trap_value` calculation (lines 1227-1237)
- Lower distance threshold for trapping (line 1225)

To make snake LESS aggressive at trapping:
- Decrease bonuses
- Increase distance threshold
- Add health/length requirements

### Tuning Edge Avoidance

To avoid edges MORE:
- Increase `edge_multiplier` (line 1623)
- Increase base penalties (lines 1626-1633)

To avoid edges LESS:
- Decrease multiplier
- Decrease base penalties
- Add exceptions for certain situations

## Performance Impact

- **Response time**: Still 1-5ms (no significant impact)
- **Computation**: Minimal - just flood fill and distance calculations
- **Memory**: Negligible - small data structures

## Strategic Impact

### Before:
- Snake would avoid edges but not aggressively
- No active trapping of opponents
- Would die alone when trapped
- Missed opportunities to eliminate opponents

### After:
- Snake actively hunts vulnerable opponents
- Cuts off escape routes strategically
- Prefers mutual kill over solo death
- More aggressive and competitive gameplay

## Future Enhancements

Possible improvements:
1. **Predictive trapping**: Simulate opponent moves to predict where they'll be trapped
2. **Multi-turn trapping**: Plan 2-3 moves ahead to set up traps
3. **Coordinated trapping**: Work with other snakes to trap a common enemy
4. **Escape route prioritization**: Block the best escape routes first
5. **Health-based aggression**: Be more aggressive when we have health advantage

## Summary

The snake now:
- ✅ Avoids edges and corners more intelligently
- ✅ Detects when opponents are vulnerable
- ✅ Actively tries to trap opponents
- ✅ Blocks opponent escape routes
- ✅ Prefers mutual kill when already doomed
- ✅ Makes more aggressive, competitive decisions

This should significantly improve win rate in competitive games!

