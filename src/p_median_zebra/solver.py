import time
from typing import Dict, List
from collections import defaultdict

import numpy as np
import networkx as nx
import highspy

from p_median_zebra import graph
from p_median_zebra import config


def compute_sorted_dist(G: nx.Graph) -> Dict[int, np.ndarray]:
    """
    Compute the sorted unique distances from each node to all other nodes in the graph.

    Parameters:
        G (nx.Graph): The input graph with edge attribute 'd' for distance.

    Returns:
        dict: A dictionary mapping each node to a sorted array of unique distances.
    """
    n = len(G.nodes)

    dists = np.zeros((n, n))
    for i, j, d in G.edges(data="d"):
        dists[i, j] = d
        dists[j, i] = d

    return {i: np.unique(dists[i, :]) for i in G.nodes}


def add_z_variables(
    h: highspy.Highs, G: nx.Graph, dsorted: Dict[int, np.ndarray], maxk: int
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
    n = len(G.nodes)

    if maxk >= len(G.nodes) or maxk < 0:
        raise ValueError("maxk must be in [0, G.nodes)")

    # Create z variables
    z = defaultdict(lambda: defaultdict(object))
    for i, ds in dsorted.items():
        numz = min(maxk + 1, len(ds))
        deltas = np.diff(np.insert(ds, 0, 0))[:numz].tolist()

        for k in range(1, numz):
            z[i][k] = h.addVariable(
                lb=0,
                ub=1,
                obj=deltas[k],
                name=f"z{i}.{k}",
            )

    return z


def add_y_variables(h: highspy.Highs, G: nx.Graph) -> List[int]:
    """
    Add binary y variables to the HiGHS model to indicate whether a node is chosen as a depot.

    Parameters:
        h (highspy.Highs): HiGHS optimization model.
        G (nx.Graph): The graph.

    Returns:
        list: A list of binary variables y[i] for each node i.
    """
    return h.addBinaries(len(G.nodes), name=[f"y{i}" for i in G.nodes])


def add_p_median_constraint(
    h: highspy.Highs, G: nx.Graph, p: int, y: List[int]
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


def get_dist(G: nx.Graph, i: int, j: int) -> int:
    if i == j:
        return 0
    return G.get_edge_data(i, j)["d"]


def add_z_y_def_constraints(
    h: highspy.Highs,
    G: nx.Graph,
    dsorted: Dict[int, np.ndarray],
    y: List[int],
    z: Dict[int, List[int]],
    maxk: int,
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
    if maxk >= len(G.nodes) or maxk < 0:
        raise ValueError("maxk must be in [0, G.nodes)")

    for i in G.nodes:
        last = min(maxk + 1, len(dsorted[i]))
        h.addConstrs(
            create_z_y_def_linexpr(h, G, y, z, i, k, d) >= 1
            for k, d in enumerate(dsorted[i][1:last], start=1)
        )

def create_z_y_def_linexpr(
    h: highspy.Highs,
    G: nx.Graph,
    y: List[int],
    z: Dict[int, List[int]],
    i: int,
    k: int,
    dik: int,
) -> None:
    return z[i][k] + h.qsum(y[j] for j in G.nodes if get_dist(G, i, j) < dik)


def get_optimal_depots(h: highspy.Highs, y: List[int]) -> List[int]:
    """
    Retrieves the indices of nodes chosen as depots in the solution.

    Parameters:
        h (highspy.Highs): The HiGHS model instance after optimization.
        y (list): List of binary variables indicating depot selection.

    Returns:
        list: Indices of nodes that are selected as depots.
    """
    return [i for i, y in enumerate(h.vals(y)) if y > 1e-2]


def create_p_median_model(
    h: highspy.Highs,
    G: nx.Graph,
    dsorted: Dict[int, np.ndarray],
    p: int,
    maxk: int = -1,
):
    if maxk >= len(G.nodes) or maxk < 0:
        raise ValueError("maxk must be in [0, G.nodes)")

    # Create model variables
    z = add_z_variables(h, G, dsorted, maxk)
    y = add_y_variables(h, G)

    # Create constraints
    add_p_median_constraint(h, G, p, y)
    add_z_y_def_constraints(h, G, dsorted, y, z, maxk)

    return y, z


def solve_p_median_mip(G: nx.Graph, p: int) -> List[int]:
    """
    Solves the p-median problem on the given graph using the HiGHS solver.

    Parameters:
        G (nx.Graph): The input graph with edge attribute 'd' for distances.
        p (int): The number of depots to be selected.

    Returns:
        list: Indices of nodes selected as depots in the optimal solution.
    """
    start = time.time()

    h = highspy.Highs()
    h.silent()

    # Create vector of Dik
    dsorted = compute_sorted_dist(G)

    y, z = create_p_median_model(h, G, dsorted, p, len(G.nodes) - 1)

    # Optimise
    h.run()

    # Get depots in solution
    depots = get_optimal_depots(h, y)

    print(f"Problem solved in {time.time() - start:.2f} seconds")

    return depots


def solve_p_median_zebra(G: nx.Graph, p: int, maxk: int = -1) -> List[int]:
    """
    Solves the p-median problem on the given graph using the zebra algorithm.

    Parameters:
        G (nx.Graph): The input graph with edge attribute 'd' for distances.
        p (int): The number of depots to be selected.

    Returns:
        list: Indices of nodes selected as depots in the optimal solution.
    """
    start = time.time()

    if maxk == -1:
        maxk = len(G.nodes) - 1

    if maxk >= len(G.nodes):
        raise ValueError("maxk must be <= G.nodes")

    # Initialise highs model
    h = highspy.Highs()
    h.silent()

    # Create vector of Dik
    dsorted = compute_sorted_dist(G)

    # Create model
    y, z = create_p_median_model(h, G, dsorted, p, maxk)

    # Relax y variables
    for var in y:
        h.setContinuous(var)

    # Initialise dictionary with largest k per node
    kdict = {i: maxk for i in G.nodes}

    for iter_ in range(100):
        # Optimise
        h.run()

        # Get nodes that need new variables and constraints
        newk = [i for i in G.nodes if h.vals(z[i][kdict[i]]) > 1e-6]

        if len(newk) == 0:
            break

        for i in newk:
            k = kdict[i] + 1

            assert k < len(dsorted[i])

            z[i][k] = h.addVariable(
                lb=0,
                ub=1,
                obj=dsorted[i][k] - dsorted[i][k - 1],
                name=f"z{i}.{k}",
            )

            kdict[i] += 1

        # Add constraints
        h.addConstrs(
            create_z_y_def_linexpr(h, G, y, z, i, kdict[i], dsorted[i][kdict[i]]) >= 1
            for i in newk
        )

    print(f"{iter_} iterations required to solve the LP")

    # Add constraints
    h.addConstrs(
        create_z_y_def_linexpr(h, G, y, z, i, kdict[i] + 1, dsorted[i][kdict[i]] + 1) >= 1
        for i in newk
    )

    # Relax y variables
    for var in y:
        h.setInteger(var)

    # Optimise
    h.run()

    # Get depots in solution
    depots = get_optimal_depots(h, y)

    print(f"Problem solved in {time.time() - start:.2f} seconds")

    return depots
