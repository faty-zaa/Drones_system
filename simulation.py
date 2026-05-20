from drone import Drone
from typing import List, Dict, Tuple, Any
from graph import Graph


class Simulation:
    """class to move drones via zones"""
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.paths = self.graph.paths_algo()

        if not self.paths:
            raise ValueError(
                "No valid path found from start to goal."
                " Check for blocked zones or disconnected graph."
            )

        self.drones = self.creat_drones()
        self.path_cost = min(list(self.paths.keys()))
        self.zones = {z.name: z for z in self.graph.zones}
        self.connections: Dict[Tuple[str, str], Any] = {}

        for c in self.graph.connections:
            self.connections[c.conx] = c
            self.connections[(c.conx[1], c.conx[0])] = c

    def creat_drones(self) -> List[Drone]:
        """give each drone it path"""
        drones: List[Drone] = []

        min_cost = min(self.paths.keys())

        drones_path1 = self.paths[min_cost][0]
        drones_path2 = drones_path1

        if len(self.paths[min_cost]) > 1:
            drones_path2 = self.paths[min_cost][1]
        elif len(self.paths) > 1:
            second_cost = sorted(self.paths.keys())[1]
            drones_path2 = self.paths[second_cost][0]

        nb_drone = self.graph.nb_drones

        for idx in range(nb_drone):
            if drones_path1 == drones_path2 or nb_drone < 10:
                drone = Drone(drones_path1)
            else:
                if idx % 2 == 0:
                    drone = Drone(drones_path1)
                else:
                    drone = Drone(drones_path2)

            drone.id = f"D{idx + 1}"
            drones.append(drone)

        return drones

    def request_zone(self, zone: str) -> bool:
        """check if zone available"""
        data = self.zones.get(zone)
        if not data:
            return False
        if zone == self.graph.start or zone == self.graph.end:
            return True

        if data.current_drones >= data.max_drones:
            return False

        return True

    def request_con(self, src: str, dst: str) -> bool:
        """check if connection available"""
        con = self.connections.get((src, dst))

        if not con:
            return False

        return bool(con.using < con.max)

    def move_drone(self, drone: Drone, future: Dict[str, int]) -> None:
        """give one drone the state of moving or not"""
        if drone.finish:
            return

        current = drone.path[drone.position]

        if drone.position == len(drone.path) - 1:
            drone.finish = True
            return

        next_node = drone.path[drone.position + 1]

        if drone.wait > 0:
            drone.wait -= 1
            if drone.wait == 0:
                if not self.request_zone(next_node):
                    drone.wait = 1
                    return
                self.zones[next_node].current_drones += 1
                future[next_node] += 1
                if drone.current_conx:
                    self.connections[drone.current_conx].using -= 1
                    drone.current_conx = None
                drone.canmove = True
            return

        if next_node != self.graph.start and next_node != self.graph.end:
            if future[next_node] >= self.zones[next_node].max_drones:
                return

        if not self.request_con(current, next_node):
            return

        self.connections[(current, next_node)].using += 1
        drone.current_conx = (current, next_node)
        next_cost = self.zones[next_node].cost
        if next_cost <= 1:
            future[current] -= 1
            future[next_node] += 1
            drone.canmove = True
        else:
            future[current] -= 1
            self.zones[current].current_drones -= 1
            drone.wait = next_cost - 1

    def move_all(self, step: int) -> List[Drone]:
        """move drones by checking it state and add position"""
        for drone in self.drones:
            drone.last_position = drone.position

        ordered = sorted(self.drones, key=lambda d: 0 if d.wait > 0 else 1)

        future: Dict[str, int] = {}

        for name, zone in self.zones.items():
            future[name] = zone.current_drones

        for drone in ordered:
            self.move_drone(drone, future)

        for drone in self.drones:
            if drone.finish:
                continue
            if not drone.canmove:
                current = drone.path[drone.position]
                drone.steps.append(self.zones[current].coords)
                continue

            drone.position += 1
            if drone.position == len(drone.path):
                drone.finish = True
            current = drone.path[drone.position]
            drone.steps.append(self.zones[current].coords)
            drone.canmove = False

            if drone.current_conx:
                self.connections[drone.current_conx].using -= 1
                drone.current_conx = None

        for name, count in future.items():
            self.zones[name].current_drones = count

        turn: List[str] = []
        for drone in self.drones:
            if drone.finish:
                continue
            if drone.position == drone.last_position and drone.wait == 0:
                continue

            if drone.wait > 0 and drone.current_conx:
                src, dst = drone.current_conx
                turn.append(f"{drone.id}-{src}-{dst}")
            else:
                current = drone.path[drone.position]
                turn.append(f"{drone.id}-{current}")
        if not all(d.finish for d in self.drones):
            print(f"Turn {step + 1}")
        if turn:
            for i in turn:
                print(i)
        return self.drones

    def count_turns(self) -> Tuple[List[Drone], int]:
        """count how many turn drones make to reach the goal"""
        for drone in self.drones:
            start = drone.path[0]
            self.zones[start].current_drones += 1
            drone.steps.append(self.zones[start].coords)
        i = 0
        while not all(d.finish for d in self.drones):
            drn = self.move_all(i)
            i += 1
        return drn, (i - 1)
