import requests
import os
from datetime import datetime, timedelta

TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

# Search repos created in last 1 day
yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

query = f"blockchain created:>{yesterday}"

url = "https://api.github.com/search/repositories"
params = {
    "q": query,
    "sort": "stars",
    "order": "desc",
    "per_page": 5
}

resp = requests.get(url, headers=HEADERS, params=params)
resp.raise_for_status()

data = resp.json()

for repo in data["items"]:
    print(f"{repo['full_name']} ⭐ {repo['stargazers_count']}")
    print(repo["html_url"])
    print("----")
