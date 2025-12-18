"""
Level Result Screen
Toont een tussenscherm na elk level met resultaten
"""

import pygame
import asyncio

class LevelResult:
    """Beheerd het tussenscherm na elk level"""
    
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        
        # Colors
        self.bg_color = (30, 30, 40)  # Dark blue-gray
        self.border_color = (100, 120, 150)  # Light blue-gray
        self.inner_border_color = (60, 70, 90)  # Medium blue-gray
        self.completed_color = (100, 255, 100)  # Bright green
        self.failed_color = (255, 80, 80)  # Bright red
        self.text_color = (240, 240, 240)  # Off-white
        self.money_color = (255, 215, 0)  # Gold
        self.button_color = (80, 120, 180)  # Blue
        self.button_hover_color = (100, 150, 220)  # Lighter blue
        self.button_border_color = (120, 160, 220)
        
        # Button
        self.button_rect = None
        
    async def show(self, level_number, completed, money_earned, previous_money):
        """
        Toont het result scherm
        
        Args:
            level_number: Het level nummer
            completed: True als level voltooid, False als gefaald
            money_earned: Hoeveelheid geld verdiend deze ronde
            previous_money: Geld voor deze ronde
        
        Returns:
            True als speler wil doorgaan, False anders
        """
        # Create panel dimensions
        panel_width = 700
        panel_height = 450
        
        # Position panel in center of screen
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        clock = pygame.time.Clock()        
        running = True
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_rect and self.button_rect.collidepoint(event.pos):
                        return True
            
            # Draw outer border (shadow effect)
            shadow_rect = pygame.Rect(panel_x + 5, panel_y + 5, panel_width, panel_height)
            pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=15)
            
            # Draw outer border
            outer_border = pygame.Rect(panel_x - 3, panel_y - 3, panel_width + 6, panel_height + 6)
            pygame.draw.rect(self.screen, self.border_color, outer_border, border_radius=15)
            
            # Draw main panel background
            panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(self.screen, self.bg_color, panel_rect, border_radius=12)
            
            # Draw inner decorative border
            inner_border = pygame.Rect(panel_x + 15, panel_y + 15, panel_width - 30, panel_height - 30)
            pygame.draw.rect(self.screen, self.inner_border_color, inner_border, width=2, border_radius=8)
            
            # Mouse position for hover effect
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw content
            y_offset = panel_y + 50
            
            # Level number with decorative line
            level_text = self.font.render(f"Level {level_number}", True, self.text_color)
            level_rect = level_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(level_text, level_rect)
            
            # Decorative line under level
            line_y = y_offset + 35
            line_width = 200
            line_x = (self.screen.get_width() - line_width) // 2
            pygame.draw.line(self.screen, self.border_color, (line_x, line_y), (line_x + line_width, line_y), 2)
            y_offset += 70
            
            # Completed or Failed with glow effect
            if completed:
                status_text = self.font.render("VOLTOOID", True, self.completed_color)
                # Add glow effect
                glow_text = self.font.render("VOLTOOID", True, (50, 150, 50))
                for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                    glow_rect = glow_text.get_rect(center=(self.screen.get_width() // 2 + offset[0], y_offset + offset[1]))
                    self.screen.blit(glow_text, glow_rect)
            else:
                status_text = self.font.render("GEFAALD", True, self.failed_color)
                # Add glow effect
                glow_text = self.font.render("GEFAALD", True, (150, 40, 40))
                for offset in [(2, 2), (-2, 2), (2, -2), (-2, -2)]:
                    glow_rect = glow_text.get_rect(center=(self.screen.get_width() // 2 + offset[0], y_offset + offset[1]))
                    self.screen.blit(glow_text, glow_rect)
            
            status_rect = status_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(status_text, status_rect)
            y_offset += 80
            
            # Money info box
            info_box_width = 450
            info_box_height = 110
            info_box_x = (self.screen.get_width() - info_box_width) // 2
            info_box_y = y_offset - 10
            info_box_rect = pygame.Rect(info_box_x, info_box_y, info_box_width, info_box_height)
            pygame.draw.rect(self.screen, (40, 40, 50), info_box_rect, border_radius=8)
            pygame.draw.rect(self.screen, self.inner_border_color, info_box_rect, width=2, border_radius=8)
            
            # Money earned this round
            money_text = self.small_font.render(f"Verdiend:", True, self.text_color)
            money_rect = money_text.get_rect(center=(self.screen.get_width() // 2, y_offset + 15))
            self.screen.blit(money_text, money_rect)
            
            money_value_text = self.font.render(f"${money_earned}", True, self.money_color)
            money_value_rect = money_value_text.get_rect(center=(self.screen.get_width() // 2, y_offset + 45))
            self.screen.blit(money_value_text, money_value_rect)
            
            # Divider line
            divider_y = y_offset + 65
            divider_x1 = info_box_x + 30
            divider_x2 = info_box_x + info_box_width - 30
            pygame.draw.line(self.screen, self.border_color, (divider_x1, divider_y), (divider_x2, divider_y), 1)
            
            # Total money
            total_label_text = self.small_font.render(f"Totaal:", True, self.text_color)
            total_label_rect = total_label_text.get_rect(center=(self.screen.get_width() // 2 - 80, y_offset + 80))
            self.screen.blit(total_label_text, total_label_rect)
            
            total_text = self.small_font.render(f"${previous_money + money_earned}", True, self.money_color)
            total_rect = total_text.get_rect(center=(self.screen.get_width() // 2 + 50, y_offset + 80))
            self.screen.blit(total_text, total_rect)
            
            y_offset += 130
            
            # Continue button with better styling
            button_width = 250
            button_height = 55
            button_x = (self.screen.get_width() - button_width) // 2
            button_y = y_offset
            self.button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Check hover
            is_hovering = self.button_rect.collidepoint(mouse_pos)
            button_color = self.button_hover_color if is_hovering else self.button_color
            
            # Button shadow
            shadow_button = pygame.Rect(button_x + 3, button_y + 3, button_width, button_height)
            pygame.draw.rect(self.screen, (0, 0, 0, 80), shadow_button, border_radius=8)
            
            # Button background
            pygame.draw.rect(self.screen, button_color, self.button_rect, border_radius=8)
            
            # Button border
            pygame.draw.rect(self.screen, self.button_border_color, self.button_rect, width=2, border_radius=8)
            
            # Button text
            button_text = self.small_font.render("Doorgaan (SPATIE)", True, self.text_color)
            button_text_rect = button_text.get_rect(center=self.button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(1/60)
        
        return False
