from pyray import (
    BLACK,
    BLUE,
    BROWN,
    GOLD,
    GREEN,
    LIME,
    MAGENTA,
    MAROON,
    ORANGE,
    PURPLE,
    RED,
    SKYBLUE,
    VIOLET,
    YELLOW,
    Color,
    Vector2,
    draw_circle_v,
    draw_line_ex,
    draw_text,
)
from graph import Graph
from drone import Drone
from typing import List
import random

COLORS = {
    "red": RED,
    "green": GREEN,
    "blue": BLUE,
    "yellow": YELLOW,
    "orange": ORANGE,
    "cyan": SKYBLUE,
    "purple": PURPLE,
    "brown": BROWN,
    "lime": LIME,
    "magenta": MAGENTA,
    "gold": GOLD,
    "black": BLACK,
    "maroon": MAROON,
    "darkred": Color(139, 0, 0, 255),
    "violet": VIOLET,
    "crimson": Color(220, 20, 60, 255),
    "rainbow": Color(255, 0, 255, 255),
}


class Visualisation:
    """visualisation of the project with pyray"""
    def __init__(self, graph: Graph, drones: List[Drone]):
        self.zone = graph.zones
        self.cords = {z.name: z.coords for z in graph.zones}
        self.conx = graph.connections
        self.drones = drones
        available_colors = [
            color for name, color in COLORS.items()
            if name != "black"
        ]

        self.drone_colors = [
            random.choice(available_colors)
            for _ in self.drones
        ]

    def draw(self, centrex: int, centrey: int, r: int, turn: int) -> None:
        for c in self.conx:
            x1 = self.cords[c.src][0] * 87 + (centrex // 2)
            y1 = self.cords[c.src][1] * 87 + (centrey // 1.4)
            x2 = self.cords[c.dst][0] * 87 + (centrex // 2)
            y2 = self.cords[c.dst][1] * 87 + (centrey // 1.4)
            draw_line_ex(Vector2(x1, y1), Vector2(x2, y2), 3, BLACK)
            draw_line_ex(
                Vector2(x1 + 6, y1 + 6),
                Vector2(x2 + 6, y2 + 6), 3, Color(0, 0, 0, 120)
            )

        for z in self.zone:
            bx, by = z.coords
            x = bx * 86 + (centrex // 2)
            y = by * 86 + (centrey // 1.4)
            color = COLORS.get(z.color.lower(), BLACK)
            draw_circle_v(Vector2(x + 6, y + 6), r + 6, Color(0, 0, 0, 120))
            draw_circle_v(Vector2(x, y), r, color)
            draw_text(z.name, int(x - 20), int(y + 30), 8, BLACK)
            draw_text(str(z.cost), int(x), int(y - 10), 22, BLACK)

        for i, d in enumerate(self.drones):
            step_idx = min(turn, len(d.steps) - 1)
            bx, by = d.steps[step_idx]

            x = bx * 86 + (centrex // 2)
            y = by * 86 + (centrey // 1.4)

            offset_x = (i % 3) * 4
            offset_y = (i // 3) * 4

            draw_circle_v(
                Vector2(x + offset_x, y + offset_y), 10, self.drone_colors[i])
            draw_text(
                "D" + str(i + 1),
                int(x + offset_x - 5),
                int(y + offset_y - 7),
                12,
                BLACK,
            )
