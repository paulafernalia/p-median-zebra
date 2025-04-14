import pytest
import networkx as nx
from typing import Dict, Tuple, List, Optional
from p_median_zebra import solver
from p_median_zebra import graph

test_cases = [
    {"name": "single_node", "nodes": {0: (0, 0)}, "p": 1, "expected_depots": [0]},
    {
        "name": "line_graph_middle",
        "nodes": {0: (0, 0), 1: (1, 0), 2: (2, 0)},
        "p": 1,
        "expected_depots": [1],
    },
    {
        "name": "star_graph_center",
        "nodes": {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (-1, 0), 4: (0, -1)},
        "edges": [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1)],
        "p": 1,
        "expected_depots": [0],
    },
    {
        "name": "two_clusters",
        "nodes": {0: (0, 0), 1: (1, 0), 2: (0, 1), 3: (10, 0), 4: (11, 0), 5: (10, 1)},
        "edges": [
            (0, 1, 1),
            (1, 2, 1),
            (2, 0, 1),
            (3, 4, 1),
            (4, 5, 1),
            (5, 3, 1),
            (0, 3, 10),
        ],
        "p": 2,
        "expected_depots": [0, 3],
    },
]


@pytest.mark.parametrize("case", test_cases, ids=[case["name"] for case in test_cases])
def test_p_median(case):
    G = nx.Graph()

    for node_id, pos in case["nodes"].items():
        G.add_node(node_id, pos=pos)

    graph.generate_all_edges(G)

    depots = solver.solve_p_median(G, case["p"])

    assert depots == case["expected_depots"]
