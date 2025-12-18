import pygame
import os
import re
import random
from levels import get_level_manager

# Cache for loaded animations
_animation_cache = {}

def load_zombie_animation_cached(folder, base_name):
    """Load animations using `load_animation` helper and cache results."""
    key = (folder, base_name)
    if key in _animation_cache:
        return _animation_cache[key]

    frames = load_animation(folder, base_name)
    flipped = [pygame.transform.flip(f, True, False) for f in frames]
    _animation_cache[key] = flipped
    return flipped


def load_animation(folder, base_name):
    """Load base and numbered frames, handling copy suffixes."""
    frames = []
    if not os.path.exists(folder):
        print(f"Warning: Folder not found: {folder}")
        return frames

    exts = ["png", "gif", "jpg", "jpeg"]
    exts_pattern = "|".join(exts)
    pattern = re.compile(
        rf'^{re.escape(base_name)}(?: \((\d+)\))?.*\.({exts_pattern})$',
        re.IGNORECASE,
    )

    candidates = []
    for fname in os.listdir(folder):
        m = pattern.match(fname)
        if m:
            idx = int(m.group(1)) if m.group(1) else 0
            candidates.append((idx, os.path.join(folder, fname)))

    candidates.sort(key=lambda t: (t[0], t[1]))

    def _safe_load(path):
        try:
            img = pygame.image.load(path)
            try:
                img = img.convert_alpha()
            except Exception:
                img = img.convert()
            img = pygame.transform.scale(img, (110, 100))
            img = pygame.transform.flip(img, True, False)
            return img
        except Exception as e:
            print(f"Error loading {path}: {e}")
            return None

    for _, path in candidates:
        img = _safe_load(path)
        if img is not None:
            frames.append(img)

    return frames


# --------------------
# Health bar helper
# --------------------

def draw_health_bar(surface, rect, current, maximum):
    if maximum <= 0 or current <= 0:
        return

    bar_width = 60
    bar_height = 6
    x = rect.x + ((rect.width/2) - (bar_width/2))
    y = rect.y - bar_height - 4

    ratio = max(0, min(1, current / maximum))
    fill_width = int(bar_width * ratio)

    pygame.draw.rect(surface, (180, 0, 0), (x, y, bar_width, bar_height))
    pygame.draw.rect(surface, (0, 180, 0), (x, y, fill_width, bar_height))
    pygame.draw.rect(surface, (0, 0, 0), (x, y, bar_width, bar_height), 1)


# --------------------
# Zombie classes
# --------------------

class Zombie:
    def __init__(self, x, level=1):
        self.x = x
        self.level = level
        self.base_damage = 10
        self._set_health(level)
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_duration = 30

    def _set_health(self, level):
        level_manager = get_level_manager()
        base_health = 50
        self.max_health = level_manager.get_zombie_health(level, base_health)
        self.health = self.max_health

        walk_path = os.path.join("assets", "images", "normal-zombie")
        death_path = os.path.join("assets", "images", "normal-zombie-damaged")

        self.walk_frames = load_zombie_animation_cached(
            walk_path, "Zombie1-ezgif.com-crop"
        )
        self.death_frames = load_zombie_animation_cached(
            death_path, "zombie1Damaged-ezgif.com-crop"
        )

        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0

        if self.walk_frames:
            self.rect = self.walk_frames[0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 22, 40)

    def update(self, car, terrain):
        money_earned = 0

        sx = self.x - car.world_x + 1024 // 3 - self.rect.width // 2
        ground_y = terrain(self.x) if callable(terrain) else terrain.get_ground_height(self.x)
        sy = ground_y - self.rect.height
        self.rect.topleft = (sx, sy)

        if self.alive and not self.dying and self.rect.colliderect(car.rect):
            self.dying = True
            self.death_timer = 0
            self.current_frame = 0

            level_manager = get_level_manager()
            scaled_damage = level_manager.get_zombie_damage(self.level, self.base_damage)
            damage = max(0, scaled_damage - car.damage_reduction)
            car.take_damage(damage)
            money_earned = int(10 * (1 + self.level * 0.1))
            
            # Give ammo to turret upgrades when zombie is killed by collision
            # Normal zombie gives 1 ammo, fat zombie gives 3 ammo
            self._give_ammo_to_turrets(car, ammo_amount=1)

        if self.dying:
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.alive = False

        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            if self.dying and self.death_frames:
                self.current_frame = min(self.current_frame + 1, len(self.death_frames) - 1)
            elif not self.dying and self.walk_frames:
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)

        return money_earned

    def _give_ammo_to_turrets(self, car, ammo_amount):
        """Give ammo to any turret-related upgrades the car has equipped."""
        if hasattr(car, 'upgrade_instances'):
            for upgrade_instance in car.upgrade_instances:
                # Check if this upgrade has shooting capability (turret-related)
                if hasattr(upgrade_instance, 'has_shooting') and upgrade_instance.has_shooting:
                    if hasattr(upgrade_instance, 'ammo'):
                        # Verify the upgrade is actually equipped
                        if hasattr(upgrade_instance, '_upgrade_ref'):
                            if upgrade_instance._upgrade_ref.equipped:
                                # Respect max_ammo limit
                                max_ammo = getattr(upgrade_instance, 'max_ammo', 999)
                                upgrade_instance.ammo = min(upgrade_instance.ammo + ammo_amount, max_ammo)
                        else:
                            # Fallback for upgrades without reference
                            max_ammo = getattr(upgrade_instance, 'max_ammo', 999)
                            upgrade_instance.ammo = min(upgrade_instance.ammo + ammo_amount, max_ammo)

    def draw(self, surface, cam_x, terrain):
        if not (self.alive or self.dying):
            return

        sx = self.x - cam_x + 1024 // 3 - self.rect.width // 2
        ground_y = terrain(self.x) if callable(terrain) else terrain.get_ground_height(self.x)
        sy = ground_y - self.rect.height
        self.rect.topleft = (sx, sy)

        if self.dying and self.death_frames:
            frame = self.death_frames[int(self.current_frame)]
        elif self.walk_frames:
            frame = self.walk_frames[int(self.current_frame)]
        else:
            frame = None

        if frame:
            surface.blit(frame, self.rect)
        else:
            pygame.draw.rect(surface, (0, 200, 0), self.rect, border_radius=4)

        if self.alive and not self.dying and self.health < self.max_health:
            draw_health_bar(surface, self.rect, self.health, self.max_health)


class fatZombie(Zombie):
    def __init__(self, x, level=1):
        super().__init__(x, level)
        self.base_damage = 25  # Fat zombies do more damage
    
    def _give_ammo_to_turrets(self, car, ammo_amount):
        """Override to give 3 ammo for fat zombies."""
        if hasattr(car, 'upgrade_instances'):
            for upgrade_instance in car.upgrade_instances:
                # Check if this upgrade has shooting capability (turret-related)
                if hasattr(upgrade_instance, 'has_shooting') and upgrade_instance.has_shooting:
                    if hasattr(upgrade_instance, 'ammo'):
                        # Verify the upgrade is actually equipped
                        if hasattr(upgrade_instance, '_upgrade_ref'):
                            if upgrade_instance._upgrade_ref.equipped:
                                # Respect max_ammo limit
                                max_ammo = getattr(upgrade_instance, 'max_ammo', 999)
                                upgrade_instance.ammo = min(upgrade_instance.ammo + 3, max_ammo)  # Fat zombie gives 3 ammo
                        else:
                            # Fallback for upgrades without reference
                            max_ammo = getattr(upgrade_instance, 'max_ammo', 999)
                            upgrade_instance.ammo = min(upgrade_instance.ammo + 3, max_ammo)  # Fat zombie gives 3 ammo
    
    def _set_health(self, level):
        level_manager = get_level_manager()
        base_health = 200
        self.max_health = level_manager.get_zombie_health(level, base_health)
        self.health = self.max_health

        walk_path = os.path.join("assets", "images", "fat-zombie")
        death_path = os.path.join("assets", "images", "fat-zombie-damaged")

        self.walk_frames = load_zombie_animation_cached(
            walk_path, "fatzombie3-ezgif.com-crop"
        )
        self.death_frames = load_zombie_animation_cached(
            death_path, "fatzombieDamaged-ezgif.com-crop"
        )

        self.current_frame = 0
        self.animation_speed = 0.12
        self.animation_counter = 0

        if self.walk_frames:
            self.rect = self.walk_frames[0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 30, 50)


# --------------------
# Spawning
# --------------------

def spawn_zombies(level):
    level_manager = get_level_manager()
    config = level_manager.get_level_config(level)

    zombies = []
    positions = level_manager.get_zombie_spawn_positions(level)

    for x in positions:
        fat_ratio = min(0.3, 0.15 + level * 0.01)
        if random.random() < fat_ratio:
            zombies.append(fatZombie(x, level))
        else:
            zombies.append(Zombie(x, level))

    random.shuffle(zombies)
    print(f"Spawned {len(zombies)} zombies for level {level} ({config.description})")
    return zombies