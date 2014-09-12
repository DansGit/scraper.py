from progressbar import ProgressBar
from time import sleep
from random import randint
from headers import get_headers
from goose import Goose
import logging
import requests
import itertools
import urlparse

class Scraper(object):
    def __init__(self, format_url, num_articles, start=1, step=1):

        logging.basicConfig(filename='log',
                filemode='w',
                level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # URL with {} in place of page number parameter.
        # e.g. ...&page=3 becomes ...&page={}
        self._format_url = format_url

        # What page to start on
        self._start = start

        # How to much to step up url parameter by each time
        # Usually can be set to 1
        self._step = step

        # The number of articles to download before stopping
        self._num_articles = num_articles

        # Get headers with a randomly chosen user-agent.
        self.headers = get_headers()

        # Set initial referer to homepage of the scraped site
        self.headers['Referer'] = 'http://www.{}'.format(
                urlparse.urlparse(format_url).hostname)

    def extract_links(self, html, url):
        """Unimplemented link extraction method.
        Arguments:
            html (str) -- raw html from which to extract links.
            url (str) -- URL of the search results page. Useful for error
                logging.
        Returns:
            An iterator that yields URLs.
        """
        raise NotImplementedError


    def extract_metadata(self, html, url):
        """This method can be overriden to extract various data from the
        webpage. Examples may include author, publication date, and
        publication. Should return a dictionary.
        Arguments:
            html (str) -- raw html from which to extract data.
            url (str) -- URL of the article. Useful for error logging.
        Returns:
            dict -- a dictionary containing data data extracted from the
                        webpage.
        """
        raise NotImplementedError

    def extract_article(self, html, url):
        """Removes boilerplate and extracts the main article of a webpage.
        Arguments:
            html (str) -- raw html from which to extract the article.
            url (str) -- URL of the article. Useful for error logging.
        Returns:
            str -- a string containing the article's text.

        This method provides article extraction via Goose, but it can be
        overridden for a customized solution.
        """

        g = Goose()
        article = g.extract(raw_html=html).cleaned_text

        # Check if article exists
        if article == '':
            raise ParseError(msg='Goose failed to extract article.',
                    url=url)

        return article


    def scrape(self, pause=(30, 60)):
        """Scraper's main loop. Pulls a news website's search result page
        via format url and extracts article links with extract_links().
        Then it loops through those extracted links and pulls out the article
        with extract_article() and metadata with extract_metadata(). Lastly,
        it yields the results in a dictionary.
        Arguments:
            pause (tuple): Program will pause for a random number of seconds
                between pause[0] and pause[1].
            pause (None): Program will not pause at all. NOT RECOMMENDED!
        Yields:
            dict -- a dictionary containing data returned by extract_metadata()
                and the article content under the 'content' key.
        """
        # Start the progress bar
        pbar = ProgressBar(self._num_articles)
        pbar.start()

        count = 0
        # Loop through search result pages.
        for i in itertools.count(self._start, self._step):
            # Stop if we have desired number of articles.
            if count > self._num_articles:
                break

            url = self._format_url.format(i)


            # log search results page turn
            self.logger.info("Extracting search results from {}".format(url))

            # Begin scraping
            try:
                # Extract search result URLs
                rawsearchresults = requests.get(url, headers=self.headers)
                searchresults = self.extract_links(rawsearchresults.text, url)

                # Add referer to headers to look like a real boy
                self.headers['Referer'] = url

                # Walk throguh search results
                for link in searchresults:
                    # Stop if we have desired number of articles.
                    if count > self._num_articles:
                        break

                    self.logger.info("Extracting article from {}".format(link))

                    # Download article
                    raw_article = requests.get(link, headers=self.headers)

                    # Extract article / remove boilerplate
                    content = self.extract_article(raw_article.text, link)

                    # Extract various metadata
                    article = self.extract_metadata(raw_article.text, link)

                    # add article content to metadata dictionary.
                    article['content'] = content

                    if pause:
                        sleep(randint(pause[0], pause[1]))

                    count += 1
                    pbar.tick()
                    yield article

            except ParseError as e:
                # Log error, then continue
                self.logger.error(str(e))

                # Update counter and progressbar
                count += 1
                pbar.tick()
            except Exception as e:
                # Log error, then exit
                self.logger.error('Error occured while in scrape()',
                        exc_info=True)
                raise e


class ParseError(Exception):
    def __init__(self, msg, source='n/a', url='n/a'):
        """Raised when something goes wrong parsing a webpage.
        Arguments:
            msg -- explanation of the error.
            source -- sourcecode of the webpage that caused the
                error.
            url -- The url of the webpage that caused the error.
        """
        Exception.__init__(self, msg)
        self.msg = msg
        self.source = source
        self.url = url


    def __str__(self):
        return "ParseError: {}\nSourcecode: {}\nURL: {}".format(self.msg,
                self.source,
                self.url
                )
