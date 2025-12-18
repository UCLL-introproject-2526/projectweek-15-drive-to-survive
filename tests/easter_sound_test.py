"""Test that EasterEgg loads and plays the pop sound when collided with a mock car.
Run with: python -m tests.easter_sound_test
"""
import os
import time
import pygame

os.environ.setdefault('SDL_VIDEODRIVER', 'windows')
pygame.init()
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
except Exception as e:
    print('Mixer init failed:', e)

from easter_egg import EasterEgg

print('mixer state =', pygame.mixer.get_init())
e = EasterEgg(x_position=0)
print('pop_sound initially =', e.pop_sound)

# Create a minimal mock car with bounding rect overlapping the egg
class MockCar:
    def __init__(self):
        self.world_x = 0
        self.y = 0
        self.rect = pygame.Rect(0, 0, 60, 60)

car = MockCar()
print('Calling check_collision...')
res = e.check_collision(car)
print('check_collision returned', res)
print('pop_sound after collision =', e.pop_sound)
# Allow short time for sound to play (if any)
time.sleep(0.5)
print('test complete')
