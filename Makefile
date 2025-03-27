run:
	@uvicorn app.main:app --reload

check:
	@ruff check app

format:
	@ruff format app
