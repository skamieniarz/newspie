# -*- coding: utf-8 -*-
'''
NewsPie - a minimalistic news aggregator built with Flask and powered by
News API (https://newsapi.org/).

Created by @skamieniarz (https://github.com/skamieniarz) in 2019.
'''
import configparser
import json
import logging
import os
from typing import Union

import requests
import requests_cache
from dateutil import parser
from flask import (Flask, make_response, redirect, render_template, request,
                   url_for)

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
API_KEY = os.environ.get('NEWS_API_KEY')
TOP_HEADLINES = CONFIG['ENDPOINTS']['TOP_HEADLINES']
EVERYTHING = CONFIG['ENDPOINTS']['EVERYTHING']
PAGE_SIZE = int(CONFIG['VARIOUS']['PAGE_SIZE'])

CATEGORIES = ('general', 'sports', 'business', 'entertainment', 'health',
              'science', 'technology')
with open('data/countries.json') as json_file:
    COUNTRIES = json.load(json_file)

logging.basicConfig(level=logging.DEBUG)
requests_cache.install_cache(cache_name='news_cache',
                             backend='sqlite',
                             expire_after=300)

APP = Flask(__name__)
SESSION = requests.Session()
SESSION.headers.update({'Authorization': API_KEY})


@APP.route('/', methods=['GET', 'POST'])
def root():
    ''' Base URL redirect to the first page of general category. '''
    return redirect(url_for('category', category='general', page=1))


@APP.errorhandler(404)
def page_not_found(error):
    ''' Not existing pages redirect to the first page of general category. '''
    return redirect(url_for('category', category='general', page=1))


@APP.route('/category/<string:category>', methods=['GET', 'POST'])
def category(category):
    ''' Handles category route.

    Parameters:
        - name: category
          in: path
          description: Name of the news category
        - name: page
          in: query
          description: Number of the page
    '''
    page = request.args.get('page', default=1, type=int)
    if page < 1:
        return redirect(url_for('category', category=category, page=1))
    if request.method == 'POST' and category in CATEGORIES:
        return do_post(page, category)
    if category in CATEGORIES:
        params = {'page': page, 'category': category, 'pageSize': PAGE_SIZE}
        country = get_cookie('country')
        if country is not None:
            params.update({'country': country})
        response = SESSION.get(TOP_HEADLINES, params=params)
        if response.status_code == 200:
            pages = count_pages(response.json())
            if page > pages:
                page = pages
                return redirect(
                    url_for('category', category=category, page=page))
            articles = parse_articles(response.json())
            return render(articles, page, pages, country, category)
        elif response.status_code == 401:
            return render_template(CONFIG['VARIOUS']['401_TEMPLATE'])
    return redirect(url_for('category', category='general', page=page))


@APP.route('/search/<string:query>', methods=['GET', 'POST'])
def search(query: str):
    ''' Handles category route.

    Parameters:
        - name: query
          in: path
          description: Query string to be searched
        - name: page
          in: query
          description: Number of the page
    '''
    page = request.args.get('page', default=1, type=int)
    if page < 1:
        return redirect(url_for('search', query=query, page=1))
    params = {
        'qInTitle': query,
        'sortBy': 'relevancy',
        'page': page,
        'pageSize': PAGE_SIZE
    }
    if request.method == 'POST':
        return do_post(page, category='search', current_query=query)
    response = SESSION.get(EVERYTHING, params=params)
    pages = count_pages(response.json())
    if page > pages:
        page = pages
        return redirect(url_for('search', query=query, page=page))
    articles = parse_articles(response.json())
    return render(articles,
                  page,
                  pages,
                  country=get_cookie('country'),
                  category='search')


def do_post(page, category='general', current_query=None):
    ''' Helper method that handles POST request basing on the input. '''
    new_query = request.form.get('search_query')
    country = request.form.get('country')
    next_page = request.form.get('next_page')
    previous_page = request.form.get('previous_page')
    if new_query is not None and new_query != '':
        return redirect(url_for('search', query=new_query, page=1))
    if country is not None and country != get_cookie('country'):
        response = make_response(
            redirect(url_for('category', category=category, page=1)))
        response.set_cookie('country', country)
        return response
    if next_page is not None:
        page = int(next_page) + 1
    elif previous_page is not None:
        page = int(previous_page) - 1
    if category == 'search':
        return redirect(url_for('search', query=current_query, page=page))
    return redirect(url_for('category', category=category, page=page))


def parse_articles(response: dict) -> list:
    ''' Parses articles fetched from News API.

    Returns:
        A list of dicts containing publishing date, title, URL and source of
        articles.
    '''
    parsed_articles = []
    if response.get('status') == 'ok':
        for article in response.get('articles'):
            parsed_articles.append({
                'published_at':
                    parser.isoparse(article['publishedAt']
                                   ).strftime('%d-%m %H:%M'),
                'title':
                    article['title'],
                'url':
                    article['url'],
                'source':
                    article['source']['name']
            })
    return parsed_articles


def count_pages(response: dict) -> int:
    ''' Helper method that counts number of total pages basing on total
        results from News API response and PAGE_SIZE.

    Returns:
        An int with a number of total pages. '''
    if response.get('status') == 'ok':
        return (-(-response.get('totalResults', 0) // PAGE_SIZE))
    return 0


def render(articles, page, pages, country, category):
    ''' Renders the template with appropriate variables. Up to 12 pages
        allowed. '''
    pages = pages if pages <= 12 else 12
    return render_template(CONFIG['VARIOUS']['TEMPLATE'],
                           articles=articles,
                           categories=CATEGORIES,
                           category=category,
                           countries=COUNTRIES,
                           country=country,
                           page=page,
                           pages=pages)


def get_cookie(key: str) -> Union[str, None]:
    ''' Helper method that gets cookie's value.

    Returns:
        A string with a value of a cookie with provided key. If a key is
        missing, None is returned.
    '''
    return request.cookies.get(key)


if __name__ == '__main__':
    APP.run()
