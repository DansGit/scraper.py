scraper.py
==========

This is where I store my various web scrapers for my projects.

Of interest to you may be the scraper.py file, which provides an abstract base class for the scraping of news websites.
All you have to do is write the extract_links(), extract_metadata(), and maybe the extract_article() methods and
scraper.py will provide you with logging, error handling, http
requests/headers, and even a progress bar!

# Features
* A progress bar that utilizes Monty Carlo estimation to predict finish times.
* Decent logging functionality.
* Headers that act like a "real boy" or rather, like a real browser.
  * User-Agent is chosen randomly from a list 19 standard user-agent strings.
  * Other headers mimic standard browser headers.
  * Referer header is automatically updated with latest search results page.

# How To
I'm far too lazy to wright this now.
Take a look at startribune.py for an example of a working web scraper. Send me a message if you have any questions.
