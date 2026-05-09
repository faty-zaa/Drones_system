from parse import GlobalValidation
from zone import Zone
from connection import Connection
import heapq

class Graph(GlobalValidation):
    def __init__(self, lines):
        """initialisation of the variables of the graph"""
        super().__init__(lines) 
        self.lines = lines
        self.zones = self.creat_zone_obj()
        self.connections = self.creat_conx_obj()
        self.nb_drones = int(self.config["nb_drones"][0].strip())
        self.start = self.config["start_hub"][0].strip().split()[0]
        self.end = self.config["end_hub"][0].strip().split()[0]
        self.zone_names = [i.name for i in self.zones]
        self.graph = self.creat_graph()

        """filling the zone class and setupping the start and the end"""

    def creat_graph(self):
        grap = {name: [] for name in self.zone_names}
        zones_map = {z.name:z for z in self.zones}
        for i in self.connections:
            grap[i.src].append((i.dst, zones_map[i.dst].cost))
            grap[i.dst].append((i.src, zones_map[i.src].cost))
        return grap

    def dijkstra(self):
        heap = [(0, [self.start])]
        # initialisation dyal heap b start
        all_path = {}

        while heap and len(all_path) < 2:
            # bghit 2 dyal low cost paths 
            total_cost, path= heapq.heappop(heap)
            # hna knpopi l path li3ndo a9al cost 
            node = path[-1]
            # knjibo akher node f path
            if node == self.end:
                # lawslna lkher walakin ba9i maytdiskovra f eap knkhzno lpath
                if total_cost in all_path:
                    #ila kano pathat bnfs lcost knzidohom f list w7da
                    all_path[total_cost] += [path]
                else:
                    # lakan path jdid kn3tiwh key hwa cost 3ad value hwa l path
                    all_path[total_cost] = [path]
                #kml bach laba9i chi node matdiskoveratch
                continue
            for neighbor, cost in self.graph[node]:
                # knexploriw neighboars dyal node l7aliya
                if neighbor in path:
                    # ila kan dak neighboard f heap n9zo matalan s -> a -> s
                    continue
                if cost == 0:
                    # blocked zone n9zha
                    continue
                new_cost = total_cost + cost
                #knjm3o costs dyal zones lifdak path
                heapq.heappush(heap, (new_cost, path + [neighbor]))
                #hna knpushiw ldak heap path jdid bcost jdid
        print(all_path)
 
    def __repr__(self):
        return f"Graph(zones ----->{self.zones}, connections------->{self.connections})"
