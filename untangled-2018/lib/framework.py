import pygame
import sys

from lib.network import Network
from lib.menu import MenuState

class Framework:
    """The core state of our app."""

    caption = 'Untangled 2018'
    dimensions = (1024, 1024)
    fps = 60
    running = True
    clock = pygame.time.Clock()

    def __init__(self, GameState):
        # Initialise pygame
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.set_caption(self.caption)
        disp_info = pygame.display.Info()
        self.dimensions = (min(1024, disp_info.current_w), min(1024, disp_info.current_h))
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
                elif event.type==pygame.VIDEORESIZE:
                    disp_info = pygame.display.Info()
                    self.dimensions = (min(1024, disp_info.current_w), min(1024, disp_info.current_h))
                    self.screen = pygame.display.set_mode(self.dimensions, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE)
                    pygame.display.flip()

            # Update the current state
            self.state.update(dt, events)

            # Display any rendered updates
            pygame.display.update()

        # We've stopped, quit the network, close pygame, kill everything
        self.net.node.leave(self.net.get_our_group() or '')
        self.net.close()
        pygame.quit()
        sys.exit()

    def enter_game(self, char_name, char_gender):
        # To be called from the menu, puts us into the game
        self.state = self.GameState(self, char_name, char_gender)
