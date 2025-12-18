import pygame
import random
import math

# ==============================
# Day/Night Cycle System
# ==============================

class DayNightCycle:
    """Manages day/night overlay that gets darker with higher levels"""
    def __init__(self):
        self.darkness_levels = {
            1: 0,      # Full day
            2: 0,      # Full day
            3: 30,     # Slight dusk
            4: 50,     # Evening
            5: 80,     # Night
            6: 100,    # Dark night
            7: 120,    # Very dark
            8: 140,    # Almost pitch black
        }
        
    def get_darkness(self, level):
        """Get darkness value for the current level"""
        # Cap at level 8 darkness
        if level >= 8:
            return 140
        return self.darkness_levels.get(level, 0)
    
    def apply_overlay(self, screen, level):
        """Apply darkness overlay to screen"""
        darkness = self.get_darkness(level)
        if darkness > 0:
            width, height = screen.get_size()
            overlay = pygame.Surface((width, height))
            overlay.fill((0, 0, 20))  # Dark blue-ish tint
            overlay.set_alpha(darkness)
            screen.blit(overlay, (0, 0))


# ==============================
# Weather System
# ==============================

class Raindrop:
    """Individual raindrop particle"""
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.length = random.randint(8, 15)
        
    def update(self, height):
        self.y += self.speed
        if self.y > height:
            self.y = -20
            
    def draw(self, screen):
        # Draw raindrop as a line
        pygame.draw.line(screen, (180, 200, 255, 180), 
                        (self.x, self.y), 
                        (self.x - 2, self.y + self.length), 2)


class Snowflake:
    """Individual snowflake particle"""
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.drift = random.uniform(-0.5, 0.5)
        self.size = random.randint(2, 5)
        
    def update(self, height):
        self.y += self.speed
        self.x += self.drift
        if self.y > height:
            self.y = -10
            
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size)


class WeatherSystem:
    """Manages weather effects like rain, snow, and fog"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.weather_type = None  # None, 'rain', 'snow', 'fog'
        self.particles = []
        
    def set_weather(self, weather_type, level=1):
        """Set weather type based on level"""
        self.weather_type = weather_type
        self.particles = []
        
        if weather_type == 'rain':
            # More rain in higher levels
            particle_count = 80 + (level * 10)
            for _ in range(min(particle_count, 200)):
                x = random.randint(0, self.width)
                y = random.randint(-self.height, self.height)
                speed = random.uniform(8, 12)
                self.particles.append(Raindrop(x, y, speed))
                
        elif weather_type == 'snow':
            particle_count = 60 + (level * 8)
            for _ in range(min(particle_count, 150)):
                x = random.randint(0, self.width)
                y = random.randint(-self.height, self.height)
                speed = random.uniform(1, 3)
                self.particles.append(Snowflake(x, y, speed))
    
    def update(self):
        """Update all weather particles"""
        for particle in self.particles:
            particle.update(self.height)
    
    def draw(self, screen):
        """Draw weather effects"""
        # Draw fog
        if self.weather_type == 'fog':
            # Create multiple layers of fog
            for i in range(3):
                fog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                alpha = 40 - (i * 10)
                fog_surface.fill((200, 200, 210, alpha))
                screen.blit(fog_surface, (0, 0))
        
        # Draw rain or snow particles
        elif self.weather_type in ['rain', 'snow']:
            for particle in self.particles:
                particle.draw(screen)


def determine_weather_for_level(level):
    """Determine weather based on level number"""
    # Level 1-2: Clear
    if level <= 2:
        return None
    # Level 3-4: Light rain
    elif level <= 4:
        return 'rain' if random.random() < 0.5 else None
    # Level 5-6: Snow or rain
    elif level <= 6:
        choices = ['rain', 'snow', None]
        return random.choice(choices)
    # Level 7+: Fog, snow, or heavy rain
    else:
        choices = ['rain', 'snow', 'fog']
        return random.choice(choices)
