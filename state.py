# Shared mutable game state
money = 1000
distance = 0
current_level = 1

def reset_state():
    global money, distance, current_level
    money = 1000
    distance = 0
    current_level = 1
