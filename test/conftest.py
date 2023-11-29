def pytest_addoption(parser):
    """
    Config function that parses the `headless` argument that we pass to
    `BootsPageScraper` during the tests setup.
    """
    parser.addoption("--headless", action = 'store_true')