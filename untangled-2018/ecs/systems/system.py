class System:
    def __init__(self):
        return

    def update(self, game: 'ecs.untangled.GameState', dt: float, events: list):
        return

    def check_components(self, entity: dict, components: tuple):
        return all(component in entity for component in components)

