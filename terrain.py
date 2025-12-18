import math

# Terrain module handles ground height generation and caches
terrain_points = {}
current_level = 1

def set_current_level(level):
    global current_level
    current_level = level

def generate_height(x):
    base = 600 - 140 - (current_level - 1) * 15
    return base + math.sin(x * 0.006) * 20 + math.sin(x * 0.02) * 5

def get_ground_height(x):
    if x not in terrain_points:
        terrain_points[x] = generate_height(x)
    return terrain_points[x]

def clear_terrain():
    terrain_points.clear()
