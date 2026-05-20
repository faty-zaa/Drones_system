from typing import List, Tuple, Dict, Union, cast


class Zone:
    """class to make zone's data objects"""
    def __init__(
        self, name: str, data: List[Union[Tuple[int, int], Dict[str, str]]]
    ) -> None:

        coords = cast(Tuple[int, int], data[0])
        meta = cast(Dict[str, str], data[1])

        self.name: str = name
        self.coords: Tuple[int, int] = coords
        self.x: int = coords[0]
        self.y: int = coords[1]

        self.zone_type: str = meta["zone"]
        self.color: str = meta["color"]
        self.max_drones: int = int(meta["max_drones"])

        self.place: str = "hub"
        self.neighbors: List[str] = []
        self.current_drones: int = 0
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
        return f"({self.name}-{self.coords}--{self.place})"
