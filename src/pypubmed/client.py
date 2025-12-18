from dataclasses import dataclass

import requests


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


@dataclass
class SearchResult:
    ids: list[str]


class PubMed:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def search(self, query: str, max_results: int = 20) -> SearchResult:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()

        data = response.json()
        ids = data.get("esearchresult", {}).get("idlist", [])

        return SearchResult(ids=ids)
