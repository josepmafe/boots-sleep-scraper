import pytest

import re
import json
from _scraper import BootsPageScraper


EXPECTED_PAGE_TITLE = 'Sleep Aid Tablets | Sleep Products | Boots'

PAGING_SIZE_PATTERN = r'paging\.size=(\d+)'
EXPECTED_PRODUCT_COUNT = 96 # this is just a fail-safe in case the regex match does not work

@pytest.fixture(scope = 'class', autouse = True)
def headless(pytestconfig):
    """
    Sets the `headless` value for TestBootsPageScraper,
    which comes from user input
    """
    TestBootsPageScraper.headless = pytestconfig.getoption('headless')

class TestBootsPageScraper:
    """Class that contains the tests for the `BootsPageScraper`"""
    @classmethod
    def setup_class(cls):
        cls.scraper = BootsPageScraper(
            headless = cls.headless,
            auto_accept_cookies = False
        )
        cls.driver = cls.scraper.driver

    def test_page_title(self):
        """Check the expected page title"""
        assert self.driver.title == EXPECTED_PAGE_TITLE

    def test_accept_cookies(self):
        """Check the `accept_cookies` method"""
        assert self.scraper.accept_cookies() is None

    def test_list_products(self):
        """Check the `list_products` method"""
        current_url = self.driver.current_url
        match = re.search(PAGING_SIZE_PATTERN, current_url)
        if match:
            expected_product_count = int(match.groups()[-1])
        else:
            expected_product_count = EXPECTED_PRODUCT_COUNT
        
        # check the number of products found
        products = self.scraper.find_products()
        assert len(products) == expected_product_count

        # check all products have name and href
        assert all(product.name for product in products)
        assert all(product.href for product in products)
    
    def test_parse_product(self):
        """Check an arbitrary product is correctly parsed"""
        product = self.scraper.find_products()[0]
        product_data = self.scraper._parse_product(product)

        # check product is parsed as a `dict`
        assert isinstance(product_data, dict)

        # check attributes are not None (NaN is fine for rating)
        assert all(value is not None for value in product_data.values())

        # check product name in main page and product page
        assert product.name == product_data['Title']

        # assert parsed product is JSON-serializable and JSON-deserializable
        assert product_data == json.loads(json.dumps(product_data))
