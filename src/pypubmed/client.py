from dataclasses import dataclass
import xml.etree.ElementTree as ET

import requests


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


@dataclass
class SearchResult:
    ids: list[str]
    count: int


@dataclass
class Article:
    pmid: str
    title: str
    abstract: str
    authors: list[str]


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
        result = data.get("esearchresult", {})
        ids = result.get("idlist", [])
        count = int(result.get("count", 0))

        return SearchResult(ids=ids, count=count)

    def fetch(self, ids: list[str]) -> list[Article]:
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        response = requests.get(f"{BASE_URL}/efetch.fcgi", params=params)
        response.raise_for_status()

        return self._parse_articles(response.text)

    def _parse_articles(self, xml_text: str) -> list[Article]:
        root = ET.fromstring(xml_text)
        articles = []

        for article_elem in root.findall(".//PubmedArticle"):
            pmid = article_elem.findtext(".//PMID", default="")
            title = article_elem.findtext(".//ArticleTitle", default="")

            abstract_parts = article_elem.findall(".//AbstractText")
            abstract = " ".join(part.text or "" for part in abstract_parts)

            authors = []
            for author in article_elem.findall(".//Author"):
                lastname = author.findtext("LastName", default="")
                forename = author.findtext("ForeName", default="")
                if lastname:
                    authors.append(f"{forename} {lastname}".strip())

            articles.append(Article(
                pmid=pmid,
                title=title,
                abstract=abstract,
                authors=authors,
            ))

        return articles
