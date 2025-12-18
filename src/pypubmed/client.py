from dataclasses import dataclass
from datetime import date
import re
import time
import defusedxml.ElementTree as ET

import requests

DATE_PATTERN = re.compile(r'^\d{4}/\d{2}/\d{2}$')


class PubMedError(Exception):
    """Base exception for PyPubMed."""
    pass


class APIError(PubMedError):
    """Raised when the PubMed API returns an error."""
    pass


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

    def to_dict(self) -> dict:
        """Convert article to dictionary with ISO date strings."""
        return {
            "pmid": self.pmid,
            "title": self.title,
            "abstract": self.abstract,
            "authors": self.authors,
            "journal": self.journal,
            "mesh_terms": self.mesh_terms,
            "keywords": self.keywords,
            "doi": self.doi,
            "url": self.url,
            "publication_date": self.publication_date.isoformat() if self.publication_date else None,
            "journal_date": self.journal_date.isoformat() if self.journal_date else None,
        }


class PubMed:
    """Client for the PubMed API.

    Args:
        api_key: Optional NCBI API key for higher rate limits.
        cache: Enable caching of fetched articles.
        cache_ttl: Cache time-to-live in seconds (default 3600).
    """

    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0  # seconds
    TIMEOUT = (5, 30)  # (connect, read) in seconds
    MAX_IDS_PER_REQUEST = 200  # PubMed API limit

    def __init__(self, api_key: str | None = None, cache: bool = False, cache_ttl: int = 3600):
        self.api_key = api_key
        self.cache = cache
        self.cache_ttl = cache_ttl  # seconds
        self._cache: dict[str, tuple[Article, float]] = {}  # pmid -> (article, timestamp)
        rate = RATE_LIMIT_WITH_KEY if api_key else RATE_LIMIT_DEFAULT
        self._rate_limiter = RateLimiter(rate)
        self._session = requests.Session()

    def clear_cache(self) -> None:
        """Clear all cached articles."""
        self._cache.clear()

    def _request(self, url: str, params: dict) -> requests.Response:
        """Make HTTP request with retry on transient errors."""
        last_error = None

        for attempt in range(self.MAX_RETRIES + 1):
            try:
                self._rate_limiter.wait()
                response = self._session.get(url, params=params, timeout=self.TIMEOUT)
                response.raise_for_status()
                return response
            except requests.ConnectionError as e:
                last_error = e
            except requests.Timeout as e:
                last_error = e
            except requests.HTTPError as e:
                # Retry on 5xx server errors and 429 rate limit
                if response.status_code >= 500 or response.status_code == 429:
                    last_error = e
                else:
                    raise APIError(str(e)) from e

            # Wait before retry (except on last attempt)
            if attempt < self.MAX_RETRIES:
                time.sleep(self.RETRY_BACKOFF * (2 ** attempt))

        raise APIError(str(last_error)) from last_error

    def search(
        self,
        query: str,
        max_results: int = 20,
        min_date: str | None = None,
        max_date: str | None = None,
    ) -> SearchResult:
        """Search PubMed for articles matching a query.

        Args:
            query: Search terms (PubMed query syntax supported).
            max_results: Maximum number of IDs to return (default 20).
            min_date: Minimum publication date (format: YYYY/MM/DD).
            max_date: Maximum publication date (format: YYYY/MM/DD).

        Returns:
            SearchResult with list of PMIDs and total count.

        Raises:
            ValueError: If max_results <= 0 or date format is invalid.
            APIError: If the PubMed API returns an error.
        """
        if max_results <= 0:
            raise ValueError("max_results must be greater than 0")
        if min_date and not DATE_PATTERN.match(min_date):
            raise ValueError("min_date must be in YYYY/MM/DD format")
        if max_date and not DATE_PATTERN.match(max_date):
            raise ValueError("max_date must be in YYYY/MM/DD format")

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "tool": "pypubmed",
        }
        if self.api_key:
            params["api_key"] = self.api_key
        if min_date:
            params["mindate"] = min_date
            params["datetype"] = "pdat"
        if max_date:
            params["maxdate"] = max_date
            params["datetype"] = "pdat"

        response = self._request(f"{BASE_URL}/esearch.fcgi", params)
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
        """Search PubMed and fetch article details in one call.

        Args:
            query: Search terms (PubMed query syntax supported).
            max_results: Maximum number of articles to return (default 20).
            min_date: Minimum publication date (format: YYYY/MM/DD).
            max_date: Maximum publication date (format: YYYY/MM/DD).

        Returns:
            List of Article objects with full details.

        Raises:
            ValueError: If max_results <= 0 or date format is invalid.
            APIError: If the PubMed API returns an error.
        """
        result = self.search(query, max_results, min_date, max_date)
        if not result.ids:
            return []
        return self.fetch(result.ids)

    def fetch(self, ids: list[str]) -> list[Article]:
        """Fetch article details by PubMed IDs.

        Args:
            ids: List of PubMed IDs (PMIDs) to fetch.

        Returns:
            List of Article objects with full details.

        Raises:
            ValueError: If ids is empty.
            APIError: If the PubMed API returns an error.

        Note:
            Large batches (>200 IDs) are automatically chunked.
        """
        if not ids:
            raise ValueError("ids cannot be empty")

        # Check cache for hits (respecting TTL)
        if self.cache:
            now = time.time()
            cached = {}
            for id in ids:
                if id in self._cache:
                    article, timestamp = self._cache[id]
                    if now - timestamp < self.cache_ttl:
                        cached[id] = article
            missing_ids = [id for id in ids if id not in cached]

            # All in cache
            if not missing_ids:
                return [cached[id] for id in ids]
        else:
            cached = {}
            missing_ids = ids

        # Fetch in chunks if needed
        fetched = []
        for i in range(0, len(missing_ids), self.MAX_IDS_PER_REQUEST):
            chunk = missing_ids[i:i + self.MAX_IDS_PER_REQUEST]
            fetched.extend(self._fetch_batch(chunk))

        # Store in cache if enabled
        if self.cache:
            now = time.time()
            for article in fetched:
                self._cache[article.pmid] = (article, now)
                cached[article.pmid] = article

        # Return in original order
        if self.cache:
            return [cached[id] for id in ids if id in cached]
        return fetched

    def _fetch_batch(self, ids: list[str]) -> list[Article]:
        """Fetch a batch of articles (max 200 IDs)."""
        params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml",
            "tool": "pypubmed",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        response = self._request(f"{BASE_URL}/efetch.fcgi", params)
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
