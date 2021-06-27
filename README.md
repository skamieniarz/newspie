# NewsPie #
A minimalistic news aggregator built with [Flask](https://www.palletsprojects.com/p/flask/) and powered by [News API](https://newsapi.org/).

![Demo!](https://raw.githubusercontent.com/skamieniarz/newspie/master/static/demo.gif)

### [Link to live demo](https://skamieniarz.github.io/newspie/) ###

## Prerequisites: ##

1. [Python3](https://www.python.org).
2. Dependencies from `requirements.txt` or `Pipfile.lock` (preferably in a virtual env).
3. API key for [News API](https://newsapi.org/register). It's free for non-commercial projects (including open-source) and allows 500 requests per day. Once acquired, save it as `NEWS_API_KEY` environment variable or directly as string to `API_KEY` in `news.py`. Just don't share it or upload the code with it.

## Starting: ##

1. Run `python news.py` or `python3 news.py` (depending on the environment) in the terminal while in the root of the repository.
2. Go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) address in the web browser.

## Features: ##

1. Get top articles headlines and their URLs by country and/or category.
2. Search articles up to a month old. Looks for a given query in the titles. Language/country independent results. Relevancy decides.
3. Results received from News API are cached for 5 minutes.
4. Country is saved as a cookie.
5. Responsive UI.

## Open-source used: ##

- [Flask](https://github.com/pallets/flask)
- [jinja](https://github.com/pallets/jinja)
- [Skeleton](https://github.com/dhg/Skeleton)
- [requests](https://github.com/psf/requests)
- [requests-cache](https://github.com/reclosedev/requests-cache)
- [dateutil](https://github.com/dateutil/dateutil)
