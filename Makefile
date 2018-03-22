VENV_PATH=./venv
PROJECT_PATH = ./

# Utils commands
.PHONY: freeze test

freeze:
	pip freeze > requirements.txt

test:
	python3 -m unittest discover