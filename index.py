# ======================== #
# Imports
# ======================== #

import requests
import os
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from dotenv import load_dotenv

# ======================== #
# Set defaults
# ======================== #

load_dotenv()

TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    'X-GitHub-Api-Version': '2022-11-28',
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {TOKEN}'
}

API_BASE = 'https://api.github.com' # The base URL for the GitHub API
ENDPOINT = 'repos' # The endpoint to get the information from
OWNER = 'boyter' # The owner of the repository
REPOSITORY = 'scc' # The repository to get the information from
PAGE = 1 # Page to start from
PER_PAGE = 100 # Maximum number of items per page

# ======================== #
# Helpers
# ======================== #

def crawl_pages_count(base_url: str, page: int, per_page: int) -> int:
    """ Get the total count of contributors
    :param url: The URL to get the contributors
    :param per_page: The number of contributors per page
    :return: The total number of contributors
    """
    url = f'{base_url}?page={page}&per_page={per_page}'

    response = requests.get(url, headers=HEADERS)

    # Check if there are more pages to get
    if 'last' in response.links.keys():
        parsed_url = urlparse(response.links['last']['url'])
        last_page = parse_qs(parsed_url.query)['page'][0]

        # Total count is per page * last page + last page count
        temp_count = (int(last_page) - 1) * per_page

        # Get the last page count
        response = requests.get(f'{base_url}?page={last_page}&per_page={per_page}', headers=HEADERS).json()
        count = temp_count + len(response)

        return count

    # If there is only one page then return the count
    return len(response.json())

def search_total_count(query: str) -> int: 
    """ Get the total count of issues
    :param query: The query to search for issues
    :return: The total number of issues
    """
    url = f'https://api.github.com/search/issues?q=repo:{OWNER}/{REPOSITORY}+{query}&per_page=1&page=1'
    response = requests.get(url, headers=HEADERS).json()

    return response['total_count']

# ======================== #
# Main
# ======================== #

repo_url = f'{API_BASE}/{ENDPOINT}/{OWNER}/{REPOSITORY}'
contributors_url = f'{repo_url}/contributors'
commits_url = f'{repo_url}/commits'
issues_url = f'{repo_url}/issues?q=type:issue+state:closed'

# Get the repository information
repository = requests.get(repo_url, headers=HEADERS).json()

# Extract the information we need
project_information = {
    'name': repository['name'],
    'created_at': repository['created_at'],
    'main_language': repository['language'],
    'contributors': crawl_pages_count(f'{contributors_url}', PAGE, PER_PAGE),
    'commits': crawl_pages_count(f'{commits_url}', PAGE, PER_PAGE),
    'open_issues': repository['open_issues'],
    'closed_issues': search_total_count('type:issue+state:closed')
}

# Print the information
print(json.dumps(project_information, indent=4, sort_keys=False))
