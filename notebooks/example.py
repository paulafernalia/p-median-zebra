import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    import os
    import marimo as mo

    from p_median_zebra import graph, config, solver
    return config, graph, mo, os, solver, sys


@app.cell
def _(config, graph, solver):
    pars = config.ModelParameters(MAPSIZE=100, NDEPOTS=5, NNODES=100)


    # Create graph
    G = graph.create_graph(pars.NNODES, pars.MAPSIZE)

    # Solve problem and get optimal list of depots
    depots = solver.solve_p_median(G, pars.NDEPOTS)

    # Plot solution
    allocation = graph.get_allocation_dict(depots, G)
    graph.plot_solution(G, allocation)
    return G, allocation, depots, pars


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
