# Shared mutable game state
money = 100000
distance = 0
current_level = 1

def reset_state():
    global money, distance, current_level
    money = 0
    distance = 0
    current_level = 1
    # Reset level manager when resetting game state
    from levels import reset_level_manager
    reset_level_manager()
