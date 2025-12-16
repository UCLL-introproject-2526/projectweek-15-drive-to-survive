import pygame
import sys
import os
import json
import math
import random
import importlib.util

# ==============================
# Initialization
# ==============================
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Car")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 22)

# ==============================
# Colors
# ==============================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GROUND = (110, 85, 55)
GROUND_DARK = (80, 60, 40)
BUTTON = (200, 70, 70)
BUTTON_HOVER = (255, 100, 80)
HEALTH_BG = (80, 0, 0)
HEALTH_FG = (200, 0, 0)
UPGRADE_BG = (50, 50, 50)
EQUIPPED_COLOR = (50, 150, 50)  # Green for equipped
PURCHASED_COLOR = (100, 100, 200)  # Blue for purchased but not equipped
CAR_BUTTON_COLOR = (70, 70, 120)  # Color for car selection buttons
ARROW_COLOR = (200, 200, 200)
ARROW_HOVER = (255, 255, 100)

ZOMBIE_COLORS = [(70,170,90),(170,70,70),(70,70,170),(170,170,0)]

# ==============================
# Game Data
# ==============================
money = 1000
distance = 0
current_level = 1
terrain_points = {}
GRAVITY = 2.2
FRICTION = 0.99
AIR_FRICTION = 0.995
TERRAIN_STEP = 10
FUEL_DELAY = 5000
fuel_empty_time = None

# Current car selection
current_car_type = "default"  # Default selected car

# ==============================
# Load Images
# ==============================
background_img = pygame.image.load("assets/background/Background.png").convert()
garage_bg_raw = pygame.image.load("assets/background/garage.png").convert()
garage_bg = pygame.transform.scale(garage_bg_raw, (WIDTH, HEIGHT))
bg_w = background_img.get_width()
bg_h = background_img.get_height()

# ==============================
# Start Screen Classes
# ==============================
class Background:
    def __init__(self, image_path):
        try:
            self.image = pygame.image.load(image_path).convert()
            self.image = pygame.transform.scale(self.image, (WIDTH, HEIGHT))
        except:
            # Fallback background if image doesn't exist
            self.image = pygame.Surface((WIDTH, HEIGHT))
            self.image.fill((30, 30, 50))
    
    def render(self, surface):
        surface.blit(self.image, (0, 0))

class Logo:
    def __init__(self, image_path, width, height, x, y):
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (width, height))
            self.rect = self.image.get_rect(center=(x, y))
        except:
            # Fallback logo
            self.image = pygame.Surface((width, height))
            self.image.fill((100, 100, 200))
            font = pygame.font.SysFont("arial", 48)
            text = font.render("ZOMBIE CAR", True, WHITE)
            text_rect = text.get_rect(center=(width//2, height//2))
            self.image.blit(text, text_rect)
            self.rect = self.image.get_rect(center=(x, y))
    
    def render(self, surface):
        surface.blit(self.image, self.rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, icon_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        
        # Load icon if provided
        self.icon = None
        if icon_path:
            try:
                self.icon = pygame.image.load(icon_path).convert_alpha()
                # Scale icon to fit the button (leave some padding)
                icon_size = min(width, height) - 20
                self.icon = pygame.transform.scale(self.icon, (icon_size, icon_size))
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")
                self.icon = None
    
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.hovered else self.color
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.hovered and mouse_pressed
    
    def render(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        if self.icon:
            icon_rect = self.icon.get_rect(center=self.rect.center)
            surface.blit(self.icon, icon_rect)
        elif self.text:
            text_surf = font.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

class ArrowButton:
    def __init__(self, x, y, width, height, direction="left"):
        self.rect = pygame.Rect(x, y, width, height)
        self.direction = direction  # "left" or "right"
        self.hovered = False
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.hovered and mouse_pressed
    
    def render(self, surface):
        color = ARROW_HOVER if self.hovered else ARROW_COLOR
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=5)
        
        # Draw arrow triangle
        center_x = self.rect.centerx
        center_y = self.rect.centery
        size = min(self.rect.width, self.rect.height) // 3
        
        if self.direction == "left":
            points = [
                (center_x + size, center_y - size),
                (center_x - size, center_y),
                (center_x + size, center_y + size)
            ]
        else:  # right
            points = [
                (center_x - size, center_y - size),
                (center_x + size, center_y),
                (center_x - size, center_y + size)
            ]
        
        pygame.draw.polygon(surface, BLACK, points)

class StartScreen:
    def __init__(self):
        # Use existing background image or create fallback
        try:
            bg_image = "assets/background/Background.png"
            self.background = Background(bg_image)
        except:
            self.background = Background("")  # Will use fallback
        
        # Create logo - adjust position as needed
        self.logo = Logo("assets/banner/image.png", 450, 300, WIDTH//2, 150)
        
        # Create buttons
        button_width = 250
        button_height = 60
        button_x = WIDTH//2 - button_width//2
        
        self.start_button = Button(button_x, 300, button_width, button_height, 
                                  'Start Game', (50, 150, 50), (70, 200, 70))
        self.credits_button = Button(button_x, 380, button_width, button_height, 
                                     'Credits', (100, 100, 150), (150, 150, 200))
        self.quit_button = Button(button_x, 460, button_width, button_height, 
                                  'Quit', (150, 50, 50), (200, 70, 70))
        
        # Settings button in top right with icon
        self.settings_button = Button(WIDTH - 70, 20, 50, 50, '', 
                                      (50, 50, 150), (70, 70, 200),
                                      icon_path="assets/banner/setting.png")
    
    def update(self, mouse_pos):
        self.start_button.update(mouse_pos)
        self.credits_button.update(mouse_pos)
        self.settings_button.update(mouse_pos)
        self.quit_button.update(mouse_pos)
    
    def handle_click(self, mouse_pos, mouse_pressed):
        if self.start_button.is_clicked(mouse_pos, mouse_pressed):
            return 'start_game'
        elif self.credits_button.is_clicked(mouse_pos, mouse_pressed):
            return 'credits'
        elif self.settings_button.is_clicked(mouse_pos, mouse_pressed):
            return 'settings'
        elif self.quit_button.is_clicked(mouse_pos, mouse_pressed):
            return 'quit'
        return None
    
    def render(self):
        self.background.render(screen)
        self.logo.render(screen)
        self.start_button.render(screen)
        self.credits_button.render(screen)
        self.quit_button.render(screen)
        self.settings_button.render(screen)

# ==============================
# Car Types Classes
# ==============================
class CarType:
    def __init__(self, folder):
        self.folder = folder
        self.name = os.path.basename(folder)
        
        info_file = os.path.join(folder, "info.json")
        if os.path.exists(info_file):
            with open(info_file, "r") as f:
                data = json.load(f)
            self.display_name = data.get("name", self.name)
            self.is_default = data.get("is_default", "False").lower() == "true"
            self.author = data.get("author", "")
            self.version = data.get("version", "1.0.0")
            # Laad de base car image uit de info.json
            self.base_image_path = data.get("base_image", "image.png")
        else:
            self.display_name = self.name.capitalize()
            self.is_default = False
            self.author = ""
            self.version = "1.0.0"
            self.base_image_path = "image.png"
        
        # Load car image
        img_file = os.path.join(folder, self.base_image_path)
        if os.path.exists(img_file):
            self.image = pygame.image.load(img_file).convert_alpha()
            self.image_small = pygame.transform.scale(self.image, (120, 80))
        else:
            # Fallback image
            self.image = pygame.Surface((200, 100), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (100, 100, 200), (0, 40, 200, 60))
            pygame.draw.rect(self.image, (100, 100, 100), (40, 20, 120, 40))
            pygame.draw.circle(self.image, BLACK, (50, 100), 20)
            pygame.draw.circle(self.image, BLACK, (150, 100), 20)
            self.image_small = pygame.transform.scale(self.image, (120, 80))
        
        # Laad upgrades specifiek voor deze auto
        self.load_car_upgrades()

    def load_car_upgrades(self):
        """Laad upgrades voor deze specifieke auto"""
        self.upgrades = []
        info_file = os.path.join(self.folder, "info.json")
        if os.path.exists(info_file):
            with open(info_file, "r") as f:
                data = json.load(f)
            
            if "upgrades" in data:
                for upgrade_name, upgrade_data in data["upgrades"].items():
                    # Zoek naar upgrade folder
                    upgrade_folder = os.path.join(self.folder, upgrade_name)
                    if os.path.exists(upgrade_folder):
                        try:
                            upgrade = Upgrade(upgrade_folder, upgrade_name)
                            self.upgrades.append(upgrade)
                        except Exception as e:
                            print(f"Error loading upgrade {upgrade_name} for car {self.name}: {e}")

# Global dictionary to store all loaded car types
ALL_CAR_TYPES = {}

def load_car_types():
    global ALL_CAR_TYPES, current_car_type
    car_types_list = []
    cars_folder = "cars"  # Changed from "upgrades" to "cars"
    
    if not os.path.exists(cars_folder):
        print(f"Warning: Cars folder '{cars_folder}' not found!")
        return car_types_list
    
    print(f"Loading car types from: {cars_folder}")
    for folder_name in os.listdir(cars_folder):
        folder_path = os.path.join(cars_folder, folder_name)
        if os.path.isdir(folder_path):
            try:
                # Create car type object
                car_type = CarType(folder_path)
                car_types_list.append(car_type)
                # Store in global dictionary
                ALL_CAR_TYPES[car_type.name.lower()] = car_type
                
                print(f"  Loaded car type: {car_type.name} (default: {car_type.is_default})")
            except Exception as e:
                print(f"Error loading car type from {folder_path}: {e}")
    
    print(f"Total cars loaded: {len(car_types_list)}")
    return car_types_list

def get_current_car_type():
    """Get the current selected car type"""
    return ALL_CAR_TYPES.get(current_car_type)

def get_car_type_list():
    """Get list of all car types"""
    return list(ALL_CAR_TYPES.values())

# ==============================
# Upgrade Classes
# ==============================
class Upgrade:
    def __init__(self, folder, upgrade_name):
        self.folder = folder
        self.name = upgrade_name
        
        # Load upgrade info from the car's info.json
        car_info_file = os.path.join(os.path.dirname(folder), "info.json")
        if os.path.exists(car_info_file):
            with open(car_info_file, "r") as f:
                car_data = json.load(f)
            
            # Check if this upgrade exists in the car's info
            if "upgrades" in car_data and upgrade_name in car_data["upgrades"]:
                upgrade_data = car_data["upgrades"][upgrade_name]
                self.car_damage = upgrade_data.get("car_damage", 0)
                self.damage_reduction = upgrade_data.get("damage_reduction", 0)
                self.speed_increase = upgrade_data.get("speed_increase", 0)
                self.price = upgrade_data.get("price", 50)
                self.has_script = upgrade_data.get("script", False)
                self.z_index = upgrade_data.get("z-index", 0)
            else:
                # Default values if upgrade not found in info
                self.car_damage = 0
                self.damage_reduction = 0
                self.speed_increase = 0
                self.price = 50
                self.has_script = False
                self.z_index = 0
        else:
            # Default values if no info.json
            self.car_damage = 0
            self.damage_reduction = 0
            self.speed_increase = 0
            self.price = 50
            self.has_script = False
            self.z_index = 0
        
        # Try to load upgrade image
        img_file = os.path.join(folder, "image.png")
        if os.path.exists(img_file):
            self.image = pygame.image.load(img_file).convert_alpha()
            self.image_small = pygame.transform.scale(self.image, (80, 60))
        else:
            # Create fallback image
            self.image = pygame.Surface((100, 60), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (150, 150, 150), (0, 0, 100, 60), border_radius=5)
            text = small_font.render(self.name[:10], True, WHITE)
            text_rect = text.get_rect(center=(50, 30))
            self.image.blit(text, text_rect)
            self.image_small = pygame.transform.scale(self.image, (80, 60))
        
        self.script_instance = None
        
        # Track purchased and equipped status separately
        self.purchased = False
        self.equipped = False
        
        # Check purchased status
        self.check_purchased_status()

    def check_purchased_status(self):
        """Check if this upgrade was purchased in a previous session"""
        try:
            if os.path.exists("upgrades_status.json"):
                with open("upgrades_status.json", "r") as f:
                    status_data = json.load(f)
                    # Use car_name.upgrade_name as key
                    key = f"{current_car_type}.{self.name}"
                    if key in status_data:
                        self.purchased = bool(status_data[key].get("purchased", False))
                        self.equipped = bool(status_data[key].get("equipped", False))
                        print(f"Loaded status for {key}: purchased={self.purchased}, equipped={self.equipped}")
        except (json.JSONDecodeError, IOError) as e:
            # If file doesn't exist or is corrupted
            print(f"Error loading status for {self.name}: {e}")
            self.purchased = False
            self.equipped = False
        except Exception as e:
            print(f"Unexpected error loading status for {self.name}: {e}")
            self.purchased = False
            self.equipped = False

    def save_status(self):
        """Save the purchased and equipped status to a file"""
        try:
            # Read existing data
            if os.path.exists("upgrades_status.json"):
                try:
                    with open("upgrades_status.json", "r") as f:
                        status_data = json.load(f)
                except (json.JSONDecodeError, IOError):
                    status_data = {}
            else:
                status_data = {}
            
            # Update the status for this upgrade
            key = f"{current_car_type}.{self.name}"
            status_data[key] = {
                "purchased": bool(self.purchased),
                "equipped": bool(self.equipped)
            }
            
            # Save back to file
            with open("upgrades_status.json", "w") as f:
                json.dump(status_data, f, indent=2)
            print(f"Saved status for {key}: purchased={self.purchased}, equipped={self.equipped}")
        except Exception as e:
            print(f"Error saving upgrade status for {self.name}: {e}")

# Global dictionary to store all loaded upgrades by name
ALL_UPGRADES = {}

def load_upgrades():
    global ALL_UPGRADES
    upgrades_list = []
    
    # Clear previous upgrades
    ALL_UPGRADES.clear()
    
    # Get current car type
    current_car = get_current_car_type()
    if not current_car:
        print("Warning: No current car type selected!")
        return upgrades_list
    
    print(f"Loading upgrades for car: {current_car.name}")
    
    # Look for upgrade folders inside the car folder
    car_folder = current_car.folder
    
    # Check if car folder exists
    if not os.path.exists(car_folder):
        print(f"Error: Car folder '{car_folder}' not found!")
        return upgrades_list
    
    # Check for subdirectories (upgrade folders)
    for folder_name in os.listdir(car_folder):
        folder_path = os.path.join(car_folder, folder_name)
        if os.path.isdir(folder_path):
            # Check if it looks like an upgrade folder (has image.png or is a known upgrade type)
            known_upgrades = ["ramp", "turret", "default", "mustang"]
            if (folder_name.lower() in known_upgrades or 
                os.path.exists(os.path.join(folder_path, "image.png"))):
                try:
                    # Create upgrade object
                    upgrade = Upgrade(folder_path, folder_name)
                    upgrades_list.append(upgrade)
                    # Store in global dictionary with unique key
                    key = f"{current_car.name}.{folder_name}"
                    ALL_UPGRADES[key] = upgrade
                    print(f"  Loaded upgrade: {folder_name} (purchased: {upgrade.purchased}, equipped: {upgrade.equipped})")
                except Exception as e:
                    print(f"Error loading upgrade from {folder_path}: {e}")
    
    print(f"Total upgrades loaded: {len(upgrades_list)}")
    return upgrades_list

def save_all_upgrades_status():
    """Save all upgrades status to file for ALL cars"""
    try:
        status_data = {}
        
        # Laad eerst de huidige status van het bestand
        if os.path.exists("upgrades_status.json"):
            try:
                with open("upgrades_status.json", "r") as f:
                    status_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                status_data = {}
        
        # Sla ook de huidige auto op
        status_data["current_car"] = current_car_type
        
        # We moeten alle auto's doorlopen om hun upgrades op te slaan
        for car_name, car_type in ALL_CAR_TYPES.items():
            # Laad upgrades voor deze auto
            old_current_car = current_car_type
            current_car_type = car_name.lower()
            
            upgrades = load_upgrades()
            for upgrade in upgrades:
                key = f"{car_name.lower()}.{upgrade.name}"
                status_data[key] = {
                    "purchased": upgrade.purchased,
                    "equipped": upgrade.equipped
                }
            
            # Herstel de originele auto
            current_car_type = old_current_car
        
        with open("upgrades_status.json", "w") as f:
            json.dump(status_data, f, indent=2)
        print(f"Saved upgrades status for {len(status_data)-1} upgrades and current car: {current_car_type}")
    except Exception as e:
        print(f"Error saving all upgrades status: {e}")

def load_all_upgrades_status():
    """Load all upgrades status and current car from file"""
    global current_car_type
    
    try:
        if os.path.exists("upgrades_status.json"):
            with open("upgrades_status.json", "r") as f:
                status_data = json.load(f)
            
            # Laad de opgeslagen auto
            if "current_car" in status_data:
                saved_car = status_data["current_car"]
                if saved_car in ALL_CAR_TYPES:
                    current_car_type = saved_car
                    print(f"Loaded saved car: {current_car_type}")
            
            # Laad de status voor de huidige auto
            current_car = get_current_car_type()
            if current_car:
                upgrades = load_upgrades()
                for upgrade in upgrades:
                    key = f"{current_car_type}.{upgrade.name}"
                    if key in status_data:
                        upgrade.purchased = bool(status_data[key].get("purchased", False))
                        upgrade.equipped = bool(status_data[key].get("equipped", False))
            
            print(f"Loaded upgrades status for {len(status_data)-1} upgrades")
    except Exception as e:
        print(f"Error loading upgrades status: {e}")

def get_upgrade_by_name(name):
    """Get an upgrade by its name from the global dictionary"""
    key = f"{current_car_type}.{name}"
    return ALL_UPGRADES.get(key)

class Car:
    def __init__(self, apply_upgrades_now=True):
        self.world_x = 200
        self.speed = 0
        self.vspeed = 0
        self.angle = 0
        self.air_angle = None
        self.health = 40
        self.fuel = 100
        self.base_speed = 0.12
        self.base_damage = 10
        self.damage_reduction = 0
        self.speed_multiplier = 1.0
        self.fuel_consumption_rate = 0.08  # Slightly increased for better visual feedback

        # Laad de auto basisafbeelding opnieuw bij elke creatie
        self.reload_car_image()
        
        self.rect = self.image.get_rect()
        self.y = get_ground_height(self.world_x) - self.rect.height
        self.upgrades_images = []  # Store tuples of (image, z_index, upgrade_name) for purchased upgrades
        self.upgrade_instances = []  # Store upgrade script instances
        
        # Apply equipped upgrades when car is created (only if apply_upgrades_now is True)
        if apply_upgrades_now:
            self.apply_equipped_upgrades()

    def reload_car_image(self):
        """Herlaad de basis auto afbeelding opnieuw"""
        current_car = get_current_car_type()
        if current_car:
            print(f"Reloading car image for: {current_car.name}")
            self.base_image = current_car.image.copy()
            self.image = pygame.transform.scale(self.base_image, 
                                              (int(self.base_image.get_width()*0.2), 
                                               int(self.base_image.get_height()*0.2)))
        else:
            print("Warning: No car type found, using fallback")
            # Fallback to default car image
            try:
                img = pygame.image.load("assets/car/car.png").convert_alpha()
                self.base_image = img
                self.image = pygame.transform.scale(self.base_image, 
                                                  (int(self.base_image.get_width()*0.2), 
                                                   int(self.base_image.get_height()*0.2)))
            except:
                # Create a simple fallback car
                self.base_image = pygame.Surface((200, 100), pygame.SRCALPHA)
                pygame.draw.rect(self.base_image, (200, 50, 50), (0, 40, 200, 60))
                pygame.draw.rect(self.base_image, (100, 100, 100), (40, 20, 120, 40))
                pygame.draw.circle(self.base_image, BLACK, (50, 100), 20)
                pygame.draw.circle(self.base_image, BLACK, (150, 100), 20)
                self.image = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), 
                                                                     int(self.base_image.get_height()*0.2)))

    def apply_equipped_upgrades(self):
        """Apply all upgrades that are equipped"""
        # Make sure upgrades are loaded
        upgrades = load_upgrades()
        
        # Herlaad eerst de basis auto afbeelding
        self.reload_car_image()
        
        # Get only equipped upgrades
        equipped_upgrades = [upgrade for upgrade in upgrades if upgrade.equipped]
        
        # Sort equipped upgrades by z-index (lowest first)
        equipped_upgrades.sort(key=lambda x: x.z_index)
        
        # Reset stats first
        self.base_damage = 10
        self.damage_reduction = 0
        self.speed_multiplier = 1.0
        self.upgrades_images = []
        self.upgrade_instances = []
        
        print(f"Applying {len(equipped_upgrades)} equipped upgrades in order:")
        for upgrade in equipped_upgrades:
            print(f"  - {upgrade.name} (z-index: {upgrade.z_index})")
            
            # Apply the upgrade stats
            self.base_damage += upgrade.car_damage
            self.damage_reduction += upgrade.damage_reduction
            self.speed_multiplier += upgrade.speed_increase
            
            # Store with z-index and name for reference
            self.upgrades_images.append({
                'image': upgrade.image,
                'z_index': upgrade.z_index,
                'name': upgrade.name
            })
            
            # Load script if it has one
            if upgrade.has_script:
                try:
                    script_path = os.path.join(upgrade.folder, "script.py")
                    if os.path.exists(script_path):
                        spec = importlib.util.spec_from_file_location("upgrade_script", script_path)
                        module = importlib.util.module_from_spec(spec)
                        
                        module.WIDTH = WIDTH
                        module.HEIGHT = HEIGHT
                        module.get_ground_height = get_ground_height
                        module.money_ref = lambda: money
                        module.screen = screen
                        
                        spec.loader.exec_module(module)
                        
                        upgrade_class_name = f"{upgrade.name.replace(' ', '')}Upgrade"
                        if hasattr(module, upgrade_class_name):
                            UpgradeClass = getattr(module, upgrade_class_name)
                            instance = UpgradeClass(self)
                            self.upgrade_instances.append(instance)
                            upgrade.script_instance = instance
                        elif hasattr(module, "UpgradeScript"):
                            instance = module.UpgradeScript(self)
                            self.upgrade_instances.append(instance)
                            upgrade.script_instance = instance
                except Exception as e:
                    print(f"Error loading upgrade script for {upgrade.name}: {e}")
        
        # Sort upgrades_images by z-index to ensure correct drawing order
        self.upgrades_images.sort(key=lambda x: x['z_index'])
        
        # Update car image with all upgrades
        self.update_combined_image()

    def apply_upgrade(self, upgrade, equip=True):
        """Apply or remove an upgrade from the car"""
        if equip:
            print(f"Equipping upgrade: {upgrade.name} (z-index: {upgrade.z_index})")
            
            # Apply the upgrade stats
            self.base_damage += upgrade.car_damage
            self.damage_reduction += upgrade.damage_reduction
            self.speed_multiplier += upgrade.speed_increase
            
            # Store upgrade with its z-index and name
            self.upgrades_images.append({
                'image': upgrade.image,
                'z_index': upgrade.z_index,
                'name': upgrade.name
            })
            
            # Sort upgrades by z-index to maintain correct drawing order
            self.upgrades_images.sort(key=lambda x: x['z_index'])
            
            # Load and initialize upgrade script if it has one
            if upgrade.has_script:
                try:
                    script_path = os.path.join(upgrade.folder, "script.py")
                    if os.path.exists(script_path):
                        spec = importlib.util.spec_from_file_location("upgrade_script", script_path)
                        module = importlib.util.module_from_spec(spec)
                        
                        module.WIDTH = WIDTH
                        module.HEIGHT = HEIGHT
                        module.get_ground_height = get_ground_height
                        module.money_ref = lambda: money
                        module.screen = screen
                        
                        spec.loader.exec_module(module)
                        
                        upgrade_class_name = f"{upgrade.name.replace(' ', '')}Upgrade"
                        if hasattr(module, upgrade_class_name):
                            UpgradeClass = getattr(module, upgrade_class_name)
                            instance = UpgradeClass(self)
                            self.upgrade_instances.append(instance)
                            upgrade.script_instance = instance
                        elif hasattr(module, "UpgradeScript"):
                            instance = module.UpgradeScript(self)
                            self.upgrade_instances.append(instance)
                            upgrade.script_instance = instance
                except Exception as e:
                    print(f"Error loading upgrade script for {upgrade.name}: {e}")
        else:
            print(f"Unequipping upgrade: {upgrade.name}")
            
            # Remove the upgrade stats
            self.base_damage -= upgrade.car_damage
            self.damage_reduction -= upgrade.damage_reduction
            self.speed_multiplier -= upgrade.speed_increase
            
            # Remove upgrade from images list
            self.upgrades_images = [up for up in self.upgrades_images if up['name'] != upgrade.name]
            
            # Remove upgrade script instance if it has one
            if upgrade.has_script and upgrade.script_instance:
                if upgrade.script_instance in self.upgrade_instances:
                    self.upgrade_instances.remove(upgrade.script_instance)
                upgrade.script_instance = None
        
        # Update equipped status
        upgrade.equipped = equip
        # Save status IMMEDIATELY after changing it
        upgrade.save_status()
        
        # Update car image
        self.update_combined_image()

    def purchase_upgrade(self, upgrade):
        """Purchase an upgrade for the first time"""
        print(f"Purchasing upgrade: {upgrade.name}")
        upgrade.purchased = True
        upgrade.equipped = True  # Auto-equip when purchased
        
        # Save status IMMEDIATELY
        upgrade.save_status()
        
        # Now apply the upgrade
        self.apply_upgrade(upgrade, equip=True)

    def update_upgrades(self, keys, zombies):
        """Update all active upgrade scripts"""
        for upgrade_instance in self.upgrade_instances:
            if hasattr(upgrade_instance, 'update'):
                upgrade_instance.update(keys, zombies)

    def draw_upgrades(self, cam_x):
        """Draw all upgrade-related graphics"""
        for upgrade_instance in self.upgrade_instances:
            if hasattr(upgrade_instance, 'draw'):
                upgrade_instance.draw(cam_x)

    def update_combined_image(self):
        """Update de gecombineerde auto afbeelding met alle upgrades"""
        # Zorg dat we de juiste basis afbeelding hebben
        scaled_base = pygame.transform.scale(self.base_image, 
                                           (int(self.base_image.get_width()*0.2), 
                                            int(self.base_image.get_height()*0.2)))
        combined = scaled_base.copy()
        
        # Draw upgrades in order of z-index (lowest first, highest last)
        for upgrade_data in self.upgrades_images:
            up_img = upgrade_data['image']
            # Schaal de upgrade afbeelding naar dezelfde grootte als de auto
            up_scaled = pygame.transform.scale(up_img, 
                                             (int(up_img.get_width()*0.2), 
                                              int(up_img.get_height()*0.2)))
            combined.blit(up_scaled, (0, 0))
        
        self.image = combined
        self.rect = self.image.get_rect()

    def update(self, keys):
        # Consume fuel when moving
        fuel_consumed = False
        
        if keys[pygame.K_RIGHT] and self.fuel > 0:
            self.speed += self.base_speed * self.speed_multiplier
            self.fuel -= self.fuel_consumption_rate
            self.fuel = max(self.fuel, 0)
            fuel_consumed = True
            
        if keys[pygame.K_LEFT] and self.fuel > 0:
            self.speed -= self.base_speed * self.speed_multiplier * 0.8
            self.fuel -= self.fuel_consumption_rate
            self.fuel = max(self.fuel, 0)
            fuel_consumed = True
        
        # Also consume a tiny amount of fuel when not moving but engine is "on" (for realism)
        if not fuel_consumed and self.fuel > 0:
            self.fuel -= self.fuel_consumption_rate * 0.1  # Idle consumption
            self.fuel = max(self.fuel, 0)

        ground_y = get_ground_height(int(self.world_x)) - self.rect.height
        next_y = get_ground_height(int(self.world_x + 1)) - self.rect.height
        slope = next_y - ground_y
        angle = math.atan2(slope, 1)

        self.vspeed += GRAVITY
        self.y += self.vspeed

        if self.y >= ground_y:
            self.y = ground_y
            self.vspeed = 0
            self.angle = -math.degrees(angle)
            self.air_angle = None
            self.speed *= FRICTION
        else:
            if self.air_angle is None:
                self.air_angle = self.angle
            self.angle = self.air_angle
            self.speed *= AIR_FRICTION

        self.world_x += self.speed
        self.rect.topleft = (WIDTH//3 - self.rect.width//2, self.y)

    def draw(self):
        rot = pygame.transform.rotate(self.image, self.angle)
        screen.blit(rot, rot.get_rect(center=self.rect.center))

class Zombie:
    def __init__(self, x):
        self.x = x
        self.alive = True
        self.rect = pygame.Rect(0, 0, 22, 40)

    def update(self, car):
        if self.alive and self.rect.colliderect(car.rect):
            self.alive = False
            damage_taken = max(0, 10 - car.damage_reduction)
            car.health -= damage_taken
            global money
            money += 10

    def draw(self, cam_x):
        if self.alive:
            sx = self.x - cam_x + WIDTH//3 - self.rect.width//2
            sy = get_ground_height(self.x) - self.rect.height
            self.rect.topleft = (sx, sy)
            pygame.draw.rect(screen, (0,200,0), self.rect, border_radius=4)

def spawn_zombies(level):
    zombies = []
    for x in range(600, 10000, 600):
        zombies.append(Zombie(x))
    return zombies

# ==============================
# Terrain Functions
# ==============================
def generate_height(x):
    base = HEIGHT - 140 - (current_level - 1) * 15
    return base + math.sin(x * 0.006) * 20 + math.sin(x * 0.02) * 5

def get_ground_height(x):
    if x not in terrain_points:
        terrain_points[x] = generate_height(x)
    return terrain_points[x]

def draw_ground(cam_x):
    pts = []
    start = int(cam_x) - 400
    for x in range(start, start + WIDTH + 800, TERRAIN_STEP):
        sx = x - cam_x + WIDTH//3
        pts.append((sx, get_ground_height(x)))
    pts += [(WIDTH, HEIGHT), (0, HEIGHT)]
    pygame.draw.polygon(screen, GROUND, pts)
    pygame.draw.lines(screen, GROUND_DARK, False, pts[:-2], 3)

# ==============================
# Health & Fuel Bars
# ==============================
def draw_health_bar(car):
    bar_width = 200
    bar_height = 20
    x = 20
    y = 50
    pygame.draw.rect(screen, HEALTH_BG, (x, y, bar_width, bar_height))
    health_width = int((car.health / 40) * bar_width)
    pygame.draw.rect(screen, HEALTH_FG, (x, y, health_width, bar_height))
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
    health_text = small_font.render(f"Health: {int(car.health)}/40", True, WHITE)
    screen.blit(health_text, (x + 5, y - 25))

def draw_fuel_bar(car):
    bar_width = 200
    bar_height = 20
    x = 20
    y = 110  # Positioned below health bar with some spacing
    pygame.draw.rect(screen, (40, 40, 0), (x, y, bar_width, bar_height))  # Dark yellow/brown for empty
    fuel_width = int((car.fuel / 100) * bar_width)
    pygame.draw.rect(screen, (255, 200, 0), (x, y, fuel_width, bar_height))  # Bright yellow for fuel
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
    fuel_text = small_font.render(f"Fuel: {int(car.fuel)}%", True, WHITE)
    screen.blit(fuel_text, (x + 5, y - 25))

# ==============================
# Garage with integrated car selection
# ==============================
def garage(car):
    global money, current_car_type
    
    # Laad alle auto's
    car_types_list = get_car_type_list()
    if not car_types_list:
        print("ERROR: No car types found!")
        return
    
    # Vind de index van de huidige auto
    current_index = 0
    for i, car_type in enumerate(car_types_list):
        if car_type.name.lower() == current_car_type:
            current_index = i
            break
    
    # Load upgrades for selected car
    load_upgrades()
    
    # Now apply equipped upgrades to the car
    car.apply_equipped_upgrades()
    
    # Now show upgrades for selected car
    running = True
    upgrades = load_upgrades()
    scroll_y = 0
    scroll_speed = 20
    confirmation_active = False
    confirmation_upgrade = None
    confirmation_action = None  # 'purchase' or 'toggle_equip'
    
    # Maak pijl buttons
    arrow_width = 40
    arrow_height = 60
    car_display_x = WIDTH // 3
    car_display_y = HEIGHT - 120
    
    left_arrow = ArrowButton(car_display_x - 150, car_display_y + 30, arrow_width, arrow_height, "left")
    right_arrow = ArrowButton(car_display_x + 110, car_display_y + 30, arrow_width, arrow_height, "right")

    while running:
        clock.tick(60)
        screen.blit(garage_bg, (0,0))

        # Show current car type
        current_car = get_current_car_type()
        if current_car:
            car_title = font.render(f"{current_car.display_name} - Upgrades", True, WHITE)
        else:
            car_title = font.render("Garage - Upgrades", True, WHITE)
        screen.blit(car_title, (WIDTH//2 - car_title.get_width()//2, 20))

        # Show current money
        money_text = small_font.render(f"Money: ${money}", True, WHITE)
        screen.blit(money_text, (50, 70))

        # Upgrade menu on the right
        upgrade_area = pygame.Rect(WIDTH - 300, 100, 250, 400)
        pygame.draw.rect(screen, UPGRADE_BG, upgrade_area)
        pygame.draw.rect(screen, WHITE, upgrade_area, 2)

        if not upgrades:
            no_upgrades_text = small_font.render("No upgrades available", True, WHITE)
            screen.blit(no_upgrades_text, (upgrade_area.centerx - no_upgrades_text.get_width()//2, 
                                          upgrade_area.centery - no_upgrades_text.get_height()//2))
        else:
            y_offset = 0
            for upgrade in upgrades:
                item_rect = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset + scroll_y, 230, 60)
                
                # Different colors based on status
                if upgrade.equipped:
                    pygame.draw.rect(screen, EQUIPPED_COLOR, item_rect)  # Green for equipped
                elif upgrade.purchased:
                    pygame.draw.rect(screen, PURCHASED_COLOR, item_rect)  # Blue for purchased but not equipped
                else:
                    pygame.draw.rect(screen, (80,80,80), item_rect)  # Gray for not purchased
                    
                if item_rect.collidepoint(pygame.mouse.get_pos()):
                    pygame.draw.rect(screen, (120,120,120), item_rect, 2)

                # Align bottom of image to bottom of the button
                img = upgrade.image_small
                img_x = item_rect.x + 5
                img_y = item_rect.bottom - img.get_height()-15
                screen.blit(img, (img_x, img_y))

                # Text based on status
                if upgrade.equipped:
                    text_color = (200, 255, 200)
                    status = ""
                elif upgrade.purchased:
                    text_color = (200, 200, 255)
                    status = ""
                elif money >= upgrade.price:
                    text_color = WHITE
                    status = ""
                else:
                    text_color = (150, 150, 150)
                    status = ""
                    
                text = small_font.render(f"{upgrade.name} - ${upgrade.price}{status}", True, text_color)
                screen.blit(text, (item_rect.x + 90, item_rect.y + 15))
                y_offset += 70

        # Car preview at bottom with arrows
        # Gebruik de huidige car image (met eventuele upgrades)
        car_display_image = pygame.transform.scale(car.image, (int(car.image.get_width()*2.8), int(car.image.get_height()*2.8)))
        car_display_rect = car_display_image.get_rect(midbottom=(car_display_x, car_display_y + 60))
        screen.blit(car_display_image, car_display_rect)
        
        # Update and draw arrows
        left_arrow.update(pygame.mouse.get_pos())
        right_arrow.update(pygame.mouse.get_pos())
        left_arrow.render(screen)
        right_arrow.render(screen)
        
        # Draw car name under the car
        if current_car:
            car_name_text = font.render(current_car.display_name, True, WHITE)
            screen.blit(car_name_text, (car_display_x - car_name_text.get_width()//2, car_display_y + 70))

        # Start level button
        btn_next = pygame.Rect(WIDTH - 200, HEIGHT - 80, 160, 50)
        color = BUTTON_HOVER if btn_next.collidepoint(pygame.mouse.get_pos()) else BUTTON
        pygame.draw.rect(screen, color, btn_next, border_radius=10)
        screen.blit(small_font.render("Start Level", True, WHITE), (btn_next.centerx - 50, btn_next.centery - 10))

        # Confirmation popup
        if confirmation_active and confirmation_upgrade:
            popup_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 120, 300, 240)
            pygame.draw.rect(screen, (60,60,60), popup_rect)
            pygame.draw.rect(screen, WHITE, popup_rect, 2)
            
            if confirmation_action == 'purchase':
                msg = small_font.render(f"Purchase {confirmation_upgrade.name} for ${confirmation_upgrade.price}?", True, WHITE)
            elif confirmation_action == 'toggle_equip':
                if confirmation_upgrade.equipped:
                    msg = small_font.render(f"Unequip {confirmation_upgrade.name}?", True, WHITE)
                else:
                    msg = small_font.render(f"Equip {confirmation_upgrade.name}?", True, WHITE)
            
            screen.blit(msg, (popup_rect.centerx - msg.get_width()//2, popup_rect.y + 20))

            # Preview image in popup - gebruik de huidige car als basis
            temp_image = car.base_image.copy()
            
            # Get all currently equipped upgrades
            current_equipped = []
            for upgrade_data in car.upgrades_images:
                # Find the upgrade object for this image
                for up in upgrades:
                    if up.name == upgrade_data['name']:
                        current_equipped.append((up.image, up.z_index))
                        break
            
            # Add or remove the upgrade for preview based on action
            if confirmation_upgrade:
                if confirmation_action == 'purchase' or (confirmation_action == 'toggle_equip' and not confirmation_upgrade.equipped):
                    # Adding the upgrade
                    current_equipped.append((confirmation_upgrade.image, confirmation_upgrade.z_index))
                # If unequipping, don't add it to the preview
            
            # Sort by z-index
            current_equipped.sort(key=lambda x: x[1])
            
            # Draw all upgrades in order
            for up_img, z_index in current_equipped:
                up_scaled = pygame.transform.scale(up_img, (int(up_img.get_width()*0.2), int(up_img.get_height()*0.2)))
                temp_image.blit(up_scaled, (0,0))
            
            temp_image_scaled = pygame.transform.scale(temp_image, (int(temp_image.get_width()*3), int(temp_image.get_height()*3)))
            temp_rect = temp_image_scaled.get_rect(midbottom=(popup_rect.centerx, popup_rect.y + 150))
            screen.blit(temp_image_scaled, temp_rect)

            # Yes/No buttons
            btn_yes = pygame.Rect(popup_rect.x + 30, popup_rect.y + 180, 100, 40)
            color = BUTTON_HOVER if btn_yes.collidepoint(pygame.mouse.get_pos()) else BUTTON
            pygame.draw.rect(screen, color, btn_yes, border_radius=5)
            screen.blit(small_font.render("Yes", True, WHITE), (btn_yes.centerx - 20, btn_yes.centery - 10))

            btn_no = pygame.Rect(popup_rect.x + 170, popup_rect.y + 180, 100, 40)
            color = BUTTON_HOVER if btn_no.collidepoint(pygame.mouse.get_pos()) else BUTTON
            pygame.draw.rect(screen, color, btn_no, border_radius=5)
            screen.blit(small_font.render("No", True, WHITE), (btn_no.centerx - 15, btn_no.centery - 10))

        # Event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # SAVE ALL STATUS BEFORE EXITING
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if confirmation_active:
                    if btn_yes.collidepoint(e.pos):
                        if confirmation_action == 'purchase':
                            if money >= confirmation_upgrade.price and not confirmation_upgrade.purchased:
                                money -= confirmation_upgrade.price
                                car.purchase_upgrade(confirmation_upgrade)
                        elif confirmation_action == 'toggle_equip':
                            # Toggle equip/unequip
                            if confirmation_upgrade.equipped:
                                car.apply_upgrade(confirmation_upgrade, equip=False)
                            else:
                                car.apply_upgrade(confirmation_upgrade, equip=True)
                        confirmation_active = False
                        confirmation_upgrade = None
                        confirmation_action = None
                    elif btn_no.collidepoint(e.pos):
                        confirmation_active = False
                        confirmation_upgrade = None
                        confirmation_action = None
                else:
                    if btn_next.collidepoint(e.pos):
                        # SAVE ALL STATUS BEFORE STARTING LEVEL
                        save_all_upgrades_status()
                        running = False
                    
                    # Check arrow clicks for car selection
                    if left_arrow.is_clicked(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
                        # Go to previous car
                        current_index = (current_index - 1) % len(car_types_list)
                        current_car_type = car_types_list[current_index].name.lower()
                        print(f"Selected car: {current_car_type}")
                        # Reset car with new selection - gebruik de nieuwe auto
                        car.__init__(apply_upgrades_now=False)
                        # Load upgrades for new car
                        load_upgrades()
                        # Now apply equipped upgrades
                        car.apply_equipped_upgrades()
                        upgrades = load_upgrades()
                    
                    elif right_arrow.is_clicked(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
                        # Go to next car
                        current_index = (current_index + 1) % len(car_types_list)
                        current_car_type = car_types_list[current_index].name.lower()
                        print(f"Selected car: {current_car_type}")
                        # Reset car with new selection - gebruik de nieuwe auto
                        car.__init__(apply_upgrades_now=False)
                        # Load upgrades for new car
                        load_upgrades()
                        # Now apply equipped upgrades
                        car.apply_equipped_upgrades()
                        upgrades = load_upgrades()
                    
                    # Check upgrade clicks
                    if upgrades:
                        y_offset_check = 0
                        for upgrade in upgrades:
                            item_rect_check = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset_check + scroll_y, 230, 60)
                            if item_rect_check.collidepoint(e.pos):
                                if not upgrade.purchased:
                                    # Not purchased yet - show purchase confirmation
                                    if money >= upgrade.price:
                                        confirmation_active = True
                                        confirmation_upgrade = upgrade
                                        confirmation_action = 'purchase'
                                else:
                                    # Already purchased - toggle equip/unequip
                                    confirmation_active = True
                                    confirmation_upgrade = upgrade
                                    confirmation_action = 'toggle_equip'
                            y_offset_check += 70
            elif e.type == pygame.MOUSEWHEEL:
                if upgrades:
                    scroll_y += e.y * scroll_speed
                    scroll_y = max(min(scroll_y, 0), -max(0, len(upgrades)*70 - upgrade_area.height))

        pygame.display.flip()

# ==============================
# Background
# ==============================
def draw_background(cam_x):
    offset = -int(cam_x % bg_w)
    screen.blit(background_img, (offset, HEIGHT - bg_h))
    screen.blit(background_img, (offset + bg_w, HEIGHT - bg_h))

# ==============================
# Simple Turret Script (backup in case script.py doesn't exist)
# ==============================
class SimpleTurret:
    def __init__(self, car):
        self.car = car
        self.bullets = []
        self.cooldown = 0
        self.max_cooldown = 15  # frames between shots
        self.bullet_speed = 8
        
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
                        global money
                        money += 15  # More money for shooting zombie
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

# ==============================
# Main Game
# ==============================
def reset_car():
    # Create car without applying upgrades yet
    car = Car(apply_upgrades_now=False)
    car.world_x = 200
    car.speed = 0
    car.vspeed = 0
    car.health = 40
    car.fuel = 100
    
    # Now apply equipped upgrades
    car.apply_equipped_upgrades()
    
    return car

# ==============================
# Game States
# ==============================
def main_game_loop():
    """Main game loop after starting from garage"""
    global money, distance, current_level, terrain_points
    
    car = reset_car()
    zombies = spawn_zombies(current_level)
    
    running = True
    while running:
        clock.tick(60)
        keys = pygame.key.get_pressed()

        draw_background(car.world_x)
        car.update(keys)
        
        # Update distance based on car's travel (200 is start position)
        distance = car.world_x - 200
        
        # Update active upgrades (like turret)
        car.update_upgrades(keys, zombies)
        
        draw_ground(car.world_x)
        car.draw()
        
        # Draw upgrade effects (like bullets)
        car.draw_upgrades(car.world_x)

        for z in zombies:
            z.update(car)
            z.draw(car.world_x)

        # Draw both health and fuel bars
        draw_health_bar(car)
        draw_fuel_bar(car)
        
        # Show shooting instruction if any upgrade has shooting capability
        has_shooting = False
        for upgrade_instance in car.upgrade_instances:
            if hasattr(upgrade_instance, 'has_shooting') or hasattr(upgrade_instance, 'shoot'):
                has_shooting = True
                break
        
        # Update UI to remove fuel from the text since we have a fuel bar
        # Position the text at the right side of the screen
        if has_shooting:
            ui_text = f"Distance: {int(distance)}  Money: ${money}  [E] to shoot"
        else:
            ui_text = f"Distance: {int(distance)}  Money: ${money}"
        
        ui = small_font.render(ui_text, True, BLACK)
        # Position at top right corner with some padding
        ui_rect = ui.get_rect()
        ui_x = WIDTH - ui_rect.width - 20  # 20 pixels from right edge
        ui_y = 20  # 20 pixels from top
        screen.blit(ui, (ui_x, ui_y))
        
        # Show warning when fuel is low
        if car.fuel < 30:
            warning_text = small_font.render("LOW FUEL!", True, (255, 50, 50))
            screen.blit(warning_text, (240, 85))  # Position near fuel bar

        if distance >= 10000 or car.health <= 0 or car.fuel <= 0:
            # Show end game reason
            if car.health <= 0:
                reason = "HEALTH DEPLETED!"
            elif car.fuel <= 0:
                reason = "OUT OF FUEL!"
            else:
                reason = "LEVEL COMPLETE!"
            
            # Display reason for a moment
            reason_text = font.render(reason, True, (255, 255, 0))
            screen.blit(reason_text, (WIDTH//2 - reason_text.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.delay(2000)  # Wait 2 seconds
            
            distance = 0
            current_level += 1
            terrain_points.clear()
            car = reset_car()  # This will reapply all purchased upgrades
            garage(car)
            zombies = spawn_zombies(current_level)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False  # Return to start screen

        pygame.display.flip()

def credits_screen():
    """Display credits screen"""
    running = True
    while running:
        clock.tick(60)
        
        # Fill background
        screen.fill((30, 30, 50))
        
        # Credits text
        title = font.render("Credits", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        credits_lines = [
            "Zombie Car Game",
            "",
            "Programming: You!",
            "Graphics: Various Sources",
            "Sound Effects: ...",
            "",
            "Special Thanks:",
            "Pygame Community",
            "",
            "Press ESC to return"
        ]
        
        y_offset = 150
        for line in credits_lines:
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 40
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.flip()

def settings_screen():
    """Display settings screen"""
    running = True
    while running:
        clock.tick(60)
        
        # Fill background
        screen.fill((30, 30, 50))
        
        # Settings text
        title = font.render("Settings", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        settings_lines = [
            "Settings are not implemented yet.",
            "",
            "Future features:",
            "- Volume controls",
            "- Graphics options",
            "- Control customization",
            "",
            "Press ESC to return"
        ]
        
        y_offset = 150
        for line in settings_lines:
            text = small_font.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_offset))
            y_offset += 40
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.flip()

# ==============================
# Main Program
# ==============================
def main():
    # Pre-load car types once at the start
    print("Starting Zombie Car...")
    print("Loading car types...")
    load_car_types()
    
    # Laad upgrades status bij start (inclusief de opgeslagen auto)
    print("Loading upgrades status...")
    load_all_upgrades_status()
    
    # Create start screen
    start_screen = StartScreen()
    
    # Game state
    game_state = "start_screen"
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        # Handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                running = False
                break
        
        # Update based on game state
        if game_state == "start_screen":
            start_screen.update(mouse_pos)
            action = start_screen.handle_click(mouse_pos, mouse_pressed)
            
            if action == 'start_game':
                # Go to garage first (which now includes car selection)
                car = Car(apply_upgrades_now=False)  # Don't apply upgrades yet
                garage(car)
                # Then start the main game
                game_state = "main_game"
            elif action == 'credits':
                game_state = "credits"
            elif action == 'settings':
                game_state = "settings"
            elif action == 'quit':
                save_all_upgrades_status()
                running = False
            
            # Render start screen
            start_screen.render()
        
        elif game_state == "main_game":
            main_game_loop()
            # After main game ends (when player presses ESC), return to start screen
            game_state = "start_screen"
        
        elif game_state == "credits":
            credits_screen()
            game_state = "start_screen"
        
        elif game_state == "settings":
            settings_screen()
            game_state = "start_screen"
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()