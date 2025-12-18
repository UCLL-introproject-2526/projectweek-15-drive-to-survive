# Shared mutable game state
money = 100000
distance = 0
current_level = 1
easter_egg_activated = False
in_survival_mode = False  # Flag to track if we're in survival mode

def reset_state():
    global money, distance, current_level, easter_egg_activated, in_survival_mode
    money = 0
    distance = 0
    current_level = 1
    easter_egg_activated = False
    in_survival_mode = False
    # Reset level manager when resetting game state
    from levels import reset_level_manager
    reset_level_manager()
