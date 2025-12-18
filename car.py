import importlib.util
import os
import math
import pygame
from typing import Any, cast
from terrain import get_ground_height
from upgrades import load_upgrades

# Physics constants
GRAVITY = 0.095  # pixels per frame^2
TERMINAL_VELOCITY = 30  # max fall speed (pixels/frame)
SLOPE_SAMPLE = 3  # how far to sample left/right when computing terrain slope (pixels)

# Launch behavior (used when hitting ramps at speed)
LAUNCH_SLOPE_THRESHOLD = 6  # minimum slope (pixels over sample width) to consider launching
LAUNCH_SPEED_THRESHOLD = 0.5  # min forward speed to trigger a launch
LAUNCH_FACTOR = 0.7  # fraction of forward speed converted into upward velocity

# Angular behavior
ANGULAR_FACTOR = 2.0  # multiplier to convert forward speed to angular velocity (deg per frame per speed unit)

class Car:
    def __init__(self, apply_upgrades_now=True, controls=None):
        self.world_x = 200
        self.speed = 0
        self.vspeed = 0
        self.angle = 0
        self.air_angle = None
        self.health = 40
        self.fuel = 100
        
        # Store controls (use defaults if not provided)
        if controls is None:
            self.controls = {
                'accelerate_right': pygame.K_RIGHT,
                'accelerate_left': pygame.K_LEFT,
                'shoot': pygame.K_e
            }
        else:
            self.controls = controls
        self.base_speed = 0.11
        self.base_damage = 10
        self.damage_reduction = 0
        self.speed_multiplier = 1.0
        self.fuel_consumption_rate = 0.08

        self.reload_car_image()

        self.rect = self.image.get_rect()
        self.y = get_ground_height(self.world_x) - self.rect.height
        self.upgrades_images = []
        self.upgrade_instances = []
        self.angular_velocity = 0.0  # degrees per frame

        if apply_upgrades_now:
            self.apply_equipped_upgrades()

    def reload_car_image(self):
        from car_types import get_current_car_type
        current_car = get_current_car_type()
        if current_car:
            self.base_image = current_car.image.copy()
            self.image = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), int(self.base_image.get_height()*0.2)))
        else:
            try:
                img = pygame.image.load("assets/car/car.png").convert_alpha()
                self.base_image = img
                self.image = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), int(self.base_image.get_height()*0.2)))
            except Exception:
                self.base_image = pygame.Surface((200, 100), pygame.SRCALPHA)
                pygame.draw.rect(self.base_image, (200, 50, 50), (0, 40, 200, 60))
                self.image = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), int(self.base_image.get_height()*0.2)))

    def apply_equipped_upgrades(self):
        upgrades = load_upgrades()
        self.reload_car_image()

        equipped_upgrades = [u for u in upgrades if u.equipped]
        equipped_upgrades.sort(key=lambda x: x.z_index)

        self.base_damage = 10
        self.damage_reduction = 0
        self.speed_multiplier = 1.0
        self.upgrades_images = []
        self.upgrade_instances = []

        for upgrade in equipped_upgrades:
            self.base_damage += upgrade.car_damage
            self.damage_reduction += upgrade.damage_reduction
            self.speed_multiplier += upgrade.speed_increase

            self.upgrades_images.append({'image': upgrade.image, 'z_index': upgrade.z_index, 'name': upgrade.name})

            if upgrade.has_script:
                try:
                    script_path = os.path.join(upgrade.folder, "script.py")
                    if os.path.exists(script_path):
                        spec = importlib.util.spec_from_file_location("upgrade_script", script_path)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            module = cast(Any, module)
                            module.WIDTH = 1000
                            module.HEIGHT = 600
                            module.get_ground_height = get_ground_height
                            # expose money and screen to script if needed
                            module.money_ref = lambda: __import__('state').money
                            module.screen = pygame.display.get_surface()
                            spec.loader.exec_module(module)
                            if hasattr(module, upgrade.name.replace(' ', '') + 'Upgrade'):
                                UpgradeClass = getattr(module, upgrade.name.replace(' ', '') + 'Upgrade')
                                instance = UpgradeClass(self)
                                instance._upgrade_ref = upgrade  # Store reference for equipped check
                                self.upgrade_instances.append(instance)
                                upgrade.script_instance = instance
                            elif hasattr(module, 'UpgradeScript'):
                                instance = module.UpgradeScript(self)
                                instance._upgrade_ref = upgrade  # Store reference for equipped check
                                self.upgrade_instances.append(instance)
                                upgrade.script_instance = instance
                except Exception as e:
                    print(f"Error loading upgrade script for {upgrade.name}: {e}")

        self.upgrades_images.sort(key=lambda x: x['z_index'])
        self.update_combined_image()

    def apply_upgrade(self, upgrade, equip=True):
        if equip:
            self.base_damage += upgrade.car_damage
            self.damage_reduction += upgrade.damage_reduction
            self.speed_multiplier += upgrade.speed_increase
            self.upgrades_images.append({'image': upgrade.image, 'z_index': upgrade.z_index, 'name': upgrade.name})
            self.upgrades_images.sort(key=lambda x: x['z_index'])
            if upgrade.has_script:
                try:
                    script_path = os.path.join(upgrade.folder, "script.py")
                    if os.path.exists(script_path):
                        spec = importlib.util.spec_from_file_location("upgrade_script", script_path)
                        if spec is not None and spec.loader is not None:
                            module = importlib.util.module_from_spec(spec)
                            module = cast(Any, module)
                            module.WIDTH = 1000
                            module.HEIGHT = 600
                            module.get_ground_height = get_ground_height
                            # expose money and screen to script if needed
                            module.money_ref = lambda: __import__('state').money
                            module.screen = pygame.display.get_surface()
                            spec.loader.exec_module(module)
                            if hasattr(module, upgrade.name.replace(' ', '') + 'Upgrade'):
                                UpgradeClass = getattr(module, upgrade.name.replace(' ', '') + 'Upgrade')
                                instance = UpgradeClass(self)
                                instance._upgrade_ref = upgrade  # Store reference for equipped check
                                self.upgrade_instances.append(instance)
                                upgrade.script_instance = instance
                            elif hasattr(module, 'UpgradeScript'):
                                instance = module.UpgradeScript(self)
                                instance._upgrade_ref = upgrade  # Store reference for equipped check
                                self.upgrade_instances.append(instance)
                                upgrade.script_instance = instance
                except Exception as e:
                    print(f"Error loading upgrade script for {upgrade.name}: {e}")
        else:
            self.base_damage -= upgrade.car_damage
            self.damage_reduction -= upgrade.damage_reduction
            self.speed_multiplier -= upgrade.speed_increase
            self.upgrades_images = [up for up in self.upgrades_images if up['name'] != upgrade.name]
            if upgrade.has_script and upgrade.script_instance:
                if upgrade.script_instance in self.upgrade_instances:
                    self.upgrade_instances.remove(upgrade.script_instance)
                upgrade.script_instance = None

        upgrade.equipped = equip
        upgrade.save_status()
        self.update_combined_image()

    def purchase_upgrade(self, upgrade):
        upgrade.purchased = True
        upgrade.equipped = True
        upgrade.save_status()
        self.apply_upgrade(upgrade, equip=True)

    def update_upgrades(self, keys, zombies):
        for upgrade_instance in self.upgrade_instances:
            if hasattr(upgrade_instance, 'update'):
                # Pass car reference so upgrades can access controls
                upgrade_instance.update(keys, zombies)

    def draw_upgrades(self, cam_x, screen):
        for upgrade_instance in self.upgrade_instances:
            if hasattr(upgrade_instance, 'draw'):
                upgrade_instance.draw(cam_x)

    def update_combined_image(self):
        scaled_base = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), int(self.base_image.get_height()*0.2)))
        combined = scaled_base.copy()
        for upgrade_data in self.upgrades_images:
            up_img = upgrade_data['image']
            up_scaled = pygame.transform.scale(up_img, (int(up_img.get_width()*0.2), int(up_img.get_height()*0.2)))
            combined.blit(up_scaled, (0, 0))
        self.image = combined
        self.rect = self.image.get_rect()

    def take_damage(self, amount: int):
        """Reduce car health by amount (minimum 0)."""
        try:
            amt = int(amount)
        except Exception:
            amt = 0
        self.health -= amt
        if self.health < 0:
            self.health = 0

    def update(self, keys):
        # 'keys' is expected to be the sequence returned by pygame.key.get_pressed()
        fuel_consumed = False
        if keys[self.controls['accelerate_right']] and self.fuel > 0:
            if self.speed < 9:
                self.speed += self.base_speed * self.speed_multiplier
            self.fuel -= self.fuel_consumption_rate
            self.fuel = max(self.fuel, 0)
            fuel_consumed = True
        if keys[self.controls['accelerate_left']] and self.fuel > 0:
            self.speed -= self.base_speed * self.speed_multiplier * 0.8
            self.fuel -= self.fuel_consumption_rate
            self.fuel = max(self.fuel, 0)
            fuel_consumed = True
        if not fuel_consumed and self.fuel > 0:
            self.fuel -= self.fuel_consumption_rate * 0.1
            self.fuel = max(self.fuel, 0)

        # sample slope farther left/right so tilt is more visible
        sample = SLOPE_SAMPLE
        left_y = get_ground_height(int(self.world_x - sample)) - self.rect.height
        right_y = get_ground_height(int(self.world_x + sample)) - self.rect.height
        slope = right_y - left_y
        dx = (sample * 2) if sample > 0 else 1
        angle_rad = math.atan2(slope, dx)
        angle_deg = math.degrees(angle_rad)

        # current ground under car (used for collision/landing)
        ground_y = get_ground_height(int(self.world_x)) - self.rect.height

        self.vspeed += GRAVITY
        if self.vspeed > TERMINAL_VELOCITY:
            self.vspeed = TERMINAL_VELOCITY
        self.y += self.vspeed

        if self.y >= ground_y:
            # landed or riding on the ground
            slope_abs = abs(slope)
            if slope_abs > LAUNCH_SLOPE_THRESHOLD and abs(self.speed) > LAUNCH_SPEED_THRESHOLD and self.vspeed > 0:
                # Launch off the ramp: give an upward impulse and some angular velocity
                self.y = ground_y - 1
                self.vspeed = -abs(self.speed) * LAUNCH_FACTOR
                self.air_angle = -angle_deg
                self.angle = self.air_angle
                # angular direction depends on ramp direction
                self.angular_velocity = abs(self.speed) * ANGULAR_FACTOR * (1 if slope > 0 else -1)
                # small speed reduction on launch
                self.speed *= 0.99
            else:
                # normal landing / on-ground behavior
                self.y = ground_y
                self.vspeed = 0
                self.angle = -angle_deg
                self.air_angle = None
                self.angular_velocity = 0.0
                self.speed *= 0.99
        else:
            # airborne: allow rotation and damp angular velocity
            if self.air_angle is None:
                self.air_angle = self.angle
            # apply angular motion
            self.angle += self.speed * -0.03
            self.speed *= 0.995

        self.world_x += self.speed
        # Use the same camera center expression as zombies (1024//3) for consistent collision coordinates
        self.rect.topleft = (1024//3 - self.rect.width//2, self.y)

    def draw(self, screen):
        rot = pygame.transform.rotate(self.image, self.angle)
        screen.blit(rot, rot.get_rect(center=self.rect.center))
