import pygame
import sys
import os
from upgrades import save_all_upgrades_status
import asyncio

async def credits_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE):
    """Display credits screen"""
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
    name_font = pygame.font.SysFont("arial", 24)
    small_info_font = pygame.font.SysFont("arial", 20, italic=True)
    
    # Colors
    TITLE_COLOR = (255, 215, 0)  # Gold
    SUBTITLE_COLOR = (255, 255, 100)  # Light yellow
    NAME_COLOR = (220, 220, 220)  # Light gray
    INFO_COLOR = (150, 150, 200)  # Light blue
    
    # Credits data structure: (text, style, spacing_after)
    # style: "title", "subtitle", "name", "info"
    credits_data = [
        ("Drive to Survive", "title", 30),
        ("Programming", "subtitle", 10),
        ("Ben Dover", "name", 5),
        ("Victor", "name", 5),
        ("Killian", "name", 5),
        ("Bram", "name", 20),
        ("Special Thanks", "subtitle", 10),
        ("Pygame Community", "name", 5),
        ("Press ESC to return", "info", 0)
    ]
    
    running = True
    while running:
        clock.tick(60)
        await asyncio.sleep(0)
        
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
        
        # Draw credits text
        y_offset = 80
        
        for text, style, spacing in credits_data:
            if style == "title":
                rendered = title_font.render(text, True, TITLE_COLOR)
            elif style == "subtitle":
                rendered = subtitle_font.render(text, True, SUBTITLE_COLOR)
            elif style == "name":
                rendered = name_font.render(text, True, NAME_COLOR)
            else:  # info
                rendered = small_info_font.render(text, True, INFO_COLOR)
            
            # Center the text
            text_rect = rendered.get_rect(center=(WIDTH // 2, y_offset))
            
            # Add subtle shadow for better readability
            shadow = rendered.copy()
            shadow.set_alpha(100)
            screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            
            # Draw the text
            screen.blit(rendered, text_rect)
            
            y_offset += rendered.get_height() + spacing
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                save_all_upgrades_status()
                pygame.quit()
                sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
        
        pygame.display.flip()
    
