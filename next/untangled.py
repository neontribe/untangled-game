import os
import sys
import pygame as pg
from system import SystemManager, RenderSystem
from player import Player

class Main:
    def __init__(self):
        self.player = Player()
        self.clock = pg.time.Clock()
        self.fps = 60
        self.running = True
        self.system_manager = SystemManager()
        self.system_manager.addSystem(RenderSystem())
        self.system_manager.addEntity(self.player)
      
    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type in (pg.KEYDOWN, pg.KEYUP):
                self.keys = pg.key.get_pressed()

    def update(self, dt):
        self.system_manager.executeSystems(dt)

    def main_loop(self):
        dt = 0
        self.clock.tick(self.fps)
        while self.running:
            self.event_loop()
            self.update(dt)
            dt = self.clock.tick(self.fps)/1000.0

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    Main().main_loop()
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()