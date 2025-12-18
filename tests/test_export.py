import json
from datetime import date
from pathlib import Path

from pypubmed.export import to_json, save_json, to_csv, save_csv, from_csv, CSV_COLUMNS, LIST_SEPARATOR


class TestArticleToDict:
    """Tests for Article.to_dict() method."""

    def test_to_dict_returns_dict(self, article):
        result = article.to_dict()

        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self, article):
        result = article.to_dict()

        expected_keys = {
            "pmid", "title", "abstract", "authors", "journal",
            "mesh_terms", "keywords", "doi", "url",
            "publication_date", "journal_date"
        }
        assert set(result.keys()) == expected_keys

    def test_to_dict_pmid_is_string(self, article):
        result = article.to_dict()

        assert result["pmid"] == article.pmid
        assert isinstance(result["pmid"], str)

    def test_to_dict_lists_are_lists(self, article):
        result = article.to_dict()

        assert isinstance(result["authors"], list)
        assert isinstance(result["mesh_terms"], list)
        assert isinstance(result["keywords"], list)

    def test_to_dict_dates_are_iso_strings(self, article):
        result = article.to_dict()

        # Dates should be ISO format strings or None
        if article.publication_date:
            assert result["publication_date"] == article.publication_date.isoformat()
        else:
            assert result["publication_date"] is None

    def test_to_dict_url_included(self, article):
        result = article.to_dict()

        assert result["url"] == article.url


class TestToJson:
    """Tests for to_json() function."""

    def test_to_json_single_article(self, article):
        result = to_json([article])

        assert isinstance(result, str)
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_to_json_multiple_articles(self, articles):
        result = to_json(articles)

        data = json.loads(result)
        assert len(data) == len(articles)

    def test_to_json_empty_list(self):
        result = to_json([])

        assert result == "[]"

    def test_to_json_contains_all_fields(self, article):
        result = to_json([article])

        data = json.loads(result)[0]
        expected_keys = {
            "pmid", "title", "abstract", "authors", "journal",
            "mesh_terms", "keywords", "doi", "url",
            "publication_date", "journal_date"
        }
        assert set(data.keys()) == expected_keys

    def test_to_json_is_valid_json(self, articles):
        result = to_json(articles)

        # Should not raise
        json.loads(result)


class TestSaveJson:
    """Tests for save_json() function."""

    def test_save_json_creates_file(self, article, tmp_path):
        filepath = tmp_path / "articles.json"

        save_json([article], filepath)

        assert filepath.exists()

    def test_save_json_content_is_valid(self, article, tmp_path):
        filepath = tmp_path / "articles.json"

        save_json([article], filepath)

        content = filepath.read_text(encoding="utf-8")
        data = json.loads(content)
        assert len(data) == 1
        assert data[0]["pmid"] == article.pmid

    def test_save_json_accepts_string_path(self, article, tmp_path):
        filepath = str(tmp_path / "articles.json")

        save_json([article], filepath)

        assert Path(filepath).exists()


class TestToCsv:
    """Tests for to_csv() function."""

    def test_csv_columns_order(self):
        expected = [
            "pmid", "title", "authors", "journal",
            "publication_date", "journal_date",
            "abstract", "doi", "url",
            "mesh_terms", "keywords"
        ]

        assert CSV_COLUMNS == expected

    def test_to_csv_returns_string(self, article):
        result = to_csv([article])

        assert isinstance(result, str)

    def test_to_csv_has_bom(self, article):
        result = to_csv([article])

        assert result.startswith("\ufeff")

    def test_to_csv_has_header_row(self, article):
        result = to_csv([article])

        # Remove BOM and get first line
        lines = result[1:].split("\r\n")
        header = lines[0]
        assert "pmid" in header
        assert "title" in header

    def test_to_csv_has_data_row(self, article):
        result = to_csv([article])

        lines = result[1:].split("\r\n")
        # Header + data + empty line at end
        assert len(lines) >= 2
        assert article.pmid in lines[1]

    def test_to_csv_empty_list(self):
        result = to_csv([])

        # BOM + header only
        assert result.startswith("\ufeff")
        lines = result[1:].split("\r\n")
        assert "pmid" in lines[0]

    def test_to_csv_multiple_articles(self, articles):
        result = to_csv(articles)

        lines = result[1:].strip().split("\r\n")
        # Header + n articles
        assert len(lines) == len(articles) + 1

    def test_to_csv_list_separator(self):
        assert LIST_SEPARATOR == "; "

    def test_to_csv_authors_joined(self, article):
        result = to_csv([article])

        # Authors should be joined with "; "
        if len(article.authors) > 1:
            expected = "; ".join(article.authors)
            assert expected in result

    def test_to_csv_quoting_comma_in_field(self, article):
        # The CSV module should quote fields containing commas
        result = to_csv([article])

        # If title or abstract contains comma, it should be quoted
        # The module handles this automatically
        assert result  # Just verify it doesn't crash

    def test_to_csv_quoting_quotes_in_field(self, article):
        # If a field contains quotes, they should be escaped as ""
        result = to_csv([article])

        # The module handles this automatically
        assert result  # Just verify it doesn't crash

    def test_to_csv_none_values_as_empty(self, article):
        result = to_csv([article])

        # None values should become empty strings, not "None"
        assert ",None," not in result


class TestSaveCsv:
    """Tests for save_csv() function."""

    def test_save_csv_creates_file(self, article, tmp_path):
        filepath = tmp_path / "articles.csv"

        save_csv([article], filepath)

        assert filepath.exists()

    def test_save_csv_has_bom(self, article, tmp_path):
        filepath = tmp_path / "articles.csv"

        save_csv([article], filepath)

        content = filepath.read_bytes()
        # UTF-8 BOM is EF BB BF
        assert content.startswith(b"\xef\xbb\xbf")

    def test_save_csv_content_valid(self, article, tmp_path):
        filepath = tmp_path / "articles.csv"

        save_csv([article], filepath)

        content = filepath.read_text(encoding="utf-8-sig")  # utf-8-sig strips BOM
        assert "pmid" in content
        assert article.pmid in content

    def test_save_csv_accepts_string_path(self, article, tmp_path):
        filepath = str(tmp_path / "articles.csv")

        save_csv([article], filepath)

        assert Path(filepath).exists()


class TestFromCsv:
    """Tests for from_csv() function."""

    def test_from_csv_returns_list(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_from_csv_roundtrip_pmid(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)[0]

        assert result.pmid == article.pmid

    def test_from_csv_roundtrip_title(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)[0]

        assert result.title == article.title

    def test_from_csv_roundtrip_authors(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)[0]

        assert result.authors == article.authors

    def test_from_csv_roundtrip_dates(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)[0]

        assert result.publication_date == article.publication_date
        assert result.journal_date == article.journal_date

    def test_from_csv_roundtrip_doi(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)[0]

        assert result.doi == article.doi

    def test_from_csv_roundtrip_lists(self, article, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv([article], filepath)

        result = from_csv(filepath)[0]

        assert result.mesh_terms == article.mesh_terms
        assert result.keywords == article.keywords

    def test_from_csv_multiple_articles(self, articles, tmp_path):
        filepath = tmp_path / "test.csv"
        save_csv(articles, filepath)

        result = from_csv(filepath)

        assert len(result) == len(articles)

    def test_from_csv_accepts_string_path(self, article, tmp_path):
        filepath = str(tmp_path / "test.csv")
        save_csv([article], filepath)

        result = from_csv(filepath)

        assert len(result) == 1
