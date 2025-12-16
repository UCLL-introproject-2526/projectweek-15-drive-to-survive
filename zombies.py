import pygame
import os
import re
import random

# Cache for loaded animations
_animation_cache = {}

def load_zombie_animation_cached(folder, base_name):
    """Load animations using `load_animation` helper and cache results.

    Frames are horizontally flipped to match previous visual orientation.
    """
    key = (folder, base_name)
    if key in _animation_cache:
        return _animation_cache[key]

    frames = load_animation(folder, base_name)
    # flip frames horizontally for consistency with previous behavior
    flipped = [pygame.transform.flip(f, True, False) for f in frames]
    _animation_cache[key] = flipped
    return flipped


def load_animation(folder, base_name):
    """Helper: load base and numbered frames robustly (handles ' - Copy' suffixes).

    Returns list of pygame Surfaces ordered: base (index 0) then numbered frames.
    """
    frames = []
    if not os.path.exists(folder):
        print(f"Warning: Folder not found: {folder}")
        return frames

    exts = ["png", "gif", "jpg", "jpeg"]
    exts_pattern = "|".join(exts)
    pattern = re.compile(rf'^{re.escape(base_name)}(?: \((\d+)\))?.*\.({exts_pattern})$', re.IGNORECASE)

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

    for idx, path in candidates:
        img = _safe_load(path)
        if img is not None:
            frames.append(img)

    print(f"Loaded {len(frames)} frames from {folder}")
    return frames

class Zombie:
    def __init__(self, x):
        self.x = x
        self.__set_health(1)
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_duration = 30  # frames for death animation

    def __set_health(self, level):
        self.__health = 50 * (1.1 ** level)
        
        # Load animations using the correct relative paths
        walk_path = os.path.join("images", "normal-zombie")
        death_path = os.path.join("images", "normal-zombie-damaged")

        self.walk_frames = self.load_zombie_animation(walk_path, "Zombie1-ezgif.com-crop")
        self.death_frames = self.load_zombie_animation(death_path, "zombie1Damaged-ezgif.com-crop")

        if not self.walk_frames:
            print(f"Warning: Could not load walk animation frames from {walk_path} (exists={os.path.exists(walk_path)})")
        
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        
        if self.walk_frames:
            self.rect = self.walk_frames[0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 22, 40)

    def load_zombie_animation(self, folder, base_name):
        """Wrapper that uses the cached loader to avoid repeated disk loads."""
        return load_zombie_animation_cached(folder, base_name)

    def update(self, car, terrain):
        """Update zombie and check collision with car. Returns money earned."""
        money_earned = 0

        # Compute and set rect position so collision checks are accurate
        sx = self.x - car.world_x + 1024//3 - self.rect.width//2
        if callable(terrain):
            ground_y = terrain(self.x)
        else:
            ground_y = terrain.get_ground_height(self.x)
        sy = ground_y - self.rect.height
        self.rect.topleft = (sx, sy)

        if self.alive and not self.dying:
            if self.rect.colliderect(car.rect):
                self.dying = True
                self.death_timer = 0
                self.current_frame = 0
                damage = max(0, 10 - car.damage_reduction)
                car.take_damage(damage)
                money_earned = 10

        if self.dying:
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.alive = False
        
        # Update animation frame
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            
            if self.dying and len(self.death_frames) > 0:
                # Death animation - play through once
                self.current_frame += 1
                if self.current_frame >= len(self.death_frames):
                    self.current_frame = len(self.death_frames) - 1  # Stay on last frame
            elif not self.dying and len(self.walk_frames) > 0:
                # Walking animation - loop continuously
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        
        return money_earned

    def draw(self, srf, cam_x, terrain):
        """Draw zombie on screen"""
        if self.alive or self.dying:
            sx = self.x - cam_x + 1024//3 - self.rect.width//2
            # Support either a function (get_ground_height) or a module with get_ground_height()
            if callable(terrain):
                ground_y = terrain(self.x)
            else:
                ground_y = terrain.get_ground_height(self.x)
            sy = ground_y - self.rect.height
            self.rect.topleft = (sx, sy)

            # Draw current animation frame
            if self.dying and self.death_frames:
                frame = self.death_frames[int(self.current_frame)]
                srf.blit(frame, self.rect)
            elif not self.dying and self.walk_frames:
                frame = self.walk_frames[int(self.current_frame)]
                srf.blit(frame, self.rect)
            else:
                # Fallback if no animation loaded
                pygame.draw.rect(srf, (0,200,0), self.rect, border_radius=4)


class fatZombie:
    def __init__(self, x):
        self.x = x
        self.__set_health(1)
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_duration = 45

    def __set_health(self, level):
        self.__health = 200 * (1.1 ** level)
        walk_path = os.path.join("images", "fat-zombie")
        death_path = os.path.join("images", "fat-zombie-damaged")

        # Use cached loader to avoid repeated disk loads
        self.walk_frames = load_zombie_animation_cached(walk_path, "fatzombie3-ezgif.com-crop")
        self.death_frames = load_zombie_animation_cached(death_path, "fatzombieDamaged-ezgif.com-crop")

        if not self.walk_frames:
            print(f"Warning: Could not load walk animation frames from {walk_path} (exists={os.path.exists(walk_path)})")
        
        self.current_frame = 0
        self.animation_speed = 0.12
        self.animation_counter = 0
        
        if self.walk_frames:
            self.rect = self.walk_frames[0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 30, 50)

    def update(self, car, terrain):
        """Update zombie and check collision with car. Returns money earned."""
        money_earned = 0

        # Place the rect for this zombie using the same camera transform as the car
        sx = self.x - car.world_x + 1024//3 - self.rect.width//2
        if callable(terrain):
            ground_y = terrain(self.x)
        else:
            ground_y = terrain.get_ground_height(self.x)
        sy = ground_y - self.rect.height
        self.rect.topleft = (sx, sy)

        if self.alive and not self.dying:
            if self.rect.colliderect(car.rect):
                self.dying = True
                self.death_timer = 0
                self.current_frame = 0
                damage = max(0, 20 - car.damage_reduction)
                car.take_damage(damage)
                money_earned = 20

        if self.dying:
            self.death_timer += 1
            if self.death_timer >= self.death_duration:
                self.alive = False

        # Update animation frame
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.animation_counter = 0
            
            if self.dying and len(self.death_frames) > 0:
                # Death animation - play through once
                self.current_frame += 1
                if self.current_frame >= len(self.death_frames):
                    self.current_frame = len(self.death_frames) - 1  # Stay on last frame
            elif not self.dying and len(self.walk_frames) > 0:
                # Walking animation - loop continuously
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
        
        return money_earned

    def draw(self, srf, cam_x, terrain):
        """Draw zombie on screen"""
        if self.alive or self.dying:
            sx = self.x - cam_x + 1024//3 - self.rect.width//2
            # Support either a function (get_ground_height) or a module with get_ground_height()
            if callable(terrain):
                ground_y = terrain(self.x)
            else:
                ground_y = terrain.get_ground_height(self.x)
            sy = ground_y - self.rect.height
            self.rect.topleft = (sx, sy)
            
            # Draw current animation frame
            if self.dying and self.death_frames:
                frame = self.death_frames[int(self.current_frame)]
                srf.blit(frame, self.rect)
            elif not self.dying and self.walk_frames:
                frame = self.walk_frames[int(self.current_frame)]
                srf.blit(frame, self.rect)
            else:
                # Fallback if no animation loaded
                pygame.draw.rect(srf, (0,200,0), self.rect, border_radius=4)


def spawn_zombies(level):
    """Spawn zombies for a given level.

    Behavior:
    - Level 0: a few fat zombies (easier)
    - Level 1: mix of normal and fat zombies
    - Level >=2: scaled number of zombies, mixture increases with level
    """
    zombies = []

    if level <= 0:
        # Beginner level: a few fat zombies
        for i in range(3):
            x = random.randint(800 + i * 2000, 2500 + i * 2000)
            zombies.append(fatZombie(x))

    elif level == 1:
        # Mix of normal and fat
        for i in range(4):
            x = random.randint(800 + i * 1500, 2200 + i * 1500)
            zombies.append(Zombie(x))
        for i in range(2):
            x = random.randint(1200 + i * 1800, 3000 + i * 1800)
            zombies.append(fatZombie(x))

    else:
        # Higher levels: scale count with level but cap to avoid overwhelming
        count = min(12, 3 + level * 2)
        for i in range(count):
            distance = 800 + i * 800
            if i % 4 == 0:
                zcls = fatZombie
            else:
                zcls = Zombie
            x = random.randint(distance, distance + 600)
            zombies.append(zcls(x))

    random.shuffle(zombies)
    print(f"Spawned {len(zombies)} zombies for level {level}")
    return zombies

    # For other levels (or if no spawning rules apply), return an empty list
    return []