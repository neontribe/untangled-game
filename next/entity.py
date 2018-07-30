class Entity:
    def __init__(self, components):
        self.components = {}

        for component in components:
            self.setComponent(component)
    
    def setComponent(self, component):
        key = type(component)
        self.components[key] = component
    
    def getComponent(self, key):
        return self.components[key]

    def hasComponent(self, key):
        return (key in self.components)