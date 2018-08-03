import pygame
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
class RenderComponent:
    x: int
    y: int
    width: int
    height: int
    color: str


@component(networked=True)
class PlayerControlComponent:
    player_id: str
