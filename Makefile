# create virtual environment
PATH := .env/bin:$(PATH)

OPENAI_API_KEY := test

export

.env:
	virtualenv .env

# install all needed for development
develop: .env
	pip install -U --upgrade-strategy eager -e .[dev]

# run the tests
test:
	# stop the build if there are Python syntax errors or undefined names
	flake8 . --count --show-source --statistics
	pytest --cov=speech_splitter --cov-report=term-missing tests/

# clean the development envrironment
clean:
	-rm -rf .env

build:
	python -m build

publish:
	twine upload dist/*

# run the streamlit app
run:
	streamlit run streamlit_app.py

.PHONY: develop test clean build run
