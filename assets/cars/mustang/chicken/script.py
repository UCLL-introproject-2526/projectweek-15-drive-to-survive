import pygame
import math
import os

class TurretUpgrade:
    def __init__(self, car):
        self.car = car
        self.bullets = []
        self.cooldown = 0
        self.max_cooldown = 15  # frames between shots
        self.bullet_speed = 8
        self.bullet_damage = 20
        self.ammo = 5  # Starting ammunition
        self.has_shooting = True  # Flag for UI detection
        
        # Load shoot sound effect
        self.shoot_sound = None
        try:
            sound_path = os.path.join("assets", "music", "kipje.mp3")
            if os.path.exists(sound_path):
                self.shoot_sound = pygame.mixer.Sound(sound_path)
                self.shoot_sound.set_volume(0.3)  # Lower volume so it's not too loud
            else:
                # Try to synthesize a simple "pew" sound as fallback
                self.shoot_sound = self._create_shoot_sound()
        except Exception as e:
            print(f"Could not load chicken shoot sound: {e}")
            self.shoot_sound = None
        
    def update(self, keys, zombies):
        # Decrease cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
            
        # Shoot when the shoot key is pressed (use car's control settings)
        shoot_key = self.car.controls.get('shoot', pygame.K_e)
        if keys[shoot_key] and self.cooldown == 0 and self.ammo > 0:
            self.shoot(zombies)
            self.cooldown = self.max_cooldown
            self.ammo -= 1
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            # Remove if off screen
            if (bullet['x'] < -100 or bullet['x'] > WIDTH + 100 or 
                bullet['y'] < -100 or bullet['y'] > HEIGHT + 100):
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                    continue
                    
            # Check collision with zombies
            bullet_rect = pygame.Rect(bullet['x'] - 3, bullet['y'] - 3, 6, 6)
            for zombie in zombies:
                if zombie.alive:
                    # Zombie position on screen - use sprite rect if available
                    if hasattr(zombie, 'rect'):
                        z_w = zombie.rect.width
                        z_h = zombie.rect.height
                    else:
                        z_w, z_h = 22, 40

                    zombie_screen_x = zombie.x - self.car.world_x + WIDTH//3 - z_w//2
                    zombie_screen_y = get_ground_height(zombie.x) - z_h
                    zombie_rect = pygame.Rect(zombie_screen_x, zombie_screen_y, z_w, z_h)
                    
                    if bullet_rect.colliderect(zombie_rect):
                        # Apply bullet damage if the zombie exposes a health attribute.
                        killed = False
                        if hasattr(zombie, 'health'):
                            try:
                                zombie.health -= self.bullet_damage
                            except Exception:
                                pass
                            if getattr(zombie, 'health', 0) <= 0:
                                # Start death animation flow used by zombies, but do not
                                # restart the animation if it's already playing.
                                if not getattr(zombie, 'dying', False):
                                    zombie.dying = True
                                    zombie.death_timer = 0
                                    zombie.current_frame = 0
                                killed = True
                        else:
                            # Fallback: mark dead immediately
                            zombie.alive = False
                            killed = True

                        # Award money only when the zombie is killed
                        if killed:
                            import sys
                            main_module = sys.modules['__main__']
                            if hasattr(main_module, 'money'):
                                main_module.money += 15
                            elif hasattr(main_module, 'money_ref'):
                                money = main_module.money_ref()
                                money += 15

                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
    
    def _create_shoot_sound(self):
        """Create a simple synthesized shoot sound effect"""
        try:
            # Create a short high-pitched "pop" sound
            sample_rate = 22050
            duration = 0.1  # 100ms
            frequency = 800  # Hz
            
            import numpy as np
            
            # Generate samples
            samples = int(sample_rate * duration)
            wave = np.zeros(samples)
            
            for i in range(samples):
                t = i / sample_rate
                # Envelope: quick attack, exponential decay
                envelope = math.exp(-15 * t)
                # Two-tone for a "pop" effect
                wave[i] = envelope * (
                    0.5 * math.sin(2 * math.pi * frequency * t) +
                    0.3 * math.sin(2 * math.pi * frequency * 1.5 * t)
                )
            
            # Convert to 16-bit integers
            wave = (wave * 32767).astype(np.int16)
            
            # Create stereo by duplicating
            stereo_wave = np.column_stack((wave, wave))
            
            # Create pygame Sound from numpy array
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(0.3)
            return sound
        except Exception as e:
            print(f"Could not synthesize shoot sound: {e}")
            return None
                        
    def shoot(self, zombies):
        if not zombies:
            return
        
        # Find nearest zombie in front of car
        nearest_zombie = None
        min_distance = float('inf')
        
        for zombie in zombies:
            if zombie.alive and zombie.x > self.car.world_x:
                distance = zombie.x - self.car.world_x
                if distance < min_distance:
                    min_distance = distance
                    nearest_zombie = zombie
                    
        if nearest_zombie:
            # Play shoot sound only when we have a target
            if self.shoot_sound:
                try:
                    self.shoot_sound.play()
                except Exception:
                    pass
            
            # Calculate direction
            start_x = WIDTH//3
            start_y = self.car.y + self.car.rect.height//2
            
            target_x = nearest_zombie.x - self.car.world_x + WIDTH//3
            target_y = get_ground_height(nearest_zombie.x) - 20
            
            dx = target_x - start_x
            dy = target_y - start_y
            length = max(0.1, math.sqrt(dx*dx + dy*dy))
            
            self.bullets.append({
                'x': start_x,
                'y': start_y,
                'dx': dx/length * self.bullet_speed,
                'dy': dy/length * self.bullet_speed
            })
            
    def draw(self, cam_x):
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(bullet['x']), int(bullet['y'])), 5)
            pygame.draw.circle(screen, (255, 200, 255), 
                             (int(bullet['x']), int(bullet['y'])), 3)

# Alternative class name for compatibility
class UpgradeScript(TurretUpgrade):
    pass