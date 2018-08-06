from typing import List
from typing import Tuple
from typing import Union

from lib.component import component

@component(networked=True)
class IngameObject:
    """Gives an entity a place and size in game."""
    position: Tuple[int, int]
    size: Tuple[int, int]

@component(networked=True)
class Health:
    """Gives the entity health"""
    value: int

@component(networked=True)
class SpriteSheet:
    """Gives an entity an image and animations."""
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
    """States that an entity will be pointing in a certain direction.
    e.g. if walking"""
    direction: str = 'default'

@component(networked=True)
class Profile:
    """Gives an entity a name and gender."""
    name: str = 'Player'
    gender: str = 'Unknown'

@component(networked=True)
class PlayerControl:
    """Lets an entity be controlled by specific player's arrow keys."""
    player_id: str

@component(networked=False)
class Collidable:
    """Lets an entity collide with another collidable"""
    def toRect(self):
        return (self.position[0], self.position[1], self.size[0], self.size[1])
    def defaultFunction(other):
        return False
    onCollide = defaultFunction
