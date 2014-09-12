from bs4 import BeautifulSoup
from scraper import Scraper, ParseError
import re

class StarTribune(Scraper):
    def __init__(self, search, num_articles, start=1):
        format_url = "http://www.startribune.com/search/?stq=" \
                + search + "&page={}"

        Scraper.__init__(self, format_url,
                num_articles=num_articles,
                start=start
                )


    def extract_links(self, html, url):
        """Extract article links from search result page."""
        soup = BeautifulSoup(html)

        divs = soup.find_all('div', {'class':'searchEntry'})

        #Check if search results exists
        if len(divs) == 0:
            raise ParseError(msg="No search result links found",
                    url=url)

        # for div in soup.find_all('div', {'class':'searchEntry'}):
        for div in divs:
            yield div.find('a')['href']


    def extract_metadata(self, html, url):
        """Find publication date, title, and url"""
        soup = BeautifulSoup(html)

        # Find Publication Date
        date_tag = soup.find(['li', 'span'], {'class':'updatedBy'})
        if date_tag is None:
            raise ParseError(
                    msg='Publication date not found',
                    url=url
                    )
        raw_date = date_tag.get_text()
        date_match = re.findall("Updated: (.*) -", raw_date)
        # Make sure we found pub date
        if len(date_match) == 0:
            raise ParseError(
                    msg="No publication date found.",
                    source=str(date_tag),
                    url=url
                    )

        # Find Title
        title_tag = soup.find('title')
        if title_tag is None:
            raise ParseError(msg="No title found.",
                    url=url
                    )
        raw_title = title_tag.get_text()

        return {
                "pub_date": date_match[0],
                "url": url,
                "title": raw_title
                }


if __name__ == '__main__':
    # Short example showing scraper usage
    import sys
    import json
    from os import path
    import codecs

    # Get command line arguments
    search_term = sys.argv[1]
    numarticles = sys.argv[2]
    save_dir = sys.argv[3]

    # Make web scraper
    star = StarTribune(search_term, numarticles)

    # Loop through scraped articles
    for i, article in enumerate(star.scrape()):
        # Save the results
        fpath = path.join(save_dir, '{}.json'.format(i))
        f = codecs.open(fpath, 'w', 'utf-8')
        json.dump(article, f)
        f.close()
