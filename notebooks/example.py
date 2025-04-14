import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Solving a random p-median instance

        This notebook creates an instance randomly given a **number of nodes** and a **number of depots** and solves the p-median problem with a radius formulation using two different methodologies:

        - Solving the p-median problem as a MIP*
        - Using the Zebra algorithm to solve the LP relaxation*, then solving a MIP* with the variables generated

        *The MIPs and LPs are solved using highspy
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""## Solving p-median problem as a MIP""")
    return


@app.cell
def _():
    import sys
    import os
    import importlib
    import marimo as mo

    from p_median_zebra import graph, config, solver

    importlib.reload(graph)
    importlib.reload(config)
    importlib.reload(solver)
    return config, graph, importlib, mo, os, solver, sys


@app.cell
def _(config, graph, solver):
    # Create an instance with 100 random nodes spread randomly and 5 depots to be allocated (p = 5)
    pars = config.ModelParameters(MAPSIZE=500, NDEPOTS=5, NNODES=100)

    # Create NetworkX graph
    G = graph.create_graph(pars.NNODES, pars.MAPSIZE)

    # Solve p-median problem as a MIP using a radius formulation and get optimal list of depots
    depots_mip = solver.solve_p_median_mip(G, pars.NDEPOTS)

    # Plot solution
    allocation_mip = graph.get_allocation_dict(depots_mip, G)
    graph.plot_solution(G, allocation_mip)
    return G, allocation_mip, depots_mip, pars


@app.cell(hide_code=True)
def _():
    ## Solve using Zebra
    return


@app.cell
def _(G, graph, pars, solver):
    # Solve p-median problem using the zebra algorithm and get optimal list of depots
    depots_zebra = solver.solve_p_median_zebra(G, pars.NDEPOTS, 2)

    # Plot solution
    allocation_zebra = graph.get_allocation_dict(depots_zebra, G)
    graph.plot_solution(G, allocation_zebra)
    return allocation_zebra, depots_zebra


if __name__ == "__main__":
    app.run()
