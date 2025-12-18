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

# Search for articles
result = pubmed.search("CRISPR diabetes", max_results=10)
print(f"Found {result.count} articles")
print(result.ids)  # ['39344136', '39340892', ...]

# Fetch article details
articles = pubmed.fetch(result.ids)

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
- `doi` - DOI (if available)
- `url` - Link to PubMed page

## License

MIT
