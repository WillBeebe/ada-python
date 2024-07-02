import json
import os

import requests


def get_top_headlines(query: str = None, country: str = None, category: str = None):
    """Retrieve top headlines from newsapi.org (API key required)"""

    base_url = "https://newsapi.org/v2/top-headlines"
    headers = {
        "x-api-key": os.environ['NEWS_API_KEY']
    }
    params = { "category": "general" }
    if query is not None:
        params['q'] = query
    if country is not None:
        params['country'] = country
    if category is not None:
        params['category'] = category

    # Fetch from newsapi.org - reference: https://newsapi.org/docs/endpoints/top-headlines
    response = requests.get(base_url, params=params, headers=headers)
    data = response.json()

    if data['status'] == 'ok':
        print(f"Processing {data['totalResults']} articles from newsapi.org")
        return json.dumps(data['articles'])
    else:
        print("Request failed with message:", data['message'])
        return 'No articles found'
