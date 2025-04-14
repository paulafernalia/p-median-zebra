import random
from scipy.spatial.distance import cityblock
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple


def generate_all_edges(G: nx.Graph) -> None:
    # Calculate Manhattan distances between node pairs
    distances = {
        (i, j): int(cityblock(G.nodes[i]["pos"], G.nodes[j]["pos"]))
        for i, j in combinations(G.nodes, 2)
    }

    # Add edges with distances
    for (i, j), dist in distances.items():
        G.add_edge(i, j, d=dist)


def create_graph(nnodes: int, mapsize: int, seed: int = 42) -> nx.Graph:
    """
    Generates a random 2D network graph with nodes, edges, and Manhattan distance weights.

    Parameters:
        pars (config.ModelParameters): A configuration object containing parameters such as
            the number of nodes (NNODES), map size (MAPSIZE), and maximum demand (MAXDEMAND).
        seed (int, optional): The random seed for reproducibility. Must be greater than or
            equal to 10. Default is 42.

    Returns:
        nx.Graph: A NetworkX graph where:
            - Nodes have attributes 'pos' (coordinates) and 'q' (demand).
            - Edges have an attribute 'd' representing the Manhattan distance between nodes.

    Raises:
        ValueError: If the provided seed is less than 10.
    """

    if seed < 10:
        raise ValueError("seed must be greater than or equal to 10")

    random.seed(seed)
    nodes = list(range(nnodes))

    # Generate random coordinates for each node
    coords = [(random.randint(0, mapsize), random.randint(0, mapsize)) for _ in nodes]

    G: nx.Graph = nx.Graph()

    # Add nodes with attributes
    for i in nodes:
        G.add_node(i, pos=coords[i])

    generate_all_edges(G)

    return G


def get_allocation_dict(depots: List[int], G: nx.Graph) -> Dict[int, int]:
    """
    Assigns each node in the graph to the closest depot based on edge distance.

    Parameters:
    - depots (List[int]): A list of depot node indices.
    - G (nx.Graph): A NetworkX graph where each edge has a 'd' attribute representing distance.

    Returns:
    - Dict[int, int]: A dictionary mapping each node to the depot it is allocated to.
                      If a node is a depot, it maps to itself.
    """

    def closest_depot(depots: List[int], i: int) -> int:
        return min(depots, key=lambda j: G.get_edge_data(i, j)["d"])

    return {i: i if i in depots else closest_depot(depots, i) for i in G.nodes}


def plot_solution(G: nx.Graph, allocation: Dict[int, int]) -> None:
    """
    Visualizes the allocation of nodes to depots by drawing the graph with edges from
    each node to its assigned depot in a unique color per depot.

    Parameters:
    - G (nx.Graph): A NetworkX graph where nodes have a 'pos' attribute for layout.
    - allocation (Dict[int, int]): A dictionary mapping each node to its assigned depot.

    Returns:
    - None
    """
    pos = nx.get_node_attributes(G, "pos")

    # Draw all nodes
    nx.draw_networkx_nodes(G, pos, node_size=10)

    # Group edges by depot
    edges_by_depot: Dict[int, List[Tuple[int, int]]] = {}
    for node, depot in allocation.items():
        if node == depot:
            continue  # skip self-edges
        edges_by_depot.setdefault(depot, []).append((node, depot))

    # Assign a random color to each depot
    colors = {
        depot: (random.random(), random.random(), random.random())
        for depot in edges_by_depot
    }

    # Draw edges connecting each node to its depot
    for depot, edges in edges_by_depot.items():
        nx.draw_networkx_edges(
            G, pos, edgelist=edges, edge_color=[colors[depot]], width=2
        )

    plt.title("Allocation")
    plt.axis("off")
    plt.show()
