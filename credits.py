import pygame

class CreditsScreen:
    def __init__(self):
        # Zorg dat pygame.font geïnitialiseerd is
        if not pygame.font.get_init():
            pygame.font.init()
        
        # Import Button hier zodat pygame al geïnitialiseerd is
        from main import Button
        
        try:
            bg_raw = pygame.image.load('images/Background-image.png')
            self.__background = pygame.transform.scale(bg_raw, (1024, 768))
        except:
            self.__background = None
        
        self.__title_font = pygame.font.Font(None, 72)
        self.__section_font = pygame.font.Font(None, 48)
        self.__text_font = pygame.font.Font(None, 32)
        
        # Back button
        self.__back_button = Button(20, 20, 120, 50, 'Back', (70, 70, 70), (100, 100, 100))
        
        # Credits tekst - hier kun je gemakkelijk dingen toevoegen/aanpassen
        self.credits_content = [
            {"type": "title", "text": "Credits"},
            {"type": "space"},
            {"type": "section", "text": "Development Team"},
            {"type": "text", "text": "Developer 1 - Programming"},
            {"type": "text", "text": "Developer 2 - Game Design"},
            {"type": "text", "text": "Developer 3 - Art & Graphics"},
            {"type": "space"},
            {"type": "section", "text": "Special Thanks"},
            {"type": "text", "text": "Thanks to everyone who helped!"},
            {"type": "space"},
            {"type": "section", "text": "Tools & Libraries"},
            {"type": "text", "text": "Pygame - Game Framework"},
            {"type": "text", "text": "Python - Programming Language"},
        ]
        
        self.scroll_y = 0
        self.scroll_speed = 20
    
    def update(self, mouse_pos):
        self.__back_button.update(mouse_pos)
    
    def handle_click(self, mouse_pos, mouse_clicked):
        if self.__back_button.is_clicked(mouse_pos, mouse_clicked):
            return 'back_to_menu'
        return None
    
    def handle_scroll(self, direction):
        self.scroll_y += direction * self.scroll_speed
        # Begrens scrollen
        self.scroll_y = min(0, self.scroll_y)
    
    def render(self, srf):
        # Background
        if self.__background:
            srf.blit(self.__background, (0, 0))
        else:
            srf.fill((30, 30, 30))
        
        # Semi-transparante overlay
        overlay = pygame.Surface((1024, 768))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        srf.blit(overlay, (0, 0))
        
        # Back button
        self.__back_button.render(srf)
        
        # Render credits content
        y_offset = 100 + self.scroll_y
        
        for item in self.credits_content:
            if item["type"] == "title":
                text = self.__title_font.render(item["text"], True, (255, 255, 255))
                text_rect = text.get_rect(center=(512, y_offset))
                srf.blit(text, text_rect)
                y_offset += 80
            
            elif item["type"] == "section":
                text = self.__section_font.render(item["text"], True, (255, 200, 0))
                text_rect = text.get_rect(center=(512, y_offset))
                srf.blit(text, text_rect)
                y_offset += 60
            
            elif item["type"] == "text":
                text = self.__text_font.render(item["text"], True, (200, 200, 200))
                text_rect = text.get_rect(center=(512, y_offset))
                srf.blit(text, text_rect)
                y_offset += 40
            
            elif item["type"] == "space":
                y_offset += 30
