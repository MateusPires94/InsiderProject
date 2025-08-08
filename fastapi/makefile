.PHONY: install run test 

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ --disable-warnings