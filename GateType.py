class GateType:
    """Stores a type of gate."""

    def __init__(self, name, color, linear_transformation, control=False):
        self.name = name
        self.color = color
        self.linear_transformation = linear_transformation
        self.control = control