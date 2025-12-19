"""
Controls Screen
Toont een tussenscherm met controls voordat het level/survival mode start
"""

import pygame
import asyncio

class ControlsScreen:
    """Beheerd het controls tussenscherm"""
    
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        
        # Colors
        self.bg_color = (30, 30, 40)  # Dark blue-gray
        self.border_color = (100, 120, 150)  # Light blue-gray
        self.inner_border_color = (60, 70, 90)  # Medium blue-gray
        self.text_color = (240, 240, 240)  # Off-white
        self.highlight_color = (255, 215, 0)  # Gold
        self.button_color = (80, 120, 180)  # Blue
        self.button_hover_color = (100, 150, 220)  # Lighter blue
        self.button_border_color = (120, 160, 220)
        self.key_bg_color = (50, 60, 80)  # Dark blue for key boxes
        
        # Button
        self.button_rect = None
        
    async def show(self, controls_dict, mode_name="Level"):
        """
        Toont het controls scherm
        
        Args:
            controls_dict: Dictionary met control mappings (bijv. {'accelerate_right': 1073741903, ...})
            mode_name: De naam van de mode ("Level" of "Survival Mode")
        
        Returns:
            True als speler wil doorgaan, False anders
        """
        # Create panel dimensions
        panel_width = 700
        panel_height = 500
        
        # Position panel in center of screen
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        clock = pygame.time.Clock()        
        running = True
        
        # Map key codes to readable names
        def get_key_name(key_code):
            """Convert pygame key code to readable name"""
            if key_code == pygame.K_SPACE:
                return "SPATIE"
            elif key_code == pygame.K_RETURN:
                return "ENTER"
            elif key_code == pygame.K_ESCAPE:
                return "ESC"
            elif key_code == pygame.K_UP or key_code == 1073741906:
                return "PIJL OMHOOG"
            elif key_code == pygame.K_DOWN or key_code == 1073741905:
                return "PIJL OMLAAG"
            elif key_code == pygame.K_LEFT or key_code == 1073741904:
                return "PIJL LINKS"
            elif key_code == pygame.K_RIGHT or key_code == 1073741903:
                return "PIJL RECHTS"
            else:
                # Try to get the character name
                try:
                    return pygame.key.name(key_code).upper()
                except:
                    return str(key_code)
        
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
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
            
            # Title with decorative line
            title_text = self.font.render(f"{mode_name} - Controls", True, self.highlight_color)
            title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(title_text, title_rect)
            
            # Decorative line under title
            line_y = y_offset + 35
            line_width = 250
            line_x = (self.screen.get_width() - line_width) // 2
            pygame.draw.line(self.screen, self.border_color, (line_x, line_y), (line_x + line_width, line_y), 2)
            y_offset += 70
            
            # Controls section
            controls_info = [
                ("Accelereer naar rechts:", get_key_name(controls_dict.get('accelerate_right', pygame.K_RIGHT))),
                ("Accelereer naar links:", get_key_name(controls_dict.get('accelerate_left', pygame.K_LEFT))),
                ("Schieten:", get_key_name(controls_dict.get('shoot', pygame.K_e))),
            ]
            
            # Draw each control
            for label, key in controls_info:
                # Label text
                label_text = self.small_font.render(label, True, self.text_color)
                label_rect = label_text.get_rect(midright=(self.screen.get_width() // 2 - 20, y_offset))
                self.screen.blit(label_text, label_rect)
                
                # Key box
                key_box_width = 150
                key_box_height = 35
                key_box_x = self.screen.get_width() // 2 + 20
                key_box_y = y_offset - key_box_height // 2
                key_box_rect = pygame.Rect(key_box_x, key_box_y, key_box_width, key_box_height)
                
                # Draw key box background
                pygame.draw.rect(self.screen, self.key_bg_color, key_box_rect, border_radius=5)
                pygame.draw.rect(self.screen, self.border_color, key_box_rect, width=2, border_radius=5)
                
                # Key text
                key_text = self.small_font.render(key, True, self.highlight_color)
                key_rect = key_text.get_rect(center=key_box_rect.center)
                self.screen.blit(key_text, key_rect)
                
                y_offset += 50
            
            y_offset += 20
            
            # Instructions
            instruction_text = self.small_font.render("Overleef de zombies en bereik het doel!", True, (180, 180, 180))
            instruction_rect = instruction_text.get_rect(center=(self.screen.get_width() // 2, y_offset))
            self.screen.blit(instruction_text, instruction_rect)
            
            y_offset += 50
            
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
            button_text = self.small_font.render("Start (SPATIE)", True, self.text_color)
            button_text_rect = button_text.get_rect(center=self.button_rect.center)
            self.screen.blit(button_text, button_text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(1/60)
        
        return False
