import pygame
import sys
import os
import json
import math
import random
import importlib.util
import io
import wave
import struct


# ==============================
# Initialization
# ==============================
# Configure audio mixer earlier to improve reliability and reduce latency
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
except Exception:
    # pre_init is best-effort; continue regardless
    pass

# Now initialize pygame
pygame.init()
# Initialize mixer with fallbacks; if it fails, audio will be disabled gracefully
MIXER_AVAILABLE = False
try:
    pygame.mixer.init()
    MIXER_AVAILABLE = True
except Exception as e:
    print(f"mixer init default failed: {e}")
    # Try a simpler fallback init
    try:
        pygame.mixer.init(frequency=22050)
        MIXER_AVAILABLE = True
        print("mixer init fallback (22050) succeeded")
    except Exception as e2:
        MIXER_AVAILABLE = False
        print(f"mixer init fallback failed: {e2}")
        print("Tip: If mixer init keeps failing, check Windows Volume Mixer, ensure a default audio device is set, and that the Windows Audio service is running.")

print(f"Mixer available: {MIXER_AVAILABLE} (init: {pygame.mixer.get_init()})")

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
# Game Data & Modules
# ==============================
import state
from car_types import load_car_types, get_current_car_type, get_car_type_list, set_current_car_type, ALL_CAR_TYPES
from upgrades import load_upgrades, save_all_upgrades_status, load_all_upgrades_status
from car import Car
from zombies import spawn_zombies
from terrain import get_ground_height, set_current_level, clear_terrain
import sys

# Compatibility money proxy so upgrade scripts that reference main_module.money or main_module.money_ref still work
class _MoneyProxy:
    def __iadd__(self, other):
        state.money += other
        return self
    def __add__(self, other):
        return state.money + other
    def __radd__(self, other):
        return state.money + other
    def __int__(self):
        return int(state.money)
    def __repr__(self):
        return str(state.money)

# Attach proxy and money_ref to main module for scripts that expect them
main_mod = sys.modules.get('__main__')
if main_mod is not None:
    main_mod.money = _MoneyProxy()
    main_mod.money_ref = lambda: main_mod.money


GRAVITY = 0.095
FRICTION = 0.99
AIR_FRICTION = 0.995
TERRAIN_STEP = 10
FUEL_DELAY = 5000
fuel_empty_time = None

# Audio configuration
AUDIO_ENABLED = True if MIXER_AVAILABLE else False
AUDIO_VOLUME_MUSIC = 0.4
AUDIO_VOLUME_SFX = 0.6
# Engine volume behaviour: idle is soft (factor 0..1 relative to AUDIO_VOLUME_SFX), drive increases to a louder factor
ENGINE_VOLUME_IDLE_FACTOR = 0.25  # softly audible when idle
ENGINE_VOLUME_DRIVE_FACTOR = 1.0   # full SFX volume when driving
ENGINE_VOLUME_STEP = 0.04         # per-frame smoothing step toward target factor

MENU_MUSIC_PATH = os.path.join("assets", "music", "menu.mp3")
BG_MUSIC_PATH = os.path.join("assets", "music", "menu.mp3")
# Engine sound file is a wav file fallback, keep as wav to match synth fallback expectations
ENGINE_SOUND_PATH = os.path.join("assets", "music", "menu.wav")

_menu_music_loaded = False
_bg_music_loaded = False
_engine_sound = None
_engine_playing = False

# Try loading audio assets if mixer is available
if MIXER_AVAILABLE:
    try:
        menu_exists = os.path.exists(MENU_MUSIC_PATH)
        bg_exists = os.path.exists(BG_MUSIC_PATH)
        engine_exists = os.path.exists(ENGINE_SOUND_PATH)

        print(f"Audio files - menu: {menu_exists}, bg: {bg_exists}, engine: {engine_exists}")

        if menu_exists:
            try:
                pygame.mixer.music.load(MENU_MUSIC_PATH)
                _menu_music_loaded = True
            except Exception as e:
                print(f"Failed to load menu music: {e}")
        if bg_exists:
            _bg_music_loaded = True
        if engine_exists:
            try:
                _engine_sound = pygame.mixer.Sound(ENGINE_SOUND_PATH)
                # set initial idle volume (will be adjusted when driving)
                try:
                    _engine_sound.set_volume(AUDIO_VOLUME_SFX * ENGINE_VOLUME_IDLE_FACTOR)
                except Exception:
                    _engine_sound.set_volume(AUDIO_VOLUME_SFX)
            except Exception as e:
                print(f"Failed to load engine sound: {e}")
    except Exception as e:
        print(f"Audio load error: {e}")
        AUDIO_ENABLED = False

print(f"_menu_music_loaded={_menu_music_loaded}, _bg_music_loaded={_bg_music_loaded}, engine_loaded={_engine_sound is not None}, AUDIO_ENABLED={AUDIO_ENABLED}")

# Start playing menu music immediately if available (auto-play without user input)
if AUDIO_ENABLED and _menu_music_loaded:
    try:
        play_menu_music()
    except Exception as e:
        print(f"Auto-start menu music failed: {e}")

# Audio control helpers
def play_menu_music():
    global _menu_music_loaded
    if not AUDIO_ENABLED or not _menu_music_loaded:
        print("play_menu_music: skipped (audio disabled or file missing)")
        return
    try:
        print("play_menu_music: attempting to play")
        pygame.mixer.music.load(MENU_MUSIC_PATH)
        pygame.mixer.music.set_volume(AUDIO_VOLUME_MUSIC)
        pygame.mixer.music.play(-1)
        print("play_menu_music: playing")
    except Exception as e:
        print(f"Failed to play menu music: {e}")

def play_bg_music():
    global _bg_music_loaded
    if not AUDIO_ENABLED:
        print("play_bg_music: skipped (audio disabled)")
        return
    try:
        # If explicit background track is missing, fall back to menu music if available
        if _bg_music_loaded:
            path = BG_MUSIC_PATH
        elif _menu_music_loaded:
            path = MENU_MUSIC_PATH
            print("play_bg_music: falling back to menu music")
        else:
            print("play_bg_music: skipped (no tracks available)")
            return

        print(f"play_bg_music: attempting to play {path}")
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(AUDIO_VOLUME_MUSIC)
        pygame.mixer.music.play(-1)
        print("play_bg_music: playing")
    except Exception as e:
        print(f"Failed to play background music: {e}")

def stop_music():
    if not AUDIO_ENABLED:
        return
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

def stop_engine_sound():
    global _engine_sound
    try:
        if _engine_sound:
            _engine_sound.stop()
    except Exception:
        pass

# Synthesize a simple sine wave Sound buffer if no engine file is present
def synth_sine_sound(frequency=100.0, duration=1.0, volume=0.5):
    """Generate a pygame.mixer.Sound containing a sine wave.

    Returns None if mixer not initialized or generation fails.
    """
    if not MIXER_AVAILABLE:
        return None
    try:
        fmt = pygame.mixer.get_init()  # (frequency, size, channels)
        if not fmt:
            sr = 44100
            channels = 2
        else:
            sr = fmt[0]
            channels = fmt[2] if len(fmt) > 2 else 2

        n_samples = int(sr * duration)
        max_amp = int(volume * 32767)

        buf = bytearray()
        for i in range(n_samples):
            t = i / sr
            sample = int(max_amp * math.sin(2.0 * math.pi * frequency * t))
            # pack as signed 16-bit little-endian
            packed = struct.pack('<h', sample)
            if channels == 2:
                buf.extend(packed)
                buf.extend(packed)
            else:
                buf.extend(packed)
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        return sound
    except Exception as e:
        print(f"synth_sine_sound failed: {e}")
        return None

# If engine sound wasn't loaded from file, synth one as fallback
if MIXER_AVAILABLE and _engine_sound is None:
    _engine_sound = synth_sine_sound(frequency=110.0, duration=1.0, volume=0.3)
    if _engine_sound:
        # set initial idle volume for synthesized sound as well
        try:
            _engine_sound.set_volume(AUDIO_VOLUME_SFX * ENGINE_VOLUME_IDLE_FACTOR)
        except Exception:
            _engine_sound.set_volume(AUDIO_VOLUME_SFX)
        print("Synthesized engine sound for fallback")
    else:
        print("No engine sound available and synthesis failed")

# Auto test: play a short synthesized tone to verify mixer outputs audio on startup
if MIXER_AVAILABLE:
    try:
        test_tone = synth_sine_sound(frequency=440.0, duration=0.5, volume=0.5)
        if test_tone:
            print("Auto test tone: playing")
            try:
                test_tone.play()
            except Exception as e:
                print(f"Auto test tone play failed: {e}")
        else:
            print("Auto test tone: synthesis failed")
    except Exception as e:
        print(f"Auto test tone failed: {e}")

# Current car selection stored in car_types module

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
        # Draw audio status on start screen
        try:
            status = "On" if AUDIO_ENABLED else "Off"
            info = small_font.render(f"Audio: {status} (M to toggle)", True, WHITE)
            surface.blit(info, (WIDTH - info.get_width() - 20, 20))

            # Detailed diagnostics
            diag_lines = [
                f"Mixer avail: {MIXER_AVAILABLE}",
                f"mixer init: {pygame.mixer.get_init()}",
                f"menu_loaded: {_menu_music_loaded}",
                f"bg_loaded: {_bg_music_loaded}",
                f"engine_loaded: {(_engine_sound is not None)}",
            ]
            y = 50
            for line in diag_lines:
                txt = small_font.render(line, True, WHITE)
                surface.blit(txt, (WIDTH - txt.get_width() - 20, y))
                y += 20
        except Exception:
            pass

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

# Car types are handled in `car_types.py` (imported earlier)

# Upgrades handled in `upgrades.py` (imported earlier)

# Car implementation moved to `car.py` (imported at top of this file)


# Upgrade related helper methods are implemented in `car.py`. Use the `Car` class from there.

# Zombies and terrain now live in separate modules:
# - `zombies.py` provides Zombie and spawn_zombies
# - `terrain.py` provides get_ground_height, set_current_level and clear_terrain

# (See modules imported at top of this file)

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
    # Laad alle auto's
    car_types_list = get_car_type_list()
    if not car_types_list:
        print("ERROR: No car types found!")
        return

    # Vind de index van de huidige auto
    current_index = 0
    cur = get_current_car_type()
    cur_name = cur.name.lower() if cur else None
    for i, car_type in enumerate(car_types_list):
        if car_type.name.lower() == cur_name:
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
        money_text = small_font.render(f"Money: ${state.money}", True, WHITE)
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
                elif state.money >= upgrade.price:
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
                            if state.money >= confirmation_upgrade.price and not confirmation_upgrade.purchased:
                                state.money -= confirmation_upgrade.price
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
                        set_current_car_type(car_types_list[current_index].name.lower())
                        print(f"Selected car: {car_types_list[current_index].name.lower()}")
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
                        set_current_car_type(car_types_list[current_index].name.lower())
                        print(f"Selected car: {car_types_list[current_index].name.lower()}")
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
                                    if state.money >= upgrade.price:
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

# Simple turret functionality moved to `upgrades.py` (SimpleTurret) and upgrade scripts. See `upgrades.py` for a fallback turret implementation.

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
    car = reset_car()
    zombies = spawn_zombies(state.current_level) or []

    # Start background music for gameplay
    if AUDIO_ENABLED and _bg_music_loaded:
        play_bg_music()
    else:
        # If no background track available, stop any menu music
        stop_music()

    engine_playing_local = False
    # Track current engine volume factor (0..1 relative multiplier to AUDIO_VOLUME_SFX)
    engine_current_factor = 0.0

    # Start a quiet idle engine loop so there's a soft hum before driving
    if AUDIO_ENABLED and _engine_sound:
        try:
            engine_current_factor = ENGINE_VOLUME_IDLE_FACTOR
            try:
                _engine_sound.set_volume(AUDIO_VOLUME_SFX * engine_current_factor)
            except Exception:
                _engine_sound.set_volume(AUDIO_VOLUME_SFX)
            _engine_sound.play(-1)
            engine_playing_local = True
        except Exception as e:
            print(f"Failed to start engine idle sound: {e}")
            engine_playing_local = False

    running = True
    while running:
        clock.tick(60)
        pressed = pygame.key.get_pressed()

        # Engine sound handling: smoothly increase volume when accelerating, lower when idle
        try:
            accel_pressed = pressed[pygame.K_RIGHT] or pressed[pygame.K_LEFT]
        except Exception:
            accel_pressed = False

        if AUDIO_ENABLED and _engine_sound:
            # Determine desired target factor
            if car.fuel <= 0:
                target_factor = 0.0
            else:
                target_factor = ENGINE_VOLUME_DRIVE_FACTOR if accel_pressed else ENGINE_VOLUME_IDLE_FACTOR

            # Ensure sound is playing if we need any audibility
            if target_factor > 0 and not engine_playing_local:
                try:
                    _engine_sound.play(-1)
                    engine_playing_local = True
                    # start from zero so it can ramp up
                    engine_current_factor = 0.0
                except Exception as e:
                    print(f"Failed to start engine sound: {e}")
                    engine_playing_local = False

            # Smoothly move current factor toward target
            if engine_playing_local:
                if engine_current_factor < target_factor:
                    engine_current_factor = min(target_factor, engine_current_factor + ENGINE_VOLUME_STEP)
                elif engine_current_factor > target_factor:
                    engine_current_factor = max(target_factor, engine_current_factor - ENGINE_VOLUME_STEP)

                # Apply volume
                try:
                    _engine_sound.set_volume(AUDIO_VOLUME_SFX * engine_current_factor)
                except Exception:
                    pass

                # If target is truly silent and we've ramped down to zero, stop to save resources
                if target_factor == 0.0 and abs(engine_current_factor) < 1e-4:
                    try:
                        _engine_sound.stop()
                    except Exception:
                        pass
                    engine_playing_local = False

        

        draw_background(car.world_x)
        car.update(pressed)

        # Update distance based on car's travel (200 is start position)
        state.distance = car.world_x - 200

        # Update active upgrades (like turret)
        car.update_upgrades(pressed, zombies)

        draw_ground(car.world_x)
        car.draw(screen)

        # Draw upgrade effects (like bullets)
        car.draw_upgrades(car.world_x, screen)

        for z in zombies:
            # Pass terrain accessor into zombie update/draw
            gained = z.update(car, get_ground_height)
            if gained:
                state.money += gained
            z.draw(screen, car.world_x, get_ground_height)

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
            ui_text = f"Distance: {int(state.distance)}  Money: ${state.money}  [E] to shoot"
        else:
            ui_text = f"Distance: {int(state.distance)}  Money: ${state.money}"
        
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

        if state.distance >= 10000 or car.health <= 0 or car.fuel <= 0:
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
            
            state.distance = 0
            state.current_level += 1
            set_current_level(state.current_level)
            clear_terrain()
            car = reset_car()  # This will reapply all purchased upgrades
            garage(car)
            zombies = spawn_zombies(state.current_level) or []

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False  # Return to start screen

        pygame.display.flip()

    # Cleanup audio when leaving the main game loop
    try:
        stop_engine_sound()
    except Exception:
        pass
    try:
        stop_music()
    except Exception:
        pass

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
            "Settings:",
            "",
            "Audio: {} (press M to toggle)".format("On" if AUDIO_ENABLED else "Off"),
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
    global AUDIO_ENABLED
    # Pre-load car types once at the start
    print("Starting Zombie Car...")
    print("Loading car types...")
    load_car_types()
    
    # Laad upgrades status bij start (inclusief de opgeslagen auto)
    print("Loading upgrades status...")
    load_all_upgrades_status()
    
    # Create start screen
    start_screen = StartScreen()
    # Debug audio status at startup
    print(f"main start: MIXER_AVAILABLE={MIXER_AVAILABLE}, AUDIO_ENABLED={AUDIO_ENABLED}, _menu_music_loaded={_menu_music_loaded}, _bg_music_loaded={_bg_music_loaded}")
    # Start menu music if available
    if AUDIO_ENABLED and _menu_music_loaded:
        play_menu_music()
    
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
            elif e.type == pygame.KEYDOWN:
                # Toggle audio with M key
                if e.key == pygame.K_m:
                    AUDIO_ENABLED = not AUDIO_ENABLED
                    print(f"Audio toggled: AUDIO_ENABLED={AUDIO_ENABLED}")
                    if not AUDIO_ENABLED:
                        stop_music()
                        stop_engine_sound()
                    else:
                        # Restart appropriate music based on state
                        if game_state == "start_screen":
                            play_menu_music()
                        elif game_state == "main_game":
                            play_bg_music()
                # Test tone (synthesized) with T key
                if e.key == pygame.K_t:
                    if MIXER_AVAILABLE:
                        print("T pressed: playing test tone")
                        tone = synth_sine_sound(frequency=440.0, duration=0.5, volume=0.5)
                        if tone:
                            tone.play()
                        else:
                            print("Failed to generate test tone")
                    else:
                        print("Mixer not available; cannot play test tone")
        
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
            if AUDIO_ENABLED and _menu_music_loaded:
                play_menu_music()
        
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