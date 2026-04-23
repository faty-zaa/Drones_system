
class Zone():
    def __init__(self, name, data):
        self.name       = name
        self.coords     = data[0]
        self.x          = data[0][0]
        self.y          = data[0][1]
        self.zone_type  = data[1]["zone"]
        self.color      = data[1]["color"]
        self.max_drones = int(data[1]["max_drones"])
        self.neighbors  = []

    def __repr__(self):
        """Instead of showing memory stuff, show this readable description."""
        return f"Zone(name={self.name}, coords={self.coords}, color={self.color})"
