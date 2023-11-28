# `Boots - Sleep` scraper

This repo contains the Boots - Sleep scraper code, which we use to extract data from the [Boots - Sleep](https://www.boots.com/health-pharmacy/medicines-treatments/sleep) page. The top-level repo structure is the following:
```
.
├── dev                     # Development code (Jupyter notebooks)
├── src                     # Source code
├── test                    # Tests               
├── .gitignore 
├── Makefile                # `make` commands
├── pytest.ini              # `pytest` configuration file
├── readme.md                  
├── requirements.txt        # Python dependencies
└── requirements-dev.txt    # Pyhton development dependencies
```
> [!WARNING]
> We have designed this project to run in a Windows OS, so if you use any other, you might have to modify the following instructions.

## Pre-requisites

> [!NOTE]
> If it's your first time using this project, consider checking this section before executing it. Otherwise, you can jump to the next one.
</summary>

<details open>
<summary><h3>Install <code>Chrome</code></h4></summary>

The project uses the `Chrome` webdriver from `selenium` to extract data, so you need to install the Google Chrome browser. You can download the installer [here](https://support.google.com/chrome/answer/95346?hl=en).
</details>

<details open>
<summary><h3>Install <code>Python</code></h4></summary>

As we use the `Python` API from `selenium`, we also need to install `Python` to run the project code. You can download the installer from the official [website](https://www.python.org/downloads/).
</details>

<details>
<summary><h3>(Optional) Install <code>make</code></h4></summary>

The instructions provided to run this project use `make`, so we recommend you to also install it. To do so in Windows, you need to [install choco](https://chocolatey.org/install), and use `choco` to [install make](https://community.chocolatey.org/packages/make).

Then, you can test `make` running
```
make --version
```
</details>

</details>

## Usage

### TL;DR
The easiest way to run the project is to execute
```bash
make all
```
which takes care of all steps in the project pipeline, i.e., setup, default execution and cleanup

> [!TIP]
> To have a deeper understanding of the project, we recommend you to avoid this very-high-level command and keep reading.

### Step by step
Before running the Python code for the first time, one needs to setup the project by running
```bash
make setup
```
This command creates a Python virtual environment, installs the dependencies and makes the necessary folders in the project root directory.

> [!TIP]
> Before running the data extraction code, and after the setup, you can test it executing
> ```bash
> make testing
> ```

Once the setup is complete, you can extract the target data by running either
```bash
# run with default options
make run

# run headlessly, i.e., without driver GUI
make headless

# run paginating over all results in the website
# this one fails, kindly check the error log
make paginate

# run with debug log level
make debug
```

> [!NOTE]
> All run commands write a file with the results in `./data/output` unless told otherwise. Moreover, note all run commands can be resumed if anything goes wrong, as the source code stores temporary files, so the process does not have start from scratch.

Finally, you can do a cleanup by running
```bash
# remove virtual environment folder
make tidy

# remove virtual environment folder and any other
# file generated during the process
make clean
```

### Custom execution

> [!TIP]
> You can check the code help as
> ```bash
> make help
> ```

To run the project with custom arguments, we recommend you to mimic the `run` make command. For instance, to run without GUI, paginating over all results forcing the removal of temporary files even if the process fails, you would do
```bash
    venv\Scripts\activate & python src -vv --headless --paginate --force-remove
```

### Development

For the first steps of the project development, we used Jupyter notebooks (which are located in the `./dev` folder). To run them, or to further develop the project, you can execute
```bash
make dev-deps
```
to install de development requirements, and then
```
make dev
```
to launch the jupyter notebook backend.

## Flaws and alternatives

Despite being in the project core, `selenium` has several limitations that are worth mentioning, such as:
- It may have a slow execution for complex web applications.
- Scripts using `selenium` tend to require frequent updates and maintenance, as changes in the web application can break the existing logic.
- Even if the webdriver manager mitigates it, `selenium` is deeply coupled with the underlying browser and might suffer compatibility issues.
- External factors such as network latency or inconsistent element locators can yield intermitent failures that are hard to diagnose.

For the above reasons, `selenium` was not our first option. Initially, we used  `requests` and `bs4`, but they are intended for static pages and do not render the JavaScript parts of the website.

Another alternative is to use [`scrapy`](https://scrapy.org/), [`Splash`](https://splash.readthedocs.io/en/latest/index.html) and [`scrapy-splash`](https://github.com/scrapy-plugins/scrapy-splash), but the latest Splash release was 3 years ago, and we do not want to build a project on a tool that is no longer maintained.

> [!NOTE]
> Despite Splash not being actively maintained, this latest alternative represents an appealing alternative to selenium. Check the how-to [here](https://scrapeops.io/python-scrapy-playbook/scrapy-splash/).
