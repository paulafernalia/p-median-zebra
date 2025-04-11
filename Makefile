run:
	uv run main.py

typecheck:
	uv tool run mypy --ignore-missing-imports --follow-imports=skip --strict-optional . 

autoformat:
	uv tool run black .