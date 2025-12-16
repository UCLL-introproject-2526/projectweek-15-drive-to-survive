from dataclasses import dataclass
from terrain import get_ground_height

@dataclass
class Zombie:
    x: int
    alive: bool = True
    rect = None

    def __post_init__(self):
        import pygame
        self.rect = pygame.Rect(0, 0, 22, 40)

    def update(self, car):
        # returns money gained
        if self.alive and self.rect.colliderect(car.rect):
            self.alive = False
            damage_taken = max(0, 10 - car.damage_reduction)
            car.health -= damage_taken
            return 10
        return 0

    def draw(self, cam_x, screen):
        if not self.alive:
            return
        sx = self.x - cam_x + 333 - self.rect.width//2
        sy = get_ground_height(self.x) - self.rect.height
        self.rect.topleft = (sx, sy)
        import pygame
        pygame.draw.rect(screen, (0,200,0), self.rect, border_radius=4)

def spawn_zombies(level):
    zombies = []
    for x in range(600, 10000, 600):
        zombies.append(Zombie(x))
    return zombies
