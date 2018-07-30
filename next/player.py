from entity import Entity
from pygame import Vector2
from component import RenderComponent

class Player(Entity):
    def __init__(self):
        super().__init__([RenderComponent(Vector2(100,100))])