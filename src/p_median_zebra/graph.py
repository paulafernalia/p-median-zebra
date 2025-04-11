from p_median_zebra import config
import random
from scipy.spatial.distance import cityblock
from itertools import combinations
import networkx as nx


def create_graph(pars: config.ModelParameters, seed: int = 42) -> nx.Graph:
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
    nodes = list(range(pars.NNODES))

    # Generate random coordinates for each node
    coords = [
        (random.randint(0, pars.MAPSIZE), random.randint(0, pars.MAPSIZE))
        for _ in nodes
    ]

    # Calculate Manhattan distances between node pairs
    distances = {
        (i, j): int(cityblock(coords[i], coords[j])) for i, j in combinations(nodes, 2)
    }

    G: nx.Graph = nx.Graph()

    # Add nodes with attributes
    for i in nodes:
        G.add_node(i, pos=coords[i])

    # Add edges with distances
    for (i, j), dist in distances.items():
        G.add_edge(i, j, d=dist)

    return G
