import os
import json
import importlib.util
from car_types import get_current_car_type, ALL_CAR_TYPES, set_current_car_type
import pygame

ALL_UPGRADES = {}

class Upgrade:
    def __init__(self, folder, upgrade_name):
        self.folder = folder
        self.name = upgrade_name

        # Load upgrade info from the car's info.json
        car_info_file = os.path.join(os.path.dirname(folder), "info.json")
        if os.path.exists(car_info_file):
            with open(car_info_file, "r") as f:
                car_data = json.load(f)

            if "upgrades" in car_data and upgrade_name in car_data["upgrades"]:
                upgrade_data = car_data["upgrades"][upgrade_name]
                self.car_damage = upgrade_data.get("car_damage", 0)
                self.damage_reduction = upgrade_data.get("damage_reduction", 0)
                self.speed_increase = upgrade_data.get("speed_increase", 0)
                self.price = upgrade_data.get("price", 50)
                self.has_script = upgrade_data.get("script", False)
                self.z_index = upgrade_data.get("z-index", 0)
            else:
                self.car_damage = 0
                self.damage_reduction = 0
                self.speed_increase = 0
                self.price = 50
                self.has_script = False
                self.z_index = 0
        else:
            self.car_damage = 0
            self.damage_reduction = 0
            self.speed_increase = 0
            self.price = 50
            self.has_script = False
            self.z_index = 0

        img_file = os.path.join(folder, "image.png")
        if os.path.exists(img_file):
            self.image = pygame.image.load(img_file).convert_alpha()
            self.image_small = pygame.transform.scale(self.image, (80, 60))
        else:
            self.image = pygame.Surface((100, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (150, 150, 150), (0, 0, 100, 60), border_radius=5)
            self.image_small = pygame.transform.scale(self.image, (80, 60))

        self.script_instance = None
        self.purchased = False
        self.equipped = False
        self.check_purchased_status()

    def check_purchased_status(self):
        try:
            if os.path.exists("upgrades_status.json"):
                with open("upgrades_status.json", "r") as f:
                    status_data = json.load(f)
                current = get_current_car_type()
                if current:
                    key = f"{current.name}.{self.name}"
                    if key in status_data:
                        self.purchased = bool(status_data[key].get("purchased", False))
                        self.equipped = bool(status_data[key].get("equipped", False))
        except Exception as e:
            print(f"Error loading status for {self.name}: {e}")
            self.purchased = False
            self.equipped = False

    def save_status(self):
        try:
            if os.path.exists("upgrades_status.json"):
                try:
                    with open("upgrades_status.json", "r") as f:
                        status_data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    status_data = {}
            else:
                status_data = {}

            current = get_current_car_type()
            if current:
                key = f"{current.name}.{self.name}"
                status_data[key] = {"purchased": bool(self.purchased), "equipped": bool(self.equipped)}
            else:
                # no current car - skip saving this individual upgrade status
                pass

            with open("upgrades_status.json", "w") as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"Error saving upgrade status for {self.name}: {e}")

def load_upgrades():
    upgrades_list = []
    ALL_UPGRADES.clear()
    current_car = get_current_car_type()
    if not current_car:
        print("Warning: No current car type selected!")
        return upgrades_list

    car_folder = current_car.folder
    if not os.path.exists(car_folder):
        print(f"Error: Car folder '{car_folder}' not found!")
        return upgrades_list

    for folder_name in os.listdir(car_folder):
        folder_path = os.path.join(car_folder, folder_name)
        if os.path.isdir(folder_path):
            if os.path.exists(os.path.join(folder_path, "image.png")) or folder_name.lower() in ["ramp", "turret", "default", "mustang"]:
                try:
                    up = Upgrade(folder_path, folder_name)
                    upgrades_list.append(up)
                    key = f"{current_car.name}.{folder_name}"
                    ALL_UPGRADES[key] = up
                except Exception as e:
                    print(f"Error loading upgrade from {folder_path}: {e}")

    return upgrades_list

def save_all_upgrades_status():
    try:
        status_data = {}
        if os.path.exists("upgrades_status.json"):
            try:
                with open("upgrades_status.json", "r") as f:
                    status_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                status_data = {}

        # store current car as a normalized key (lowercase) so restores match ALL_CAR_TYPES keys
        current = get_current_car_type()
        status_data["current_car"] = (current.name.lower() if current and getattr(current, 'name', None) else "")

        # iterate all cars and store their upgrades
        original = (current.name.lower() if current and getattr(current, 'name', None) else None)
        for car_name, car_type in ALL_CAR_TYPES.items():
            set_current_car_type(car_name)
            saved = load_upgrades()
            for up in saved:
                key = f"{car_name}.{up.name}"
                status_data[key] = {"purchased": up.purchased, "equipped": up.equipped}
        # restore original selection
        if original:
            set_current_car_type(original)

        with open("upgrades_status.json", "w") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Error saving all upgrades status: {e}")

def load_all_upgrades_status():
    try:
        if os.path.exists("upgrades_status.json"):
            with open("upgrades_status.json", "r") as f:
                status_data = json.load(f)
            # restore saved car selection if present
            if "current_car" in status_data:
                saved_car = status_data["current_car"]
                if saved_car:
                    saved_key = saved_car.lower()
                    if saved_key in ALL_CAR_TYPES:
                        set_current_car_type(saved_key)
            # apply statuses to current car
            current_car = get_current_car_type()
            if current_car:
                upgrades = load_upgrades()
                for upgrade in upgrades:
                    key = f"{current_car.name}.{upgrade.name}"
                    if key in status_data:
                        upgrade.purchased = bool(status_data[key].get("purchased", False))
                        upgrade.equipped = bool(status_data[key].get("equipped", False))
    except Exception as e:
        print(f"Error loading upgrades status: {e}")

def get_upgrade_by_name(name):
    current = get_current_car_type()
    if not current or not getattr(current, 'name', None):
        return None
    key = f"{current.name}.{name}"
    return ALL_UPGRADES.get(key)

class SimpleTurret:
    def __init__(self, car):
        self.car = car
        self.bullets = []
        self.cooldown = 0
        self.max_cooldown = 15
        self.bullet_speed = 8
        self.ammo = 5  # Starting ammunition
        self.has_shooting = True  # Flag for UI detection

    def update(self, keys, zombies):
        if self.cooldown > 0:
            self.cooldown -= 1
        if keys.get('e') and self.cooldown == 0 and self.ammo > 0:
            self.shoot(zombies)
            self.cooldown = self.max_cooldown
            self.ammo -= 1

        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            if bullet['x'] < -100 or bullet['x'] > 2000 or bullet['y'] < -100 or bullet['y'] > 2000:
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                    continue

            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            for zombie in zombies:
                if zombie.alive:
                    # Use zombie sprite width for hitbox if available (keep previous y behavior)
                    if hasattr(zombie, 'rect'):
                        z_w = zombie.rect.width
                    else:
                        z_w = 22

                    zombie_screen_x = zombie.x - self.car.world_x + 100 - z_w//2
                    zombie_screen_y = 0
                    zombie_rect = pygame.Rect(zombie_screen_x, zombie_screen_y, z_w, 40)
                    if bullet_rect.colliderect(zombie_rect):
                        # Apply bullet damage if zombie exposes `health`
                        killed = False
                        if hasattr(zombie, 'health'):
                            try:
                                zombie.health -= 20
                            except Exception:
                                pass
                            if getattr(zombie, 'health', 0) <= 0:
                                # Do not restart death animation if already dying
                                if not getattr(zombie, 'dying', False):
                                    zombie.dying = True
                                    zombie.death_timer = 0
                                    zombie.current_frame = 0
                                killed = True
                        else:
                            zombie.alive = False
                            killed = True

                        # Give ammo based on zombie type when killed
                        if killed:
                            from zombies import fatZombie
                            if isinstance(zombie, fatZombie):
                                self.ammo += 3  # Fat zombie gives 3 ammo
                            else:
                                self.ammo += 1  # Normal zombie gives 1 ammo

                        # Remove bullet regardless; caller awards money if needed
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break

    def shoot(self, zombies):
        if not zombies:
            return
        nearest = None
        min_d = float('inf')
        for z in zombies:
            if z.alive and z.x > self.car.world_x:
                d = z.x - self.car.world_x
                if d < min_d:
                    min_d = d
                    nearest = z
        if nearest:
            start_x = 100
            start_y = self.car.y + self.car.rect.height//2
            target_x = nearest.x - self.car.world_x + 100
            target_y = 0
            dx = target_x - start_x
            dy = target_y - start_y
            length = max(0.1, (dx*dx + dy*dy)**0.5)
            self.bullets.append({'x': start_x, 'y': start_y, 'dx': dx/length*self.bullet_speed, 'dy': dy/length*self.bullet_speed})
