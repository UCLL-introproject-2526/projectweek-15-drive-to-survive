import pygame
import sys
from upgrades import save_all_upgrades_status


def settings_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE, AUDIO_ENABLED):
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
