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

## Pre-requisites

> [!WARNING]
> We have designed this project to run in a Windows OS, so if you use any other, you might have to modify the following instructions.

<details open>
<summary><h3>Install <code>Chrome</code></h3></summary>

The project uses the `Chrome` webdriver from `selenium` to extract data, so you need to install the Google Chrome browser. You can download the installer [here](https://support.google.com/chrome/answer/95346?hl=en).
</details>

<details open>
<summary><h3>Install <code>Python</code></h3></summary>

As we use the `Python` API from `selenium`, we also need to install `Python` to run the project code. You can download the installer from the official [website](https://www.python.org/downloads/).
</details>

<details>
<summary><h3>(Optional) Install <code>wsl</code></h3></summary>

Open the Windows CMD and update the WSL app running
```
wsl --update
```

Then, install the latest Ubuntu distribution
```
wsl --install -d Ubuntu-22.04
```

Next, check the installation with
```
wsl --version
```

Finally, set 2 as the default version
```
wsl --set-version Ubuntu-22.04 2
```

Check the [official documentation](https://learn.microsoft.com/en-us/windows/wsl/install) for more info. 
</details>

<details>
<summary><h3>(Optional) Install <code>docker</code></h3></summary>

The production-ready implementation of this project uses Docker, so we suggest you to install it. To do so, install [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/), and then [enable the WSL 2 backend](https://docs.docker.com/desktop/wsl/#turn-on-docker-desktop-wsl-2). 

You can check the installation by running the following from Windows CMD
```
docker ps
```

</details>

<details>
<summary><h3>(Optional) Install <code>make</code></h3></summary>

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
> To have a deeper understanding of the project, we recommend you to avoid this very-high-level command and follow the [step by step](#step-by-step)  guide.

### Step by step

Before running the Python code for the first time, one needs to setup the project by running
```bash
make setup
```
This command creates a Python virtual environment, installs the dependencies, makes the necessary folders in the project root directory, and pulls the `selenium/standalone-chrome` Docker image from [Docker Hub](https://hub.docker.com/.)

> [!TIP]
> At this point, you can test the data extraction code executing one of
> ```bash
> # default testing (with Docker backend, and without GUI)
> make tst
>
> # testing with GUI on local Chrome
> make tst-gui
> ```

Once the setup is complete, you can extract the target data by running either
```bash
# run default execution, i.e.,
# with selenium running inside a Docker container, 
# without GUI and with debug log level
make run

# run with GUI debug log level (no Docker)
make debug

# run paginating over all results in the website
# this one fails, kindly check the error log
make paginate
```

> [!NOTE]
> All run commands write a file with the results in `./data/output` unless told otherwise. Moreover, note all run commands can be resumed if anything goes wrong, as the source code stores temporary files in `./data/tmp`.

Finally, you can do a cleanup by running
```bash
# remove virtual environment
make clean

# remove virtual environment and any other
# file generated during the process
make purge
```

### Custom execution

> [!TIP]
> You can check the code help as
> ```bash
> make help
> ```

To run the project with custom arguments, we recommend you to mimic the `run` make command. For instance, to run without GUI, paginating over all results forcing the removal of temporary files even if the process fails, you would do
```bash
    # the headless option uses the Docker backend, so we need to run it beforehand
    make docker-run

    venv\Scripts\activate & python src -vv --headless --paginate --force-remove
```

### Development

For the first steps of the project development, we used Jupyter notebooks (which are located in the `./dev` folder). To run them, or to further develop the project, you can execute
```bash
make deps-dev
```
to install de development requirements, and then
```
make run-dev
```
to launch the jupyter notebook backend.

## Further improvements
In subsequent iterations of the project, we could consider the following improvements:
- Use `docker-compose.yml` to enable multiple services and remove the need for the standalone container to be up and running. We could use the [official compose file](https://github.com/SeleniumHQ/docker-selenium/blob/trunk/docker-compose-v3.yml).
- Remove rarely used `make` commands as the project progresses.
- Dig deeper into the `selenium` Docker image to enable GUI execution; that would allow us to remove Chrome as a pre-requisite and make the code browser-agnostic during the development stage.
- Make the app logging more robust by writing its logs in a file.
- Add CI/CD pipelines, e.g., GHA, to automate tests, code linting, etc.

## Flaws and (discarded) alternatives

Despite being in the project core, `selenium` has several limitations that are worth mentioning, such as:
- It may have a slow execution for complex web applications.
- Scripts using `selenium` tend to require frequent updates and maintenance, as changes in the web application can break the existing logic.
- `selenium` is deeply coupled with the underlying browser and might suffer compatibility issues. However, the webdriver manager and the Docker image mitigate this issue. 
- External factors such as network latency or inconsistent element locators can yield intermittent failures that are hard to diagnose.
- 

For the above reasons, `selenium` was not our first option. Initially, we used  `requests` and `bs4`, but they are intended for static pages and do not render the JavaScript parts of the website.

Another alternative is to use [`scrapy`](https://scrapy.org/), [`Splash`](https://splash.readthedocs.io/en/latest/index.html), and [`scrapy-splash`](https://github.com/scrapy-plugins/scrapy-splash), but the latest Splash release was three years ago, and we do not want to build a project on a tool that is no longer maintained.
