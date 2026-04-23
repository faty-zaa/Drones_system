
from parse import GlobalValidation
import sys
import os
from zone import Zone

class Graph(GlobalValidation):
    def __init__(self, lines):
        super().__init__(lines)
        self.hubs, self.conx =  GlobalValidation(lines).connection_check()
        #print(self.hubs)#, '\n\n\n', self.conx)
        zones = {}
        for name, value in self.hubs.items():
            zones[name] = Zone(name, value)
        print(zones)
    # def add_nighbors(self, i):
    #     for n in self.conx.keys():
    #         if i in n:
                
    def creat_graph(self):
        start = self.config["start_hub"][0].strip().split()[0]
        goal = self.config["end_hub"][0].strip().split()[0]
        nb = self.config["nb_drones"][0].strip()
        hub = self.hubs
        graph = {}
        graph["nb_drones"] = int(nb)
        for i in hub.keys():
            if i == goal:
                graph["goal"] = hub[goal]
            elif i == start:
                graph["start"]= hub[start]
            else:
                graph[f"{i}"] = hub[i]
            self.add_nighbors(i)
        # print(graph)  

if __name__ == "__main__":
    try:
        file = sys.argv[1]
        if file == os.path.basename(__file__):
            raise FileExistsError(
                "Config file name must differ from the code file name"
            )
        with open(file, "r") as f:
            lines = f.readlines()
            
            Graph(lines).creat_graph()
    except Exception as e:
        print(e)