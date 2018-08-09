from typing import Tuple
from lib.system import System
from game.components import *
from random import randint
import math, time

class DamageSystem(System):
    def update(self, game, dt, events):
        for key, entity in dict(game.entities).items():
            if Health in entity and PlayerControl not in entity:
                if entity[Health].value <= 0:
                    del game.entities[key]

    def onDamage(self, event):
        target = None
        other = None
        
        for k in event.keys:

            if k not in game.entities:
                continue
            entity = game.entities[k]

            entity = event.game.entities[k]

            if Damager in entity:
                other = entity
            if PlayerControl in entity or ChasePlayer in entity:
                target = entity

        if target != None and other != None:
            other_DamagerComponent = other[Damager]
            if target[IngameObject].id in other_DamagerComponent.exclude:
                return
            if other_DamagerComponent.lasthit + other_DamagerComponent.cooldown < time.time():
                damage = randint(other_DamagerComponent.damagemin, other_DamagerComponent.damagemax)
                target_HealthComponent = target[Health]
                target_HealthComponent.value -= damage
                other_DamagerComponent.lasthit = time.time()

                

        
            if target[Health].value<=0:
               target[Health].value=100
               target[IngameObject].position=(0,0)

