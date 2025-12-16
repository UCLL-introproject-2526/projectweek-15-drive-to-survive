import pygame
import math

class Player: 
    def __init__(self, image):
        self.x = 1024 // 3  # Positie van de speler (op 1/3 van het scherm)
        self.world_x = 200  # Positie in de wereld
        self.speed = 0
        self.vspeed = 0
        self.angle = 0
        self.air_angle = None
        self.health = 100  # Player health
        self.max_health = 100  # Maximum health
        self.GRAVITY = 0.095
        self.FRICTION = 0.99
        self.AIR_FRICTION = 0.995
        self.__create_image(image)
        self.rect = self.__base_image.get_rect()
        self.y = 0  # Wordt goedgezet na dat State is aangemaakt

    def __create_image(self, image):
        # Laad de auto en zet het op 200 bij 200 pixels
        self.__base_image = pygame.image.load(image)
        self.__base_image = pygame.transform.scale(self.__base_image, (200, 200))
        self.__image = self.__base_image
    
    def initialize_position(self, state):
        """Call this after state is created to set initial ground position"""
        self.y = state.get_ground_height(int(self.world_x)) - self.rect.height

    def update(self, state):
        # De huidige ground height krijgen
        ground_y = state.get_ground_height(int(self.world_x)) - self.rect.height
        
        # Helling berekenen voor angle van auto te zetten
        next_y = state.get_ground_height(int(self.world_x + 1)) - self.rect.height
        slope = next_y - ground_y
        terrain_angle = math.atan2(slope, 1)
        
        # Zwaartekracht toepassen
        self.vspeed += self.GRAVITY
        self.y += self.vspeed
        
        # Checkt of je op de grond zit of in de lucht
        if self.y >= ground_y:
            # Op de grond - ga dan naar grond positie
            self.y = ground_y
            self.vspeed = 0
            # Smooth transitie naar terrain angle
            target_angle = -math.degrees(terrain_angle)
            angle_diff = target_angle - self.angle
            self.angle += angle_diff * 0.3  # Smooth interpolatie
            self.air_angle = None
            self.speed *= self.FRICTION
        else:
            # In de lucht
            if self.air_angle is None:
                self.air_angle = self.angle
            # Pas de angle aan gebaseerd op de bewegingsrichting (vspeed en speed)
            if self.speed != 0:
                self.angle = -math.degrees(math.atan2(self.vspeed, self.speed))
            self.speed *= self.AIR_FRICTION
        
        # Update de world positie gebaseerd op de snelheid
        self.world_x += self.speed
        
        # Update de hitbox voor botsing te detecteren - centreer horizontaal
        self.rect.topleft = (self.x - self.rect.width//2, self.y)

    def render(self, srf, state):
        # Draai de auto gebaseerd op de angle
        rotated_image = pygame.transform.rotate(self.__base_image, self.angle)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        srf.blit(rotated_image, rotated_rect)
    
    def draw_health_bar(self, srf):
        """Draw health bar on screen"""
        bar_width = 200
        bar_height = 20
        x = 20
        y = 50
        
        # Background (rood)
        pygame.draw.rect(srf, (80, 0, 0), (x, y, bar_width, bar_height))
        
        # Foreground (health)
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(srf, (200, 0, 0), (x, y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(srf, (0, 0, 0), (x, y, bar_width, bar_height), 2)
    
    def take_damage(self, damage):
        """Reduce player health by damage amount"""
        self.health -= damage
        self.health = max(0, self.health)  # Don't go below 0
    
    def is_alive(self):
        """Check if player is still alive"""
        return self.health > 0
