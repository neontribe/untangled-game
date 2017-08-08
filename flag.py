import pygame

NEUTRALFLAG = "assets/tilesets/flag.png"
REDFLAG = "assets/tilesets/Red Flag.png"
BLUEFLAG = "assets/tilesets/Blue Flag.png"

class FlagException(Exception):
    pass

class Flag():
    def __init__(self, screen, map, team):
        self.screen = screen
        self.map = map
        self.ready = False
        self.is_centre = False
        self.x, self.y = (0, 0)
        self.animation_ticker = 0
        self.image = pygame.image.load(NEUTRALFLAG)

        self.initial_position = (0, 0)
        found = False
        for x in range(map.level.width):
            for y in range(map.level.height):
                if map.level.is_safe(x, y):
                    self.initial_position = (x, y)
                    found = True
                    break
            if found:
                break
        self.set_position(self.initial_position)
        self.team = team
    
    def set_position(self, position):
        self.x,  self.y = position
        self.ready = True
        
    def set_position_from_authority(self, received):
        print(received)
        self.x = int(received["x"])
        self.y = int(received["y"])
        self.ready = True
    
    def render(self):
        centre = self.map.get_pixel_pos(self.x, self.y)
        
        if self.team == "red":
            self.image = pygame.image.load(REDFLAG)
        elif self.team == "blue":
            self.image = pygame.image.load(BLUEFLAG)
        #sprite = pygame.sprite.Sprite(self.image)
        self.screen.blit(self.image, centre)

        # create collision rectangle
        self.rect = self.image.get_rect()
        self.rect.topleft = centre
