import pygame
import sys
import json
import os
from upgrades import save_all_upgrades_status


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


def settings_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE, AUDIO_ENABLED):
    """Display settings screen"""
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
        mouse_pos = pygame.mouse.get_pos()
        
        # Fill background
        screen.fill((30, 30, 50))
        
        # Settings text
        title = font.render("Settings", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Audio section
        y_offset = 120
        audio_title = small_font.render("Audio:", True, WHITE)
        screen.blit(audio_title, (100, y_offset))
        y_offset += 40
        
        audio_status = small_font.render(f"Audio: {'On' if AUDIO_ENABLED else 'Off'} (press M to toggle)", True, WHITE)
        screen.blit(audio_status, (120, y_offset))
        y_offset += 40
        
        # Volume controls
        music_label = small_font.render(f"Music Volume: {int(music_volume * 100)}%", True, WHITE)
        screen.blit(music_label, (120, y_offset))
        
        # Music volume slider
        slider_x = 350
        slider_y = y_offset + 5
        slider_width = 200
        slider_height = 10
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, int(slider_width * music_volume), slider_height))
        pygame.draw.circle(screen, WHITE, (int(slider_x + slider_width * music_volume), slider_y + slider_height//2), 8)
        music_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_width + 20, slider_height + 20)
        
        y_offset += 40
        
        sfx_label = small_font.render(f"SFX Volume: {int(sfx_volume * 100)}%", True, WHITE)
        screen.blit(sfx_label, (120, y_offset))
        
        # SFX volume slider
        slider_y = y_offset + 5
        pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))
        pygame.draw.rect(screen, (200, 200, 200), (slider_x, slider_y, int(slider_width * sfx_volume), slider_height))
        pygame.draw.circle(screen, WHITE, (int(slider_x + slider_width * sfx_volume), slider_y + slider_height//2), 8)
        sfx_slider_rect = pygame.Rect(slider_x - 10, slider_y - 10, slider_width + 20, slider_height + 20)
        
        y_offset += 60
        
        # Controls section
        controls_title = small_font.render("Control Customization:", True, WHITE)
        screen.blit(controls_title, (100, y_offset))
        y_offset += 40
        
        # Display controls
        control_labels = {
            'accelerate_right': 'Accelerate Right',
            'accelerate_left': 'Accelerate Left',
            'shoot': 'Shoot'
        }
        
        control_rects = {}
        for key, label in control_labels.items():
            key_name = pygame.key.name(controls[key]).upper()
            control_text = small_font.render(f"{label}: {key_name}", True, WHITE)
            
            # Highlight if this control is being remapped
            if selected_control == key:
                control_text = small_font.render(f"{label}: Press a key...", True, (255, 255, 0))
            
            rect = control_text.get_rect(topleft=(120, y_offset))
            control_rects[key] = rect.inflate(20, 10)
            
            # Draw button background
            color = (80, 80, 120) if control_rects[key].collidepoint(mouse_pos) else (50, 50, 80)
            if selected_control == key:
                color = (120, 120, 0)
            pygame.draw.rect(screen, color, control_rects[key], border_radius=5)
            pygame.draw.rect(screen, WHITE, control_rects[key], 2, border_radius=5)
            
            screen.blit(control_text, (120, y_offset))
            y_offset += 45
        
        # Instructions
        y_offset += 20
        instruction = small_font.render("Click on a control to remap it", True, (150, 150, 150))
        screen.blit(instruction, (WIDTH//2 - instruction.get_width()//2, y_offset))
        
        # Exit instruction
        exit_text = small_font.render("Press ESC to return", True, WHITE)
        screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT - 50))
        
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
