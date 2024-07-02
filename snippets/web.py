from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build


def web_search(query: str, num_results: int = 5, language: str = "en",
               safe_search: bool = True, site_restrict: str = None,
               time_range: str = None) -> dict:
    """
    Perform a web search based on the given query and return relevant results.

    Args:
        query (str): The search query string.
        num_results (int, optional): Number of search results to return. Defaults to 5.
        language (str, optional): Language code for the search results. Defaults to "en".
        safe_search (bool, optional): Whether to enable safe search filtering. Defaults to True.
        site_restrict (str, optional): Restrict the search to a specific website or domain.
        time_range (str, optional): Time range for the search results.

    Returns:
        dict: A dictionary containing the search results and metadata.
    """
    try:
        # Set up the API client
        service = build('customsearch', 'v1', developerKey='YOUR_API_KEY')

        # Define the search parameters
        search_params = {
            'q': query,
            'num': num_results,
            'lr': f'lang_{language}',
            'safe': 'active' if safe_search else 'off'
        }
        if site_restrict:
            search_params['siteSearch'] = site_restrict
        if time_range:
            search_params['dateRestrict'] = time_range

        # Perform the search
        results = service.cse().list(**search_params).execute()

        # Process results
        processed_results = {
            "query": query,
            "total_results": results.get('searchInformation', {}).get('totalResults'),
            "items": [{
                "title": item.get('title'),
                "link": item.get('link'),
                "snippet": item.get('snippet'),
                "displayLink": item.get('displayLink')
            } for item in results.get('items', [])]
        }

        return processed_results

    except Exception as e:
        return {"error": str(e)}

def web_browse(url: str) -> dict:
    """
    Visits the given URL and returns the web page contents as plain text,
    along with metadata about the page.

    Args:
        url (str): The URL to visit.

    Returns:
        dict: A dictionary containing the page content and metadata.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the text content
        text_content = soup.get_text(separator='\n', strip=True)

        # Extract metadata
        title = soup.title.string if soup.title else "No title found"
        meta_description = soup.find('meta', attrs={'name': 'description'})
        description = meta_description['content'] if meta_description else "No description found"

        # Extract the main content (this is a simple heuristic and may need refinement)
        main_content = ""
        for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            main_content += tag.get_text(strip=True) + "\n\n"

        return {
            "url": url,
            "domain": urlparse(url).netloc,
            "title": title,
            "description": description,
            "full_text": text_content,
            "main_content": main_content.strip(),
            "status_code": response.status_code,
            "content_type": response.headers.get('Content-Type', '')
        }

    except requests.RequestException as e:
        return {
            "url": url,
            "error": str(e),
            "status_code": getattr(e.response, 'status_code', None)
        }
