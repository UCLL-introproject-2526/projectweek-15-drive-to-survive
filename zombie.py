import pygame
import os
import re
import random


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
        
        print(f"Attempting to load walk animation from: {walk_path}")
        print(f"Path exists: {os.path.exists(walk_path)}")
        
        self.walk_frames = self.load_zombie_animation(walk_path, "Zombie1-ezgif.com-crop")
        self.death_frames = self.load_zombie_animation(death_path, "zombie1Damaged-ezgif.com-crop")
        
        if not self.walk_frames:
            print("ERROR: Could not load walk animation frames!")
            print(f"Current working directory: {os.getcwd()}")
            if os.path.exists(walk_path):
                print(f"Files in {walk_path}:")
                print(os.listdir(walk_path))
        
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        
        if self.walk_frames:
            self.rect = self.walk_frames[0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 22, 40)

    def load_zombie_animation(self, folder, base_name):
        """Load animation frames from a folder starting from (1).png upwards"""
        frames = []
        
        if not os.path.exists(folder):
            print(f"Warning: Folder not found: {folder}")
            return frames
        
        # Load frames starting from (1).png and go up
        frame_num = 1
        while True:
            frame_path = os.path.join(folder, f"{base_name} ({frame_num}).png")
            
            if os.path.exists(frame_path):
                try:
                    img = pygame.image.load(frame_path).convert_alpha()
                    img = pygame.transform.scale(img, (90,80))
                    img = pygame.transform.flip(img, True, False)
                    frames.append(img)
                    frame_num += 1
                except Exception as e:


                    print(f"Error loading {frame_path}: {e}")
                    break
            else:
                # No more frames found
                break
        
        print(f"Loaded {len(frames)} frames from {folder}")
        return frames

    def update(self, car, terrain):
        """Update zombie and check collision with car. Returns money earned."""
        money_earned = 0
        
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
            sy = terrain.get_ground_height(self.x) - self.rect.height
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
        self.death_duration = 30  # frames for death animation

    def __set_health(self, level):
        #health word per level exponentieel verhoogd met 10%
        self.__health = 200 * (1.1 ** level)
        
        # Load animations using the correct relative paths
        walk_path = os.path.join("images", "fat-zombie")
        death_path = os.path.join("images", "fat-zombie-damaged")
        
        print(f"Attempting to load walk animation from: {walk_path}")
        print(f"Path exists: {os.path.exists(walk_path)}")
        
        # filenames in images/fat-zombie use 'fatzombie3-ezgif.com-crop' (lowercase)
        self.walk_frames = load_animation(walk_path, "fatzombie3-ezgif.com-crop")
        # damaged frames are gifs and use 'fatzombieDamaged-ezgif.com-crop'
        self.death_frames = load_animation(death_path, "fatzombieDamaged-ezgif.com-crop")
        
        if not self.walk_frames:
            print("ERROR: Could not load walk animation frames!")
            print(f"Current working directory: {os.getcwd()}")
            if os.path.exists(walk_path):
                print(f"Files in {walk_path}:")
                print(os.listdir(walk_path))
        
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        
        if self.walk_frames:
            self.rect = self.walk_frames[0].get_rect()
        else:
            self.rect = pygame.Rect(0, 0, 22, 40)

    def load_zombie_animation(self, folder, base_name):







        """Load animation frames from `folder`.

        Behavior:
        - Try the unnumbered file first: `<base_name>.<ext>`
        - Then load numbered frames starting at 1: `<base_name> (1).<ext>`, `<base_name> (2).<ext>`, ...
        - Supports `.png`, `.gif`, `.jpg`, `.jpeg` and is tolerant to missing files.
        """
        frames = []

        if not os.path.exists(folder):
            print(f"Warning: Folder not found: {folder}")
            return frames

        exts = [".png", ".gif", ".jpg", ".jpeg"]

        def _safe_load(path):
            try:
                img = pygame.image.load(path)
                try:
                    img = img.convert_alpha()
                except Exception:
                    img = img.convert()
                img = pygame.transform.scale(img, (110, 100))
                return img
            except Exception as e:
                print(f"Error loading {path}: {e}")
                return None

        # 1) try unnumbered base file
        for ext in exts:
            candidate = os.path.join(folder, f"{base_name}{ext}")
            if os.path.exists(candidate):
                img = _safe_load(candidate)
                if img is not None:
                    frames.append(img)
                break

        # 2) numbered frames starting at 1
        i = 1
        while True:
            found = False
            for ext in exts:
                candidate = os.path.join(folder, f"{base_name} ({i}){ext}")
                if os.path.exists(candidate):
                    img = _safe_load(candidate)
                    if img is not None:
                        frames.append(img)
                        found = True
                        break
            if not found:
                break
            i += 1

        print(f"Loaded {len(frames)} frames from {folder}")
        return frames

    def update(self, car, terrain):
        """Update zombie and check collision with car. Returns money earned."""
        money_earned = 0
        
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
            sy = terrain.get_ground_height(self.x) - self.rect.height
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
    if level < 2:
        zombies = []
        # Spawn 3 zombies at random positions
        for i in range(3):
            x = random.randint(800 + i * 2000, 2500 + i * 2000)
            zombies.append(fatZombie(x))
        return zombies