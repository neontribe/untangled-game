from lib.system import System
from game.components import *
class TimeSystem(System):

    def update(self,game,dt,events):
            for key, entity in game.entities.items():
                if Clock in entity:
                    if Timed in entity:
                        if game.net.is_hosting():
                            entity[Timed].time += 1
                            if entity[Timed].time >= 3600:
                                entity[Timed].time = 0
                                entity[Clock].minute += 1
                            if entity[Clock].minute >= 6:
                                entity[Clock].minute = 0
                                entity[Clock].cycle += 1
                                #entity[GrowthRate] -= 1
                                #Growthrate for when plants merged in. Every day, the growth time reduces by one. 
                            if entity[Clock].cycle >= 360:
                                entity[Clock].cycle = 0
                                entity[Clock].year += 1