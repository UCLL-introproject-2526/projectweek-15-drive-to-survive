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