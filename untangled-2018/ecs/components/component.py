import pygame
from typing import List
from typing import Tuple
from typing import Union
from dataclasses import dataclass
import dataclasses

def component(networked: bool = False):
    def componentWrapper(clas):
        class Component(dataclass(clas)):
            _changed=True

            def __setattr__(self, name, value):
                if name != '_changed':
                    self._changed = True
                super().__setattr__(name, value)

            def replace(self, **changes):
                return dataclasses.replace(self, **changes)

            def get_name(self):
                return clas.__name__

            def has_changed(self):
                return self._changed

            def observed_changes(self):
                self._changed = False

            def as_dict(self):
                return dataclasses.asdict(self)

            def is_networked(self):
                return networked
        return Component
    return componentWrapper

@component(networked=True)
class IngameObject:
    position: Tuple[int, int]
    size: Tuple[int, int]

@component(networked=True)
class SpriteSheet:
    path: str
    tile_size: int
    default: List[int]
    left: Union[List[int], None]
    right: Union[List[int], None]
    up: Union[List[int], None]
    down: Union[List[int], None]
    moving: bool = False

@component(networked=True)
class Directioned:
    direction: str

@component(networked=True)
class Profile:
    name: str = 'Player'
    gender: str = 'Unknown'

@component(networked=True)
class PlayerControl:
    player_id: str
