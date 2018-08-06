from ecs.systems.system import System
from ecs.components.component import *

PROFILE_SPRITES = {
    'Girl': {
        'path': './assets/sprites/player.png',
        'tile_size': 48,
        'default': [58],
        'left': [70, 71, 69],
        'right': [82, 83, 81],
        'up': [94, 95, 93],
        'down': [58, 59, 57]
    },
    'Boy': {
        'path': './assets/sprites/player.png',
        'tile_size': 48,
        'default': [10],
        'left': [22, 23, 21],
        'right': [34, 35, 33],
        'up': [46, 47, 45],
        'down': [10, 11, 9],
        'moving': False
    }
}

class ProfileSystem(System):
    def __init__(self, name, gender):
        self.ourName = name
        self.ourGender = gender

    def update(self, game, dt, events):
        for key, entity in game.entities.items():
            if Profile in entity:
                if PlayerControl in entity and game.net.is_me(entity[PlayerControl].player_id):
                    # Update our Profile component
                    if entity[Profile].name != self.ourName:
                        entity[Profile].name = self.ourName
                    if entity[Profile].gender != self.ourGender:
                        entity[Profile].gender = self.ourGender

                if SpriteSheet in entity:
                    # Update the sprite based on gender
                    if entity[Profile].gender in PROFILE_SPRITES:
                        gender_sheet = PROFILE_SPRITES[entity[Profile].gender]
                        changed = False
                        for sheet_key, value in gender_sheet.items():
                            if entity[SpriteSheet].__dict__[sheet_key] != value:
                                changed = True
                                break
                        if changed:
                            entity[SpriteSheet].path = gender_sheet['path']
                            entity[SpriteSheet].tile_size = gender_sheet['tile_size']
                            entity[SpriteSheet].default = gender_sheet['default']
                            entity[SpriteSheet].left = gender_sheet['left']
                            entity[SpriteSheet].right = gender_sheet['right']
                            entity[SpriteSheet].up = gender_sheet['up']
                            entity[SpriteSheet].down = gender_sheet['down']
