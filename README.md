*This project has been created as part of the 42 curriculum by <falamlih>*

# FLY_IN

# Description
    
    FLY_IN is a drone routing and simulation project that manages the movement
    of multiple drones from a start zone to an end zone across a network of
    connected zones.

    The project simulates drone traffic while respecting multiple constraints:

    - zone types
    - movement cost
    - zone capacities
    - connection capacities
    - blocked areas
    - simultaneous drone movement

    Each zone can only contain a limited number of drones, and each connection
    between two zones also has a maximum traffic capacity.

    The goal of the project is to move all drones from the start zone to the
    destination while minimizing congestion and total simulation turns.

    The project also includes a graphical visualization system using pyray/raylib
    to display the simulation in real time.

# Zone Types

    The simulation supports 4 different zone types:

    | Zone Type | Cost | Description |
    |---|---|---|
    | normal | 1 | Standard zone |
    | priority | 1 | Preferred path zone |
    | restricted | 2 | Requires additional turn to cross |
    | blocked | 0 | Cannot be entered |

# Graph Structure

    The project is built using a custom bidirectional graph implementation.

    A graph is a non-linear data structure composed of:
    - vertices (zones/nodes)
    - edges (connections)

    Each zone represents a node in the graph and each valid connection
    represents an edge.

    Connections are bidirectional, meaning drones can move in both directions.

# Algorithm Explanation

    The project uses a custom pathfinding approach inspired by Dijkstra's algorithm.

    Standard Dijkstra only returns a single shortest-cost path.
    That approach was insufficient for this project because multiple drones
    must move simultaneously while avoiding congestion.

    Instead of storing only one path, the algorithm:

    - explores all valid paths
    - groups paths by total cost
    - prioritizes paths containing more priority zones
    - distributes drones between paths to reduce congestion

    The implementation uses `heapq` (min heap) to efficiently explore paths.

## Heapq / Min Heap

    A min heap is a tree-based data structure where:
    - the smallest value is always at the top
    - parent nodes are always smaller than child nodes

    Operations:
    - `heappush()` → insert while preserving heap order
    - `heappop()` → remove smallest element

    Average complexity:
    - insertion → O(log n)
    - removal → O(log n)

    The algorithm complexity depends on:
    - number of zones
    - number of connections
    - number of discovered paths

    The more possible paths exist, the higher the complexity becomes.

# Drone Simulation Logic

    The simulation is turn-based.

    Each drone:
    - follows a selected path
    - waits when a zone is full
    - waits when a connection is occupied
    - spends additional turns inside restricted zones

    The simulation handles:
    - simultaneous movement
    - collision prevention
    - connection capacity
    - zone capacity
    - congestion management

    Drones are distributed across different paths whenever possible
    to minimize total turns.

# Visual Representation

    The project includes a graphical visualization using pyray/raylib.

    Visualization features:
    - zones displayed as colored nodes
    - connections displayed as edges
    - drones rendered as moving circles
    - real-time simulation display
    - turn-by-turn navigation

    The visualization improves:
    - debugging
    - readability
    - congestion analysis
    - movement tracking
    - simulation understanding

## Instructions

    Requirements:
    - Python 3.10+
    - raylib==5.5.0.4
    - flake8
    - mypy

    Install dependencies:

    pip install -r requirements.txt

    Run the project:

    make run ARG=maps/example.txt

    Controls:
    - Right arrow → next turn
    - Left arrow → previous turn

# Example
    ##start
    A 1 1 zone=normal color=red max_drones=3

    ##end
    C 5 1 zone=priority color=blue max_drones=3

    B 3 1 zone=normal color=green max_drones=2
    ## connections
    A-B
    B-C
    ## Output
    Turn 1
    D1-A
    D2-A
    D3-A

    Turn 2
    D1-B
    D2-B
    D3-A

    Turn 3
    D1-C
    D2-C
    D3-B

    Turn 4
    D3-C

# References
[text](https://docs.python.org/3/library/heapq.html)
[text](https://www.raylib.com/cheatsheet/cheatsheet.html)
[text](https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/)
[text](https://www.geeksforgeeks.org/dsa/graph-data-structure-and-algorithms/)
[text](https://www.researchgate.net/publication/336611576_Multi-Agent_Path_Finding_-_An_Overview)
[text](https://www.youtube.com/watch?v=M6cm8UeeziI&t=320s&pp=ygURZGluaWMncyBhbGdvcml0aG0%3D)
[text](https://www.youtube.com/watch?v=bZkzH5x0SKU&t=197s&pp=ygUJZGlqaWtzdHJh)
[text](https://www.youtube.com/watch?v=L9PiYPH-L_4&list=PLyhV2Ad6HvIG0ffrwyRtCmQ_h-GLuUFQ4)