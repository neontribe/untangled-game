from dataclasses import dataclass
import dataclasses

def component(networked: bool = False):
    """Is wrapped around a component.

    Let's us:
    - See changes
    - Auto-create an __init__ function and other niceties
    - Keep track of whether any properties have been changed"""

    # TODO can we do this with a class instead of a decorator?

    # We call our decoraters, so we must return an actual decorator function
    def componentWrapper(clas):
        # Dirty hack. Extend the given class with @dataclass to do some dirty work.
        class Component(dataclass(clas)):
            _changed=True

            def __setattr__(self, name, value):
                # A property may have been changed! Store this.
                if name != '_changed':
                    self._changed = True
                super().__setattr__(name, value)

            def replace(self, **changes):
                # We want to replace all values with new ones, accommodate this.
                return dataclasses.replace(self, **changes)

            def get_name(self):
                # Get the original name of the component, pre-messing around with it.
                return clas.__name__

            def has_changed(self):
                # Has the element been changed since we last checked?
                return self._changed

            def observed_changes(self):
                # Acknowledge that we've seen all new changes.
                self._changed = False

            def as_dict(self):
                # Get the component as a JSON object.
                return dataclasses.asdict(self)

            def is_networked(self):
                # Should this component be sent across the network?
                return networked
        return Component
    return componentWrapper

