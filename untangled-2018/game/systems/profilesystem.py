from lib.system import System
from game.components import *

# The default images for each gender
PROFILE_SPRITES = {
    'Girl': {
        'path': './assets/sprites/player.png',
        'tile_size': 48,
        'tiles':{
            'default': [58],
            'left': [70, 71, 69],
            'right': [82, 83, 81],
            'up': [94, 95, 93],
            'down': [58, 59, 57]
        },
        'moving':False
    },
    'Boy': {
        'path': './assets/sprites/player.png',
        'tile_size': 48,
        'tiles':{
            'default': [10],
            'left': [22, 23, 21],
            'right': [34, 35, 33],
            'up': [46, 47, 45],
            'down': [10, 11, 9]
        },
        'moving': False
    },
}

class ProfileSystem(System):
    """Updates an entities profile and appearance based on ours and others'
    name and gdner."""

    def __init__(self, name, gender):
        self.ourName = name
        self.ourGender = gender

    def update(self, game, dt, events):
        for key, entity in game.entities.items():
            # Does this entity have a profile we can use to do things?
            if Profile in entity:
                if PlayerControl in entity and game.net.is_me(entity[PlayerControl].player_id):
                    # It's us, update our Profile component based on what we know
                    if entity[Profile].name != self.ourName:
                        entity[Profile].name = self.ourName
                    if entity[Profile].gender != self.ourGender:
                        entity[Profile].gender = self.ourGender

                if SpriteSheet in entity:
                    # This entity should change appearance based on gender, let's do that
                    if entity[Profile].gender in PROFILE_SPRITES:
                        # Get the appearance properties
                        gender_sheet = PROFILE_SPRITES[entity[Profile].gender]
                        changed = False
                        
                        # Do they need updating?
                        for sheet_key, value in gender_sheet["tiles"].items():
                            if entity[SpriteSheet].tiles[sheet_key] != value:
                                changed = True
                                break

                        # Yes, update them
                        if changed:
                            entity[SpriteSheet].path = gender_sheet['path']
                            entity[SpriteSheet].tile_size = gender_sheet['tile_size']
                            entity[SpriteSheet].tiles = {
                                'default' : gender_sheet["tiles"]['default'],
                                'left' : gender_sheet["tiles"]['left'],
                                'right' : gender_sheet["tiles"]['right'],
                                'up' : gender_sheet["tiles"]['up'],
                                'down' : gender_sheet["tiles"]['down']
                            }
