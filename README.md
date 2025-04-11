# p-median problem with column generation

This is a Python project that uses [`uv`](https://github.com/astral-sh/uv), a fast Python package manager and workflow tool to manage dependencies, virtual environments, and more.

## Requirements

- Python 3.13+
- [`uv`](https://github.com/astral-sh/uv) (instead of `pip` or `poetry`)

If you don't have `uv` installed, you can follow the intructions in the uv [documentation](https://docs.astral.sh/uv/getting-started/installation/). Make sure `uv` is on your `PATH`. 

## Usage

This project uses a `Makefile` to simplify running the most used commands.

To run the code go to `src/p_median_zebra` and run:
```
make run
```

To autoformat the code with black run
```
make autoformat
```

To execute typechecking run
```
make typecheck