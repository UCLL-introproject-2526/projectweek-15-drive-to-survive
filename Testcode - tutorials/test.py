import pygame, time

class Background: 
    def __init__(self):
        self.__image = self.__create_image()

    def __create_image(self):
        return pygame.image.load('background.png')

    def render(self, surface):
        surface.blit(self.__image, (0, 0))

class State:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.__background = Background()

    def update(self, dt):
        self.x += dt

    def render(self, srf):
        self.__background.render(srf)
        pygame.draw.circle(srf, (255, 0, 0), (self.x, self.y), 50)

    def __repr__(self):
        return f'State("{self.x}")'


def create_main_surface():
    # Tuple representing width and height in pixels
    screen_size = (1024, 768)

    # Create window with given size
    srf = pygame.display.set_mode(screen_size)
    return srf

def clear_surface(srf):
    srf.fill((0, 0, 0))

def render_frame(srf, state):
    clear_surface(srf)
    state.render(srf)
    pygame.display.flip()

def process_key_input(state, key):
    if key == pygame.K_UP:
        state.y -= 10
    elif key == pygame.K_DOWN:
        state.y += 10
    elif key == pygame.K_LEFT:
        state.x -= 10
    elif key == pygame.K_RIGHT:
        state.x += 10


def main():
    #Initialize Pygame
    pygame.init()
    srf = create_main_surface()
    state = State()
    clock = pygame.time.Clock()
    while True:
        dt = clock.tick() / 1000
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                process_key_input(state, event.key)
        render_frame(srf, state)
        state.update(dt)

main()