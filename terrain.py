import pygame
import math

class Terrain:
    def __init__(self):
        self.terrain_points = {}
        self.TERRAIN_STEP = 10
        self.GROUND_COLOR = (110, 85, 55)
        self.GROUND_DARK_COLOR = (80, 60, 40)

    def generate_height(self, x):
        base = 768 - 140
        return base + math.sin(x * 0.006) * 20 + math.sin(x * 0.02) * 5
    
    def get_ground_height(self, x):
        if x not in self.terrain_points:
            self.terrain_points[x] = self.generate_height(x)
        return self.terrain_points[x]
    
    def draw_ground(self, srf, cam_x):
        pts = []
        start = int(cam_x) - 400
        for x in range(start, start + 1024 + 800, self.TERRAIN_STEP):
            sx = x - cam_x + 1024//3
            pts.append((sx, self.get_ground_height(x)))
        pts += [(1024, 768), (0, 768)]
        pygame.draw.polygon(srf, self.GROUND_COLOR, pts)
        pygame.draw.lines(srf, self.GROUND_DARK_COLOR, False, pts[:-2], 3)
