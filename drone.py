from typing import List, Optional, Tuple


class Drone:
    """class to make drones objects"""
    def __init__(self, path: List[str]) -> None:
        self.path: List[str] = path
        self.id: str = ""
        self.position: int = 0
        self.finish: bool = False
        self.wait: int = 0
        self.current_conx: Optional[Tuple[str, str]] = None
        self.canmove: bool = False
        self.last_position: int = 0
        self.steps: List[Tuple[int, int]] = []
