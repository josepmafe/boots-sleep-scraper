# create virtual environment
venv: 
	python -m venv venv

# activate virtual environment and install dependencies
deps: 
	venv\Scripts\activate & pip install -r requirements.txt

# create the necessary directories for the code to run
dir:
	python -c "import os; os.makedirs('./data/output', exist_ok = True)"
	python -c "import os; os.makedirs('./log', exist_ok = True)"

# create virtual env and install dependencies
setup: venv deps dir

# show help
help:
	venv\Scripts\activate & python src --help

# activate virtual environment and run scraper
run:
	venv\Scripts\activate & python src

# activate virtual environment and run scraper headless
# (and with info log level)
headless:
	venv\Scripts\activate & python src --headless -v

# activate virtual environment and run scraper paginating
# NOTE: this fails, kindly check error
paginate:
	venv\Scripts\activate & python src --paginate

# activate virtual environment and run scraper with debug verbosity
debug:
	venv\Scripts\activate & python src -vv

# run tests
testing:
	venv\Scripts\activate & pytest test/

# remove virtual environment folder, as a minimum sanitazing task
tidy:
	python -c "import shutil; shutil.rmtree('./venv')"

# remove all extra files and folders potentially created
clean: tidy
	python -c "import shutil; shutil.rmtree('./data')"
	python -c "import shutil; shutil.rmtree('./log')"

# run full pipeline (not removing data nor logs)
all: setup run tidy