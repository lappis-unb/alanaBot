from bs4 import BeautifulSoup
from abc import ABC
import sys
sys.path.append('../')
import utils  # noqa: E402


class Crawl(ABC):
    def __init__(self):
        if (self.api_url is None and self.web_url is None):
            raise NotImplementedError('Subclasses must define api '
                                      'and web urls')

    def get_page_content(self, request_url):
        page_url = (request_url)
        page_content = utils.get_request(page_url)
        soup = BeautifulSoup(page_content.text, 'html.parser')
        return soup
