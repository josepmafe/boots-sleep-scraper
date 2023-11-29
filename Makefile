### setup commands ###
# create virtual environment
venv: 
	python -m venv venv

# activate virtual environment and install dependencies
deps: 
	venv\Scripts\activate & pip install -r requirements.txt

# activate virtual environment and install development dependencies
deps-dev: 
	venv\Scripts\activate & pip install -r requirements-dev.txt

# create the necessary directories for the code to run
dir:
	python -c "import os; os.makedirs('./data/output', exist_ok = True)"
	python -c "import os; os.makedirs('./log', exist_ok = True)"

# pull selenium docker image
pull:
	docker pull selenium/standalone-chrome

# create virtual env and install dependencies
setup: venv deps dir pull

### run commands ###
# activate virtual environment and run scraper in debug mode,
# i.e., with GUI and debug log level
debug:
	venv\Scripts\activate & python src -vv

# run selenium/standalone-chrome image as container named selenium
docker-run:
	docker run -d -p 4444:4444 -v /dev/shm:/dev/shm --rm --name selenium selenium/standalone-chrome

# activate virtual environment and run in headless mode, i.e.,
# with the selenium in a docker container and info log level
headless:
	venv\Scripts\activate & python src --headless -v

# default run mode
run: docker-run headless stop

# activate virtual environment and run scraper paginating
# NOTE: this fails, kindly check error
paginate:
	venv\Scripts\activate & python src --paginate

### test commands ###
# run tests
tst-gui:
	venv\Scripts\activate & pytest test/

# run tests in headless mode
tst-h:
	venv\Scripts\activate & pytest test/ --headless

# run tests in headless mode (auto-handling docker commands)
tst: docker-run tst-h stop

### dev commands ###
# show help
help:
	venv\Scripts\activate & python src --help

# run jupyter notebook backend
run-dev:
	venv\Scripts\activate & jupyter notebook

### cleanup commands ###
# stop selenium docker container
stop:
	-docker stop selenium

# remove virtual environment folder, as a minimum sanitazing task
clean:
	-python -c "import shutil; shutil.rmtree('./venv')"

# remove all extra files and folders potentially created
purge: clean
	-python -c "import shutil; shutil.rmtree('./data')"
	-python -c "import shutil; shutil.rmtree('./log')"

### high-level commands ###
# run full pipeline (not removing data nor logs)
all: setup run stop clean

# run full pipeline (remove all files)
all-rm: setup run stop purge