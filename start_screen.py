import pygame

class Background:
    def __init__(self, image_path, width, height):
        try:
            self.image = pygame.image.load(image_path).convert()
            self.image = pygame.transform.scale(self.image, (width, height))
        except:
            # Fallback background if image doesn't exist
            self.image = pygame.Surface((width, height))
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
            WHITE = (255, 255, 255)
            text = font.render("ZOMBIE CAR", True, WHITE)
            text_rect = text.get_rect(center=(width//2, height//2))
            self.image.blit(text, text_rect)
            self.rect = self.image.get_rect(center=(x, y))
    
    def render(self, surface):
        surface.blit(self.image, self.rect)

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font, icon_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.hovered = False
        self.font = font
        
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
        WHITE = (255, 255, 255)
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        if self.icon:
            icon_rect = self.icon.get_rect(center=self.rect.center)
            surface.blit(self.icon, icon_rect)
        elif self.text:
            text_surf = self.font.render(self.text, True, WHITE)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

class StartScreen:
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
        
        # Use existing background image or create fallback
        try:
            bg_image = "assets/background/Background.png"
            self.background = Background(bg_image, width, height)
        except:
            self.background = Background("", width, height)  # Will use fallback
        
        # Create logo - adjust position as needed
        self.logo = Logo("assets/banner/image.png", 450, 300, width//2, 150)
        
        # Create buttons
        button_width = 250
        button_height = 60
        button_x = width//2 - button_width//2
        
        self.start_button = Button(button_x, 280, button_width, button_height, 
                                  'Campaign', (50, 150, 50), (70, 200, 70), font)
        self.survival_button = Button(button_x, 360, button_width, button_height,
                                     'Survival Mode', (150, 100, 50), (200, 130, 70), font)
        self.credits_button = Button(button_x, 440, button_width, button_height, 
                                     'Credits', (100, 100, 150), (150, 150, 200), font)
        self.quit_button = Button(button_x, 520, button_width, button_height, 
                                  'Quit', (150, 50, 50), (200, 70, 70), font)
        
        # Settings button in top right with icon
        self.settings_button = Button(width - 70, 20, 50, 50, '', 
                                      (50, 50, 150), (70, 70, 200), font,
                                      icon_path="assets/banner/setting.png")
    
    def update(self, mouse_pos):
        self.start_button.update(mouse_pos)
        self.survival_button.update(mouse_pos)
        self.credits_button.update(mouse_pos)
        self.settings_button.update(mouse_pos)
        self.quit_button.update(mouse_pos)
    
    def handle_click(self, mouse_pos, mouse_pressed):
        if self.start_button.is_clicked(mouse_pos, mouse_pressed):
            return 'start_game'
        elif self.survival_button.is_clicked(mouse_pos, mouse_pressed):
            return 'survival_mode'
        elif self.credits_button.is_clicked(mouse_pos, mouse_pressed):
            return 'credits'
        elif self.settings_button.is_clicked(mouse_pos, mouse_pressed):
            return 'settings'
        elif self.quit_button.is_clicked(mouse_pos, mouse_pressed):
            return 'quit'
        return None
    
    def render(self, screen):
        self.background.render(screen)
        self.logo.render(screen)
        self.start_button.render(screen)
        self.survival_button.render(screen)
        self.credits_button.render(screen)
        self.quit_button.render(screen)
        self.settings_button.render(screen)
