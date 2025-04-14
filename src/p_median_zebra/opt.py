import highspy
import numpy as np
import graph
import config
import networkx as nx
from typing import Dict, List


def compute_sorted_dist(G: nx.Graph) -> Dict[int, np.ndarray]:
    """
    Compute the sorted unique distances from each node to all other nodes in the graph.

    Parameters:
        G (nx.Graph): The input graph with edge attribute 'd' for distance.

    Returns:
        dict: A dictionary mapping each node to a sorted array of unique distances.
    """

    dists = np.zeros((nnodes, nnodes))
    for i, j, d in G.edges(data="d"):
        dists[i, j] = d
        dists[j, i] = d

    return {i: np.unique(dists[i, :]) for i in G.nodes}

def add_z_variables(
    h: highspy.Highs,
    G: nx.Graph,
    dsorted: Dict[int, np.ndarray]
) -> Dict[int, List[int]]:
    """
    Add continuous z variables to the HiGHS model.

    Each z[i][k] variable represents whether node i is within distance threshold k.

    Parameters:
        h (highspy.Highs): HiGHS optimization model.
        G (nx.Graph): The graph.
        dsorted (dict): Sorted distance thresholds per node.

    Returns:
        dict: A nested dictionary of z variables for each node and distance index.
    """

    # Generate variable names like "z0.0", "x0.1", ..., "zn.k"
    var_names = [
        f"z{i}.{j}" for i in range(nnodes) for j in range(nnodes)
    ]

    # Create z variables
    return {
        i: h.addVariables(
            len(ds),
            obj=np.diff(np.insert(ds, 0, 0)).tolist(),
            name=[f"z{i}.{k}" for k in range(len(ds))],
        )
        for i, ds in dsorted.items()
    }

def add_y_variables(
    h: highspy.Highs,
    G: nx.Graph
) -> List[int]:
    """
    Add binary y variables to the HiGHS model to indicate whether a node is chosen as a depot.

    Parameters:
        h (highspy.Highs): HiGHS optimization model.
        G (nx.Graph): The graph.

    Returns:
        list: A list of binary variables y[i] for each node i.
    """
    return h.addBinaries(nnodes, name=[f"y{i}" for i in G.nodes])


def add_p_median_constraint(
    h: highspy.Highs,
    G: nx.Graph,
    p: int,
    y: List[int]
) -> None:
    """
    Add a constraint ensuring exactly p depots are selected.

    Parameters:
        h (highspy.Highs): HiGHS optimization model.
        G (nx.Graph): The graph.
        p (int): Number of depots to select.
        y (list): Binary depot indicator variables.
    """
    h.addConstrs(h.qsum(y[i] for i in G.nodes) == p)
    

def add_z_y_def_constraints(
    h: highspy.Highs,
    G: nx.Graph,
    dsorted: Dict[int, np.ndarray],
    y: List[int],
    z: Dict[int, List[int]]
) -> None:
    """
    Adds constraints linking z and y variables to ensure each node is assigned to a nearby depot.

    Parameters:
        h (highspy.Highs): The HiGHS model instance.
        G (nx.Graph): The graph representing the problem.
        dsorted (dict): Sorted distance values for each node.
        y (list): List of binary variables indicating depot selection.
        z (dict): Dictionary of z variables grouped by node.
    """
    def get_dist(i, j):
        if i == j:
            return 0
        return G.get_edge_data(i, j)['d']

    for i in G.nodes:
        h.addConstrs(
            z[i][k] + h.qsum(y[j] for j in G.nodes if get_dist(i, j) < d) >= 1
            for k, d in enumerate(dsorted[i][1:], start=1)
        )


def get_optimal_depots(
    h: highspy.Highs,
    y: List[int]
) -> List[int]:
    """
    Retrieves the indices of nodes chosen as depots in the solution.

    Parameters:
        h (highspy.Highs): The HiGHS model instance after optimization.
        y (list): List of binary variables indicating depot selection.

    Returns:
        list: Indices of nodes that are selected as depots.
    """
    return [i for i, y in enumerate(h.vals(y)) if y > 1e-2]


def solve_p_median(G: nx.Graph, p: int):
    """
    Solves the p-median problem on the given graph using the HiGHS solver.

    Parameters:
        G (nx.Graph): The input graph with edge attribute 'd' for distances.
        p (int): The number of depots to be selected.

    Returns:
        list: Indices of nodes selected as depots in the optimal solution.
    """
    h = highspy.Highs()

    # Create vector of Dik
    dsorted = compute_sorted_dist(G)

    # Create model variables
    z = add_z_variables(h, G, dsorted)
    y = add_y_variables(h, G)

    # Create constraints
    add_p_median_constraint(h, G, p, y)
    add_z_y_def_constraints(h, G, dsorted, y, z)

    # Optimise
    h.run()

    # Get depots in solution
    depots = get_optimal_depots(h, y)

    return depots


nnodes = 100
mapsize = 100
ndepots = 5

# Create graph
G = graph.create_graph(nnodes, mapsize)

# Solve problem and get optimal list of depots
depots = solve_p_median(G, ndepots)

# Plot solution
allocation = graph.get_allocation_dict(depots, G)
graph.plot_solution(G, allocation)
