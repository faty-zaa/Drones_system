from typing import List, Tuple, Dict, Union


class Zone:
    def __init__(
        self,
        name: str,
        data: List[Union[Tuple[int, int], Dict[str, str]]]
    ) -> None:
        coords = data[0]
        meta = data[1]
        assert isinstance(coords, tuple)
        assert isinstance(meta, dict)
        self.name: str = name
        self.coords: Tuple[int, int] = coords
        self.x: int = coords[0]
        self.y: int = coords[1]
        self.zone_type: str = meta["zone"]
        self.color: str = meta["color"]
        self.max_drones: int = int(meta["max_drones"])
        self.place: str = "hub"
        self.neighbors: List[str] = []
        self.current_drones: List[str] = []
        self.cost: int = self.search_cost()

    def search_cost(self) -> int:
        if self.zone_type in ["normal", "priority"]:
            cost = 1
        elif self.zone_type == "restricted":
            cost = 2
        elif self.zone_type == "blocked":
            cost = 0
        else:
            cost = 1
        return cost

    def __repr__(self) -> str:
        """Instead of showing memory stuff, show this readable description."""
        return f"({self.name}-{self.coords}--{self.place})"