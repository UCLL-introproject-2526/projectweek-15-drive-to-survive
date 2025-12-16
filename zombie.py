import pygame

class Zombie:
    def __init__(self, x):
        self.x = x
        self.alive = True
        self.rect = pygame.Rect(0, 0, 22, 40)

    def update(self, car, terrain):
        """Update zombie and check collision with car"""
        if self.alive and self.rect.colliderect(car.rect):
            self.alive = False
            car.take_damage(10)  # Use take_damage method
            return 10  # Money reward
        return 0

    def draw(self, srf, cam_x, terrain):
        """Draw zombie on screen"""
        if self.alive:
            sx = self.x - cam_x + 1024//3 - self.rect.width//2
            sy = terrain.get_ground_height(self.x) - self.rect.height
            self.rect.topleft = (sx, sy)
            pygame.draw.rect(srf, (0, 200, 0), self.rect, border_radius=4)

def spawn_zombies(level):
    """Spawn zombies for the given level"""
    zombies = []
    for x in range(600, 10000, 600):
        zombies.append(Zombie(x))
    return zombies

class normalZombie:
    def __init__(self, level):
        self.__set_health(level)
        self.__set_speed(level)
    
    def __set_health(self, level):
        #health word per level exponentieel verhoogd met 10%
        self.__health = 50 * (1.1 ** level)
        
    def __set_speed(self, level):
        pass

class bigZombie:
    def __init__(self, level):
        self.__set_health(level)
        self.__set_speed(level)

    def __set_health(self, level):
        #health word per level exponentieel verhoogd met 10%
        self.__health = 200 * (1.1 ** level)
    
    def __set_speed(self, level):
        pass