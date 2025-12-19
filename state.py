# Shared mutable game state
money = 0
distance = 0
current_level = 1
easter_egg_activated = False
in_survival_mode = False  # Flag to track if we're in survival mode
kills = 0  # Track total kills across all levels

def reset_state():
    global money, distance, current_level, easter_egg_activated, in_survival_mode, kills
    money = 0
    distance = 0
    current_level = 1
    easter_egg_activated = False
    in_survival_mode = False
    kills = 0
    # Reset level manager when resetting game state
    from levels import reset_level_manager
    reset_level_manager()
