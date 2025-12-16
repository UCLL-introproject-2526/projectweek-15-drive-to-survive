import pygame
import sys
import os
import json
import math
import random

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

ZOMBIE_COLORS = [(70,170,90),(170,70,70),(70,70,170),(170,170,0)]

# ==============================
# Game Data
# ==============================
money = 0
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
# Classes
# ==============================
class Upgrade:
    def __init__(self, folder):
        info_file = os.path.join(folder, "info.json")
        with open(info_file, "r") as f:
            data = json.load(f)
        self.name = data.get("name")
        self.car_damage = data.get("car_damage", 0)
        self.damage_reduction = data.get("damage_reduction", 0)
        self.speed_increase = data.get("speed_increase", 0)
        self.price = data.get("price", 50)
        img_file = os.path.join(folder, "image.png")
        self.image = pygame.image.load(img_file).convert_alpha()
        self.image_small = pygame.transform.scale(self.image, (80, 60))
        self.purchased = False

def load_upgrades():
    upgrades_list = []
    upgrades_folder = "upgrades"
    if not os.path.exists(upgrades_folder):
        return upgrades_list
    for folder_name in os.listdir(upgrades_folder):
        folder_path = os.path.join(upgrades_folder, folder_name)
        if os.path.isdir(folder_path):
            upgrades_list.append(Upgrade(folder_path))
    return upgrades_list

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
        self.upgrades_images = []  # Store images of purchased upgrades

    def apply_upgrade(self, upgrade):
        self.base_damage += upgrade.car_damage
        self.damage_reduction += upgrade.damage_reduction
        self.speed_multiplier += upgrade.speed_increase
        self.upgrades_images.append(upgrade.image)
        self.update_combined_image()

    def update_combined_image(self):
        scaled_base = pygame.transform.scale(self.base_image, (int(self.base_image.get_width()*0.2), int(self.base_image.get_height()*0.2)))
        combined = scaled_base.copy()
        for up_img in self.upgrades_images:
            up_scaled = pygame.transform.scale(up_img, (int(up_img.get_width()*0.2), int(up_img.get_height()*0.2)))
            combined.blit(up_scaled, (0,0))
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
            pygame.draw.rect(screen, (80,80,80), item_rect)
            if item_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.draw.rect(screen, (120,120,120), item_rect)

            # Align bottom of image to bottom of the button
            img = upgrade.image_small
            img_x = item_rect.x + 5
            img_y = item_rect.bottom - img.get_height()-15
            screen.blit(img, (img_x, img_y))

            # Gray out if not enough money
            text_color = WHITE if money >= upgrade.price else (150, 150, 150)
            text = small_font.render(f"{upgrade.name} - ${upgrade.price}", True, text_color)
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
            msg = small_font.render(f"Purchase {confirmation_upgrade.name} for ${confirmation_upgrade.price}?", True, WHITE)
            screen.blit(msg, (popup_rect.centerx - msg.get_width()//2, popup_rect.y + 20))

            # Preview image in popup
            temp_image = car.base_image.copy()
            for up_img in car.upgrades_images:
                up_scaled = pygame.transform.scale(up_img, (int(up_img.get_width()*0.2), int(up_img.get_height()*0.2)))
                temp_image.blit(up_scaled, (0,0))
            up_scaled = pygame.transform.scale(confirmation_upgrade.image, (int(confirmation_upgrade.image.get_width()*0.2), int(confirmation_upgrade.image.get_height()*0.2)))
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
                        if money >= confirmation_upgrade.price:
                            money -= confirmation_upgrade.price
                            confirmation_upgrade.purchased = True
                            car.apply_upgrade(confirmation_upgrade)
                        confirmation_active = False
                        confirmation_upgrade = None
                    elif btn_no.collidepoint(e.pos):
                        confirmation_active = False
                        confirmation_upgrade = None
                else:
                    if btn_next.collidepoint(e.pos):
                        running = False
                    # Check upgrade clicks
                    y_offset_check = 0
                    for upgrade in upgrades:
                        item_rect_check = pygame.Rect(upgrade_area.x + 10, upgrade_area.y + 10 + y_offset_check + scroll_y, 230, 60)
                        if item_rect_check.collidepoint(e.pos) and not upgrade.purchased:
                            if money >= upgrade.price:
                                confirmation_active = True
                                confirmation_upgrade = upgrade
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

car = reset_car()
garage(car)
zombies = spawn_zombies(current_level)

running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    draw_background(car.world_x)
    car.update(keys)
    
    # Update distance based on car's travel (200 is start position)
    distance = car.world_x - 200
    
    draw_ground(car.world_x)
    car.draw()

    for z in zombies:
        z.update(car)
        z.draw(car.world_x)

    draw_health_bar(car)
    ui = small_font.render(f"Distance: {int(distance)}  Fuel: {int(car.fuel)}  Money: {money}", True, BLACK)
    screen.blit(ui, (20, 20))

    if distance >= 10000 or car.health <= 0 or car.fuel <= 0:
        distance = 0
        current_level += 1
        terrain_points.clear()
        car = reset_car()
        garage(car)
        zombies = spawn_zombies(current_level)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.flip()