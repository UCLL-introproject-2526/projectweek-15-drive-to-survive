import pygame 
from player import Player
from zombie import normalZombie, bigZombie

class Logo:
    def __init__(self, image_path, x, y, width=None, height=None):
        self.__image = pygame.image.load(image_path)
        if width and height:
            self.__image = pygame.transform.scale(self.__image, (width, height))
        self.__x = x
        self.__y = y
    
    def render(self, srf):
        srf.blit(self.__image, (self.__x, self.__y))

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150), text_color=(255, 255, 255), icon_path=None):
        self.__rect = pygame.Rect(x, y, width, height)
        self.__text = text
        self.__color = color
        self.__hover_color = hover_color
        self.__text_color = text_color
        self.__is_hovered = False
        self.__font = pygame.font.Font(None, 36)
        self.__icon = None
        if icon_path:
            self.__icon = pygame.image.load(icon_path)
            # Scale icon to fit button with some padding
            icon_size = min(width - 10, height - 10)
            self.__icon = pygame.transform.scale(self.__icon, (int(icon_size), int(icon_size)))
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        if self.__rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False
    
    def update(self, mouse_pos):
        self.__is_hovered = self.__rect.collidepoint(mouse_pos)
    
    def render(self, srf):
        color = self.__hover_color if self.__is_hovered else self.__color
        pygame.draw.rect(srf, color, self.__rect)
        pygame.draw.rect(srf, (255, 255, 255), self.__rect, 2)  # Border
        
        if self.__icon:
            # Center the icon in the button
            icon_rect = self.__icon.get_rect(center=self.__rect.center)
            srf.blit(self.__icon, icon_rect)
        
        if self.__text:
            text_surface = self.__font.render(self.__text, True, self.__text_color)
            text_rect = text_surface.get_rect(center=self.__rect.center)
            srf.blit(text_surface, text_rect)

class Background: 
    def __init__(self, image):
        self.__image = self.__create_image(image)

    def __create_image(self, image):
        return pygame.image.load(image)
    
    def render(self, srf):
        srf.blit(self.__image, (0, 0))
    
class StartScreen:
    def __init__(self):
        self.__background = Background('images/Background-image.png')
        # self.__logo = Logo('images/logo.png', 412, 100, 200, 150)
        
        # Buttons
        self.__start_button = Button(412, 350, 200, 60, 'Start Game', (50, 150, 50), (70, 200, 70))
        self.__credits_button = Button(412, 430, 200, 60, 'Credits', (100, 100, 50), (150, 150, 70))
        self.__quit_button = Button(412, 510, 200, 60, 'Quit', (150, 50, 50), (200, 70, 70))
        self.__settings_button = Button(954, 10, 60, 60, '', (50, 50, 150), (70, 70, 200), icon_path='images/ui/settings-icon.png')
        
    def update(self, mouse_pos):
        self.__start_button.update(mouse_pos)
        self.__credits_button.update(mouse_pos)
        self.__settings_button.update(mouse_pos)
        self.__quit_button.update(mouse_pos)
    
    def handle_click(self, mouse_pos, mouse_pressed):
        if self.__start_button.is_clicked(mouse_pos, mouse_pressed):
            return 'start_game'
        elif self.__credits_button.is_clicked(mouse_pos, mouse_pressed):
            return 'credits'
        elif self.__settings_button.is_clicked(mouse_pos, mouse_pressed):
            return 'settings'
        elif self.__quit_button.is_clicked(mouse_pos, mouse_pressed):
            return 'quit'
        return None
    
    def render(self, srf):
        self.__background.render(srf)
        # self.__logo.render(srf)
        self.__start_button.render(srf)
        self.__credits_button.render(srf)
        self.__quit_button.render(srf)
        self.__settings_button.render(srf)

class State:
    def __init__(self):
        self.__background = Background('images/Background-image.png')

    def render(self, srf):
        self.__background.render(srf)

def create_main_surface():
    screen_size = (1024, 768)
    srf = pygame.display.set_mode(screen_size)
    return srf

def clear_surface(srf):
    srf.fill((0,0,0))

def render_frame(srf, state, player):
    clear_surface(srf)
    state.render(srf)
    player.render(srf)
    
    # Display player.x rechtsboven
    font = pygame.font.Font(None, 36)
    text = font.render(f'X: {int(player.x)}', True, (255, 255, 255))
    text_rect = text.get_rect(topright=(1024 - 10, 10))
    srf.blit(text, text_rect)
    
    pygame.display.flip()

def process_key_input(player, keys, screen_width):
    # Player image is 200 pixels breed, dus we checken van 0 tot screen_width - 200
    if keys[pygame.K_LEFT] and player.x > 0:
        player.x -= 5
    if keys[pygame.K_RIGHT] and player.x < screen_width - 200:
        player.x += 5

def main():
    pygame.init()
    # Maakt scherm
    srf = create_main_surface()
    # Clock voor fps vast te zetten - anders gaat spel te snel
    clock = pygame.time.Clock()
    
    # Game states
    current_state = 'start_screen'  # 'start_screen' of 'playing'
    start_screen = StartScreen()
    state = State()
    player = Player('images/first-car-concept.png')
    
    # Gameloop
    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        if current_state == 'start_screen':
            start_screen.update(mouse_pos)
            action = start_screen.handle_click(mouse_pos, mouse_pressed)
            
            if action == 'start_game':
                current_state = 'playing'
            elif action == 'quit':
                pygame.quit()
                return
            elif action == 'credits':
                # Voeg credits functionaliteit toe
                pass
            elif action == 'settings':
                # Voeg settings functionaliteit toe
                pass
            
            clear_surface(srf)
            start_screen.render(srf)
            pygame.display.flip()
            
        elif current_state == 'playing':
            keys = pygame.key.get_pressed()
            process_key_input(player, keys, 1024)
            render_frame(srf, state, player)
        
        clock.tick(60)  # 60 FPS
        
main()
