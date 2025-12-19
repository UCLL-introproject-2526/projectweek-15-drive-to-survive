import pygame
import sys
import os
import json
import math
import random
import importlib.util
import io
import shutil
try:
    import wave
except Exception:
    wave = None
import struct
import asyncio



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
pygame.display.set_caption("Drive to Survive")
clock = pygame.time.Clock()

# Load custom pixel font
try:
    font = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 26)
    small_font = pygame.font.Font("assets/fonts/Grand9K Pixel.ttf", 18)
except:
    # Fallback to system font if custom font fails to load
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
from settings import settings_screen, load_settings
from garage import garage
from credits import credits_screen
from audio import AudioManager
from levels import get_level_manager, reset_level_manager
from easter_egg import EasterEgg, invert_screen_colors
from visual_effects import DayNightCycle, WeatherSystem, determine_weather_for_level
from level_result import LevelResult
from upgrades import save_all_upgrades_status, load_all_upgrades_status
from start_screen import StartScreen
from controls_screen import ControlsScreen

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


GRAVITY = 0.095
FRICTION = 0.99
AIR_FRICTION = 0.995
TERRAIN_STEP = 10
FUEL_DELAY = 5000
fuel_empty_time = None

# Initialize audio manager
audio_manager = AudioManager(MIXER_AVAILABLE)

# Current car selection stored in car_types module

# ==============================
# Load Images
# ==============================
background_img = pygame.image.load("assets/background/Background.png").convert()
garage_bg_raw = pygame.image.load("assets/background/garage.png").convert()
garage_bg = pygame.transform.scale(garage_bg_raw, (WIDTH, HEIGHT))
bg_w = background_img.get_width()
bg_h = background_img.get_height()

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
    health_width = int((car.health / car.max_health) * bar_width)
    pygame.draw.rect(screen, HEALTH_FG, (x, y, health_width, bar_height))
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
    health_text = small_font.render(f"Health: {int(car.health)}/{int(car.max_health)}", True, WHITE)
    screen.blit(health_text, (x + 5, y - 25))

def draw_fuel_bar(car):
    bar_width = 200
    bar_height = 20
    x = 20
    y = 110  # Positioned below health bar with some spacing
    pygame.draw.rect(screen, (40, 40, 0), (x, y, bar_width, bar_height))  # Dark yellow/brown for empty
    fuel_width = int((car.fuel / car.max_fuel) * bar_width)
    pygame.draw.rect(screen, (255, 200, 0), (x, y, fuel_width, bar_height))  # Bright yellow for fuel
    pygame.draw.rect(screen, BLACK, (x, y, bar_width, bar_height), 2)
    fuel_text = small_font.render(f"Fuel: {int(car.fuel)}Liters", True, WHITE)
    screen.blit(fuel_text, (x + 5, y - 25))

def draw_level_info():
    """Display current level information"""
    level_manager = get_level_manager()
    config = level_manager.get_current_level_config()
    
    # Display level number and description at top center
    level_text = small_font.render(f"Level {config.level_number}: {config.description}", True, WHITE)
    level_rect = level_text.get_rect()
    level_x = WIDTH // 2 - level_rect.width // 2
    screen.blit(level_text, (level_x, 20))
    
    # Display progress bar for level completion
    bar_width = 300
    bar_height = 15
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 50
    
    # Calculate progress
    progress = min(1.0, state.distance / config.distance_required)
    
    # Draw progress bar
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    progress_width = int(progress * bar_width)
    pygame.draw.rect(screen, (50, 200, 50), (bar_x, bar_y, progress_width, bar_height))
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    # Display distance progress
    progress_text = small_font.render(f"{int(state.distance)}m / {config.distance_required}m", True, WHITE)
    screen.blit(progress_text, (bar_x + bar_width + 10, bar_y - 3))

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

async def show_level_intro(level_number):
    """Display level introduction screen before starting the level"""
    level_manager = get_level_manager()
    config = level_manager.get_level_config(level_number)
    
    # Display level info
    intro_duration = 120  # frames (2 seconds at 60 FPS)
    for frame in range(intro_duration):
        screen.fill((20, 20, 30))  # Dark background
        
        # Title
        level_title = font.render(f"LEVEL {config.level_number}", True, (255, 255, 100))
        screen.blit(level_title, (WIDTH//2 - level_title.get_width()//2, HEIGHT//3))
        
        # Description
        desc_text = small_font.render(config.description, True, WHITE)
        screen.blit(desc_text, (WIDTH//2 - desc_text.get_width()//2, HEIGHT//3 + 60))
        
        # Stats
        y_offset = HEIGHT//2
        stats = [
            f"Distance to Complete: {config.distance_required}m",
            f"Zombies: {config.zombie_count}",
            f"Completion Bonus: ${config.money_reward}"
        ]
        
        for stat in stats:
            stat_text = small_font.render(stat, True, (200, 200, 200))
            screen.blit(stat_text, (WIDTH//2 - stat_text.get_width()//2, y_offset))
            y_offset += 35
        
        # Ready message
        if frame > intro_duration // 2:
            ready_text = font.render("GET READY!", True, (255, 100, 100))
            screen.blit(ready_text, (WIDTH//2 - ready_text.get_width()//2, HEIGHT - 100))
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
        
        # Allow skipping with any key
        for e in pygame.event.get():
            if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                return
            elif e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def reset_car(controls=None):
    # Create car without applying upgrades yet
    car = Car(apply_upgrades_now=False, controls=controls)
    car.world_x = 200
    car.speed = 0
    car.vspeed = 0
    car.health = 40
    car.fuel = 100
    car.max_fuel = car.fuel
    car.max_health = car.health
    
    # Now apply equipped upgrades
    car.apply_equipped_upgrades()
    
    return car

# ==============================
# Game States
# ==============================
async def main_game_loop(controls=None):
    """Main game loop after starting from garage"""
    # Default controls if none provided
    if controls is None:
        controls = {
            'accelerate_right': pygame.K_RIGHT,
            'accelerate_left': pygame.K_LEFT,
            'shoot': pygame.K_e
        }
    
    # Stop menu music before showing level intro
    try:
        audio_manager.stop_music()
    except Exception:
        pass
    
    # Show level intro screen
    await show_level_intro(state.current_level)
    
    # Show controls screen after level intro
    controls_screen = ControlsScreen(screen, font, small_font)
    continue_game = await controls_screen.show(controls, f"Level {state.current_level}")
    if not continue_game:
        return  # Player cancelled, return to menu
    
    # Track starting money for this level attempt
    level_start_money = state.money
    
    car = reset_car(controls)
    zombies = spawn_zombies(state.current_level) or []
    
    # Create easter egg at position -2000
    easter_egg = EasterEgg(x_position=-2000)
    # Reset easter egg state when starting new game
    state.easter_egg_activated = False
    
    # Initialize visual effects
    day_night = DayNightCycle()
    weather = WeatherSystem(WIDTH, HEIGHT)
    weather.set_weather(determine_weather_for_level(state.current_level), state.current_level)

    # Ensure all audio is stopped and reset before starting
    try:
        audio_manager.stop_engine_sound()
        audio_manager.stop_music()
    except Exception:
        pass
    
    # Small delay to ensure clean state
    await asyncio.sleep(0.05)
    
    # Start game audio (music and engine)
    if audio_manager.AUDIO_ENABLED and audio_manager._bg_music_loaded:
        audio_manager.play_bg_music()

    engine_playing_local = False
    # Track current engine volume factor (0..1 relative multiplier to AUDIO_VOLUME_SFX)
    engine_current_factor = 0.0
    _engine_sound = audio_manager.get_engine_sound()

    # Start a quiet idle engine loop so there's a soft hum before driving
    if audio_manager.AUDIO_ENABLED and _engine_sound:
        try:
            engine_current_factor = audio_manager.ENGINE_VOLUME_IDLE_FACTOR
            try:
                _engine_sound.set_volume(audio_manager.AUDIO_VOLUME_SFX * engine_current_factor)
            except Exception:
                _engine_sound.set_volume(audio_manager.AUDIO_VOLUME_SFX)
            _engine_sound.play(-1)
            engine_playing_local = True
        except Exception as e:
            print(f"Failed to start engine idle sound: {e}")
            engine_playing_local = False

    running = True
    while running:
        clock.tick(60)
        await asyncio.sleep(0)
        pressed = pygame.key.get_pressed()

        # Engine sound handling: smoothly increase volume when accelerating, lower when idle
        try:
            accel_pressed = pressed[controls['accelerate_right']] or pressed[controls['accelerate_left']]
        except Exception:
            accel_pressed = False

        if audio_manager.AUDIO_ENABLED and _engine_sound:
            # Determine desired target factor
            if car.fuel <= 0:
                target_factor = 0.0
            else:
                target_factor = audio_manager.ENGINE_VOLUME_DRIVE_FACTOR if accel_pressed else audio_manager.ENGINE_VOLUME_IDLE_FACTOR

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
                    engine_current_factor = min(target_factor, engine_current_factor + audio_manager.ENGINE_VOLUME_STEP)
                elif engine_current_factor > target_factor:
                    engine_current_factor = max(target_factor, engine_current_factor - audio_manager.ENGINE_VOLUME_STEP)

                # Apply volume
                try:
                    _engine_sound.set_volume(audio_manager.AUDIO_VOLUME_SFX * engine_current_factor)
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
        
        # Check easter egg collision
        if easter_egg.check_collision(car):
            state.easter_egg_activated = True
            # Play a sound effect if available
            try:
                # You could add a special sound effect here
                pass
            except Exception:
                pass

        # Update active upgrades (like turret)
        car.update_upgrades(pressed, zombies)
        
        # Update weather effects
        weather.update()

        draw_ground(car.world_x)
        
        # Draw easter egg before car
        easter_egg.draw(screen, car.world_x)
        
        car.draw(screen)

        # Draw upgrade effects (like bullets)
        car.draw_upgrades(car.world_x, screen)

        # Update zombie positions - make them walk towards the car
        for z in zombies:
            if z.alive and not z.dying:
                # Calculate direction to car and move towards it
                if z.x < car.world_x:
                    # Zombie is to the left, move right
                    z.x += 1.5  # Zombie speed
                elif z.x > car.world_x:
                    # Zombie is to the right, move left
                    z.x -= 1.5

        for z in zombies:
            # Pass terrain accessor into zombie update/draw
            gained = z.update(car, get_ground_height)
            if gained:
                state.money += gained
            
            z.draw(screen, car.world_x, get_ground_height)

        # Draw both health and fuel bars
        draw_health_bar(car)
        draw_fuel_bar(car)
        draw_level_info()  # Display level information
        
        # Show shooting instruction if any upgrade has shooting capability
        has_shooting = False
        shooting_upgrade = None
        for upgrade_instance in car.upgrade_instances:
            if hasattr(upgrade_instance, 'has_shooting') or hasattr(upgrade_instance, 'shoot'):
                has_shooting = True
                shooting_upgrade = upgrade_instance
                break
        
        # Update UI: reserve space on the right for an ammo badge and place
        # money immediately to its left. When ammo is present the badge
        # width is computed from the actual text so it grows as needed.
        padding = 6

        ammo_bg_y = 20

        if has_shooting and shooting_upgrade and hasattr(shooting_upgrade, 'ammo'):
            # Compute width from actual ammo text so badge adapts to number length
            ammo_display = f"Ammo: {shooting_upgrade.ammo}"
            ammo_text = small_font.render(ammo_display, True, WHITE)
            ammo_bg_w = ammo_text.get_width() + padding * 2
            ammo_bg_h = ammo_text.get_height() + padding * 2
            ammo_bg_x = WIDTH - 20 - ammo_bg_w

            # Money sits to the left of the ammo badge (fixed relative to badge)
            money_text = small_font.render(f"Money: ${state.money}", True, WHITE)
            money_rect = money_text.get_rect(topright=(ammo_bg_x - 8, ammo_bg_y))
            screen.blit(money_text, money_rect)

            # Semi-transparent black background for readability
            ammo_bg = pygame.Surface((ammo_bg_w, ammo_bg_h), pygame.SRCALPHA)
            ammo_bg.fill((0, 0, 0, 160))
            screen.blit(ammo_bg, (ammo_bg_x, ammo_bg_y))

            # Blit ammo count inside the badge
            screen.blit(ammo_text, (ammo_bg_x + padding, ammo_bg_y + padding))
        else:
            # No ammo shown: reserve a small width so money stays in same place
            placeholder_ammo = "Ammo: 0"
            measure_text = small_font.render(placeholder_ammo, True, WHITE)
            ammo_bg_w = measure_text.get_width() + padding * 2
            ammo_bg_x = WIDTH - 20 - ammo_bg_w

            # Money sits at the fixed position left of the reserved area
            money_text = small_font.render(f"Money: ${state.money}", True, WHITE)
            money_rect = money_text.get_rect(topright=(ammo_bg_x - 8, ammo_bg_y))
            screen.blit(money_text, money_rect)
        
        # Show warning when fuel is low
        if car.fuel < 30:
            warning_text = small_font.render("LOW FUEL!", True, (255, 50, 50))
            screen.blit(warning_text, (240, 85))  # Position near fuel bar
        
        # Draw weather effects
        weather.draw(screen)
        
        # Apply day/night overlay
        day_night.apply_overlay(screen, state.current_level)

        # Check for level completion or game over
        level_manager = get_level_manager()
        level_complete = level_manager.is_level_complete(state.distance, state.current_level)
        
        if level_complete or car.health <= 0 or car.fuel <= 0:
            # Show end game reason
            if car.health <= 0:
                reason = "HEALTH DEPLETED!"
                reward = 0
            elif car.fuel <= 0:
                reason = "OUT OF FUEL!"
                reward = 0
            else:
                reason = "LEVEL COMPLETE!"
                # Award completion bonus
                reward = level_manager.get_completion_reward(state.current_level)
                state.money += reward
            
            # Calculate total money earned this attempt (zombies + bonus)
            money_earned_this_round = state.money - level_start_money
            
            # Display reason for a moment
            reason_text = font.render(reason, True, (255, 255, 0))
            screen.blit(reason_text, (WIDTH//2 - reason_text.get_width()//2, HEIGHT//2 - 40))
            
            if reward > 0:
                reward_text = small_font.render(f"Bonus: ${reward}", True, (100, 255, 100))
                screen.blit(reward_text, (WIDTH//2 - reward_text.get_width()//2, HEIGHT//2 + 10))
            
            pygame.display.flip()
            await asyncio.sleep(2)
            
            # Show level result screen
            level_result = LevelResult(screen, font, small_font)
            try:
                continue_game = await level_result.show(
                    level_number=state.current_level,
                    completed=level_complete,
                    money_earned=money_earned_this_round,
                    previous_money=level_start_money
                )
            except Exception as e:
                print(f"Error showing level result screen: {e}")
                # In web environments, if the result screen fails, continue to garage
                continue_game = True
            
            if not continue_game:
                running = False
                return
            
            # Stop engine sound before going to garage
            try:
                audio_manager.stop_engine_sound()
            except Exception:
                pass
            
            # Advance to next level or reset
            if level_complete:
                state.current_level += 1
                level_manager.advance_level()
            
            state.distance = 0
            set_current_level(state.current_level)
            clear_terrain()
            
            # Reset easter egg for next game
            easter_egg = EasterEgg(x_position=-2000)
            state.easter_egg_activated = False
            
            # Ensure engine sound is stopped before garage
            try:
                audio_manager.stop_engine_sound()
            except Exception:
                pass
            
            car = reset_car(controls)  # This will reapply all purchased upgrades
            garage_result = await garage(car, screen, clock, WIDTH, HEIGHT, font, small_font, garage_bg,
                   audio_manager.stop_engine_sound, audio_manager.play_menu_music, audio_manager.AUDIO_ENABLED, audio_manager._menu_music_loaded,
                   WHITE, BUTTON, BUTTON_HOVER, UPGRADE_BG, EQUIPPED_COLOR, PURCHASED_COLOR)
            # If they went back to menu, exit the game loop
            if garage_result == 'back_to_menu':
                running = False
            
            # Restart audio after garage when starting new game
            if garage_result == 'start_game':
                # Reset level_start_money for the next attempt
                level_start_money = state.money
                
                # Stop all audio first
                try:
                    audio_manager.stop_engine_sound()
                    audio_manager.stop_music()
                except Exception:
                    pass
                
                # Small delay
                await asyncio.sleep(0.05)
                
                # Restart game music
                if audio_manager.AUDIO_ENABLED and audio_manager._bg_music_loaded:
                    audio_manager.play_bg_music()
                
                # Restart engine sound
                engine_playing_local = False
                engine_current_factor = 0.0
                if audio_manager.AUDIO_ENABLED and _engine_sound:
                    try:
                        engine_current_factor = audio_manager.ENGINE_VOLUME_IDLE_FACTOR
                        try:
                            _engine_sound.set_volume(audio_manager.AUDIO_VOLUME_SFX * engine_current_factor)
                        except Exception:
                            _engine_sound.set_volume(audio_manager.AUDIO_VOLUME_SFX)
                        _engine_sound.play(-1)
                        engine_playing_local = True
                    except Exception as e:
                        print(f"Failed to restart engine idle sound: {e}")
                        engine_playing_local = False
            
            zombies = spawn_zombies(state.current_level) or []
            
            # Reset weather for new level
            weather.set_weather(determine_weather_for_level(state.current_level), state.current_level)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # Reset all upgrade save files when quitting
                try:
                    with open("upgrades_status.json", "w") as f:
                        json.dump({}, f)
                    if os.path.exists("survival_upgrades.json"):
                        with open("survival_upgrades.json", "w") as f:
                            json.dump({}, f)
                except Exception as e:
                    print(f"Error resetting upgrade files: {e}")
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False  # Return to start screen
        
        # Apply color inversion if easter egg is activated
        if state.easter_egg_activated:
            invert_screen_colors(screen)
            # Show easter egg active indicator
            easter_text = small_font.render("CHEAT MODE ACTIVE!", True, (255, 255, 100))
            screen.blit(easter_text, (WIDTH//2 - easter_text.get_width()//2, HEIGHT - 30))

        pygame.display.flip()

    # Cleanup audio when leaving the main game loop
    try:
        audio_manager.stop_engine_sound()
    except Exception:
        pass
    
    # Start menu music when returning to start screen
    if audio_manager.AUDIO_ENABLED and audio_manager._menu_music_loaded:
        audio_manager.play_menu_music()

# ==============================
# Main Program
# ==============================
async def main():
    # Pre-load car types once at the start
    print("Starting Zombie Car...")
    print("Loading car types...")
    load_car_types()
    
    # Initialize level manager
    print("Initializing level system...")
    level_manager = get_level_manager()
    print(f"Level system ready - Current level: {level_manager.current_level}")
    
    # Laad upgrades status bij start (inclusief de opgeslagen auto)
    print("Loading upgrades status...")
    load_all_upgrades_status()
    
    # Load settings
    settings = load_settings()
    audio_manager.set_volumes(
        settings.get('music_volume', 0.4),
        settings.get('sfx_volume', 0.6)
    )
    game_controls = settings.get('controls', {
        'accelerate_right': pygame.K_RIGHT,
        'accelerate_left': pygame.K_LEFT,
        'shoot': pygame.K_e
    })
    
    # Create start screen
    start_screen = StartScreen(WIDTH, HEIGHT, font)
    # Debug audio status at startup
    print(f"main start: MIXER_AVAILABLE={MIXER_AVAILABLE}, AUDIO_ENABLED={audio_manager.AUDIO_ENABLED}, _menu_music_loaded={audio_manager._menu_music_loaded}, _bg_music_loaded={audio_manager._bg_music_loaded}")
    
    # Game state
    game_state = "start_screen"
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        # Handle events
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # Reset all upgrade save files when quitting
                try:
                    with open("upgrades_status.json", "w") as f:
                        json.dump({}, f)
                    if os.path.exists("survival_upgrades.json"):
                        with open("survival_upgrades.json", "w") as f:
                            json.dump({}, f)
                except Exception as e:
                    print(f"Error resetting upgrade files: {e}")
                running = False
                break
            elif e.type == pygame.KEYDOWN:
                # Test tone (synthesized) with T key
                if e.key == pygame.K_t:
                    if MIXER_AVAILABLE:
                        print("T pressed: playing test tone")
                        tone = audio_manager.synth_sine_sound(frequency=440.0, duration=0.5, volume=0)
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
                car = Car(apply_upgrades_now=False, controls=game_controls)  # Don't apply upgrades yet
                garage_result = await garage(car, screen, clock, WIDTH, HEIGHT, font, small_font, garage_bg,
                       audio_manager.stop_engine_sound, audio_manager.play_menu_music, audio_manager.AUDIO_ENABLED, audio_manager._menu_music_loaded,
                       WHITE, BUTTON, BUTTON_HOVER, UPGRADE_BG, EQUIPPED_COLOR, PURCHASED_COLOR)
                # Then start the main game only if they chose to start
                if garage_result == 'start_game':
                    game_state = "main_game"
                # Otherwise stay on start_screen
            elif action == 'survival_mode':
                game_state = "survival"
            elif action == 'credits':
                game_state = "credits"
            elif action == 'settings':
                game_state = "settings"
            elif action == 'quit':
                save_all_upgrades_status()
                running = False
            
            # Render start screen
            start_screen.render(screen)
        
        elif game_state == "main_game":
            await main_game_loop(game_controls)
            # After main game ends (when player presses ESC), return to start screen
            game_state = "start_screen"
            if audio_manager.AUDIO_ENABLED and audio_manager._menu_music_loaded:
                audio_manager.play_menu_music()
        
        elif game_state == "survival":
            # Start survival mode with garage - keep upgrades and money separate
            # Save current campaign state (money only, not upgrades)
            original_money = state.money
            
            # Backup campaign upgrades to a temp variable
            campaign_upgrades_backup = None
            if os.path.exists("upgrades_status.json"):
                try:
                    with open("upgrades_status.json", "r") as f:
                        campaign_upgrades_backup = json.load(f)
                except Exception:
                    campaign_upgrades_backup = {}
            
            # Load survival-specific upgrades into upgrades_status.json
            if os.path.exists("survival_upgrades.json"):
                try:
                    with open("survival_upgrades.json", "r") as f:
                        survival_data = json.load(f)
                    with open("upgrades_status.json", "w") as f:
                        json.dump(survival_data, f)
                    load_all_upgrades_status()
                except Exception as e:
                    print(f"Error loading survival upgrades: {e}")
                    with open("upgrades_status.json", "w") as f:
                        json.dump({}, f)
                    load_all_upgrades_status()
            else:
                # First time survival - start with empty upgrades
                with open("upgrades_status.json", "w") as f:
                    json.dump({}, f)
                load_all_upgrades_status()
            
            # Set infinite money for survival mode garage
            state.money = 999999999
            state.in_survival_mode = True  # Flag that we're in survival mode
            
            # Go to garage first
            car = Car(apply_upgrades_now=False, controls=game_controls)
            garage_result = await garage(car, screen, clock, WIDTH, HEIGHT, font, small_font, garage_bg,
                   audio_manager.stop_engine_sound, audio_manager.play_menu_music, audio_manager.AUDIO_ENABLED, audio_manager._menu_music_loaded,
                   WHITE, BUTTON, BUTTON_HOVER, UPGRADE_BG, EQUIPPED_COLOR, PURCHASED_COLOR)
            
            # Save survival upgrades DIRECTLY to survival_upgrades.json
            # Read current state from upgrades_status.json (which has survival data)
            try:
                with open("upgrades_status.json", "r") as f:
                    current_survival_data = json.load(f)
                # Write directly to survival_upgrades.json
                with open("survival_upgrades.json", "w") as f:
                    json.dump(current_survival_data, f, indent=2)
            except Exception as e:
                print(f"Error saving survival upgrades: {e}")
            
            # Restore campaign upgrades IMMEDIATELY (before any save_all_upgrades_status call)
            if campaign_upgrades_backup is not None:
                with open("upgrades_status.json", "w") as f:
                    json.dump(campaign_upgrades_backup, f, indent=2)
            else:
                with open("upgrades_status.json", "w") as f:
                    json.dump({}, f)
            load_all_upgrades_status()  # Reload campaign upgrades
            
            # Apply survival upgrades to car if starting game
            if garage_result == 'start_game':
                # Temporarily load survival upgrades just for the car
                with open("survival_upgrades.json", "r") as f:
                    survival_data = json.load(f)
                with open("upgrades_status.json", "w") as f:
                    json.dump(survival_data, f)
                load_all_upgrades_status()
                car.apply_equipped_upgrades()
                # Restore campaign upgrades again
                if campaign_upgrades_backup is not None:
                    with open("upgrades_status.json", "w") as f:
                        json.dump(campaign_upgrades_backup, f)
                else:
                    with open("upgrades_status.json", "w") as f:
                        json.dump({}, f)
                load_all_upgrades_status()
            
            # Restore original money
            state.money = original_money
            
            # Start survival if they chose to start
            if garage_result == 'start_game':
                # Keep infinite money during survival gameplay
                state.money = 999999999
                from survival_mode import SurvivalMode
                survival = SurvivalMode(screen, clock, WIDTH, HEIGHT, font, small_font, car)
                await survival.run()
                # Restore campaign money after survival ends
                state.money = original_money
            
            # Clear survival mode flag (whether they played or went back to menu)
            state.in_survival_mode = False
            
            # Return to menu
            game_state = "start_screen"
            if audio_manager.AUDIO_ENABLED and audio_manager._menu_music_loaded:
                audio_manager.play_menu_music()
        
        elif game_state == "credits":
            await credits_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE)
            game_state = "start_screen"
        
        elif game_state == "settings":
            music_vol, sfx_vol, game_controls = await settings_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE, audio_manager.AUDIO_ENABLED)
            # Apply the new volumes
            audio_manager.set_volumes(music_vol, sfx_vol)
            game_state = "start_screen"
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    
    # Reset all upgrade save files when quitting
    try:
        with open("upgrades_status.json", "w") as f:
            json.dump({}, f)
        if os.path.exists("survival_upgrades.json"):
            with open("survival_upgrades.json", "w") as f:
                json.dump({}, f)
    except Exception as e:
        print(f"Error resetting upgrade files: {e}")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # In some embed environments (like browsers/pygbag) the event loop may already be running.
        loop = asyncio.get_event_loop()
        loop.create_task(main())