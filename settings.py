import pygame
import sys
import json
import os
from upgrades import save_all_upgrades_status
import asyncio


def load_settings():
    """Load settings from config file"""
    default_settings = {
        'music_volume': 0.4,
        'sfx_volume': 0.6,
        'controls': {
            'accelerate_right': pygame.K_RIGHT,
            'accelerate_left': pygame.K_LEFT,
            'shoot': pygame.K_e
        }
    }
    
    if os.path.exists('settings_config.json'):
        try:
            with open('settings_config.json', 'r') as f:
                settings = json.load(f)
                return settings
        except:
            return default_settings
    return default_settings


def save_settings(music_volume, sfx_volume, controls):
    """Save settings to config file"""
    settings = {
        'music_volume': music_volume,
        'sfx_volume': sfx_volume,
        'controls': controls
    }
    try:
        with open('settings_config.json', 'w') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")


async def settings_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE, AUDIO_ENABLED):
    """Display settings screen"""
    # Load background image
    try:
        background = pygame.image.load("assets/background/Background.png").convert()
        background = pygame.transform.scale(background, (WIDTH, HEIGHT))
        # Darken the background for better text visibility
        dark_overlay = pygame.Surface((WIDTH, HEIGHT))
        dark_overlay.set_alpha(180)
        dark_overlay.fill((0, 0, 0))
    except:
        background = None
        dark_overlay = None
    
    # Create fonts for different text styles
    title_font = pygame.font.SysFont("arial", 48, bold=True)
    subtitle_font = pygame.font.SysFont("arial", 28, bold=True)
    label_font = pygame.font.SysFont("arial", 22)
    info_font = pygame.font.SysFont("arial", 18, italic=True)
    
    # Colors
    TITLE_COLOR = (255, 215, 0)  # Gold
    SUBTITLE_COLOR = (255, 255, 100)  # Light yellow
    LABEL_COLOR = (220, 220, 220)  # Light gray
    INFO_COLOR = (150, 150, 200)  # Light blue
    BUTTON_COLOR = (70, 70, 120)
    BUTTON_HOVER = (100, 100, 160)
    BUTTON_SELECTED = (150, 150, 50)
    
    running = True
    
    # Load current settings
    settings = load_settings()
    music_volume = settings.get('music_volume', 0.4)
    sfx_volume = settings.get('sfx_volume', 0.6)
    controls = settings.get('controls', {
        'accelerate_right': pygame.K_RIGHT,
        'accelerate_left': pygame.K_LEFT,
        'shoot': pygame.K_e
    })
    
    # UI elements
    selected_control = None  # Which control is being remapped
    
    while running:
        clock.tick(60)
        await asyncio.sleep(0)
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw background
        if background:
            screen.blit(background, (0, 0))
            if dark_overlay:
                screen.blit(dark_overlay, (0, 0))
        else:
            screen.fill((30, 30, 50))
        
        # Draw decorative border
        border_color = (100, 100, 150)
        pygame.draw.rect(screen, border_color, (40, 40, WIDTH - 80, HEIGHT - 80), 3, border_radius=15)
        
        # Settings title with shadow
        title = title_font.render("Settings", True, TITLE_COLOR)
        title_rect = title.get_rect(center=(WIDTH//2, 70))
        # Shadow
        shadow = title.copy()
        shadow.set_alpha(100)
        screen.blit(shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title, title_rect)
        
        screen.blit(title, title_rect)
        
        # Audio section
        y_offset = 140
        audio_title = subtitle_font.render("Audio", True, SUBTITLE_COLOR)
        audio_rect = audio_title.get_rect(center=(WIDTH//2, y_offset))
        # Shadow
        shadow = audio_title.copy()
        shadow.set_alpha(100)
        screen.blit(shadow, (audio_rect.x + 2, audio_rect.y + 2))
        screen.blit(audio_title, audio_rect)
        y_offset += 50
        
        # Volume controls
        music_label = label_font.render(f"Music Volume: {int(music_volume * 100)}%", True, LABEL_COLOR)
        label_x = WIDTH//2 - 200
        screen.blit(music_label, (label_x, y_offset))
        
        # Music volume slider with improved style
        slider_width = 250
        slider_x = WIDTH//2 - slider_width//2
        slider_y = y_offset + 30
        slider_height = 12
        # Slider background
        pygame.draw.rect(screen, (50, 50, 70), (slider_x, slider_y, slider_width, slider_height), border_radius=6)
        # Slider fill
        pygame.draw.rect(screen, (100, 200, 100), (slider_x, slider_y, int(slider_width * music_volume), slider_height), border_radius=6)
        # Slider handle
        pygame.draw.circle(screen, (200, 255, 200), (int(slider_x + slider_width * music_volume), slider_y + slider_height//2), 10)
        pygame.draw.circle(screen, WHITE, (int(slider_x + slider_width * music_volume), slider_y + slider_height//2), 10, 2)
        music_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_width + 20, slider_height + 20)
        
        y_offset += 60
        
        sfx_label = label_font.render(f"SFX Volume: {int(sfx_volume * 100)}%", True, LABEL_COLOR)
        screen.blit(sfx_label, (label_x, y_offset))
        
        # SFX volume slider with improved style
        slider_x = WIDTH//2 - slider_width//2
        slider_y = y_offset + 30
        # Slider background
        pygame.draw.rect(screen, (50, 50, 70), (slider_x, slider_y, slider_width, slider_height), border_radius=6)
        # Slider fill
        pygame.draw.rect(screen, (100, 150, 200), (slider_x, slider_y, int(slider_width * sfx_volume), slider_height), border_radius=6)
        # Slider handle
        pygame.draw.circle(screen, (150, 200, 255), (int(slider_x + slider_width * sfx_volume), slider_y + slider_height//2), 10)
        pygame.draw.circle(screen, WHITE, (int(slider_x + slider_width * sfx_volume), slider_y + slider_height//2), 10, 2)
        sfx_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_width + 20, slider_height + 20)
        
        y_offset += 75
        
        # Controls section
        controls_title = subtitle_font.render("Control Customization", True, SUBTITLE_COLOR)
        controls_rect = controls_title.get_rect(center=(WIDTH//2, y_offset))
        # Shadow
        shadow = controls_title.copy()
        shadow.set_alpha(100)
        screen.blit(shadow, (controls_rect.x + 2, controls_rect.y + 2))
        screen.blit(controls_title, controls_rect)
        y_offset += 50
        
        # Display controls
        control_labels = {
            'accelerate_right': 'Accelerate Right',
            'accelerate_left': 'Accelerate Left',
            'shoot': 'Shoot'
        }
        
        control_rects = {}
        for key, label in control_labels.items():
            key_name = pygame.key.name(controls[key]).upper()
            
            # Highlight if this control is being remapped
            if selected_control == key:
                control_text = label_font.render(f"{label}: Press a key...", True, (255, 255, 100))
            else:
                control_text = label_font.render(f"{label}: {key_name}", True, LABEL_COLOR)
            
            # Center the control button
            text_rect = control_text.get_rect(center=(WIDTH//2, y_offset + 15))
            control_rects[key] = text_rect.inflate(40, 20)
            
            # Draw button background with improved style
            if selected_control == key:
                color = BUTTON_SELECTED
            elif control_rects[key].collidepoint(mouse_pos):
                color = BUTTON_HOVER
            else:
                color = BUTTON_COLOR
            
            pygame.draw.rect(screen, color, control_rects[key], border_radius=8)
            pygame.draw.rect(screen, (180, 180, 220), control_rects[key], 2, border_radius=8)
            
            screen.blit(control_text, text_rect)
            y_offset += 50
        
        # Instructions with shadow
        y_offset += 10
        instruction = info_font.render("Click on a control to remap it", True, INFO_COLOR)
        instr_rect = instruction.get_rect(center=(WIDTH//2, y_offset))
        shadow = instruction.copy()
        shadow.set_alpha(80)
        screen.blit(shadow, (instr_rect.x + 1, instr_rect.y + 1))
        screen.blit(instruction, instr_rect)
        
        # Exit instruction with shadow (at bottom)
        exit_text = info_font.render("Press ESC to save and return", True, INFO_COLOR)
        exit_rect = exit_text.get_rect(center=(WIDTH//2, HEIGHT - 20))
        shadow = exit_text.copy()
        shadow.set_alpha(80)
        screen.blit(shadow, (exit_rect.x + 1, exit_rect.y + 1))
        screen.blit(exit_text, exit_rect)
        
        # Event handling
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if selected_control:
                    # Remap the control
                    controls[selected_control] = e.key
                    selected_control = None
                elif e.key == pygame.K_ESCAPE:
                    # Save settings before exiting
                    save_settings(music_volume, sfx_volume, controls)
                    running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:  # Left click
                    # Check if clicking on a control button
                    for key, rect in control_rects.items():
                        if rect.collidepoint(e.pos):
                            selected_control = key
                            break
                    
                    # Check if clicking on volume sliders
                    if music_slider_rect.collidepoint(e.pos):
                        music_volume = max(0.0, min(1.0, (e.pos[0] - slider_x) / slider_width))
                    elif sfx_slider_rect.collidepoint(e.pos):
                        sfx_volume = max(0.0, min(1.0, (e.pos[0] - slider_x) / slider_width))
            elif e.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:  # Left button held
                    # Dragging volume sliders
                    if music_slider_rect.collidepoint(e.pos):
                        music_volume = max(0.0, min(1.0, (e.pos[0] - slider_x) / slider_width))
                    elif sfx_slider_rect.collidepoint(e.pos):
                        sfx_volume = max(0.0, min(1.0, (e.pos[0] - slider_x) / slider_width))
        
        pygame.display.flip()
    
    # Return the settings values
    return music_volume, sfx_volume, controls
