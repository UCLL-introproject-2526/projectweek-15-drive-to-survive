import pygame 
from player import Player

class Background: 
    def __init__(self, image):
        self.__image = self.__create_image(image)

    def __create_image(self, image):
        return pygame.image.load(image)
    
    def render(self, srf):
        srf.blit(self.__image, (0, 0))
    
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
        player.x -= 2
    if keys[pygame.K_RIGHT] and player.x < screen_width - 200:
        player.x += 2

def main():
    pygame.init()
    # Maakt scherm
    srf = create_main_surface()
    # Clock voor fps vast te zetten - anders gaat spel te snel
    state = State()
    player = Player('images/first-car-concept.png')
    clock = pygame.time.Clock()
    # Gameloop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        keys = pygame.key.get_pressed()
        process_key_input(player, keys, 1024)
        render_frame(srf, state, player)
main()
