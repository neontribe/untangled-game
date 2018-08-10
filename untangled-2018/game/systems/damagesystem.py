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

    def onDamage(self, game, event):
        targetKey, target = event.get_entity_with_component(Health)
        if target != None:
            otherKey, other = event.get_entity_with_component(Damager, [targetKey])
            if other != None:
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
                    target[IngameObject].position=(100, 100)