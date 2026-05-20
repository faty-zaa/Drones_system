from parse import GlobalValidation
from zone import Zone
from connection import Connection
import heapq
from collections import deque
from typing import List, Dict, Tuple, Set


class Graph:
    """class to creat graph and algo"""
    def __init__(self, parser: GlobalValidation) -> None:
        self._parser = parser
        self.zones: List[Zone] = self._parser.creat_zone_obj()
        self.connections: List[Connection] = self._parser.creat_conx_obj()
        nb_drones, start, end = self._parser.start_end_nbdrone()
        self.nb_drones: int = nb_drones
        self.start: str = start
        self.end: str = end
        self.zone_names: List[str] = [i.name for i in self.zones]
        self.zones_map: Dict[str, Zone] = {z.name: z for z in self.zones}
        self.graph: Dict[str, List[Tuple[str, int]]] = self.creat_graph()

        """filling the zone class and setupping the start and the end"""

    def creat_graph(self) -> Dict[str, List[Tuple[str, int]]]:
        grap: Dict[str, List[Tuple[str, int]]] = {
            name: [] for name in self.zone_names}
        for i in self.connections:
            grap[i.src].append((i.dst, self.zones_map[i.dst].cost))
            grap[i.dst].append((i.src, self.zones_map[i.src].cost))
        return grap

    """Algo to check disconnected graph"""
    def check_graph(self, zone: str, dest: str) -> List[str]:
        q: deque[str] = deque([zone])
        explored: Set[str] = set()
        explored.add(zone)
        parent: Dict[str, str] = {}
        while q:
            node = q.popleft()
            if node == dest:
                break
            neighboars = self.graph[node]
            for i, _ in neighboars:
                if i in explored:
                    continue
                explored.add(i)
                parent[i] = node
                q.append(i)
        if dest not in explored:
            return []
        path: List[str] = []
        current: str = dest
        while current != zone:
            path.append(current)
            current = parent[current]
        path.append(zone)
        path.reverse()
        return path

    def validate_graph(self) -> bool:
        for zone in self.zone_names:
            path = self.check_graph(zone, self.start)
            if not path:
                return False
        return True

    """Algo to find multi-paths"""
    def paths_algo(self) -> Dict[int, List[List[str]]]:
        heap: List[Tuple[int, int, List[str]]] = [(0, 0, [self.start])]
        all_path: Dict[int, List[List[str]]] = {}

        if not self.validate_graph():
            raise ValueError("Error: Disconnected Graph")

        while heap and len(all_path) < self.nb_drones:
            total_cost, priority_first, path = heapq.heappop(heap)
            node = path[-1]
            if node == self.end:
                if total_cost in all_path:
                    all_path[total_cost] += [path]
                else:
                    all_path[total_cost] = [path]
                continue
            for neighbor, cost in self.graph[node]:
                if neighbor in path:
                    continue
                if self.zones_map[neighbor].zone_type == "blocked":
                    continue
                new_cost = total_cost + cost
                if self.zones_map[neighbor].zone_type == "priority":
                    priority = 0
                else:
                    priority = 1
                heapq.heappush(
                    heap, (
                        new_cost, priority_first + priority, path + [neighbor])
                )
        return all_path
