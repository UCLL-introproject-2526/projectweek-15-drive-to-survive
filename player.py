import pygame

class Player: 
    def __init__(self, image):
        self.x = 25
        self.y = 500
        self.__create_image(image)

    def __create_image(self, image):
        self.__image = pygame.image.load(image)
        self.__image = pygame.transform.scale(self.__image, (200, 200))

    def update(self, dt):
        self.x += dt

    def render(self, srf):
        srf.blit(self.__image, (self.x, self.y))
