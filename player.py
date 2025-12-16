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
        self.fuel = 100  # Fuel level
        self.max_fuel = 100  # Maximum fuel
        self.base_speed = 0.12  # Base acceleration
        self.damage_reduction = 0  # Damage reduction from upgrades
        self.speed_multiplier = 1.0  # Speed multiplier from upgrades
        self.FUEL_CONSUMPTION_RATE = 0.1 # verandert hoeveel brandstof we per seconden verbruiken
        self.last_fuel_tick = pygame.time.get_ticks() # houd bij wanneer de laatste keer brandstof is afgegaan
        self.GRAVITY = 0.095
        self.FRICTION = 0.99
        self.AIR_FRICTION = 0.995
        self.__original_image_path = image  # Store path to reload fresh
        self.__create_image(image)
        self.__base_car_image = self.__base_image.copy()  # Store original
        self.purchased_upgrades = []  # Store purchased upgrade objects
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

    def update(self, state, keys):
        # Fuel-based acceleration
        if keys[pygame.K_RIGHT] and self.fuel > 0:
            self.speed += self.base_speed * self.speed_multiplier
        if keys[pygame.K_LEFT] and self.fuel > 0:
            self.speed -= self.base_speed * self.speed_multiplier * 0.8
            

        if self.speed != 0:
            self.update_fuel()
        
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
            # Behoud de angle in de lucht
            self.speed *= self.AIR_FRICTION
        
        # Update de world positie gebaseerd op de snelheid
        self.world_x += self.speed
        
        # Update de hitbox voor botsing te detecteren - centreer horizontaal
        self.rect.topleft = (self.x - self.rect.width//2, self.y)

    #update het brandstof niveau elke seconde dat de auto rijd
    def update_fuel(self): 
        now = pygame.time.get_ticks()
        if now - self.last_fuel_tick >= 10:
            self.fuel -= self.FUEL_CONSUMPTION_RATE
            self.fuel = max(self.fuel, 0)
            self.last_fuel_tick = now

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
    
    def apply_upgrade(self, upgrade):
        """Apply an upgrade to the player"""
        # Check if already purchased
        if upgrade in self.purchased_upgrades:
            return
        
        self.damage_reduction += upgrade.damage_reduction
        self.speed_multiplier += upgrade.speed_increase
        self.purchased_upgrades.append(upgrade)
        self.update_combined_image()
    
    def update_combined_image(self):
        """Use the latest upgrade image as the car image"""
        if self.purchased_upgrades:
            # Gebruik de laatst gekochte upgrade als de auto image
            latest_upgrade = self.purchased_upgrades[-1]
            
            # Check if this is the ramp upgrade and scale it differently
            if "ramp" in latest_upgrade.name.lower():
                up_scaled = pygame.transform.scale(latest_upgrade.image, (220, 200))
            else:
                up_scaled = pygame.transform.scale(latest_upgrade.image, (200, 200))
            
            self.__base_image = up_scaled
            self.rect = self.__base_image.get_rect()
        else:
            # Als er geen upgrades zijn, gebruik de originele auto
            self.__create_image(self.__original_image_path)
    
    def draw_fuel_bar(self, srf):
        """Draw fuel bar on screen"""
        bar_width = 200
        bar_height = 20
        x = 20
        y = 80
        
        # Background (dark gray)
        pygame.draw.rect(srf, (60, 60, 60), (x, y, bar_width, bar_height))
        
        # Foreground (fuel) - yellow/orange
        fuel_width = int((self.fuel / self.max_fuel) * bar_width)
        pygame.draw.rect(srf, (255, 200, 0), (x, y, fuel_width, bar_height))
        
        # Border
        pygame.draw.rect(srf, (0, 0, 0), (x, y, bar_width, bar_height), 2)
