import pygame, sys, platform, os

from lib.network import Network
from lib.menu import MenuState

class Framework:
    """The core state of our app."""

    caption = 'Untangled 2018'
    
    dimensions = (1024, 824)

    fps = 60
    running = True
    clock = pygame.time.Clock()

    def __init__(self, GameState):
        # Initialise pygame
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.dimensions, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)

        # Delegate
        self.net = Network()
        self.GameState = GameState
        self.state = MenuState(self)

    def main_loop(self):
        # Initial tick so our first tick doesn't return all the time since __init__
        self.clock.tick()
        

        # While we haven't been stopped
        while self.running:
            # Black-out the screen
            self.screen.fill((0, 0, 0))

            # Count how long has passed since we last did this
            dt = self.clock.tick(self.fps) / 1000.0

            # Grab any keyboard/window events
            events = [ event for event in pygame.event.get() ]

            for event in events:
                # The user probably closed the window, let's quit
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.VIDEORESIZE:
                    SCREENSIZE = (event.w,event.h)
                    pygame.display.set_mode(SCREENSIZE, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                    self.dimensions = SCREENSIZE

            # Update the current state
            self.state.update(dt, events)

            # Display any rendered updates
            pygame.display.update()

        # We've stopped, quit the network, close pygame, kill everything
        self.net.node.leave(self.net.get_our_group() or '')
        pygame.display.quit()
        self.net.close()
        if platform.system() == "Windows":
            os.system("taskkill /f /pid "+str(os.getpid()))
        elif platform.system() == "Linux":
            pygame.quit()
            sys.exit()
        

    def enter_game(self, char_name, char_gender, char_colour):
        # To be called from the menu, puts us into the game
        final_colour = list(char_colour) if char_colour is not None else (00,255,29)
        if char_colour is not None:
            for i in range(0,len(char_colour)):
                if char_colour[i] not in range(0,256):
                    final_colour[i] = 128
        self.state = self.GameState(self, char_name, char_gender, (final_colour[0],final_colour[1],final_colour[2]) if char_colour != (-1,-1,-1) else (-1,-1,-1))
