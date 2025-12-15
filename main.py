import pygame

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

def render_frame(srf, state):
    clear_surface(srf)
    state.render(srf)
    pygame.display.flip()

def main():
    pygame.init()
    # Maakt scherm
    srf = create_main_surface()
    # Clock voor fps vast te zetten - anders gaat spel te snel
    state = State()
    clock = pygame.time.Clock()
    # Gameloop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        render_frame(srf, state)
main()
