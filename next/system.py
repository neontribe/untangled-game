import pygame as pg
import pygame.locals

from component import RenderComponent

class SystemManager:
    def __init__(self):
        self.systems = []
        self.entities = []

    def addSystem(self, system):
        self.systems.append(system)

    def addEntity(self, entity):
        self.entities.append(entity)

    def executeSystems(self, dt):
        for s in self.systems:
            s.update(self.entities)


class RenderSystem():
    def __init__(self, width = 1024, height = 1024, caption = 'Untangled 2018'):
        pg.init()
        pg.display.set_caption(caption)
        pg.display.set_mode((width, height))
        self.screen = pg.display.set_mode((width, height), pg.HWSURFACE | pg.DOUBLEBUF)

    def update(self, entities):
        self.screen.fill((0,0,0))
        for e in entities:
            renderComponent = e.getComponent(RenderComponent)
            testRectangle = pg.Surface((100,100))
            testRectangle.fill((255,255,255))
            self.screen.blit(testRectangle, renderComponent.position)
            pg.display.update()