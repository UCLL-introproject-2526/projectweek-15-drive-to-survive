import pygame
import math
from terrain import get_ground_height

# ==============================
# Easter Egg Module
# ==============================

class EasterEgg:
    """A special easter egg that activates cheat mode when hit"""
    def __init__(self, x_position=-2000):
        self.world_x = x_position
        self.width = 60
        self.height = 60
        self.collected = False
        self.rotation = 0
        
        # Create a colorful egg shape
        self.create_egg_surface()
        
    def create_egg_surface(self):
        """Create a visually appealing easter egg"""
        self.base_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw egg shape (ellipse)
        pygame.draw.ellipse(self.base_surface, (255, 100, 255), (10, 5, 40, 50))  # Magenta egg
        pygame.draw.ellipse(self.base_surface, (255, 255, 100), (10, 5, 40, 50), 3)  # Yellow outline
        
        # Add decorative stripes
        pygame.draw.arc(self.base_surface, (100, 255, 255), (10, 15, 40, 30), 0, 3.14, 3)
        pygame.draw.arc(self.base_surface, (255, 150, 255), (10, 25, 40, 30), 0, 3.14, 3)
        
        # Add sparkle effect
        pygame.draw.circle(self.base_surface, (255, 255, 255), (25, 20), 4)
        pygame.draw.circle(self.base_surface, (255, 255, 255), (35, 30), 2)
        
    def check_collision(self, car):
        """Check if car has hit the easter egg"""
        if self.collected:
            return False
        
        # Simple distance-based collision
        car_center_x = car.world_x + car.rect.width // 2
        egg_center_x = self.world_x + self.width // 2
        car_center_y = car.y + car.rect.height // 2
        egg_y = get_ground_height(self.world_x) - self.height
        egg_center_y = egg_y + self.height // 2
        
        distance = math.sqrt((car_center_x - egg_center_x)**2 + (car_center_y - egg_center_y)**2)
        
        # DEBUG: Print collision info
        if car.world_x < -1500:  # Only print when car is near easter egg area
            print(f"DEBUG: Car X: {car.world_x:.1f}, Egg X: {self.world_x}, Distance: {distance:.1f}")
        
        if distance < 50:  # Collision threshold
            self.collected = True
            print(f"EASTER EGG COLLECTED! Distance was: {distance:.1f}")
            return True
        return False
    
    def draw(self, screen, cam_x, screen_width=1000):
        """Draw the easter egg on screen"""
        if self.collected:
            return
        
        # Calculate screen position
        screen_x = self.world_x - cam_x + screen_width // 3
        screen_y = get_ground_height(self.world_x) - self.height
        
        # DEBUG: Always draw if car is near, regardless of visibility
        is_near = abs(cam_x - self.world_x) < 2500
        
        # Only draw if visible on screen OR if car is near
        if (-self.width < screen_x < screen_width + self.width) or is_near:
            # Rotate the egg for visual appeal
            self.rotation = (self.rotation + 2) % 360
            rotated_surface = pygame.transform.rotate(self.base_surface, self.rotation)
            rotated_rect = rotated_surface.get_rect(center=(screen_x + self.width // 2, screen_y + self.height // 2))
            screen.blit(rotated_surface, rotated_rect)
            
            # Draw a glow effect
            glow_radius = 35 + int(5 * math.sin(self.rotation * 0.1))
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 100, 30), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (screen_x + self.width // 2 - glow_radius, screen_y + self.height // 2 - glow_radius))
            
            # DEBUG: Draw collision box and position text
            if is_near:
                # Draw collision radius
                pygame.draw.circle(screen, (255, 0, 0), (int(screen_x + self.width // 2), int(screen_y + self.height // 2)), 50, 2)
                
                # Show position info
                try:
                    debug_font = pygame.font.Font(None, 20)
                    debug_text = debug_font.render(f"Egg @ {self.world_x}", True, (255, 255, 255))
                    screen.blit(debug_text, (screen_x, screen_y - 20))
                except:
                    pass


def invert_screen_colors(screen):
    """Apply a visual effect for easter egg activation"""
    # Create a color tint overlay that's compatible with all systems
    width, height = screen.get_size()
    
    # Create a rainbow/psychedelic tint effect
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Add a pulsing color overlay (changes based on frame)
    import time
    pulse = abs(int((time.time() * 500) % 510 - 255))
    
    # Create gradient effect
    overlay.fill((255 - pulse, pulse, 200, 60))
    screen.blit(overlay, (0, 0))
    
    # Add some visual borders to make it obvious
    pygame.draw.rect(screen, (255, 255, 0), (0, 0, width, height), 5)
    pygame.draw.rect(screen, (255, 0, 255), (5, 5, width-10, height-10), 3)
