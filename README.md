# pypubmed

Simple, fast, and efficient Python client for the PubMed API.

## Installation

```bash
uv add git+https://github.com/lescientifik/pypubmed.git
```

Or with pip:

```bash
pip install git+https://github.com/lescientifik/pypubmed.git
```

## Quick Start

```python
from pypubmed import PubMed

pubmed = PubMed()
articles = pubmed.search_and_fetch("CRISPR gene editing", max_results=10)

for article in articles:
    print(f"{article.title}")
    print(f"  Authors: {', '.join(article.authors[:3])}")
    print(f"  URL: {article.url}")
```

## Features

- Search PubMed with date filters
- Fetch article details by PMID
- Export to JSON and CSV (Excel/LibreOffice compatible)
- Import from JSON and CSV
- Automatic rate limiting
- Retry on network errors
- Optional caching
- Command-line interface

## Usage

### Search

```python
from pypubmed import PubMed

pubmed = PubMed()

# Basic search
result = pubmed.search("cancer immunotherapy", max_results=100)
print(f"Found {result.count} articles, retrieved {len(result.ids)} IDs")

# Search with date filter
result = pubmed.search(
    "COVID-19",
    min_date="2024/01/01",
    max_date="2024/12/31",
)
```

### Fetch Articles

```python
# Fetch by IDs
articles = pubmed.fetch(["39344136", "39344137"])

# Search and fetch in one call
articles = pubmed.search_and_fetch("machine learning", max_results=20)
```

### Export and Import

```python
from pypubmed import save_csv, save_json, from_csv, from_json

# Export
save_csv(articles, "articles.csv")   # Excel/LibreOffice compatible
save_json(articles, "articles.json")

# Import
articles = from_csv("articles.csv")
articles = from_json(open("articles.json").read())
```

### API Key

For higher rate limits (10 req/sec instead of 3), get an [NCBI API key](https://www.ncbi.nlm.nih.gov/account/settings/):

```python
pubmed = PubMed(api_key="your_api_key")
```

### Caching

```python
pubmed = PubMed(cache=True, cache_ttl=3600)  # Cache for 1 hour

articles = pubmed.fetch(["39344136"])  # API call
articles = pubmed.fetch(["39344136"])  # From cache

pubmed.clear_cache()
```

## Command-Line Interface

```bash
# Search
pypubmed search "CRISPR" --max 10
pypubmed search "cancer" --csv results.csv
pypubmed search "COVID-19" --json results.json

# Fetch by PMID
pypubmed fetch 39344136 39344137
pypubmed fetch 39344136 --csv article.csv

# With API key
pypubmed --api-key YOUR_KEY search "query"
```

## Article Fields

| Field | Type | Description |
|-------|------|-------------|
| `pmid` | `str` | PubMed ID |
| `title` | `str` | Article title |
| `abstract` | `str` | Abstract text |
| `authors` | `list[str]` | Author names |
| `journal` | `str` | Journal name |
| `doi` | `str \| None` | DOI identifier |
| `url` | `str` | PubMed URL |
| `mesh_terms` | `list[str]` | MeSH terms |
| `keywords` | `list[str]` | Author keywords |
| `publication_date` | `date \| None` | Electronic publication date |
| `journal_date` | `date \| None` | Print publication date |

## License

MIT
