from typing import Tuple


class Connection:
    def __init__(self, keys: Tuple[str, str], values: int) -> None:
        self.src: str = keys[0]
        self.dst: str = keys[1]
        self.max: int = int(values)
        self.using: int = 0

    def __repr__(self) -> str:
        return f"{self.src} -> {self.dst} (max={self.max})"