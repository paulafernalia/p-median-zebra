# p-median problem with column generation

This project provides a solution approach to solve the p-median problem, a classical facility location problem where the goal is to select p locations from a set of nodes to minimise the total distance between customers and the facilities they are assigned to. The problem is formulated as an integer program using a radius formulation, and it is solved using a heuristic based on the column-generation method from Garcia et al. (2010). Both the LPs in the column-generation algorithm and the MIP solved with the generated variables are solved with [HiGHS](https://highs.dev/), using their Python API, `highspy`.

This is a Python project that uses [`uv`](https://github.com/astral-sh/uv), a fast Python package manager and workflow tool to manage dependencies, virtual environments, and more.

## Requirements

- Python 3.13+
- [`uv`](https://github.com/astral-sh/uv) (instead of `pip` or `poetry`)

If you don't have `uv` installed, you can follow the intructions in the uv [documentation](https://docs.astral.sh/uv/getting-started/installation/). Make sure `uv` is on your `PATH`. 

## Installation

```
# Clone the repository
git clone https://github.com/paulafernalia/p-median-zebra.git
cd p-median-zebra

# Install as an editable package (required to run examples)
uv pip install -e .
```

## Usage

This project uses a `Makefile` to simplify running the most used commands. To open the example in `notebooks/` run
```
make example
```

To run unit tests, autoformat code and more, check the `Makefile`.

## References
Garcia, J. A., Orozco, J. M., & Pérez, M. A. (2010). A Column-Generation Approach for the P-Median Problem. INFORMS Journal on Computing, 22(2), 177-190. doi:10.1287/ijoc.1100.0418
