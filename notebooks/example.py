import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    import os
    import marimo as mo

    from p_median_zebra import graph, config
    return config, graph, mo, os, sys


@app.cell
def _(config, graph):
    params = {
        "NNODES": 15,
        "MAPSIZE": 100,
        "NDEPOTS": 3,
    }

    model_params = config.ModelParameters(**params)

    G = graph.create_graph(model_params)
    return G, model_params, params


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
