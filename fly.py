import sys
import os
from graph import Graph
from parse import GlobalValidation
from path import Path

if __name__ == "__main__":
        file = sys.argv[1]
        if file == os.path.basename(__file__):
            raise FileExistsError(
                "Config file name must differ from the code file name"
            )
        try:
            with open(file, "r") as f:
                lines = f.readlines()
                data = GlobalValidation(lines)
                zones = Graph(lines)
                zones.dijkstra()
        except Exception as e:
            print(e)