import sys
import os
from graph import Graph
from parse import GlobalValidation
from simulation import Simulation
from visualisation import Visualisation
from pyray import (
    BLACK,
    GOLD,
    begin_drawing,
    clear_background,
    close_window,
    draw_text,
    end_drawing,
    get_screen_height,
    get_screen_width,
    init_window,
    is_key_pressed,
    window_should_close,
)

if __name__ == "__main__":
    """this is the entry point of the project"""
    try:
        file = sys.argv[1]
        if file == os.path.basename(__file__):
            raise FileExistsError(
                "Config file name must differ from the code file name")
        with open(file, "r") as f:
            lines = f.readlines()
            data = GlobalValidation(lines)
            zones = Graph(data)
            sm = Simulation(zones)
            drones, maxt = sm.count_turns()
            a = Visualisation(zones, drones)
            init_window(1900, 900, "FLY-IN")
            radius = int(min(get_screen_width(), get_screen_height()) * 0.03)
            center_x = 100
            center_y = get_screen_height() // 2
            turn = 0
            while not window_should_close():
                begin_drawing()
                clear_background(GOLD)

                a.draw(center_x, center_y, radius, turn)
                if is_key_pressed(262) and turn < maxt:
                    turn += 1
                if is_key_pressed(263) and turn > 0:
                    turn -= 1
                draw_text(f"Turn {turn}", 10, 10, 20, BLACK)
                end_drawing()
            close_window()

    except Exception as e:
        print(e)
