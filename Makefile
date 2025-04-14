run:
	uv run src/p_median_zebra/opt.py

typecheck:
	uv tool run mypy --ignore-missing-imports --follow-imports=skip --strict-optional . 

autoformat:
	uv tool run black .

example:
	uv run marimo edit notebooks/example.py