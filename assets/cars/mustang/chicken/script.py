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
        self.max_ammo = 5  # Maximum ammunition (can be increased by upgrades)
        self.has_shooting = True  # Flag for UI detection
        
        # Load shoot sound effect
        self.shoot_sound = None
        try:
            # Prefer browser-friendly formats first (wav/ogg), then mp3
            candidates = [
                os.path.join("assets", "music", "kipje.wav"),
                os.path.join("assets", "music", "kipje.ogg"),
                os.path.join("assets", "music", "kipje.mp3"),
            ]
            found = None
            for p in candidates:
                if os.path.exists(p):
                    found = p
                    break

            if found:
                try:
                    # Ensure mixer is initialised (in browser this must happen after a user gesture)
                    if not pygame.mixer.get_init():
                        try:
                            pygame.mixer.init()
                        except Exception:
                            pass

                    # Try to load as a Sound object first
                    self.shoot_sound = pygame.mixer.Sound(found)
                    self.shoot_sound.set_volume(0.3)
                except Exception as e:
                    # In some environments Sound() fails for certain codecs; fall back to using music streaming
                    print(f"Could not load chicken shoot as Sound ({found}): {e}; will try music-playback fallback.")
                    self.shoot_sound = None
                    self._music_fallback = found
            else:
                # No file found; synthesize fallback
                self.shoot_sound = self._create_shoot_sound()
                self._music_fallback = None
        except Exception as e:
            print(f"Could not load or synthesize chicken shoot sound: {e}")
            self.shoot_sound = None
            self._music_fallback = None
        
    def update(self, keys, zombies):
        # Decrease cooldown
        if self.cooldown > 0:
            self.cooldown -= 1
            
        # Shoot when the shoot key is pressed (use car's control settings)
        shoot_key = self.car.controls.get('shoot', pygame.K_e)
        if keys[shoot_key] and self.cooldown == 0 and self.ammo > 0:
            if self.shoot(zombies):  # Only consume ammo if we actually shot
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
                            
                            # Give ammo based on zombie type
                            # Fat zombies have more health, normal zombies have less
                            from zombies import fatZombie
                            if isinstance(zombie, fatZombie):
                                self.ammo += 3  # Fat zombie gives 3 ammo
                            else:
                                self.ammo += 1  # Normal zombie gives 1 ammo

                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
    
    def _create_shoot_sound(self):
        """Create a simple synthesized shoot sound effect"""
        try:
            # Create a short high-pitched "pop" sound without numpy
            sample_rate = 22050
            duration = 0.12  # 120ms
            frequency = 900  # Hz
            n_samples = int(sample_rate * duration)

            import struct
            buf = bytearray()
            max_amp = int(0.3 * 32767)
            for i in range(n_samples):
                t = i / sample_rate
                envelope = math.exp(-12 * t)
                sample = int(max_amp * envelope * (0.6 * math.sin(2.0 * math.pi * frequency * t) + 0.4 * math.sin(2.0 * math.pi * frequency * 1.6 * t)))
                packed = struct.pack('<h', sample)
                # stereo
                buf.extend(packed)
                buf.extend(packed)

            try:
                sound = pygame.mixer.Sound(buffer=bytes(buf))
                sound.set_volume(0.3)
                return sound
            except Exception as e:
                print(f"Failed to create pygame Sound from buffer: {e}")
                return None
        except Exception as e:
            print(f"Could not synthesize shoot sound: {e}")
            return None
                        
    def shoot(self, zombies):
        if not zombies:
            return False
        
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
            try:
                if self.shoot_sound:
                    # Ensure mixer ready
                    if not pygame.mixer.get_init():
                        try:
                            pygame.mixer.init()
                        except Exception:
                            pass
                    self.shoot_sound.play()
                elif getattr(self, '_music_fallback', None):
                    # Fallback: use music channel to play the short file (may interrupt music)
                    try:
                        if not pygame.mixer.get_init():
                            try:
                                pygame.mixer.init()
                            except Exception:
                                pass
                        pygame.mixer.music.load(self._music_fallback)
                        pygame.mixer.music.set_volume(0.3)
                        pygame.mixer.music.play(0)
                    except Exception as e:
                        # give up silently
                        print(f"Failed to play chicken fallback via music: {e}")
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
            return True
        return False
            
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