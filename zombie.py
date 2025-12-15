class normalZombie:
    def __init__(self, level):
        self.__set_health(level)
        self.__set_speed(level)
    
    def __set_health(self, level):
        #health word per level exponentieel verhoogd met 10%
        self.__health = 50 * (1.1 ** level)
        
    def __set_speed(self, level):
        pass

class bigZombie:
    def __init__(self, level):
        self.__set_health(level)
        self.__set_speed(level)

    def __set_health(self, level):
        #health word per level exponentieel verhoogd met 10%
        self.__health = 200 * (1.1 ** level)
    
    def __set_speed(self, level):
        pass