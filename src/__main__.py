import click
import logging

from _logs import set_logger_config
from _scraper import BootsPageScraper

@click.command()
@click.option(
    '--url', 
    default = None, 
    type = str, 
    help = 'Target URL for the Boots - Sleep page.'
)
@click.option(
    '--webdriver-path', 
    default = None, 
    type = str, 
    help = 'Path to the webdriver executable.'
)
@click.option(
    '--headless', 
    is_flag = True, 
    default = False, 
    show_default = True, 
    help = 'Whether to run with GUI.'
)
@click.option(
    '--output-path',
    default = None, 
    type = str, 
    help = 'Path where the output data is saved.'
)
@click.option(
    '--output-file', 
    default = None, 
    type = str, 
    help = 'File containing the output data.'
)
@click.option(
    '--force-remove', 
    is_flag = True, 
    default = False, 
    show_default = True, 
    help = 'Whether to remove temp files when the process ends.'
)
@click.option(
    '-v', '--verbose', 
    count = True, 
    help = (
        'The verbosity level. Not setting it means `logging.WARNING, ' 
        '`-v` equals `logging.INFO`, and `-vv` `logging.DEBUG`.'
    )
)
@click.option(
    '--paginate', 
    is_flag = True, 
    default = False, 
    show_default = True, 
    help = 'Whether to paginate over all results in the Boots - Sleep page.'
)
def main(
    url, 
    webdriver_path, 
    headless,
    output_path,
    output_file,
    force_remove,
    verbose,
    paginate
):  
    if paginate:
        raise NotImplementedError(
            'Paginating over all pages of the Boots - Sleep page is not '
            'implemented yet. If you want the scraper to do so, kindly '
            'do hire me :)'
        )
    
    log_level = max(logging.WARNING - verbose*10, 0)
    set_logger_config(log_level = log_level)

    scraper = BootsPageScraper(
        url = url,
        driver_path = webdriver_path,
        headless = headless
    )
    products = scraper.find_products()
    scraper.parse_products(
        products,
        output_path = output_path, 
        output_file = output_file, 
        force_remove = force_remove
    )

if __name__ == '__main__':
    main()
