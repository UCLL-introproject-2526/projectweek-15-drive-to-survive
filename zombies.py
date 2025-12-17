import pygame
import os
import re
import random
from levels import get_level_manager

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
    def __init__(self, x, level=1):
        self.x = x
        self.level = level
        self.base_damage = 10
        self.__set_health(level)
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_duration = 30  # frames for death animation

    def __set_health(self, level):
        # Public health attribute so other systems (bullets, scripts)
        # can apply damage without relying on name-mangled internals.
        level_manager = get_level_manager()
        base_health = 50
        self.health = level_manager.get_zombie_health(level, base_health)
        
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
                # Use level-scaled damage
                level_manager = get_level_manager()
                scaled_damage = level_manager.get_zombie_damage(self.level, self.base_damage)
                damage = max(0, scaled_damage - car.damage_reduction)
                car.take_damage(damage)
                # Money reward scales with level
                money_earned = int(10 * (1 + self.level * 0.1))

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
    def __init__(self, x, level=1):
        self.x = x
        self.level = level
        self.base_damage = 20
        self.__set_health(level)
        self.alive = True
        self.dying = False
        self.death_timer = 0
        self.death_duration = 45

    def __set_health(self, level):
        # Public health attribute so other systems (bullets, scripts)
        # can apply damage without relying on name-mangled internals.
        level_manager = get_level_manager()
        base_health = 100  # Fat zombies have more health
        self.health = level_manager.get_zombie_health(level, base_health)
        
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
                # Use level-scaled damage
                level_manager = get_level_manager()
                scaled_damage = level_manager.get_zombie_damage(self.level, self.base_damage)
                damage = max(0, scaled_damage - car.damage_reduction)
                car.take_damage(damage)
                # Money reward scales with level (fat zombies give more)
                money_earned = int(20 * (1 + self.level * 0.1))

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
    """Spawn zombies for a given level using the level manager.
    
    Uses level configuration to determine:
    - Number of zombies
    - Spawn positions
    - Mix of normal vs fat zombies
    """
    level_manager = get_level_manager()
    config = level_manager.get_level_config(level)
    
    zombies = []
    positions = level_manager.get_zombie_spawn_positions(level)
    
    # Create zombies at calculated positions
    # Mix of normal and fat zombies (20% fat, 80% normal)
    for i, x in enumerate(positions):
        # Every 5th zombie is a fat zombie, or based on level
        fat_zombie_ratio = min(0.3, 0.15 + level * 0.01)  # Increases with level
        if random.random() < fat_zombie_ratio:
            zombies.append(fatZombie(x, level))
        else:
            zombies.append(Zombie(x, level))
    
    # Shuffle to randomize placement
    random.shuffle(zombies)
    
    print(f"Spawned {len(zombies)} zombies for level {level} (Config: {config.description})")
    return zombies
