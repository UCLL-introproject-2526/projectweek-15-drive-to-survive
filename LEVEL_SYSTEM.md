# Level System Documentation

## Overview
The game now features a comprehensive level system with increasing difficulty as players progress through the game.

## Features

### 1. **Progressive Difficulty**
- 10 predefined levels with unique names and challenges
- Levels 11-50 automatically generated with scaling difficulty
- Each level has its own:
  - Distance requirement to complete
  - Number of zombies
  - Zombie health multiplier
  - Zombie damage multiplier
  - Completion bonus reward
  - Terrain difficulty rating

### 2. **Level Progression**
Players must complete distance requirements to advance to the next level:
- Level 1: 5,000m (Tutorial Zone)
- Level 2: 7,000m (The Suburbs)
- Level 3: 8,000m (City Outskirts)
- Level 4: 9,000m (Downtown)
- Level 5: 10,000m (Industrial Zone)
- Level 6: 11,000m (The Quarantine)
- Level 7: 12,000m (Military Base)
- Level 8: 13,000m (Ground Zero)
- Level 9: 14,000m (The Horde)
- Level 10: 15,000m (Final Stand)
- Level 11+: Increasing distances (Endless Mode)

### 3. **Difficulty Scaling**

#### Zombie Count
- Starts with 6 zombies in Level 1
- Increases to 30 zombies by Level 10
- Continues scaling in endless mode

#### Zombie Health
- Base health: 50 (normal), 100 (fat)
- Multiplied by level-specific factor
- Level 1: 1.0x, Level 10: 3.0x
- Continues scaling beyond Level 10

#### Zombie Damage
- Base damage: 10 (normal), 20 (fat)
- Multiplied by level-specific factor
- Level 1: 1.0x, Level 10: 2.0x
- Continues scaling beyond Level 10

#### Zombie Mix
- Ratio of fat zombies increases with level
- Starts at 15%, reaches up to 30%
- More dangerous enemies as you progress

### 4. **Rewards**
- Completion bonuses for finishing levels
- Level 1: $100, Level 10: $1,500
- Money from defeating zombies also scales with level
- Use rewards to purchase upgrades in the garage

### 5. **Visual Feedback**

#### Level Intro Screen
- Displays before each level starts
- Shows level number, description, and requirements
- Can be skipped by pressing any key

#### In-Game HUD
- Current level name and description at top
- Progress bar showing distance completion
- Distance counter (current / required)

### 6. **Game Over Conditions**
- **Health Depleted**: Car takes too much damage
- **Out of Fuel**: Fuel runs out before completing level
- **Level Complete**: Successfully reach distance requirement

## File Structure

### `levels.py` (New File)
Contains all level management logic:
- `LevelConfig`: Configuration class for individual levels
- `LevelManager`: Manages level progression and difficulty
- `get_level_manager()`: Global access to level system
- `reset_level_manager()`: Reset to level 1

### Modified Files

#### `zombies.py`
- Updated `Zombie` and `fatZombie` classes to accept level parameter
- Integrated with level manager for health/damage scaling
- Updated `spawn_zombies()` to use level manager for positioning

#### `run.py`
- Added level intro screen function
- Integrated level info display in game HUD
- Updated level completion logic with rewards
- Added level manager initialization

#### `state.py`
- Added level manager reset to `reset_state()`

## Usage

The level system is automatically integrated into the game. Players will:
1. See level intro screen when starting/completing levels
2. Track progress via the HUD
3. Receive completion bonuses
4. Face increasingly difficult challenges

## Customization

To modify level configurations, edit the `_initialize_levels()` method in `levels.py`:
- Adjust distance requirements
- Change zombie counts
- Modify difficulty multipliers
- Update rewards
- Change level descriptions

## Technical Details

### Level Manager
- Singleton pattern for global access
- Dynamically generates configurations for levels beyond 50
- Calculates zombie spawn positions based on level distance
- Provides level-scaled health and damage values

### Integration Points
- Zombie spawning uses level manager for positioning
- Zombie classes query level manager for stats
- Game loop checks level completion via level manager
- State management includes level reset functionality

## Future Enhancements

Potential additions:
- Boss battles at milestone levels
- Special events or modifiers per level
- Unlock requirements for certain levels
- Leaderboards per level
- Time attack modes
