
class Path():
    def __init__(self, graph, start, end):
        self.graph = graph
        self.start = start
        self.end = end
        self.len = len(self.graph.keys())
        self.dist = dict.fromkeys(self.graph.keys(), float('inf'))

    def search(self):
        self.dist[self.start] = 0
        
