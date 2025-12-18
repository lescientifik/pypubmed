# pypubmed

Simple Python client for the PubMed API.

## Installation

```bash
pip install pypubmed
```

## Usage

```python
from pypubmed import PubMed

pubmed = PubMed()
# Or with API key for higher rate limit (10 req/sec vs 3 req/sec)
pubmed = PubMed(api_key="your_api_key")

# Search for articles
result = pubmed.search("CRISPR diabetes", max_results=10)
print(f"Found {result.count} articles")
print(result.ids)  # ['39344136', '39340892', ...]

# Search with date filters
result = pubmed.search("cancer", min_date="2024/01/01", max_date="2024/06/30")

# Fetch article details
articles = pubmed.fetch(result.ids)

# Or search and fetch in one call
articles = pubmed.search_and_fetch("CRISPR diabetes", max_results=10)

for article in articles:
    print(article.title)
    print(article.authors)
    print(article.abstract)
    print(article.doi)
    print(article.url)
```

## Article fields

- `pmid` - PubMed ID
- `title` - Article title
- `abstract` - Abstract text
- `authors` - List of author names
- `journal` - Journal name
- `doi` - DOI (if available)
- `url` - Link to PubMed page
- `publication_date` - Electronic publication date (when available online)
- `journal_date` - Journal issue date (print publication)

## License

MIT
