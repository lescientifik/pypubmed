from dataclasses import dataclass
from datetime import date
import time
import xml.etree.ElementTree as ET

import requests


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
# PubMed API limits
RATE_LIMIT_DEFAULT = 3   # requests/sec without API key
RATE_LIMIT_WITH_KEY = 10  # requests/sec with API key


class RateLimiter:
    """Limits requests to a maximum rate per second."""

    def __init__(self, requests_per_second: int = RATE_LIMIT_DEFAULT):
        self.min_interval = 1.0 / requests_per_second
        self.last_request = 0.0

    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()


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
    journal: str
    mesh_terms: list[str]
    keywords: list[str]
    doi: str | None
    # Date when article became available online (most precise, has day)
    publication_date: date | None
    # Date of the journal issue (often just year/month, day defaults to 1)
    journal_date: date | None

    @property
    def url(self) -> str:
        return f"https://pubmed.ncbi.nlm.nih.gov/{self.pmid}/"


class PubMed:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        rate = RATE_LIMIT_WITH_KEY if api_key else RATE_LIMIT_DEFAULT
        self._rate_limiter = RateLimiter(rate)

    def search(
        self,
        query: str,
        max_results: int = 20,
        min_date: str | None = None,
        max_date: str | None = None,
    ) -> SearchResult:
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        if min_date:
            params["mindate"] = min_date
            params["datetype"] = "pdat"
        if max_date:
            params["maxdate"] = max_date
            params["datetype"] = "pdat"

        self._rate_limiter.wait()
        response = requests.get(f"{BASE_URL}/esearch.fcgi", params=params)
        response.raise_for_status()

        data = response.json()
        result = data.get("esearchresult", {})
        ids = result.get("idlist", [])
        count = int(result.get("count", 0))

        return SearchResult(ids=ids, count=count)

    def search_and_fetch(
        self,
        query: str,
        max_results: int = 20,
        min_date: str | None = None,
        max_date: str | None = None,
    ) -> list[Article]:
        result = self.search(query, max_results, min_date, max_date)
        if not result.ids:
            return []
        return self.fetch(result.ids)

    def fetch(self, ids: list[str]) -> list[Article]:
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        self._rate_limiter.wait()
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

            doi = None
            for article_id in article_elem.findall(".//ArticleId"):
                if article_id.get("IdType") == "doi":
                    doi = article_id.text
                    break

            journal = article_elem.findtext(".//Journal/Title", default="")

            mesh_terms = [
                mesh.findtext("DescriptorName", default="")
                for mesh in article_elem.findall(".//MeshHeading")
                if mesh.findtext("DescriptorName")
            ]

            keywords = [
                kw.text for kw in article_elem.findall(".//Keyword")
                if kw.text
            ]

            # Parse publication_date (electronic) from ArticleDate
            publication_date = self._parse_date(article_elem.find(".//ArticleDate"))
            # Parse journal_date (print) from PubDate
            journal_date = self._parse_date(article_elem.find(".//PubDate"))

            articles.append(Article(
                pmid=pmid,
                title=title,
                abstract=abstract,
                authors=authors,
                journal=journal,
                mesh_terms=mesh_terms,
                keywords=keywords,
                doi=doi,
                publication_date=publication_date,
                journal_date=journal_date,
            ))

        return articles

    def _parse_date(self, date_elem) -> date | None:
        if date_elem is None:
            return None
        year = date_elem.findtext("Year")
        if not year:
            return None
        month = date_elem.findtext("Month", "1")
        day = date_elem.findtext("Day", "1")
        try:
            month = int(month)
        except ValueError:
            # Month as text (Jan, Feb, etc.)
            months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4,
                      "may": 5, "jun": 6, "jul": 7, "aug": 8,
                      "sep": 9, "oct": 10, "nov": 11, "dec": 12}
            month = months.get(month.lower()[:3], 1)
        return date(int(year), month, int(day))
