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
FUEL_CONSUMPTION_RATE = 0.05

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
# Classes
# ==============================
class Upgrade:
    def __init__(self, folder):
        self.folder = folder
        info_file = os.path.join(folder, "info.json")
        with open(info_file, "r") as f:
            data = json.load(f)
        self.name = data.get("name")
        self.car_damage = data.get("car_damage", 0)
        self.damage_reduction = data.get("damage_reduction", 0)
        self.speed_increase = data.get("speed_increase", 0)
        self.price = data.get("price", 50)
        self.has_script = data.get("script", False)
        self.z_index = data.get("z-index", 0)  # Default z-index is 0
        
        img_file = os.path.join(folder, "image.png")
        self.image = pygame.image.load(img_file).convert_alpha()
        self.image_small = pygame.transform.scale(self.image, (80, 60))
        self.script_instance = None
        
        # Track purchased and equipped status separately
        self.purchased = False
        self.equipped = False
        self.check_purchased_status()

    def check_purchased_status(self):
        """Check if this upgrade was purchased in a previous session"""
        try:
            if os.path.exists("upgrades_status.json"):
                with open("upgrades_status.json", "r") as f:
                    status_data = json.load(f)
                    if self.name in status_data:
                        self.purchased = status_data[self.name].get("purchased", False)
                        self.equipped = status_data[self.name].get("equipped", False)
        except (json.JSONDecodeError, IOError):
            # If file doesn't exist or is corrupted
            pass

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
            status_data[self.name] = {
                "purchased": self.purchased,
                "equipped": self.equipped
            }
            
            # Save back to file
            with open("upgrades_status.json", "w") as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            print(f"Error saving upgrade status: {e}")

# Global dictionary to store all loaded upgrades by name
ALL_UPGRADES = {}

def load_upgrades():
    global ALL_UPGRADES
    upgrades_list = []
    upgrades_folder = "upgrades"
    
    if not os.path.exists(upgrades_folder):
        return upgrades_list
    
    for folder_name in os.listdir(upgrades_folder):
        folder_path = os.path.join(upgrades_folder, folder_name)
        if os.path.isdir(folder_path):
            try:
                # Create upgrade object
                upgrade = Upgrade(folder_path)
                upgrades_list.append(upgrade)
                # Store in global dictionary
                ALL_UPGRADES[upgrade.name] = upgrade
            except Exception as e:
                print(f"Error loading upgrade from {folder_path}: {e}")
    
    return upgrades_list

def save_all_upgrades_status():
    """Save all upgrades status to file"""
    try:
        status_data = {}
        for upgrade_name, upgrade in ALL_UPGRADES.items():
            status_data[upgrade.name] = {
                "purchased": upgrade.purchased,
                "equipped": upgrade.equipped
            }
        
        with open("upgrades_status.json", "w") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Error saving all upgrades status: {e}")

def get_upgrade_by_name(name):
    """Get an upgrade by its name from the global dictionary"""
    return ALL_UPGRADES.get(name)

class Car:
    def __init__(self):
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

        img = pygame.image.load("assets/car/car.png").convert_alpha()
        self.base_image = img  # Keep base car
        self.image = pygame.transform.scale(img, (int(img.get_width()*0.2), int(img.get_height()*0.2)))
        self.rect = self.image.get_rect()
        self.y = get_ground_height(self.world_x) - self.rect.height
        self.upgrades_images = []  # Store tuples of (image, z_index, upgrade_name) for purchased upgrades
        self.upgrade_instances = []  # Store upgrade script instances
        
        # Apply equipped upgrades when car is created
        self.apply_equipped_upgrades()

    def apply_equipped_upgrades(self):
        """Apply all upgrades that are equipped"""
        # Make sure upgrades are loaded
        upgrades = load_upgrades()
        
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
        
        print(f"Applying {len(equipped_upgrades)} equipped upgrades in order:")  # Debug
        for upgrade in equipped_upgrades:
            print(f"  - {upgrade.name} (z-index: {upgrade.z_index})")  # Debug
            
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
            print(f"Equipping upgrade: {upgrade.name} (z-index: {upgrade.z_index})")  # Debug
            
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
                        # Dynamically import the script
                        spec = importlib.util.spec_from_file_location("upgrade_script", script_path)
                        module = importlib.util.module_from_spec(spec)
                        
                        # Inject necessary globals into the module
                        module.WIDTH = WIDTH
                        module.HEIGHT = HEIGHT
                        module.get_ground_height = get_ground_height
                        module.money_ref = lambda: money  # Reference to money variable
                        module.screen = screen
                        
                        spec.loader.exec_module(module)
                        
                        # Look for a class named after the upgrade
                        upgrade_class_name = f"{upgrade.name.replace(' ', '')}Upgrade"
                        if hasattr(module, upgrade_class_name):
                            UpgradeClass = getattr(module, upgrade_class_name)
                            instance = UpgradeClass(self)
                            self.upgrade_instances.append(instance)
                            upgrade.script_instance = instance
                        # Also check for generic "UpgradeScript" class
                        elif hasattr(module, "UpgradeScript"):
                            instance = module.UpgradeScript(self)
                            self.upgrade_instances.append(instance)
                            upgrade.script_instance = instance
                except Exception as e:
                    print(f"Error loading upgrade script for {upgrade.name}: {e}")
        else:
            print(f"Unequipping upgrade: {upgrade.name}")  # Debug
            
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
        save_all_upgrades_status()
        
        # Update car image
        self.update_combined_image()

    def purchase_upgrade(self, upgrade):
        """Purchase an upgrade for the first time"""
        print(f"Purchasing upgrade: {upgrade.name}")  # Debug
        upgrade.purchased = True
        upgrade.equipped = True  # Auto-equip when purchased
        save_all_upgrades_status()
        
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
        scaled_base = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), int(self.base_image.get_height()*0.2)))
        combined = scaled_base.copy()
        
        # Draw upgrades in order of z-index (lowest first, highest last)
        for upgrade_data in self.upgrades_images:
            up_img = upgrade_data['image']
            up_scaled = pygame.transform.scale(up_img, (int(up_img.get_width()*0.2), int(up_img.get_height()*0.2)))
            combined.blit(up_scaled, (0, 0))
        
        self.image = combined
        self.rect = self.image.get_rect()

    def update(self, keys):
        if keys[pygame.K_RIGHT] and self.fuel > 0:
            self.speed += self.base_speed * self.speed_multiplier
            self.fuel -= FUEL_CONSUMPTION_RATE
            self.fuel = max(self.fuel, 0)
        if keys[pygame.K_LEFT] and self.fuel > 0:
            self.speed -= self.base_speed * self.speed_multiplier * 0.8
            self.fuel -= FUEL_CONSUMPTION_RATE
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
# Garage with confirmation
# ==============================
def garage(car):
    global money
    running = True
    upgrades = load_upgrades()
    scroll_y = 0
    scroll_speed = 20
    confirmation_active = False
    confirmation_upgrade = None
    confirmation_action = None  # 'purchase' or 'toggle_equip'

    while running:
        clock.tick(60)
        screen.blit(garage_bg, (0,0))

        title = font.render("Garage - Upgrades", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 20))

        # Show current money
        money_text = small_font.render(f"Money: ${money}", True, WHITE)
        screen.blit(money_text, (50, 70))

        # Upgrade menu on the right
        upgrade_area = pygame.Rect(WIDTH - 300, 100, 250, 400)
        pygame.draw.rect(screen, UPGRADE_BG, upgrade_area)
        pygame.draw.rect(screen, WHITE, upgrade_area, 2)

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

        # Car preview at bottom
        car_display_image = pygame.transform.scale(car.image, (int(car.image.get_width()*2.8), int(car.image.get_height()*2.8)))
        car_display_rect = car_display_image.get_rect(midbottom=(WIDTH//3, HEIGHT - 10))
        screen.blit(car_display_image, car_display_rect)

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

            # Preview image in popup
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
                        running = False
                    # Check upgrade clicks
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
                scroll_y += e.y * scroll_speed
                scroll_y = max(min(scroll_y, 0), -max(0, len(upgrades)*70 - upgrade_area.height))

        pygame.display.flip()

# ==============================
# Health Bar
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
    car = Car()
    car.world_x = 200
    car.speed = 0
    car.vspeed = 0
    car.health = 40
    car.fuel = 100
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

        draw_health_bar(car)
        
        # Show shooting instruction if any upgrade has shooting capability
        has_shooting = False
        for upgrade_instance in car.upgrade_instances:
            if hasattr(upgrade_instance, 'has_shooting') or hasattr(upgrade_instance, 'shoot'):
                has_shooting = True
                break
        
        if has_shooting:
            ui = small_font.render(f"Distance: {int(distance)}  Fuel: {int(car.fuel)}  Money: {money}  [E] to shoot", True, BLACK)
        else:
            ui = small_font.render(f"Distance: {int(distance)}  Fuel: {int(car.fuel)}  Money: {money}", True, BLACK)
        screen.blit(ui, (20, 20))

        if distance >= 10000 or car.health <= 0 or car.fuel <= 0:
            distance = 0
            current_level += 1
            terrain_points.clear()
            car = reset_car()  # This will reapply all purchased upgrades
            garage(car)
            zombies = spawn_zombies(current_level)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
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
    # Pre-load upgrades once at the start
    load_upgrades()
    
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
                running = False
                break
        
        # Update based on game state
        if game_state == "start_screen":
            start_screen.update(mouse_pos)
            action = start_screen.handle_click(mouse_pos, mouse_pressed)
            
            if action == 'start_game':
                # Go to garage first
                car = reset_car()
                garage(car)
                # Then start the main game
                game_state = "main_game"
            elif action == 'credits':
                game_state = "credits"
            elif action == 'settings':
                game_state = "settings"
            elif action == 'quit':
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