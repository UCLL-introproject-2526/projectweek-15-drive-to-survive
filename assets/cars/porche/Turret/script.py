import pygame
import math

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
                        # Apply bullet damage if zombie exposes `health`
                        killed = False
                        if hasattr(zombie, 'health'):
                            try:
                                zombie.health -= self.bullet_damage
                            except Exception:
                                pass
                            if getattr(zombie, 'health', 0) <= 0:
                                # Start death animation but don't restart if already dying
                                if not getattr(zombie, 'dying', False):
                                    zombie.dying = True
                                    zombie.death_timer = 0
                                    zombie.current_frame = 0
                                killed = True
                        else:
                            zombie.alive = False
                            killed = True

                        # Add money through the global reference only when killed
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
            
    def draw(self, cam_x):
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(bullet['x']), int(bullet['y'])), 5)
            pygame.draw.circle(screen, (255, 200, 0), 
                             (int(bullet['x']), int(bullet['y'])), 3)

# Alternative class name for compatibility
class UpgradeScript(TurretUpgrade):
    pass