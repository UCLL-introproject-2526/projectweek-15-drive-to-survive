import pygame
import sys
from upgrades import save_all_upgrades_status

def credits_screen(screen, clock, WIDTH, HEIGHT, font, small_font, WHITE):
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
