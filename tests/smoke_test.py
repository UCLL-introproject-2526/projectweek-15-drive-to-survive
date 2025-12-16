"""Simple smoke tests for core game flows.
Run with: python -m tests.smoke_test
"""
import os
import pygame
import sys

os.environ.setdefault('SDL_VIDEODRIVER', 'windows')
pygame.init()
pygame.display.set_mode((100, 100))

from car_types import load_car_types, set_current_car_type, ALL_CAR_TYPES
from upgrades import load_upgrades, save_all_upgrades_status, load_all_upgrades_status
from car import Car
from terrain import get_ground_height
import state

print("--- Smoke test: load car types and upgrades ---")
load_car_types()
# ensure a default is selected
for name, ct in ALL_CAR_TYPES.items():
    if ct.is_default:
        set_current_car_type(name)
        print('Selected default car:', name)
        break

car = Car(apply_upgrades_now=False)
upgrades = load_upgrades()
print('Available upgrades:', [u.name for u in upgrades])

# purchase Ramp if present
ramp = next((u for u in upgrades if u.name.lower() == 'ramp'), None)
if ramp:
    print('Ramp purchased before:', ramp.purchased)
    car.purchase_upgrade(ramp)
    print('Ramp after purchase:', ramp.purchased, ramp.equipped)
else:
    print('No Ramp upgrade found; skipping purchase test')

# save and restore status
save_all_upgrades_status()
# change selection and reload
for n in list(ALL_CAR_TYPES.keys()):
    set_current_car_type(n)
load_all_upgrades_status()
upgrades_after = load_upgrades()
ra = next((u for u in upgrades_after if u.name.lower()=='ramp'), None)
print('Ramp after reload:', (ra.purchased, ra.equipped) if ra else None)

# drive simulation
print('\n--- Smoke test: drive simulation ---')
car = Car(apply_upgrades_now=True)
# simple pressed object
class Press:
    def __getitem__(self, k):
        return 1 if k == pygame.K_RIGHT else 0

press = Press()
airborne = False
for f in range(400):
    car.update(press)
    if car.vspeed < 0 or car.y < (get_ground_height(int(car.world_x)) - car.rect.height - 1):
        airborne = True
        break
print('Car became airborne during simulation:', airborne)
print('Final state: x=%.1f y=%.1f angle=%.2f health=%s' % (car.world_x, car.y, car.angle, car.health))

# Collision test: spawn a zombie at the car's x and ensure collision happens
from zombies import Zombie
z = Zombie(car.world_x)
# Show rects before update for diagnostics
print('Before update: car.rect =', car.rect, 'z.rect (unpositioned) =', z.rect)
money = z.update(car, get_ground_height)
# Show rects after update for diagnostics
print('After update: car.rect =', car.rect, 'z.rect =', z.rect)
print('Rect overlap?', car.rect.colliderect(z.rect))
print('Collision test: money returned =', money, 'car health =', car.health)
print('\nSmoke tests finished')
