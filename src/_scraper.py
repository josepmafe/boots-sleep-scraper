  
import logging
import os
import sys
import json
import re
from pandas import to_numeric

from selenium.webdriver import Chrome, ChromeOptions, ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from typing import Callable

from _product import Product
from _decorator import retry


RETRY = retry(exceptions = (NoSuchElementException, TimeoutException), backoff = 2)

URL = 'https://www.boots.com/health-pharmacy/medicines-treatments/sleep'

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_PATH = os.path.join(ROOT_DIR, 'data')
LOG_PATH = os.path.join(ROOT_DIR, 'log')
OUTPUT_PATH = os.path.join(DATA_PATH, 'output')
TMP_DATA_PATH = os.path.join(DATA_PATH, 'tmp')

OUTPUT_FILE = 'sleep_products.json'
OUTPUT_FP = os.path.join(OUTPUT_PATH, OUTPUT_FILE)

FAILED_PRODUCTS_LOG_FILE = 'failed_products_{time}.txt'
FAILED_PRODUCTS_LOG_FP = os.path.join(LOG_PATH, FAILED_PRODUCTS_LOG_FILE)

ACCEPT_COOKIES_BUTTON_ID = 'onetrust-pc-btn-handler'
ACCEPT_RECOMMENDED_COOKIES_BUTTON_ID = 'accept-recommended-btn-handler'

PRODUCT_ELEMENT_CLASS_NAME = 'oct-teaser__title-link'

PRODUCT_TITLE_ID = 'estore_product_title'
PRODUCT_RATING_CLASS_NAME = 'bv_avgRating_component_container'
PRODUCT_TEXT_CLASS_NAME = 'product_text'
PRODUCT_PRICE_STR_CLASS_NAME = 'price'

PRICE_STR_PATTERN = re.compile(r'(\D)(\d+\.\d{2})')


logger = logging.getLogger(__name__)

class ScrapingException(Exception):
    """Custom exception raised when the product parsing process fails"""

class ChromeDriverWrapper:
    """Convenience wrapper around the selenium `ChromeDriver` web driver"""
    def __init__(self, driver_path: str = None, headless: bool = False):
        """
        Parameters
        ----------
        driver_path: str, optional
            Path to the webdriver executable
        headless: bool, optional
            Whether to run headless, i.e., without GUI.
        """
        self.driver = self._init_driver(driver_path, headless)
    
    def _init_driver(self, driver_path, headless):
        """Instantiate the Chrome WebDriver with the given options"""
        service = ChromeService(executable_path = driver_path)

        options = ChromeOptions()
        
        # silence DevTools log msg
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        if headless:
            options.add_argument('--headless')
            options.add_argument('--log-level=3')

        return Chrome(service = service, options = options)
    
    def _wait_until(self, condition: Callable, *, timeout: int | float = 10):
        """
        Convenience method that wraps `WebDriverWait` for the WebDriver to wait
        until the condition `condition` is fulfilled
        
        Parameters
        ----------
        condition: function
            a function to be by the WebDriver. either
                - a lambda function, e.g.,
                        self._wait_until(lambda x: x.find_elements(by, value))
                - or one of selenium.webdriver.support.expected_conditions, e.g.,
                        self._wait_until(expected_conditions.element_to_be_clickable((by, value))
        timeout: int or float
            time to wait before raising TimeoutException, in seconds
        
        Returns
        -------
        WebElement | list[WebElements]
            WebElement, or list of WebElements, if condition is fulfilled.

            Note that this may also return None if a function that returns None 
            is given as condition, or even a boolean if the condition passed is
            a boolean, which is not recommended
        
        Raises
        ------
        TimeoutException, if condition is not True before `timeout` seconds
        """
        return WebDriverWait(self.driver, timeout).until(condition)

    def _wait_until_clickable(self, by: str, value: str, *, timeout: int | float = 10):
        """
        Convenience method that uses `self._wait_until` to wait until an element
        is clickable, i.e., with `condition = EC.element_to_be_clickable`
        
        Parameters
        ----------
        by: str
            locate the element expected to be clickable by the attribute `by`
        value: str
            locate the element expected to be clickable when the attribute `by`
            value is `value`
        timeout: int or float, optional
            time to wait before raising TimeoutException, in seconds
        
        Returns
        -------
        element: WebElement
            WebDriver element, if condition is fulfilled. 
        
        Raises
        ------
        TimeoutException, if the element is not clickable after `timeout` seconds
        """
        return self._wait_until(condition = EC.element_to_be_clickable((by, value)), timeout = timeout)

class BootsPageScraper(ChromeDriverWrapper):
    def __init__(self, *, url: str = None, driver_path: str = None, headless: bool = False, auto_accept_cookies = True):
        super().__init__(driver_path, headless)

        # load the given URL, or the default one
        url = url or URL
        logger.debug(f'Navigating to {url!r}')
        self.driver.get(url)

        logger.debug('Creating tmp files folder')
        self.tmp_dir = TMP_DATA_PATH
        os.makedirs(self.tmp_dir, exist_ok = True)

        if auto_accept_cookies:
            try:
                logger.debug('Auto-accepting cookies')
                self.accept_cookies()
            except Exception as e:
                # we might not get the prompt to accept the cookies
                pass
    
    @RETRY
    def _accept_cookies(self):
        """Helper method to auto-accept cookies"""
        self._wait_until_clickable(By.ID, ACCEPT_COOKIES_BUTTON_ID).click()

    @RETRY
    def _accept_recommended_cookies(self):
        """Helper method to auto-accept the recommended cookies"""
        self._wait_until_clickable(By.ID, ACCEPT_RECOMMENDED_COOKIES_BUTTON_ID).click()

    def accept_cookies(self):
        """Helper method to auto-accept cookies"""
        self._accept_cookies()
        self._accept_recommended_cookies()

    @RETRY
    def _find_product_elements(self, product_elements_class_name: str):
        """
        Helper method to find the product elements in the URL according to
        their class name `product_elements_class_name`
        """
        self._wait_until_clickable(By.CLASS_NAME, product_elements_class_name)
        return self.driver.find_elements(By.CLASS_NAME, product_elements_class_name)

    def find_products(self, product_elements_class_name: str = PRODUCT_ELEMENT_CLASS_NAME):
        """
        Finds the products in the initial URL and stores them in `Product` instances,
        for later information retrieval.

        Parameters
        ----------
        product_elements_class_name: str, optional
            class name of the products

        Returns
        -------
        products: list[Product]
            list of products found, as `Product` instances
        """
        logger.debug(f'Searching products in the URL')

        product_elements = self._find_product_elements(product_elements_class_name)
        self._n_products = len(product_elements)
        logger.info(f'Found {self._n_products} products')

        products = []
        for product in product_elements:
            try:
                name = product.text
            except:
                logger.error(f'Unable to get product name')
                name = ''
                
            try:
                href = product.get_attribute('href')
            except NoSuchElementException:
                logger.error(f'Unable to get product {name!r} href')
                href = None

            products.append(Product(href = href, name = name))

        return products
    
    def _parse_product(self, product: Product):
        """Parse the given product to extract the necessary information"""
        # navigate to the product page
        self.driver.get(product.href)

        # extract data
        # rating is one of the latest elements to show, and there are some products that have none
        try:
            rating_element = self._wait_until_clickable(By.CLASS_NAME, PRODUCT_RATING_CLASS_NAME, timeout = 15)
        except TimeoutException:
            # we assume 15 seconds is enough time for the page to load,
            # thus `TimeoutException` means the product has no rating
            import numpy as np
            product.rating = np.NaN
        else:
            product.rating = rating_element.text

        # name is rendered from the beginning (even before than JS)
        product.name = self.driver.find_element(By.ID, PRODUCT_TITLE_ID).text
            
        # some items do not have a description
        try:
            text_raw = self.driver.find_element(By.CLASS_NAME, PRODUCT_TEXT_CLASS_NAME).text
        except NoSuchElementException:
            product.description = 'Missing product description.'
        else:
            product.description = text_raw.split('\n')[0]

        # split price and unit; we could store it as float, but it does not make
        # a difference if saving the data as JSON
        price_str = self.driver.find_element(By.CLASS_NAME, PRODUCT_PRICE_STR_CLASS_NAME).text
        try:
            product.price_unit, product.price = PRICE_STR_PATTERN.match(price_str).groups()
        except:
            product.price_unit = price_str[0]
            product.price = price_str[1:]

        # note that `sys.getsizeof` might not give the exact size of the HTML page,
        # as it also includes additional overhead from Python's object management
        product.page_size = sys.getsizeof(self.driver.page_source.encode('utf-8'))//1024 # in KB

        return product.as_dict()
    
    def do_cleanup(self, force = False):
        """Helper method to remove the temporary files"""
        n_parsed_files = len(os.listdir(self.tmp_dir))

        # because default item sorting is by relevance, the listed
        # products may change between a failed execution and the
        # resumed one, so we might end up with more products than
        # the ones listed
        if force or (n_parsed_files >= self._n_products):
            import shutil

            logger.debug(f'Removing tmp files from {self.tmp_dir!r}')
            shutil.rmtree(self.tmp_dir)
        else:
            logger.warning(
                f'Skipping cleanup, as {n_parsed_files} of {self._n_products} products have been scraped. '
                f'to force it, set `force = True`'
            )

    @retry(exceptions = ScrapingException, n_tries = 2)
    def parse_products(
        self, 
        products: list[Product], 
        *,
        output_path: str = None, 
        output_file: str = None,
        auto_remove: bool = True,
        force_remove: bool = False
    ):
        """
        Extracts the target data from the given products and stores it as a JSON file.

        This method can be resumed, meaning that if the extraction from any product fails,
        you can call it again and it will iterate over the given products skipping those
        already processed (i.e., those present in the tmp folder).

        Parameters
        ----------
        products: list[Product]
            list of products to retrieve data from, as returned by `self.find_products` 
        output_path: str, optional
            path where the output file is written
        output_file: str, optional
            name of the output file
        auto_remove: bool, optional
            whether to automatically do clean up when all products have been parsed
        force_remove: bool = False
            whether to automatically do clean up when the process finishes, even if
            there have been any errors when parsing products (not recommended)
        """
        output_path = output_path or OUTPUT_PATH
        output_file = output_file or OUTPUT_FILE

        failed_products = {}
        for idx, product in enumerate(products):
            idx += 1
            if idx%10 == 0:
                logger.info(f'Parsing product #{idx}')

            if product.name:
                tmp_product_name = re.sub(r'[\W]+', '_', product.name).lower()
            else:
                import uuid
                tmp_product_name = uuid.uuid4()
                
            tmp_fp = os.path.join(self.tmp_dir, f'{tmp_product_name}.json')

            # skip already parsed products (to make the process resumable)
            if os.path.isfile(tmp_fp):
                logger.debug(f'skipping already parsed product {product.name!r}')
                continue

            try:
                logger.debug(f'Parsing product {product.name!r} data')
                product_data = self._parse_product(product)
            except Exception as e:
                e_str = f'{type(e).__name__}: {e}'
                logger.error(
                    f'Unable to parse product {product.name!r} due to the '
                    f'following error: {e_str}'
                )
                failed_products[product.name] = e_str
            else:
                logger.debug(f'Retrieved the following data: {product_data}')

                logger.debug(f'Storing product data in the temp file {tmp_fp!r}')
                with open(tmp_fp, 'w') as f_out:
                    json.dump(product_data, f_out)

        # read from tmp files
        parsed_products = []
        for file in os.listdir(self.tmp_dir):
            tmp_fp = os.path.join(self.tmp_dir, file)
            with open(tmp_fp) as f_in:
                parsed_products.append(json.load(f_in))
        
        # store final data
        median_product_price = to_numeric([product['Price'] for product in parsed_products]).mean().round(2)
        curated_product_data = {'Products': parsed_products, 'Median': median_product_price}

        out_fp = os.path.join(output_path, output_file)
        logger.info(f'Writing output data to {out_fp!r}')
        with open(out_fp, 'w') as f_out:
            json.dump(curated_product_data, f_out)

        # print log for failed products, if any, and clean up
        if failed_products:
            import time

            log_fp = FAILED_PRODUCTS_LOG_FP.format(time = int(time.time()))
            # write failed
            with open(log_fp, 'w') as f_out:
                json.dump(failed_products, f_out)
            
            if force_remove:
                self.do_cleanup(force = True)

            raise ScrapingException(
                f'Scrapping process failed for {len(failed_products)} products. '
                f'See error log {log_fp!r} for more info'
            )
        
        elif auto_remove:
            self.do_cleanup()
