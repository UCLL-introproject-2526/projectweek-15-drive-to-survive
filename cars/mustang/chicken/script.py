import pygame
import math
import numpy as np

class TurretUpgrade:
    def __init__(self, car):
        self.car = car
        self.bullets = []
        self.cooldown = 0
        self.max_cooldown = 15  
        self.bullet_speed = 8
        self.bullet_damage = 20
        
        # Audio - generate procedural sounds if no files exist
        self.shoot_sound = None
        self.hit_sound = None
        self.init_procedural_sounds()
        
    def init_procedural_sounds(self):
        """Create procedural sounds if audio files don't exist"""
        try:
            # Create shoot sound (short beep)
            self.create_shoot_sound()
            
            # Create hit sound (explosion-like)
            self.create_hit_sound()
        except Exception as e:
            print(f"Could not create procedural sounds: {e}")
    
    def create_shoot_sound(self):
        """Create a simple shoot sound"""
        sample_rate = 22050
        duration = 0.1  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create a short beep (descending frequency)
        freq = 800 * np.exp(-t * 20)  # Frequency drops from 800 to ~100 Hz
        wave = 0.3 * np.sin(2 * np.pi * freq * t) * np.exp(-t * 40)
        
        # Convert to pygame sound
        sound_array = (wave * 32767).astype(np.int16)
        sound_array = np.repeat(sound_array[:, np.newaxis], 2, axis=1)  # Stereo
        self.shoot_sound = pygame.mixer.Sound(buffer=sound_array)
        self.shoot_sound.set_volume(0.2)
    
    def create_hit_sound(self):
        """Create a simple hit/explosion sound"""
        sample_rate = 22050
        duration = 0.3  # seconds
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create explosion sound (noise with decay)
        noise = np.random.normal(0, 1, len(t))
        envelope = np.exp(-t * 15)  # Fast decay
        wave = 0.4 * noise * envelope
        
        # Add low frequency thump
        thump = 0.6 * np.sin(2 * np.pi * 60 * t) * np.exp(-t * 10)
        wave += thump
        
        # Convert to pygame sound
        sound_array = (wave * 32767).astype(np.int16)
        sound_array = np.repeat(sound_array[:, np.newaxis], 2, axis=1)  # Stereo
        self.hit_sound = pygame.mixer.Sound(buffer=sound_array)
        self.hit_sound.set_volume(0.3)
    
    def play_shoot_sound(self):
        """Play shooting sound if available"""
        if self.shoot_sound:
            try:
                self.shoot_sound.play()
            except:
                pass
    
    def play_hit_sound(self):
        """Play hit sound if available"""
        if self.hit_sound:
            try:
                self.hit_sound.play()
            except:
                pass
            
    def update(self, keys, zombies):
        # Decrease cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
            
        # Shoot when E is pressed
        if keys[pygame.K_e] and self.cooldown == 0:
            self.shoot(zombies)
            self.cooldown = self.max_cooldown
            
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
                    # Zombie position on screen
                    zombie_screen_x = zombie.x - self.car.world_x + WIDTH//3 - 11
                    zombie_screen_y = get_ground_height(zombie.x) - 40
                    zombie_rect = pygame.Rect(zombie_screen_x, zombie_screen_y, 22, 40)
                    
                    if bullet_rect.colliderect(zombie_rect):
                        zombie.alive = False
                        self.play_hit_sound()  # Play hit sound
                        
                        # Add money through the global reference
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
        else:
            # If no zombie in front, shoot forward at 45 degree angle
            start_x = WIDTH//3
            start_y = self.car.y + self.car.rect.height//2
            
            # Shoot at 45 degree angle forward
            self.bullets.append({
                'x': start_x,
                'y': start_y,
                'dx': self.bullet_speed,
                'dy': -self.bullet_speed * 0.5
            })
        
        # Always play shoot sound
        self.play_shoot_sound()
            
    def draw(self, cam_x):
        # Draw bullets
        for bullet in self.bullets:
            # Bullet glow effect
            pygame.draw.circle(screen, (255, 100, 100), 
                             (int(bullet['x']), int(bullet['y'])), 7)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (int(bullet['x']), int(bullet['y'])), 5)
            pygame.draw.circle(screen, (255, 200, 0), 
                             (int(bullet['x']), int(bullet['y'])), 3)

# Alternative class name for compatibility
class UpgradeScript(TurretUpgrade):
    pass