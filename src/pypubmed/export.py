"""Export functions for PubMed articles."""
import csv
import io
import json
from pathlib import Path

from pypubmed.client import Article


# CSV column order (abstract at end because it's often long)
CSV_COLUMNS = [
    "pmid", "title", "authors", "journal",
    "publication_date", "journal_date",
    "abstract", "doi", "url",
    "mesh_terms", "keywords"
]

# Separator for list fields (authors, mesh_terms, keywords)
LIST_SEPARATOR = "; "


def to_json(articles: list[Article]) -> str:
    """Convert articles to JSON string.

    Args:
        articles: List of Article objects to convert.

    Returns:
        JSON string representation of articles.
    """
    return json.dumps([article.to_dict() for article in articles])


def save_json(articles: list[Article], path: str | Path) -> None:
    """Save articles to a JSON file.

    Args:
        articles: List of Article objects to save.
        path: File path (string or Path object).
    """
    Path(path).write_text(to_json(articles), encoding="utf-8")


def _article_to_csv_row(article: Article) -> list[str]:
    """Convert an article to a list of CSV values."""
    data = article.to_dict()
    row = []
    for col in CSV_COLUMNS:
        value = data[col]
        if isinstance(value, list):
            row.append(LIST_SEPARATOR.join(value))
        elif value is None:
            row.append("")
        else:
            row.append(str(value))
    return row


def to_csv(articles: list[Article]) -> str:
    """Convert articles to CSV string with UTF-8 BOM.

    Args:
        articles: List of Article objects to convert.

    Returns:
        CSV string with BOM for Excel/LibreOffice compatibility.
        List fields (authors, mesh_terms, keywords) are joined with "; ".
    """
    output = io.StringIO()
    output.write("\ufeff")  # UTF-8 BOM

    writer = csv.writer(output, dialect="excel")
    writer.writerow(CSV_COLUMNS)

    for article in articles:
        writer.writerow(_article_to_csv_row(article))

    return output.getvalue()


def save_csv(articles: list[Article], path: str | Path) -> None:
    """Save articles to a CSV file with UTF-8 BOM.

    Args:
        articles: List of Article objects to save.
        path: File path (string or Path object).
    """
    Path(path).write_text(to_csv(articles), encoding="utf-8")
